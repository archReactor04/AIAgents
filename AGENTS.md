# Repository Guidelines

## Project Structure & Module Organization
- `travel-planner/agents/` hosts Swarm agent builders; each new agent should expose a `build_<agent>` factory and mirror a test in `travel-planner/tests/`.
- `travel-planner/planner_runtime/` contains the orchestration runtime configured for optional Tavily usage; adjust here when introducing new coordination features.
- UI code lives under `travel-planner/ui/`, with reusable visuals and forms split by concern. Shared helpers reside in `travel-planner/utils/`; external integrations in `travel-planner/services/`.
- Documentation is in `travel-planner/docs/`; keep architecture notes synchronized with code changes.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate` — set up the local Python 3.11 environment (Windows: `.venv\Scripts\activate`).
- `pip install -r travel-planner/requirements.txt` — install runtime and dev dependencies.
- `streamlit run travel-planner/app.py` — launch the multi-agent travel planner UI.
- `pytest travel-planner/tests` — run the full automated suite; use `-q --maxfail=1` while iterating.

## Coding Style & Naming Conventions
- Use 4-space indentation and type hints on public functions. Follow `snake_case` for modules/functions, `UpperCamelCase` for classes, and `SCREAMING_SNAKE_CASE` for constants.
- Format with `black travel-planner` and lint with `ruff check travel-planner` before committing.
- Co-locate new assets under `travel-planner/assets/` and export minimal module APIs via `__all__` where applicable.

## Testing Guidelines
- Tests use `pytest` (plus `pytest-asyncio`, `respx`). Name files `test_<feature>.py` and functions `test_<behavior>()`.
- Maintain ≥80 % statement coverage on new code; mock network-heavy Tavily and OpenAI calls with `pytest-mock` or `unittest.mock`.
- Store sample payloads under `travel-planner/tests/data/` and load them via fixtures to keep tests deterministic.

## Commit & Pull Request Guidelines
- Follow Conventional Commits (`feat:`, `fix:`, `docs:`) with imperative subjects under 50 characters.
- Squash or rebase noisy commits; ensure PR descriptions cover problem, solution, and validation commands (include `pytest`/`streamlit run` snippets).
- Flag breaking changes or migration steps explicitly and run lint + tests before requesting review.

## Security & Configuration Tips
- Never commit secrets; populate `.env` (ignored by git) with `OPENAI_API_KEY`
- Document any new environment variables in `travel-planner/README.md` and review third-party licenses before extending dependencies.

## Agent Runtime Notes
- Re-run `pytest travel-planner/tests/test_runtime.py` after modifying orchestration to verify prompt formatting and offline fallbacks.
