"""Call a Cursor agent by name from anywhere in Python.

The Cursor SDK wants ``Agent.create(...)`` then ``agent.send(...)``. This
module hides that behind one function:

    from sdk.cursor_agents import invoke_agent, register_agent

    register_agent("reviewer", default_prompt="Review the current diff")
    result = invoke_agent("reviewer")
    print(result.text)

``name`` is the only required identity. Unregistered names still work: they
create a local agent with that display name and the default model. Call
:func:`register_agent` when a name needs its own model, runtime, tools, or
cloud repos.

Requires ``pip install cursor-sdk`` and ``CURSOR_API_KEY`` (or ``api_key=``).
See https://cursor.com/docs/sdk/python
"""

from __future__ import annotations

import os
import threading
from dataclasses import dataclass, field, replace
from typing import Any, Literal, Mapping, Sequence

DEFAULT_MODEL = "composer-2.5"
Runtime = Literal["local", "cloud"]
Mode = Literal["agent", "plan"]


@dataclass(frozen=True)
class AgentSpec:
    """Recipe for a named agent. ``name`` is what :func:`invoke_agent` looks up."""

    name: str
    model: str = DEFAULT_MODEL
    runtime: Runtime = "local"
    cwd: str | None = None
    api_key: str | None = None
    tools: tuple[str, ...] | None = None
    disallowed_tools: tuple[str, ...] | None = None
    repos: tuple[Mapping[str, str], ...] | None = None
    auto_create_pr: bool = False
    work_on_current_branch: bool = False
    env_vars: Mapping[str, str] | None = None
    metadata: Mapping[str, str] | None = None
    mcp_servers: Mapping[str, Any] | None = None
    agents: Mapping[str, Any] | None = None
    mode: Mode | None = None
    setting_sources: tuple[str, ...] | None = None
    default_prompt: str | None = None


@dataclass(frozen=True)
class InvokeResult:
    """Outcome of one :func:`invoke_agent` call."""

    name: str
    agent_id: str
    text: str
    status: str | None = None
    run_id: str | None = None


# Process-wide registry and live handles. A lock keeps get-or-create atomic
# when two callers hit the same name at once.
_lock = threading.RLock()
_REGISTRY: dict[str, AgentSpec] = {}
_SESSIONS: dict[str, Any] = {}


class UnknownAgentError(KeyError):
    """Raised only when ``require_registered=True`` and ``name`` is not in the registry."""


def register_agent(
    name: str,
    *,
    model: str = DEFAULT_MODEL,
    runtime: Runtime = "local",
    cwd: str | None = None,
    api_key: str | None = None,
    tools: Sequence[str] | None = None,
    disallowed_tools: Sequence[str] | None = None,
    repos: Sequence[Mapping[str, str]] | None = None,
    auto_create_pr: bool = False,
    work_on_current_branch: bool = False,
    env_vars: Mapping[str, str] | None = None,
    metadata: Mapping[str, str] | None = None,
    mcp_servers: Mapping[str, Any] | None = None,
    agents: Mapping[str, Any] | None = None,
    mode: Mode | None = None,
    setting_sources: Sequence[str] | None = None,
    default_prompt: str | None = None,
) -> AgentSpec:
    """Remember how to build the agent called ``name``.

    Later ``invoke_agent(name, prompt)`` uses this recipe. Re-registering the
    same name replaces the recipe and drops any live session for that name.
    """
    spec = AgentSpec(
        name=name,
        model=model,
        runtime=runtime,
        cwd=cwd,
        api_key=api_key,
        tools=tuple(tools) if tools is not None else None,
        disallowed_tools=tuple(disallowed_tools) if disallowed_tools is not None else None,
        repos=tuple(dict(repo) for repo in repos) if repos is not None else None,
        auto_create_pr=auto_create_pr,
        work_on_current_branch=work_on_current_branch,
        env_vars=dict(env_vars) if env_vars is not None else None,
        metadata=dict(metadata) if metadata is not None else None,
        mcp_servers=dict(mcp_servers) if mcp_servers is not None else None,
        agents=dict(agents) if agents is not None else None,
        mode=mode,
        setting_sources=tuple(setting_sources) if setting_sources is not None else None,
        default_prompt=default_prompt,
    )
    with _lock:
        _REGISTRY[name] = spec
        _drop_session(name)
    return spec


def registered_agent(name: str) -> AgentSpec | None:
    """Return the registered recipe for ``name``, or ``None``."""
    with _lock:
        return _REGISTRY.get(name)


def list_registered_agents() -> tuple[str, ...]:
    """Registered names, sorted."""
    with _lock:
        return tuple(sorted(_REGISTRY))


def invoke_agent(
    name: str,
    prompt: str | None = None,
    *,
    oneshot: bool = False,
    resume: bool = True,
    require_registered: bool = False,
    sdk: Any | None = None,
    **overrides: Any,
) -> InvokeResult:
    """Create or reuse the Cursor agent called ``name`` and send ``prompt``.

    Parameters
    ----------
    name:
        Registry key and the SDK display name passed to ``Agent.create``.
    prompt:
        The user message for this run.
    oneshot:
        If true, use ``Agent.prompt`` (create, run, dispose). No session is kept.
    resume:
        If true (default), reuse a live handle for ``name``, or ``Agent.resume``
        an existing agent that already has this display name.
    require_registered:
        If true, raise :class:`UnknownAgentError` when ``name`` was never
        registered. Default is to fall back to a local agent with defaults.
    sdk:
        Injectable Cursor SDK surface for tests. Production code leaves this
        unset and loads ``cursor_sdk`` on first use.
    **overrides:
        Per-call fields that replace the registered recipe (``model``,
        ``runtime``, ``cwd``, ``api_key``, ``tools``, …).
    """
    if not name or not str(name).strip():
        raise ValueError("agent name must be a non-empty string")

    spec = _resolve_spec(name, require_registered=require_registered, **overrides)
    message = prompt if prompt is not None else spec.default_prompt
    if message is None:
        raise ValueError(
            f"prompt is required unless register_agent({name!r}, default_prompt=...) was set"
        )
    client = sdk if sdk is not None else _load_sdk()

    if oneshot:
        result = client.Agent.prompt(message, _to_create_options(spec, client))
        return _result_from_run(name, result, agent_id=getattr(result, "agent_id", "") or "")

    agent = _get_or_create_agent(spec, client, resume=resume)
    run = agent.send(message)
    payload = _wait_for_run(run)
    agent_id = getattr(agent, "agent_id", None) or getattr(payload, "agent_id", "") or ""
    return _result_from_run(name, payload, agent_id=agent_id)


def get_agent(
    name: str,
    *,
    resume: bool = True,
    require_registered: bool = False,
    sdk: Any | None = None,
    **overrides: Any,
) -> Any:
    """Return a live SDK agent handle for ``name``, creating it if needed.

    Use this when you want ``agent.send`` / streaming yourself instead of the
    one-call :func:`invoke_agent` helper.
    """
    spec = _resolve_spec(name, require_registered=require_registered, **overrides)
    client = sdk if sdk is not None else _load_sdk()
    return _get_or_create_agent(spec, client, resume=resume)


def close_agent(name: str) -> None:
    """Dispose the live handle for ``name``, if one exists."""
    with _lock:
        _drop_session(name)


def close_all_agents() -> None:
    """Dispose every live handle. Registry recipes are left in place."""
    with _lock:
        for name in list(_SESSIONS):
            _drop_session(name)


def reset_agents() -> None:
    """Drop live handles and registered recipes. For tests and process teardown."""
    with _lock:
        for name in list(_SESSIONS):
            _drop_session(name)
        _REGISTRY.clear()


def _resolve_spec(name: str, *, require_registered: bool, **overrides: Any) -> AgentSpec:
    with _lock:
        spec = _REGISTRY.get(name)
    if spec is None:
        if require_registered:
            raise UnknownAgentError(
                f"no agent registered as {name!r}; call register_agent({name!r}, ...)"
            )
        spec = AgentSpec(name=name)
    if not overrides:
        return spec

    allowed = {key for key in AgentSpec.__dataclass_fields__ if key != "name"}
    unknown = set(overrides) - allowed
    if unknown:
        raise TypeError(f"unknown invoke_agent override(s): {sorted(unknown)}")

    cooked: dict[str, Any] = {}
    for key, value in overrides.items():
        if key in {"tools", "disallowed_tools", "setting_sources"} and value is not None:
            cooked[key] = tuple(value)
        elif key == "repos" and value is not None:
            cooked[key] = tuple(dict(repo) for repo in value)
        elif key in {"env_vars", "metadata", "mcp_servers", "agents"} and value is not None:
            cooked[key] = dict(value)
        else:
            cooked[key] = value
    return replace(spec, **cooked)


def _get_or_create_agent(spec: AgentSpec, client: Any, *, resume: bool) -> Any:
    with _lock:
        existing = _SESSIONS.get(spec.name)
        if existing is not None:
            return existing

        agent = None
        if resume:
            agent = _resume_by_name(spec, client)
        if agent is None:
            created = client.Agent.create(_to_create_options(spec, client))
            agent = created
        _SESSIONS[spec.name] = agent
        return agent


def _resume_by_name(spec: AgentSpec, client: Any) -> Any | None:
    """Resume the newest listed agent whose display name matches ``spec.name``."""
    list_fn = getattr(client.Agent, "list", None)
    resume_fn = getattr(client.Agent, "resume", None)
    if list_fn is None or resume_fn is None:
        return None

    list_kwargs: dict[str, Any] = {"runtime": spec.runtime}
    if spec.runtime == "local":
        list_kwargs["cwd"] = spec.cwd or os.getcwd()
    elif spec.api_key:
        list_kwargs["api_key"] = spec.api_key

    try:
        listed = list_fn(**list_kwargs)
    except TypeError:
        try:
            listed = list_fn()
        except Exception:
            return None
    except Exception:
        return None

    items = getattr(listed, "items", listed)
    if isinstance(listed, Mapping):
        items = listed.get("items", [])
    matches = [
        item
        for item in items or []
        if getattr(item, "name", None) == spec.name
        or (isinstance(item, Mapping) and item.get("name") == spec.name)
    ]
    if not matches:
        return None

    def _modified(item: Any) -> float:
        if isinstance(item, Mapping):
            return float(item.get("lastModified") or item.get("last_modified") or 0)
        return float(getattr(item, "last_modified", None) or getattr(item, "lastModified", 0) or 0)

    newest = max(matches, key=_modified)
    agent_id = (
        newest.get("agentId") or newest.get("agent_id")
        if isinstance(newest, Mapping)
        else getattr(newest, "agent_id", None) or getattr(newest, "agentId", None)
    )
    if not agent_id:
        return None

    resume_options = _to_create_options(spec, client)
    try:
        return resume_fn(agent_id, resume_options)
    except TypeError:
        try:
            return resume_fn(agent_id)
        except Exception:
            return None
    except Exception:
        return None


def _to_create_options(spec: AgentSpec, client: Any) -> Any:
    """Build the object ``Agent.create`` / ``Agent.prompt`` expect."""
    options: dict[str, Any] = {
        "name": spec.name,
        "model": spec.model,
    }
    api_key = spec.api_key or os.environ.get("CURSOR_API_KEY")
    if api_key:
        options["api_key"] = api_key
    if spec.tools is not None:
        options["tools"] = list(spec.tools)
    if spec.disallowed_tools is not None:
        options["disallowed_tools"] = list(spec.disallowed_tools)
    if spec.mcp_servers is not None:
        options["mcp_servers"] = dict(spec.mcp_servers)
    if spec.agents is not None:
        options["agents"] = dict(spec.agents)
    if spec.mode is not None:
        options["mode"] = spec.mode

    if spec.runtime == "cloud":
        cloud: dict[str, Any] = {
            "auto_create_pr": spec.auto_create_pr,
            "work_on_current_branch": spec.work_on_current_branch,
        }
        if spec.repos is not None:
            cloud["repos"] = [dict(repo) for repo in spec.repos]
        if spec.env_vars is not None:
            cloud["env_vars"] = dict(spec.env_vars)
        if spec.metadata is not None:
            cloud["metadata"] = dict(spec.metadata)
        cloud_cls = getattr(client, "CloudAgentOptions", None)
        repo_cls = getattr(client, "CloudRepository", None)
        if cloud_cls is not None:
            repos = cloud.pop("repos", None)
            if repos is not None and repo_cls is not None:
                built = []
                for repo in repos:
                    try:
                        built.append(repo_cls(**_snake_repo(repo)))
                    except TypeError:
                        built.append(repo)
                cloud["repos"] = built
            try:
                options["cloud"] = cloud_cls(**cloud)
            except TypeError:
                options["cloud"] = cloud
        else:
            options["cloud"] = cloud
    else:
        local: dict[str, Any] = {"cwd": spec.cwd or os.getcwd()}
        if spec.setting_sources is not None:
            local["setting_sources"] = list(spec.setting_sources)
        local_cls = getattr(client, "LocalAgentOptions", None)
        if local_cls is not None:
            try:
                options["local"] = local_cls(**local)
            except TypeError:
                options["local"] = local
        else:
            options["local"] = local

    options_cls = getattr(client, "AgentOptions", None)
    if options_cls is not None:
        try:
            return options_cls(**options)
        except TypeError:
            return options
    return options


def _snake_repo(repo: Mapping[str, str]) -> dict[str, str]:
    out = dict(repo)
    if "startingRef" in out and "starting_ref" not in out:
        out["starting_ref"] = out.pop("startingRef")
    if "prUrl" in out and "pr_url" not in out:
        out["pr_url"] = out.pop("prUrl")
    return out


def _wait_for_run(run: Any) -> Any:
    text_fn = getattr(run, "text", None)
    if callable(text_fn):
        try:
            return text_fn()
        except TypeError:
            pass
    wait_fn = getattr(run, "wait", None)
    if callable(wait_fn):
        return wait_fn()
    return run


def _result_from_run(name: str, payload: Any, *, agent_id: str) -> InvokeResult:
    if isinstance(payload, str):
        return InvokeResult(name=name, agent_id=agent_id, text=payload)
    text = (
        getattr(payload, "result", None)
        or getattr(payload, "text", None)
        or (payload.get("result") if isinstance(payload, Mapping) else None)
        or (payload.get("text") if isinstance(payload, Mapping) else None)
        or ""
    )
    if callable(text):
        text = text()
    status = getattr(payload, "status", None)
    if isinstance(payload, Mapping):
        status = payload.get("status", status)
        agent_id = agent_id or payload.get("agent_id") or payload.get("agentId") or ""
    run_id = getattr(payload, "id", None) or getattr(payload, "run_id", None)
    if isinstance(payload, Mapping):
        run_id = payload.get("id") or payload.get("run_id") or run_id
    return InvokeResult(
        name=name,
        agent_id=str(agent_id or getattr(payload, "agent_id", "") or ""),
        text=str(text),
        status=str(status) if status is not None else None,
        run_id=str(run_id) if run_id is not None else None,
    )


def _drop_session(name: str) -> None:
    agent = _SESSIONS.pop(name, None)
    if agent is None:
        return
    close = getattr(agent, "close", None)
    if callable(close):
        try:
            close()
        except Exception:
            pass


def _load_sdk() -> Any:
    try:
        import cursor_sdk
    except ImportError as exc:
        raise ImportError(
            "The Cursor Python SDK is not installed. Run: pip install cursor-sdk"
        ) from exc

    @dataclass
    class _Sdk:
        Agent: Any = field(default=cursor_sdk.Agent)
        AgentOptions: Any = field(default=getattr(cursor_sdk, "AgentOptions", None))
        LocalAgentOptions: Any = field(default=getattr(cursor_sdk, "LocalAgentOptions", None))
        CloudAgentOptions: Any = field(default=getattr(cursor_sdk, "CloudAgentOptions", None))
        CloudRepository: Any = field(default=getattr(cursor_sdk, "CloudRepository", None))

    return _Sdk()
