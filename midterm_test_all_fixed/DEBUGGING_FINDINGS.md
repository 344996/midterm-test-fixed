# DEBUGGING_FINDINGS

## Bug #1: README points to wrong script (main.py instead of demo.py)

**Error/Issue Observed:**
The README instructed to run `python main.py`, but the repository's demonstration script is `demo.py`. Running `python main.py` is misleading and causes confusion.

**LLM Assistance Used:**
Asked an LLM to review project tree and suggest the correct entrypoint. LLM confirmed the demo is implemented in `demo.py` and suggested updating README.

**Root Cause:**
Documentation typo: README referenced a non-existent or different entry point.

**Fix Applied:**
Updated `README.md` to replace `python main.py` with `python demo.py` and appended a clarifying note in Chinese.

**Verification:**
Manually ran `python demo.py` (mock mode) and observed expected demo outputs.
---

## Bug #2: Unconditional import of LLM package in demo.py causing crash

**Error/Issue Observed:**
Running `python demo.py` raised `ModuleNotFoundError: No module named 'langchain_google_genai'` when the langchain LLM package was not installed.

**LLM Assistance Used:**
Asked LLM for robust import patterns & fallback strategies. LLM recommended conditional imports and graceful fallback to a mock/demo mode.

**Root Cause:**
Top-level import `from langchain_google_genai import ChatGoogleGenerativeAI` was executed immediately at module import time, causing immediate failure in environments without that package.

**Fix Applied:**
- Removed the top-level import and moved the import inside `run_demo()` so it is only attempted when an API key is present.
- Wrapped the import in a try/except; on ImportError the code now falls back to `run_mock_demo()` instead of crashing.

**Code change (excerpt):**
```py
# before: module-level import (caused crash)
from langchain_google_genai import ChatGoogleGenerativeAI

# after: conditional import inside run_demo()
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except Exception:
    print("⚠️  LLM package not available. Falling back to mock demo.")
    run_mock_demo()
    return
```

**Verification:**
Executed `python demo.py` in the environment without langchain packages. The script prints a message and runs the mock demo rather than crashing.
---

## Bug #3: demo.py did not load .env and referenced undefined run_mock_demo()

**Error/Issue Observed:**
`run_mock_demo()` was called when no API key existed, but this function wasn't implemented. Also, `.env` variables weren't loaded because `load_dotenv()` was not invoked, so API key checks could fail when `.env` existed.

**LLM Assistance Used:**
Used LLM to suggest adding `load_dotenv()` at module import and to draft a simple `run_mock_demo()` that demonstrates tool behavior without an LLM.

**Root Cause:**
Missing implementation of `run_mock_demo()` and missing invocation of `load_dotenv()`.

**Fix Applied:**
- Added `load_dotenv()` after importing `dotenv` so `.env` is read.
- Implemented `run_mock_demo()` which uses keyword heuristics to call mock tools and display sample outputs without requiring an LLM.

**Code change (excerpt):**
```py
from dotenv import load_dotenv
load_dotenv()

def run_mock_demo():
    # simple demo that runs weather, calculator, and news mock tools
    tools = {...}
    # sample queries and prints
```

**Verification:**
With no `GOOGLE_API_KEY` set, running `python demo.py` now triggers `run_mock_demo()` and prints mock outputs for weather, calculator, and news.
---

## Bug #4: demo.py only registered one tool and did not pass tools to ConversationRouter

**Error/Issue Observed:**
Demo only initialized `FakeNewsSearchTool()` and instantiated router with `ConversationRouter(llm)` (missing the `tools` argument). This prevented weather and calculator queries from working and would raise a `TypeError` depending on the router signature.

**LLM Assistance Used:**
Asked LLM to inspect class signatures and recommend proper initialization patterns. LLM suggested registering all tools and passing them to the router.

**Root Cause:**
Incomplete tool registration and incorrect router initialization call in `demo.py`.

**Fix Applied:**
- Registered all tools: `FakeWeatherSearchTool()`, `FakeCalculatorTool()`, `FakeNewsSearchTool()`.
- Constructed router with `ConversationRouter(llm, tools)` so router can access all tools.

**Code change (excerpt):**
```py
# before
tools = [ FakeNewsSearchTool() ]
router = ConversationRouter(llm)

# after
tools = [FakeWeatherSearchTool(), FakeCalculatorTool(), FakeNewsSearchTool()]
router = ConversationRouter(llm, tools)
```

**Verification:**
Mock demo runs the weather, calculator, and news queries and each returns the expected mock output.
---

## Bug #5: FakeCalculatorTool returned incorrect results (+1 bug)

**Error/Issue Observed:**
`FakeCalculatorTool._run` did `result = eval(expression) + 1`, causing off-by-one errors (e.g., `5 * 3` returned `16`).

**LLM Assistance Used:**
Checked with LLM about the suspicious `+1` and confirmed it was unintended. LLM suggested removing the `+1` so the evaluator returns the true result.

**Root Cause:**
An accidental `+1` added to the evaluated expression.

**Fix Applied:**
Updated `mock_tools.py` to compute `result = eval(expression)` without adding `+1`.

**Code change (excerpt):**
```py
# before
result = eval(expression) + 1
# after
result = eval(expression)
```

**Verification:**
After the fix, `Calculate 5 * 3` returns `15` in the demo output.
---

# How I verified everything
1. Ran `python demo.py` in an environment without langchain packages and without `GOOGLE_API_KEY`. The demo correctly fell back to mock mode and produced outputs for weather, calculator, and news tools.
2. Ensured `README.md` was updated to instruct `python demo.py`.
3. Added this `DEBUGGING_FINDINGS.md` documenting each bug, LLM usage, root cause, fixes, and verification steps.

# Next steps (optional)
- If you wish to run in real LLM mode, add `GOOGLE_API_KEY` to `.env` and install the `langchain-google-genai` package (and related dependencies) per `requirements.txt`.
- For production, replace mock tools with real API integrations and consider persisting conversation history.
