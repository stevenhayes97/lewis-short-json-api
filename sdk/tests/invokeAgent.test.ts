import assert from "node:assert/strict";
import { afterEach, beforeEach, test } from "node:test";

import {
  invokeAgent,
  listRegisteredAgents,
  registerAgent,
  resetAgents,
  toCreateOptions,
  UnknownAgentError,
  type CursorSdk,
} from "../invokeAgent.ts";

function fakeSdk(overrides: Partial<CursorSdk["Agent"]> = {}): {
  sdk: CursorSdk;
  created: unknown[];
  prompted: unknown[];
  resumed: unknown[];
} {
  const created: unknown[] = [];
  const prompted: unknown[] = [];
  const resumed: unknown[] = [];
  const agent = {
    agentId: "agent-created",
    prompts: [] as string[],
    async send(prompt: string) {
      this.prompts.push(prompt);
      return {
        id: "run-1",
        agentId: this.agentId,
        status: "finished",
        result: `ok:${prompt}`,
        async wait() {
          return this;
        },
      };
    },
  };

  const sdk: CursorSdk = {
    Agent: {
      async create(options) {
        created.push(options);
        return agent;
      },
      async prompt(message, options) {
        prompted.push([message, options]);
        return {
          result: `oneshot:${message}`,
          agentId: "agent-oneshot",
          status: "finished",
        };
      },
      async list() {
        return { items: [] };
      },
      async resume(agentId, options) {
        resumed.push([agentId, options]);
        return { ...agent, agentId };
      },
      ...overrides,
    },
  };
  return { sdk, created, prompted, resumed };
}

beforeEach(async () => {
  await resetAgents();
});

afterEach(async () => {
  await resetAgents();
});

test("invokeAgent creates a local agent for an unregistered name", async () => {
  const { sdk, created } = fakeSdk();
  const result = await invokeAgent("reviewer", "look at translate.py", { sdk });

  assert.equal(result.name, "reviewer");
  assert.equal(result.text, "ok:look at translate.py");
  assert.equal(result.agentId, "agent-created");
  assert.equal(created.length, 1);
  const options = created[0] as Record<string, unknown>;
  assert.equal(options.name, "reviewer");
  assert.deepEqual(options.model, { id: "composer-2.5" });
  assert.ok(options.local);
});

test("second call reuses the live session", async () => {
  const { sdk, created } = fakeSdk();
  await invokeAgent("reviewer", "first", { sdk });
  const second = await invokeAgent("reviewer", "second", { sdk });

  assert.equal(created.length, 1);
  assert.equal(second.text, "ok:second");
});

test("registerAgent applies a cloud recipe", async () => {
  registerAgent("cloud-fix", {
    runtime: "cloud",
    model: "gpt-5.5",
    repos: [{ url: "https://github.com/org/repo", startingRef: "main" }],
    autoCreatePR: true,
  });
  const { sdk, created } = fakeSdk();
  await invokeAgent("cloud-fix", "open a PR", { sdk });

  const options = created[0] as Record<string, any>;
  assert.deepEqual(options.model, { id: "gpt-5.5" });
  assert.equal(options.cloud.autoCreatePR, true);
  assert.equal(options.cloud.repos[0].url, "https://github.com/org/repo");
  assert.equal(options.local, undefined);
});

test("oneshot uses Agent.prompt and does not keep a session", async () => {
  const { sdk, created, prompted } = fakeSdk();
  await invokeAgent("reviewer", "once", { sdk, oneshot: true });
  await invokeAgent("reviewer", "twice", { sdk, oneshot: true });

  assert.equal(prompted.length, 2);
  assert.equal(created.length, 0);
});

test("requireRegistered rejects unknown names", async () => {
  const { sdk } = fakeSdk();
  await assert.rejects(
    () => invokeAgent("missing", "hi", { sdk, requireRegistered: true }),
    UnknownAgentError,
  );
});

test("empty name is rejected", async () => {
  const { sdk } = fakeSdk();
  await assert.rejects(() => invokeAgent("  ", "hi", { sdk }), /non-empty/);
});

test("resumes the newest listed agent with the same name", async () => {
  const { sdk, created, resumed } = fakeSdk({
    async list() {
      return {
        items: [
          { name: "reviewer", agentId: "agent-old", lastModified: 1 },
          { name: "reviewer", agentId: "agent-new", lastModified: 9 },
        ],
      };
    },
  });
  const result = await invokeAgent("reviewer", "continue", { sdk });

  assert.equal(resumed[0][0], "agent-new");
  assert.equal(created.length, 0);
  assert.equal(result.agentId, "agent-new");
});

test("listRegisteredAgents is sorted", () => {
  registerAgent("zeta");
  registerAgent("alpha");
  assert.deepEqual(listRegisteredAgents(), ["alpha", "zeta"]);
});

test("defaultPrompt allows a name-only call", async () => {
  registerAgent("reviewer", { defaultPrompt: "Review the current diff" });
  const { sdk } = fakeSdk();
  const result = await invokeAgent("reviewer", { sdk });
  assert.equal(result.text, "ok:Review the current diff");
});

test("toCreateOptions uses the given cwd", () => {
  const options = toCreateOptions({ name: "n", cwd: "/tmp/work" });
  assert.deepEqual((options.local as { cwd: string }).cwd, "/tmp/work");
});
