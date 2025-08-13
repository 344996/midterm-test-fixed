## Bug #1: Wrong module used / missing tools passed
**Issue:** `ConversationRouter(llm)` called without tools; or wrong file name used (`roter.py` vs `router.py` in some copies).
**Root Cause:** Router expects `(llm, tools)`; filename mismatch in earlier scaffold.
**Fix:** Ensure file is named `router.py` and initialize router with tools: `ConversationRouter(llm, tools)`.

## Bug #2: .env not loaded
**Issue:** `GOOGLE_API_KEY` not found though `.env` exists.
**Fix:** Call `load_dotenv()` before reading env in `demo.py`.

## Bug #3: Missing `run_mock_demo()`
**Issue:** Script calls `run_mock_demo()` when no API key, but function not defined.
**Fix:** Implement a mock-mode fallback that calls tools via simple heuristics.

## Bug #4: Calculator adds +1 (logic bug)
**Issue:** `eval(expression) + 1` returns wrong result.
**Fix:** Remove the `+ 1` so it returns the true value.

## Bug #5: Placeholder prompts break routing/param extraction
**Issue:** Prompts like “this prompt is correct” return garbage tool names/params.
**Fix:** Replace with strict prompts that return ONLY a valid tool name or `general_chat`, and ONLY the single argument string.
