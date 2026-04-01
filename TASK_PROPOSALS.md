# Codebase issue triage and proposed tasks

## 1) Typo fix task
- **Issue found:** The CLI validation error text says `not exists`, which is ungrammatical and user-facing.
- **Task:** Update the `--input` validation error message to `does not exist` and keep wording consistent with the neighboring validation message.
- **Why:** Improves UX and professionalism of CLI errors.
- **Location:** `lama_cleaner/parse_args.py`.

## 2) Bug fix task
- **Issue found:** `_parse_preload_models` treats any list containing `all` as exactly `MODEL_CHOICES`, which silently drops unexpected extra values.
  - Example: `--preload-models all,typo_model` currently succeeds instead of failing.
- **Task:** Tighten parser behavior so `all` is only accepted when it is the sole token (or, alternatively, preserve strict validation over all tokens and error when extras are provided).
- **Why:** Avoids silently accepting invalid CLI input and makes misconfiguration obvious.
- **Location:** `lama_cleaner/parse_args.py`.

## 3) Code comment / documentation discrepancy task
- **Issue found:** `--host` is implemented in argument parsing but omitted from the README "Available arguments" table.
- **Task:** Add `--host` to documentation with default `127.0.0.1` and a short explanation.
- **Why:** Prevents confusion for users trying to bind to non-local interfaces.
- **Locations:** `lama_cleaner/parse_args.py` and `README.md`.

## 4) Test improvement task
- **Issue found:** Existing runtime settings tests do not cover malformed persisted config JSON (corrupt `config.json`) even though `_load_persisted_cache_dir` has fallback behavior for this case.
- **Task:** Add a test that writes invalid JSON to the config file and asserts `configure_cache_settings(None)` gracefully falls back to disabled/default cache settings instead of raising.
- **Why:** Protects startup robustness against user-edited or corrupted config files.
- **Locations:** `lama_cleaner/runtime_settings.py` and `lama_cleaner/tests/test_runtime_settings.py`.
