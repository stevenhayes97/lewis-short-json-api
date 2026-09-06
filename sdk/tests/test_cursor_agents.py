"""Unit tests for the named Cursor agent wrapper.

These mock the SDK surface so they run without cursor-sdk or an API key.
"""

from __future__ import annotations

import os
import sys
import unittest
from types import SimpleNamespace

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from sdk.cursor_agents import (  # noqa: E402
    AgentSpec,
    UnknownAgentError,
    _to_create_options,
    invoke_agent,
    list_registered_agents,
    register_agent,
    reset_agents,
)


class FakeRun:
    def __init__(self, text, *, run_id="run-1", agent_id="agent-1", status="finished"):
        self._text = text
        self.id = run_id
        self.agent_id = agent_id
        self.status = status
        self.result = text

    def text(self):
        return self

    def wait(self):
        return self


class FakeAgent:
    def __init__(self, agent_id="agent-1"):
        self.agent_id = agent_id
        self.prompts = []
        self.closed = False

    def send(self, prompt):
        self.prompts.append(prompt)
        return FakeRun(f"ok:{prompt}", agent_id=self.agent_id)

    def close(self):
        self.closed = True


class FakeSdk:
    def __init__(self, *, listed=None, resume_agent=None):
        self.created = []
        self.prompted = []
        self.resumed = []
        self.listed = listed or SimpleNamespace(items=[])
        self.resume_agent = resume_agent
        self.Agent = SimpleNamespace(
            create=self.create,
            prompt=self.prompt,
            list=self.list,
            resume=self.resume,
        )
        self.AgentOptions = None
        self.LocalAgentOptions = None
        self.CloudAgentOptions = None
        self.CloudRepository = None

    def create(self, options):
        self.created.append(options)
        return FakeAgent(agent_id="agent-created")

    def prompt(self, message, options):
        self.prompted.append((message, options))
        return FakeRun(f"oneshot:{message}", agent_id="agent-oneshot")

    def list(self, **kwargs):
        return self.listed

    def resume(self, agent_id, options=None):
        self.resumed.append((agent_id, options))
        return self.resume_agent or FakeAgent(agent_id=agent_id)


class CursorAgentsTests(unittest.TestCase):
    def setUp(self):
        reset_agents()

    def tearDown(self):
        reset_agents()

    def test_invoke_unregistered_name_creates_local_agent(self):
        sdk = FakeSdk()
        result = invoke_agent("reviewer", "look at translate.py", sdk=sdk)

        self.assertEqual(result.name, "reviewer")
        self.assertEqual(result.text, "ok:look at translate.py")
        self.assertEqual(result.agent_id, "agent-created")
        self.assertEqual(len(sdk.created), 1)
        options = sdk.created[0]
        self.assertEqual(options["name"], "reviewer")
        self.assertEqual(options["model"], "composer-2.5")
        self.assertIn("local", options)
        self.assertEqual(options["local"]["cwd"], os.getcwd())

    def test_second_call_reuses_live_session(self):
        sdk = FakeSdk()
        first = invoke_agent("reviewer", "first", sdk=sdk)
        second = invoke_agent("reviewer", "second", sdk=sdk)

        self.assertEqual(len(sdk.created), 1)
        self.assertEqual(first.text, "ok:first")
        self.assertEqual(second.text, "ok:second")

    def test_register_agent_applies_recipe(self):
        register_agent(
            "cloud-fix",
            runtime="cloud",
            model="gpt-5.5",
            repos=[{"url": "https://github.com/org/repo", "starting_ref": "main"}],
            auto_create_pr=True,
        )
        sdk = FakeSdk()
        invoke_agent("cloud-fix", "open a PR", sdk=sdk)

        options = sdk.created[0]
        self.assertEqual(options["model"], "gpt-5.5")
        self.assertIn("cloud", options)
        self.assertTrue(options["cloud"]["auto_create_pr"])
        self.assertEqual(options["cloud"]["repos"][0]["url"], "https://github.com/org/repo")
        self.assertNotIn("local", options)

    def test_per_call_override_wins(self):
        register_agent("reviewer", model="composer-2.5")
        sdk = FakeSdk()
        invoke_agent("reviewer", "go", model="auto", sdk=sdk)
        self.assertEqual(sdk.created[0]["model"], "auto")

    def test_oneshot_does_not_keep_a_session(self):
        sdk = FakeSdk()
        invoke_agent("reviewer", "once", oneshot=True, sdk=sdk)
        invoke_agent("reviewer", "twice", oneshot=True, sdk=sdk)

        self.assertEqual(len(sdk.prompted), 2)
        self.assertEqual(len(sdk.created), 0)

    def test_require_registered_unknown_name(self):
        with self.assertRaises(UnknownAgentError):
            invoke_agent("missing", "hi", require_registered=True, sdk=FakeSdk())

    def test_empty_name_rejected(self):
        with self.assertRaises(ValueError):
            invoke_agent("  ", "hi", sdk=FakeSdk())

    def test_unknown_override_rejected(self):
        with self.assertRaises(TypeError):
            invoke_agent("reviewer", "hi", not_a_field=True, sdk=FakeSdk())

    def test_resume_existing_agent_by_name(self):
        listed = SimpleNamespace(
            items=[
                SimpleNamespace(name="reviewer", agent_id="agent-old", last_modified=1),
                SimpleNamespace(name="reviewer", agent_id="agent-new", last_modified=9),
            ]
        )
        sdk = FakeSdk(listed=listed)
        result = invoke_agent("reviewer", "continue", sdk=sdk)

        self.assertEqual(sdk.resumed[0][0], "agent-new")
        self.assertEqual(len(sdk.created), 0)
        self.assertEqual(result.agent_id, "agent-new")

    def test_list_registered_agents(self):
        register_agent("zeta")
        register_agent("alpha")
        self.assertEqual(list_registered_agents(), ("alpha", "zeta"))

    def test_default_prompt_allows_name_only_call(self):
        register_agent("reviewer", default_prompt="Review the current diff")
        sdk = FakeSdk()
        result = invoke_agent("reviewer", sdk=sdk)
        self.assertEqual(result.text, "ok:Review the current diff")

    def test_to_create_options_local_uses_cwd(self):
        sdk = FakeSdk()
        options = _to_create_options(AgentSpec(name="n", cwd="/tmp/work"), sdk)
        self.assertEqual(options["local"]["cwd"], "/tmp/work")


if __name__ == "__main__":
    unittest.main()
