/**
 * Call a Cursor agent by name from anywhere in TypeScript.
 *
 * The Cursor SDK wants `Agent.create(...)` then `agent.send(...)`. This
 * module hides that behind one function:
 *
 *     import { invokeAgent } from "./invokeAgent.js";
 *
 *     const result = await invokeAgent("reviewer", "Review api/services/translate.py");
 *     console.log(result.text);
 *
 * `name` is the only required identity. Unregistered names still work: they
 * create a local agent with that display name and the default model. Call
 * `registerAgent` when a name needs its own model, runtime, tools, or cloud
 * repos.
 *
 * Requires `npm install @cursor/sdk` (Node.js 22.13+) and `CURSOR_API_KEY`
 * (or `apiKey` on the spec). See https://cursor.com/docs/sdk/typescript
 */

export const DEFAULT_MODEL = "composer-2.5";

export type Runtime = "local" | "cloud";
export type Mode = "agent" | "plan";

export type CloudRepo = {
  url: string;
  startingRef?: string;
  prUrl?: string;
};

export type AgentSpec = {
  name: string;
  model?: string;
  runtime?: Runtime;
  cwd?: string;
  apiKey?: string;
  tools?: string[];
  disallowedTools?: string[];
  repos?: CloudRepo[];
  autoCreatePR?: boolean;
  workOnCurrentBranch?: boolean;
  envVars?: Record<string, string>;
  metadata?: Record<string, string>;
  mcpServers?: Record<string, unknown>;
  agents?: Record<string, unknown>;
  mode?: Mode;
  settingSources?: string[];
  defaultPrompt?: string;
};

export type InvokeResult = {
  name: string;
  agentId: string;
  text: string;
  status?: string;
  runId?: string;
};

export type InvokeOptions = Partial<Omit<AgentSpec, "name">> & {
  oneshot?: boolean;
  resume?: boolean;
  requireRegistered?: boolean;
  /** Injectable Cursor SDK surface for tests. */
  sdk?: CursorSdk;
};

/** Minimal SDK surface this wrapper actually calls. */
export type CursorSdk = {
  Agent: {
    create: (options: Record<string, unknown>) => Promise<SdkAgent> | SdkAgent;
    prompt?: (
      message: string,
      options: Record<string, unknown>,
    ) => Promise<SdkRunResult> | SdkRunResult;
    list?: (options?: Record<string, unknown>) => Promise<SdkListResult> | SdkListResult;
    resume?: (
      agentId: string,
      options?: Record<string, unknown>,
    ) => Promise<SdkAgent> | SdkAgent;
  };
};

type SdkAgent = {
  agentId: string;
  send: (message: string) => Promise<SdkRun> | SdkRun;
  close?: () => void | Promise<void>;
};

type SdkRun = {
  id?: string;
  agentId?: string;
  status?: string;
  result?: string;
  wait?: () => Promise<SdkRunResult> | SdkRunResult;
};

type SdkRunResult = {
  result?: string;
  text?: string;
  status?: string;
  id?: string;
  agentId?: string;
  agent_id?: string;
};

type SdkListResult = {
  items?: Array<{
    name?: string;
    agentId?: string;
    agent_id?: string;
    lastModified?: number;
    last_modified?: number;
  }>;
};

const registry = new Map<string, AgentSpec>();
const sessions = new Map<string, SdkAgent>();

export class UnknownAgentError extends Error {
  constructor(name: string) {
    super(`no agent registered as "${name}"; call registerAgent("${name}", ...)`);
    this.name = "UnknownAgentError";
  }
}

export function registerAgent(name: string, spec: Omit<AgentSpec, "name"> = {}): AgentSpec {
  const stored: AgentSpec = { ...spec, name };
  registry.set(name, stored);
  void dropSession(name);
  return stored;
}

export function registeredAgent(name: string): AgentSpec | undefined {
  return registry.get(name);
}

export function listRegisteredAgents(): string[] {
  return [...registry.keys()].sort();
}

export async function invokeAgent(
  name: string,
  prompt?: string,
  options?: InvokeOptions,
): Promise<InvokeResult>;
export async function invokeAgent(name: string, options?: InvokeOptions): Promise<InvokeResult>;
export async function invokeAgent(
  name: string,
  promptOrOptions?: string | InvokeOptions,
  options: InvokeOptions = {},
): Promise<InvokeResult> {
  if (!name || !name.trim()) {
    throw new Error("agent name must be a non-empty string");
  }

  const prompt = typeof promptOrOptions === "string" ? promptOrOptions : undefined;
  const resolvedOptions =
    promptOrOptions != null && typeof promptOrOptions === "object" ? promptOrOptions : options;
  const { oneshot = false, resume = true, requireRegistered = false, sdk, ...overrides } =
    resolvedOptions;
  const spec = resolveSpec(name, requireRegistered, overrides);
  const message = prompt ?? spec.defaultPrompt;
  if (message == null) {
    throw new Error(
      `prompt is required unless registerAgent("${name}", { defaultPrompt }) was set`,
    );
  }
  const client = sdk ?? (await loadSdk());

  if (oneshot) {
    if (!client.Agent.prompt) {
      throw new Error("sdk.Agent.prompt is not available");
    }
    const payload = await client.Agent.prompt(message, toCreateOptions(spec));
    return resultFromRun(name, payload, payload.agentId ?? payload.agent_id ?? "");
  }

  const agent = await getOrCreateAgent(spec, client, resume);
  const run = await agent.send(message);
  const payload = await waitForRun(run);
  const agentId = agent.agentId || payload.agentId || payload.agent_id || "";
  return resultFromRun(name, payload, agentId);
}

export async function getAgent(
  name: string,
  options: InvokeOptions = {},
): Promise<SdkAgent> {
  const { resume = true, requireRegistered = false, sdk, ...overrides } = options;
  const spec = resolveSpec(name, requireRegistered, overrides);
  const client = sdk ?? (await loadSdk());
  return getOrCreateAgent(spec, client, resume);
}

export async function closeAgent(name: string): Promise<void> {
  await dropSession(name);
}

export async function closeAllAgents(): Promise<void> {
  await Promise.all([...sessions.keys()].map((name) => dropSession(name)));
}

/** Drop live handles and registered recipes. For tests and process teardown. */
export async function resetAgents(): Promise<void> {
  await closeAllAgents();
  registry.clear();
}

function resolveSpec(
  name: string,
  requireRegistered: boolean,
  overrides: Partial<Omit<AgentSpec, "name">>,
): AgentSpec {
  const registered = registry.get(name);
  if (!registered && requireRegistered) {
    throw new UnknownAgentError(name);
  }
  return {
    model: DEFAULT_MODEL,
    runtime: "local",
    ...registered,
    ...overrides,
    name,
  };
}

async function getOrCreateAgent(
  spec: AgentSpec,
  client: CursorSdk,
  resume: boolean,
): Promise<SdkAgent> {
  const existing = sessions.get(spec.name);
  if (existing) {
    return existing;
  }

  let agent: SdkAgent | undefined;
  if (resume) {
    agent = await resumeByName(spec, client);
  }
  if (!agent) {
    agent = await client.Agent.create(toCreateOptions(spec));
  }
  sessions.set(spec.name, agent);
  return agent;
}

async function resumeByName(spec: AgentSpec, client: CursorSdk): Promise<SdkAgent | undefined> {
  if (!client.Agent.list || !client.Agent.resume) {
    return undefined;
  }

  const listOptions: Record<string, unknown> = { runtime: spec.runtime ?? "local" };
  if (spec.runtime !== "cloud") {
    listOptions.cwd = spec.cwd ?? process.cwd();
  } else if (spec.apiKey) {
    listOptions.apiKey = spec.apiKey;
  }

  let listed: SdkListResult;
  try {
    listed = await client.Agent.list(listOptions);
  } catch {
    return undefined;
  }

  const matches = (listed.items ?? []).filter((item) => item.name === spec.name);
  if (matches.length === 0) {
    return undefined;
  }
  const newest = matches.reduce((best, item) => {
    const score = item.lastModified ?? item.last_modified ?? 0;
    const bestScore = best.lastModified ?? best.last_modified ?? 0;
    return score >= bestScore ? item : best;
  });
  const agentId = newest.agentId ?? newest.agent_id;
  if (!agentId) {
    return undefined;
  }
  try {
    return await client.Agent.resume(agentId, toCreateOptions(spec));
  } catch {
    return undefined;
  }
}

export function toCreateOptions(spec: AgentSpec): Record<string, unknown> {
  const options: Record<string, unknown> = {
    name: spec.name,
    model: { id: spec.model ?? DEFAULT_MODEL },
  };
  const apiKey = spec.apiKey ?? process.env.CURSOR_API_KEY;
  if (apiKey) {
    options.apiKey = apiKey;
  }
  if (spec.tools) {
    options.tools = spec.tools;
  }
  if (spec.disallowedTools) {
    options.disallowedTools = spec.disallowedTools;
  }
  if (spec.mcpServers) {
    options.mcpServers = spec.mcpServers;
  }
  if (spec.agents) {
    options.agents = spec.agents;
  }
  if (spec.mode) {
    options.mode = spec.mode;
  }

  if (spec.runtime === "cloud") {
    const cloud: Record<string, unknown> = {
      autoCreatePR: spec.autoCreatePR ?? false,
      workOnCurrentBranch: spec.workOnCurrentBranch ?? false,
    };
    if (spec.repos) {
      cloud.repos = spec.repos;
    }
    if (spec.envVars) {
      cloud.envVars = spec.envVars;
    }
    if (spec.metadata) {
      cloud.metadata = spec.metadata;
    }
    options.cloud = cloud;
  } else {
    const local: Record<string, unknown> = { cwd: spec.cwd ?? process.cwd() };
    if (spec.settingSources) {
      local.settingSources = spec.settingSources;
    }
    options.local = local;
  }
  return options;
}

async function waitForRun(run: SdkRun): Promise<SdkRunResult> {
  if (typeof run.wait === "function") {
    return run.wait();
  }
  return run;
}

function resultFromRun(name: string, payload: SdkRunResult, agentId: string): InvokeResult {
  const text = payload.result ?? payload.text ?? "";
  return {
    name,
    agentId,
    text: String(text),
    status: payload.status,
    runId: payload.id,
  };
}

async function dropSession(name: string): Promise<void> {
  const agent = sessions.get(name);
  sessions.delete(name);
  if (agent?.close) {
    try {
      await agent.close();
    } catch {
      // Disposal is best-effort; the map entry is already gone.
    }
  }
}

async function loadSdk(): Promise<CursorSdk> {
  try {
    return (await import("@cursor/sdk")) as CursorSdk;
  } catch (error) {
    throw new Error(
      "The Cursor TypeScript SDK is not installed. Run: npm install @cursor/sdk",
      { cause: error },
    );
  }
}
