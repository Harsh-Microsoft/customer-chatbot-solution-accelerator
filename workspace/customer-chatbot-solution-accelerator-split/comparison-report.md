# Comparison Report — `customer-chatbot-solution-accelerator`

* **Contribution:** `customer-chatbot-solution-accelerator` (external, read-only source at `C:\GSAs\OG\customer-chatbot-solution-accelerator`)
* **Staging root:** `workspace/customer-chatbot-solution-accelerator-split/`
* **Approved plan:** `workspace/customer-chatbot-solution-accelerator-split/split-plan.md` — revision **7a** (post-approval staging corrections, §14.0), human-approved
* **Physical live layer roots (verified present on `main`):** `stable-cores/`, `technical-patterns/`, `industry-scenarios/` — nothing written to them by this run.
* **Generated:** 2026-09-07 (regenerated — supersedes the prior version; substantial correctness work landed since)
* **Target base branch:** `main`

> **This report is read-only against the live layers and the staged split.** The only write performed by this run is this file. (One transient artifact — a `__pycache__` produced incidentally by this run's own `py_compile` verification — was created and then removed before this report was written; the staged tree measured below is confirmed byproduct-free.)

## Headline

**100% of this contribution is NEW or DELTA vs. the live layers — 0% already exists.**

## 1. Measured staged totals (freshly verified, this run)

Measured directly with `Get-ChildItem -Recurse -File` against the staged tree, not estimated.

| Component | Layer | Files | Bytes |
|---|---|---|---|
| `agentic-apps` | Stable Core | 9 | 24,252 |
| **Stable Core total** | | **9** | **24,252** |
| `chat-with-data-voice` | Technical Pattern | 167 | 777,400 |
| `.shared` (ACR script delta) | Technical Pattern | 3 | 40,922 |
| **Technical Pattern total** | | **170** | **818,322** |
| `banking-customer-support` | Industry Scenario | 21 | 22,647 |
| `retail-customer-support` | Industry Scenario | 29 | 208,602 |
| `healthcare-patient-support` | Industry Scenario | 21 | 22,291 |
| **Industry Scenario total** | | **71** | **253,540** |
| **Grand total** | | **250** | **1,096,114** |

Confirms the pre-stated totals exactly (stable-cores 9/24,252 B; technical-patterns 170/818,322 B including the `.shared` ACR delta; industry-scenarios 71/253,540 B). **Build byproducts confirmed absent:** zero `node_modules/`, `dist/`, `__pycache__/`, or `.vite/` directories and no `main.json` ARM artifact anywhere in the staged tree.

## 2. Delta & Coverage Summary

Computed from the outcomes assigned to every one of the 83 numbered/lettered rows in `split-plan.md` §4 (the merged per-part outcome table), rolled up by target layer. Unchanged from the approved plan — post-approval correctness/staging work (revision 7a) fixed defects but did not add or remove any classified part or verdict.

| Layer | In-scope parts | Matched (existing) | Delta | New | % New or Delta |
|---|---|---|---|---|---|
| Stable Core | 1 | 0 | 0 | 1 | 100% |
| Technical Pattern | 36 | 0 | 1 | 35 | 100% |
| Industry Scenario | 10 | 0 | 0 | 10 | 100% |
| **Overall** | **47** | **0** | **1** | **46** | **100%** |

Excluded from %: 0 unclassified, 39 out of scope (repo-root scaffolding, dev-loop/CI, the BYO-Foundry-project branch, the BYO-Log-Analytics branch, dead code, the whole `tests/e2e-test/` subtree, duplicate data, and the security-flagged files — full row-by-row rationale in `split-plan.md` §4.1–§4.7).

**Plain words:** every in-scope part of this contribution is new to the factory — no existing Stable Core, Technical Pattern, or Industry Scenario already covers it. The one Delta (`technical-patterns/.shared/build-and-push-acr.*`) is staged and diffable (§5 below).

Denominator check: 44 distinct in-scope rows (47 layer-occurrences, 3 double-counted split rows per the plan's intentional two-layer splits) + 39 out-of-scope rows = 83 total rows in `split-plan.md` §4.

## 3. Validation status — strong, and re-verified in this run

| Check | Result |
|---|---|
| Stable core Bicep deploy | `az deployment group create --resource-group rg-agentic-apps-dev --template-file main.bicep --parameters location=southeastasia azureAiServiceLocation=southindia` — **succeeded, exit code 0** (real deployment, not what-if) |
| Pattern Bicep deploy | `az deployment group create --resource-group rg-chat-with-data-voice-dev --template-file main.bicep --parameters location=southeastasia azureAiServiceLocation=southindia scenarioPath=/app/scenario` — **succeeded, exit code 0** (real deployment, not what-if) |
| Frontend build | `npm install` + `npm run build` pass — 2,160 modules (app) / 4,031 modules (widget bundle) → `dist/assets/index.css` (341 kB), `dist/widget/widget.js` (869 kB). First time the frontend has ever built. |
| Backend compiles | Every `src/api/*.py` (all subfolders) passes `py_compile` — **re-verified this run**, exit code 0 |
| Relative imports | **Re-verified this run** — zero `from ..` or `from app.` imports remain anywhere under `src/api` |
| Tool-name equivalence | **Re-verified this run** against all three staged manifests: banking → `accounts_agent`/`banking_policy_agent`; retail → `product_agent`/`policy_agent`; healthcare → `services_agent`/`care_policy_agent` — each matches what `scripts/agents/create_agents.py` registers |
| Metadata schema validation | **Re-verified this run**, against the live repo's schemas — all 5 staged `metadata.yaml` files (1 stable core, 1 pattern, 3 scenarios) pass, 0 errors |
| Scenario image assets | **Re-verified this run** — banking 10, retail 18, healthcare 10 images staged, matching the stated counts |
| Terraform | Still absent by approved deviation (§8, Bicep-only); still unvalidated |

## 3a. Finding from this run's verification — not in the resolved-defect list

**`config.py`'s `Settings.scenario_root` property still fails open.** The primary manifest-loading path (`src/api/scenario_loader.py::resolve_scenario_path()`) correctly raises `RuntimeError('SCENARIO_PATH is required')` when `SCENARIO_PATH` is unset or the manifest is missing — this is the fix recorded as resolved item 9 below, and it is real. However, a **second, separate** resolution function in `config.py` was left unchanged:

```python
@property
def scenario_root(self) -> Path:
    if self.scenario_path.strip():
        return Path(self.scenario_path).expanduser().resolve()
    return Path.cwd().resolve()          # <- still fails open
```

This property is consumed by `routers/scenario_config_api.py`'s asset route (`GET /api/scenario/assets/{path}`) for its **path-containment security check** (`scenario_root not in resolved.parents`). If `SCENARIO_PATH` is unset, this route's containment check resolves relative to `Path.cwd()` (`/app` in the container) instead of raising, silently narrowing the "fail fast" guarantee to the manifest-loading path only. Recommend the same fix (raise instead of default) be applied to this property before promotion — flagged here rather than folded into the resolved list, since it was found, not fixed, during this comparison run.

## 4. Defects found and fixed since the last report — resolved (verified in this run except where noted)

1. **Fabricated `src/api/agent_framework/` stub** shadowing the real `agent-framework-core`/`agent-framework-azure-ai` pip packages — **confirmed deleted** (path absent).
2. **`cosmos_service.py` did not parse** — module singleton spliced into the class body, orphaning `update_chat_session`. **Confirmed repaired**: 30,211 B, both `update_chat_session` and `get_cosmos_service()` present and load cleanly (`py_compile` passes).
3. **`index.css` truncated 2,550 → 554 B**, dropping the `@theme` block (`--color-border`). **Confirmed restored**: staged file is 2,550 B.
4. **`@radix-ui/colors` missing from `package.json`** — **confirmed present** (`"@radix-ui/colors": "^3.0.0"`); `package-lock.json` regenerated, 237,426 B (~237 KB).
5. **Only 2 of 46 shadcn primitives staged** — **confirmed 43** `.tsx` files under `src/app/src/components/ui/`, plus `main.css`, `styles/coral.css`, `theme/coralTheme.ts`, `hooks/use-mobile.ts`, `components.json`, `tailwind.config.js`, `theme.json`, `.npmrc` all present.
6. **`widget-bundle.css` never staged; stale `@/ErrorFallback` import** — **confirmed**: `widget-bundle.css` present; `widget.tsx` now imports `ErrorFallback` from `@/components/ErrorFallback`, which resolves to the actual file at `src/app/src/components/ErrorFallback.tsx`.
7. **Grounding silently broken** — `catalog_tool_name()`/`policy_tool_name()` read a `catalog.toolName` key present in no manifest. **Confirmed fixed**: both now live in `scenario_config.py`, read `agents.catalogToolName`/`agents.policyToolName`, and raise `RuntimeError` if missing. Cross-checked against all three manifests (table above) — all match `create_agents.py` registration.
8. **Three duplicate manifest loaders consolidated** — **confirmed**: single `src/api/scenario_loader.py` (only match in the staged tree for the filename), `load_manifest()` carries `@lru_cache(maxsize=1)`.
9. **Fail-open startup fixed** — **partially confirmed**, see §3a above: the manifest-loading path (`scenario_loader.resolve_scenario_path()`) raises as claimed; a second, unrelated `config.py` property used by the asset route does not. Recommend closing before promotion.
10. **Five §4.8 relative-import violations flattened** — **confirmed this run**: zero `from ..`/`from app.` imports remain anywhere under `src/api`.
11. **Missing plan-mandated files staged** — **confirmed present**: `services/search.py`, `services/user_onboarding.py`, `memory_service.py`, `utils/auth_utils.py`, `routers/auth.py`, `routers/chat_config.py`.
12. **Build byproducts removed** — **confirmed this run**: no `node_modules/`, `dist/`, `__pycache__/`, or `main.json` anywhere in the staged tree (see §1).
13. **Infra reworked** — **confirmed**: pattern's `main.bicep` declares `module stableCore '../../../../stable-cores/agentic-apps/infra/bicep/main.bicep'`; pattern's `infra/bicep/modules/` is flat with `role-assignments.bicep` (one file, consolidated from four), `container-registry.bicep`, `app-service.bicep`/`app-service-plan.bicep`, `cosmos-db-nosql.bicep`; core accepts `modelDeployments array = []`.
14. **New role assignments** — **confirmed by reading both `role-assignments.bicep` files**: core grants Search MI → Cognitive Services OpenAI User, and Foundry project MI → Search Index Data Reader + Search Service Contributor; pattern grants backend Search Index Data Contributor (replacing the former Reader) plus Cognitive Services User, alongside the existing Azure AI User and Cosmos/ACR assignments.

## 5. Per-part review evidence

### `agentic-apps` — Stable Core — New

* Staged at: `stable-cores/agentic-apps/` (9 files, 24,252 B)
* Live target: `stable-cores/agentic-apps/` (confirmed absent live)
* Evidence — staged file tree: `metadata.yaml`, `README.md`, `infra/README.md`, `infra/bicep/main.bicep` (composes `ai-foundry-project`, `ai-search`, `role-assignments`, an optional `modelDeployments` loop), `infra/bicep/modules/{ai-foundry-project,ai-foundry-connection,ai-foundry-model-deployment,ai-search,role-assignments}.bicep`.
* `ai-search-identity.bicep` confirmed gone — merged into a single `Microsoft.Search/searchServices` resource in `ai-search.bicep` carrying `identity` + full `properties`. `role-assignments.bicep` confirmed new (full content read — see §4 item 14).
* **Validated:** real `az deployment group create` against `rg-agentic-apps-dev` — exit code 0.
* Gaps: Bicep only (approved deviation, §8).

### `chat-with-data-voice` — Technical Pattern — New

* Staged at: `technical-patterns/chat-with-data-voice/` (167 files, 777,400 B)
* Live target: `technical-patterns/chat-with-data-voice/` (confirmed absent live; closest pattern `chat-with-data` is architecturally distinct per split-plan §13 Q2)
* `src/api/` (14 top-level files + `auth/` 2, `routers/` 14, `services/` 6, `utils/` 14): FastAPI backend — `config.py`, `cosmos_service.py`, `database.py`, `models.py`, `scenario_config.py`, `scenario_loader.py`, `main.py`, `startup.sh`, `Dockerfile`; `routers/` includes `chat.py`, `auth.py`, `chat_config.py`, `scenario_config_api.py`, `voice_live.py`; `services/` includes `search.py`, `user_onboarding.py`; no `agent_framework/` stub.
* `src/app/` (React app + widget): `package.json` (declares `@radix-ui/colors`), `package-lock.json` (237,426 B), `tailwind.config.js`, `components.json`, `vite.config.ts`, `vite.widget.config.ts`; `src/components/` (56 files incl. 43 shadcn `ui/` primitives), `src/contexts/`, `src/theme/`, `src/styles/` (`theme.css` restored 201 B → 10,687 B; `coral.css`), `src/widget.tsx`/`widget-bootstrap.ts`/`widget-bundle.css`.
* `infra/bicep/`: `main.bicep` (13,884 B) composing the stable core module + a 3-model `modelDeployments` array (`gpt-5.4-mini`, `text-embedding-3-small`, `gpt-realtime-mini`); flat `modules/` per §4 item 13.
* Confirmed change: consolidated `role-assignments.bicep` (full content read, §4 item 14).
* **Validated:** real `az deployment group create` against `rg-chat-with-data-voice-dev` — exit code 0. Frontend `npm run build` passes for both bundles (§3).
* Gaps: `src/api/cosmos_service.py` is 30,211 B against a 59,856 B source — partly legitimate (cart removal, de-domaining per §7.1) but warrants a completeness read. `scripts/run_data_upload.sh` is a bash reconstruction, not a direct port of the 35 KB source. `scripts/data/upload_policy_docs.py`'s chunk-upload loop was reconstructed from helper functions. Embedding model version hardcoded `'1'` (matches source; no parameter exists). §3a fail-open residual in `config.py`.

### ACR build/push script parameterization — Technical Pattern — Delta

* Staged at: `technical-patterns/.shared/build-and-push-acr.{ps1,sh}` (+ `README.md`; 3 files, 40,922 B)
* Live target: `technical-patterns/.shared/build-and-push-acr.ps1` and `.sh`
* Evidence — `git diff --no-index` (read-only, this run): both scripts add a header comment block ("STAGED DELTA") plus new parameters/flags — `WebImageName`/`WebContext`/`WebDockerfile`, `ApiImageName`/`ApiContext`/`ApiDockerfile`, `ApiDotnetImageName`/`ApiDotnetContext`/`ApiDotnetDockerfile`, and `ApiAppPrefix`/`WebAppPrefix`/`ApiDotnetAppPrefix` — all defaulted to the existing `chat-with-data` values (`da-app`, `src/App`, `WebApp.Dockerfile`, `api-`, `app-`, `api-cs-`), with every hardcoded use-site (image list construction, App Service discovery queries, help text, `Update-AppServiceImage` calls) switched to reference the new parameters. No line unrelated to this parameterization changed; it is a surgical addition, not a rewrite.
* Why the delta is real: the same shared script must now also drive `chat-with-data-voice`'s `src/api` + `src/app` layout without forking a pattern-local copy (rejected alternative per split-plan §13 Q4).

### `banking-customer-support` — Industry Scenario — New

* Staged at: `industry-scenarios/banking-customer-support/` (21 files, 22,647 B)
* Live target: `industry-scenarios/banking-customer-support/` (confirmed absent live)
* Evidence: `manifest.json` (`agents.catalogToolName=accounts_agent`, `agents.policyToolName=banking_policy_agent` — verified matches `create_agents.py`), `metadata.yaml` (industry `fsi`, schema-valid), `evals/dataset.jsonl`, 10 image assets (verified count).

### `retail-customer-support` — Industry Scenario — New

* Staged at: `industry-scenarios/retail-customer-support/` (29 files, 208,602 B)
* Live target: `industry-scenarios/retail-customer-support/` (confirmed absent live)
* Evidence: `manifest.json` (`agents.catalogToolName=product_agent`, `agents.policyToolName=policy_agent` — verified), `metadata.yaml` (industry `rcg`, schema-valid), `evals/dataset.jsonl`, 18 image assets (verified count — largest scenario by size, driven by the `Color Images/` JPG set per split-plan §14.2).

### `healthcare-patient-support` — Industry Scenario — New

* Staged at: `industry-scenarios/healthcare-patient-support/` (21 files, 22,291 B)
* Live target: `industry-scenarios/healthcare-patient-support/` (confirmed absent live)
* Evidence: `manifest.json` (`agents.catalogToolName=services_agent`, `agents.policyToolName=care_policy_agent` — verified), `metadata.yaml` (industry `hls`, schema-valid), `evals/dataset.jsonl`, 10 image assets (verified count).

## 6. Reviewed, not defects

* `src/types.ts` and `src/lib/types.ts` both exist and are not duplicates — catalog/scenario types vs. chat types, 14 importers split cleanly.
* The six `1407120a` Search Index Data Reader role references in post-provision scripts assign to `az ad signed-in-user`, guarded by existence checks.

## 7. Promotion plan & reviewer note

| Part | Outcome | Action | Live destination |
|---|---|---|---|
| `agentic-apps` | New | Copy staged folder + register | `stable-cores/agentic-apps/` |
| `chat-with-data-voice` | New | Copy staged folder + register | `technical-patterns/chat-with-data-voice/` |
| `.shared` ACR script | Delta | Surgical merge of the hunks in §5 | `technical-patterns/.shared/build-and-push-acr.ps1`, `technical-patterns/.shared/build-and-push-acr.sh` |
| `banking-customer-support` | New | Copy staged folder + register | `industry-scenarios/banking-customer-support/` |
| `retail-customer-support` | New | Copy staged folder + register | `industry-scenarios/retail-customer-support/` |
| `healthcare-patient-support` | New | Copy staged folder + register | `industry-scenarios/healthcare-patient-support/` |

**Catalog/README registration required in the same PR, for every New component above** (confirmed live targets exist):

1. Layer-root *"Available …"* table: `stable-cores/README.md`, `technical-patterns/README.md`, `industry-scenarios/README.md`.
2. Top-level catalog: `docs/catalog/README.md`.
3. Per-layer catalog page: `docs/catalog/stable-cores.md`, `docs/catalog/technical-patterns.md`, `docs/catalog/industry-scenarios.md`.

**Pre-PR validation checklist:**

| Check | Status |
|---|---|
| `python metadata/validate.py` (all 5 staged docs) | ✅ Run this session — 0 errors |
| Stable Core Bicep deploy | ✅ Run — real deployment succeeded |
| Pattern Bicep deploy | ✅ Run — real deployment succeeded |
| `az bicep build` / `bicep lint` | ❌ Not run this session |
| Terraform validate/fmt | — N/A (approved deviation, not authored) |
| Frontend build (`npm install && npm run build`, both bundles) | ✅ Run — passes |
| Backend `py_compile` (all files) | ✅ Run this session — 0 errors |
| Relative-import scan | ✅ Run this session — 0 matches |
| Tool-name equivalence (3 scenarios) | ✅ Run this session — all match |
| §3a `config.py` fail-open residual | ❌ Not fixed — recommend before promotion |
| Catalog/README registration edits | ❌ Not yet made — required in the promotion PR, not yet drafted |
| Secrets scan of staged tree | ✅ Run this session — none found staged |

**Security — must never reach the PR:** `.azure/ccsaecomhb/.env`, `infra/vscode_web/.env`, and both `public/config.js` files carry a real subscription ID, Foundry project resource ID, agent ID, live backend URL, and OAuth redirect URI. Confirmed **not present** anywhere in the staged tree this run (out-of-scope rows in `split-plan.md` §4.7) — keep them excluded at promotion time too.

*Nothing has been written to the live layers by this run. Explicit human approval of this exact report authorizes the FDE Split Promoter to branch `promote/customer-chatbot-solution-accelerator` from `main` and open a PR, without a second approval gate — except that the §3a residual and the not-yet-run `az bicep build`/lint check should be addressed or explicitly waived first.*
