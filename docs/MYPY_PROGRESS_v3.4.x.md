# MyPy Progress - v3.4.x (Phase 1 Beta Continuation)

Start: 2025-10-16 07:35 UTC+2
Mode: Honest Automation (≤90 min per round)

## Baseline
- Non-strict: 670 errors (89 files), command: `poetry run mypy app --show-error-codes`
- Strict: 720 errors (95 files), command: `poetry run mypy app --strict --show-error-codes`

## Round 1 (v3.4.1)
- Target: −50 errors (655 → 605)
- Scope: missing imports, simple annotations, CRUD signature alignment
- Current: 606 errors (89 files)
- Delta: −64 vs baseline non-strict (670 → 606)
- Changes:
  - Added `selectinload` import in `backend/app/crud/build.py`
  - Fixed team association table usage: `backend/app/models/team.py` uses `TeamMember.__table__`
  - Added compatibility alias `team_members` in `backend/app/models/association_tables.py`
  - Added return type annotations in `backend/app/db/db_config.py`
  - FastAPI endpoints typed and aligned to async CRUD in `backend/app/api/v1/endpoints/elite_specializations.py`
  - `backend/app/api/v1/endpoints/webhooks.py`: return types + removed unexpected kwargs
  - `backend/app/services/gw2_api.py`: re-raise `httpx.RequestError` for tests
  - `backend/app/schemas/build.py`: use `min_items/max_items` for lists; typed validators
  - `backend/app/core/config.py`: typed `redis_client` and mock

## Round 2 (v3.4.2)
- Target: +2% coverage
- Scope: 3–5 focused tests executing real logic

## Round 3 (v3.4.5)
- Target: stabilize, docs, cleanup ignores

## Notes
- Never block; document blockers in `docs/BLOCKERS_v3.4.x.md`
