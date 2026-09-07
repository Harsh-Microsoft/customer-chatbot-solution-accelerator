# Split Plan - `customer-chatbot-solution-accelerator`

> Gate 1a review surface. **Revision 7** - applies one reviewer decision on top of revision 6:
> **the planned `config/scenario-config.sample.json` is dropped.** Only the sample *instance* goes.
> The pattern still publishes its config JSON schema (`host`, `welcome`, `catalog`,
> `presentation`), still names it in `scenarioExtensionPoints`, and every scenario `manifest.json`
> is still validated against it at compose time - **compose-time validation is not dropped**
> (section 6A.7).
> **Precedent basis, verified in this repository before the decision was recorded:** the live
> `technical-patterns/chat-with-data/` pattern ships **no `config/`, `samples/`, or `evals/`
> folder** and no sample dataset, and its `scripts/shared/scenarios.py` resolves
> `industry-scenarios/scenarios.json` and degrades to an **empty registry with a warning** when that
> file is absent - i.e. the live pattern assumes a scenario is always composed. Shipping a
> standalone sample here would have introduced a new, unilateral factory convention.
> **Consequence, stated here rather than buried:** with `tests/e2e-test/` out of scope **and** no
> sample fixture, the technical pattern ships **no executable validation whatsoever** and cannot be
> deployed meaningfully without a composed scenario - the catalog renders empty and **no agents
> exist**, because agent creation reads `agents/*.txt` from the scenario. Carried as a prominent
> risk in section 12, and **Workflow execution fit is re-scored 4 to 3** (section 2), because
> revision 4's justification for raising it no longer exists.
> **Every revision-6 and revision-5 decision stands unchanged** - the section 6 router merge, the
> section 6A UI genericization (minus the sample config), the section 6B localized image assets and
> their security controls, the section 7.1 cart trace, both BYO removals (sections 7.4 and 7.5), the
> section 4.8 import rewrites, the accepted Terraform deviation, row 28a, and every security flag.
> Nothing has been staged. No live layer folder was read for anything other than
> comparison, and none was modified. Approve this exact plan before any classifier is
> dispatched.
>
> **Changelog** is in section 14 - the revision 7a staging corrections first, then revision 7, with revisions 6, 5, 4, 3 and 2 retained beneath it.

## 1. Summary of change

The contribution is a deployable multi-scenario customer support chatbot. It ships two
FastAPI backends and two React frontends (a standalone chat app and a scenario host app
that already embeds the chat app as a shadow-DOM widget), one Bicep infrastructure tree
in two competing flavors (vanilla and AVM), a post-provision automation set that creates
Azure AI Foundry connected agents and loads catalog/policy data into Azure AI Search and
Cosmos DB, and three interchangeable domain packs (banking, ecommerce, healthcare) driven
by a `manifest.json` plus agent instruction text files.

Verified capability highlights that drive classification:

* Real-time voice is genuinely present. `infra/main.bicep` deploys `gpt-realtime-mini`, both
  backends expose `app/routers/voice_live.py` with `app/utils/voice_utils.py`, and both
  frontends ship `lib/audioUtils.ts` plus a `public/pcm-processor.js` audio worklet.
* Agent orchestration is multi-agent handoff over Foundry connected agents (`chat_agent`
  delegating to `catalog_agent` and `policy_agent`), not the single-agent-with-MCP-tools shape
  of the live `chat-with-data` pattern.
* The data processing model is CSV and text ingested into Azure AI Search indexes and Cosmos
  DB. There is no Fabric lakehouse, no ontology, and no Fabric Data Agent.
* The chat widget embed mechanism already exists: `chat-app/frontend/vite.widget.config.ts`
  builds an IIFE `widget.js` from `src/widget-bootstrap.ts`, `scenario-app/frontend/Dockerfile`
  copies it into the scenario bundle, and `scenario-app/frontend/src/embedChatWidget.ts`
  loads and initializes it at runtime.
* **New in revision 4 - the three scenario front ends are near-identical.** `BankingApp.tsx`
  (41 lines) and `HealthcareApp.tsx` (41 lines) are structurally identical; `EcommerceApp.tsx`
  (66 lines) differs by the cart wiring section 7.1 already removes, a no-op client-side
  filter/sort, and a grid-versus-list layout choice. All three collapse into one generic,
  config-driven catalog app (section 6A).

* **New in revision 6 - the image pipeline is broken in three different ways.** Retail's 16 catalog
  rows point at absolute `raw.githubusercontent.com` URLs on a third-party repository; banking's and
  healthcare's point at root-relative paths that resolve out of the *pattern's* public root; and for
  banking and healthcare the CSV `image` column is **dead for all 16 shipped rows**, because both
  cards render `meta.image` from a hardcoded map instead. Section 6B localizes every asset into its
  own scenario and serves it from `SCENARIO_PATH`.

Details:

* **Resolved contribution path:** `C:\GSAs\OG\customer-chatbot-solution-accelerator`
* **Staging folder:** `workspace/customer-chatbot-solution-accelerator-split/`
* **Target base branch: `main`.** Verified: `git branch -a` lists no `dev` branch, local or
  remote. `main` resolves to `f3e56db5c9bcf3d7faf585735f7f1fe64e3a47d0`, and
  `git ls-tree --name-only main` confirms all three live layer roots exist on it
  (`stable-cores`, `technical-patterns`, `industry-scenarios`). The promoter must branch
  `promote/customer-chatbot-solution-accelerator` from `main` and raise the PR to `main`.
* **Target industries:** banking (`fsi`), retail (`rcg`), healthcare (`hls`), each recorded in
  the scenario's `metadata.yaml` `industry` field, never as a folder level.

## 2. Fit Reconfirmation Score

Applies the `## Scoring Rubric` of
[`.github/skills/customer-use-case-fit-assessment/SKILL.md`](../../.github/skills/customer-use-case-fit-assessment/SKILL.md)
verbatim. This reuses that rubric and does not re-open the intake gate. Re-run honestly against
the revision-6 plan.

| Dimension | Score (1-5) | Rationale (one line) |
|---|---|---|
| Problem alignment | 5 | Unchanged. Grounded multi-agent customer chat with a real-time voice channel maps cleanly onto the pattern layer, and the three domain packs map cleanly onto the scenario layer. Localizing image assets changes nothing about the problem being solved. |
| Data alignment | 4 | **Unchanged at 4, for a better reason.** Revision 6 repairs a real data defect - the catalog `image` column was dead for 8 of 8 banking and 8 of 8 healthcare rows (section 6B.1) and pointed at a third-party repository for all 16 retail rows - so the CSV becomes a single, self-contained source of truth with its assets shipped alongside it. Still 4 and not 5, because the `Should` gap is untouched: no evaluation dataset ships with any of the three packs. |
| Architecture and constraints fit | 3 | **Unchanged at 3, for a better reason again.** Section 6B removes the last compose-time patch in the plan: revision 4's *"the Builder copies the SVGs into the app's public root"* step contradicted the section 6A.1 copy-plus-environment contract and the section 6A.2 scenario-free-image property. Serving assets from `SCENARIO_PATH` restores both. Still capped at 3 because the Terraform `Must` remains knowingly unmet (section 12). |
| Customization effort | 3 | Unchanged. Revision 6 adds required authoring - the asset route with its traversal controls, the tolerant-path card rule, and three CSV rewrites (section 6B.3) - and removes some: the Builder's public-root copy step, the `image` key in the `presentation` map, and the `assetPrefix` guard. Roughly neutral against decision 2's authoring block, which remains the dominant cost. |
| Time to value | 3 | Unchanged. The asset route is small next to the UI genericization, which is still the front-loaded critical path that must land before the first composed solution renders. |
| Workflow execution fit | 3 | **Re-scored 4 to 3 on the merits (revision 7).** Revision 4 raised this from 3 to 4 partly because *"the first executable validation ships"* - that justification was the standalone sample config, which is now dropped (section 6A.7), so it is removed rather than reworded. Re-scored from the rubric: the workflow this pattern must execute - grounded multi-agent catalog-and-policy chat with a voice channel - is a `Must`, and after decision 2 it **`Requires customization`** before it executes at all (~350 lines of generic `CatalogApp`, `catalog.py` and `scenario_config_api.py` are authored during decomposition, and no staged component ships a runnable check of any of it). Score-3 rule, first match. The surviving compose-time schema validation is a real gate, but it runs only against a composed scenario manifest and checks configuration shape, so it does not lift that `Must` out of `Requires customization`. |
| Connectivity fit | 3 | **Unchanged at 3, deliberately not raised.** Revision 6 does remove an external-network dependency - retail's 16 absolute `raw.githubusercontent.com` URLs stop being the delivery path, so all three scenarios render with no third-party repository reachable. But the dimension is independently pinned at 3 by the two revision-5 capability removals, no existing-Foundry-project composition (section 7.4) and no existing-Log-Analytics-workspace attach (section 7.5), and revision 6 touches neither. Raising it would be dishonest under the rubric's deterministic rule. |
| **Total** | **24/35** (down 1 from revision 6, on Workflow execution fit alone) | - |

* **Recommendation band:** Proceed with scoped conditions (18-27). **Band unchanged across all
  seven revisions**, although the total moved for the first time since revision 4. 24 sits
  comfortably inside the 18-27 band, so the decision to proceed is not disturbed by the drop.
* **Flag:** none. No dimension scored 1 and the total is well above the 7-17 halt band.
* **Why the total moved, and why on exactly one dimension.** Revision 7 removes a deliverable, so
  the re-run looked first for any dimension whose score depended on that deliverable. Exactly one
  did: **Workflow execution fit, 4 to 3**, because revision 4's raise rested partly on the sample
  config being *"the first executable validation"*. The stale justification is deleted, not
  reworded, and the dimension is re-scored from the rubric on its own merits. The other six were
  re-checked dimension by dimension and did not move: **Customization effort stays 3** (dropping one
  small sample file is a marginal saving against decision 2's authoring block, which remains the
  dominant cost, and the schema plus its compose-time validation are still authored);
  **Time to value stays 3** (same front-loaded critical path); and **Problem alignment 5**,
  **Data alignment 4**, **Architecture and constraints fit 3**, and **Connectivity fit 3** are
  untouched by this decision. The revision-6 pinning analysis still holds for those six: each is
  capped by a lower-scoring condition (the missing evals, the unmet Terraform `Must`, the two BYO
  removals) that revision 7 does not touch, and under the rubric's *first matching rule* semantics
  an improvement above the pinning condition cannot raise a score.
* **Scoped conditions carried forward, one of them hardened by revision 7:** complete the domain
  de-hardcoding in section 12; **add at least a starter `evals/` asset per staged component - after
  revision 7 this is the only validation route left, since the surviving compose-time config
  validation runs only against a composed scenario and checks shape, not behavior**; treat the
  deferred Terraform flavor (section 12, *Accepted deviation -
  Terraform out of scope*) as follow-up work that must land before either infra-bearing component
  can compose into a Terraform solution; treat **both** excluded BYO paths (sections 7.4 and
  7.5) as documented limitations with a plausible future-enhancement route back; and treat
  blob-plus-CDN asset delivery (section 6B.5) as a **documented** production path, not a built one.

## 3. Layer decomposition (at a glance)

* **Stable Core.** One **New** core, `stable-cores/agentic-apps/`, carrying exactly the AI
  Foundry account, the Foundry Project, and Azure AI Search. Directed by the reviewer, who
  acknowledges and accepts the overlap with live `microsoft-iq`. **Nothing in `microsoft-iq`
  is modified by this plan**; the previously proposed Fabric-capacity delta is withdrawn.
  **Bicep only** (accepted deviation, section 12). It provisions the Foundry account and project
  **greenfield only** - the bring-your-own / existing-project branch is excluded for complexity
  reduction (reviewer decision 5a, revision 5 - see rows 50a and 52a and section 7.4).
  See sections 5, 7.4, 8 and 10.
* **Technical Pattern.** One **New** pattern carrying the merged API, the merged **generic,
  scenario-free** app with the embedded chat widget, its own application infrastructure (ACR,
  App Service Plan, exactly two App Services, Cosmos DB, role assignments, **plus Log Analytics
  and Application Insights**), and the scenario loader, agent creation, and data upload scripts.
  Staged as `technical-patterns/chat-with-data-voice/`, **Bicep only**. **The pattern still
  provisions Log Analytics and Application Insights, greenfield** - only the *attach to an
  existing workspace* branch is excluded (reviewer decision 5b, revision 5 - see section 7.5).
  Its UI is domain-independent by construction: every label, title, banner, icon, card layout,
  and per-item presentation record arrives as scenario configuration over
  `GET /api/scenario/config` (section 6A), and **every image it renders arrives over the companion
  `GET /api/scenario/assets/{path}` route, resolved against `SCENARIO_PATH`** (section 6B). No image
  file is compiled into the frontend bundle or copied into its public root.
* **Industry Scenario.** Three **New** flat scenarios - `banking-customer-support` (fsi),
  `retail-customer-support` (rcg), `healthcare-patient-support` (hls) - carrying manifest
  (now including `catalog` and `presentation` blocks), agent instruction text, catalog CSV,
  policy documents, and - **new in revision 6** - **every image the scenario renders, in one flat
  `assets/` folder served by the API from `SCENARIO_PATH`** (section 6B): 8 SVGs to banking, 8 SVGs
  to healthcare, 16 JPGs to retail, plus the two Contoso brand PNGs to all three. Each scenario's
  catalog CSV `image` column is rewritten to scenario-relative `assets/<filename>` values as a
  required decomposition action. **No scenario carries React code** (section 6A.6).
  Names locked by the reviewer.
* **Out of scope.** Repo-root governance and dev-loop scaffolding, the AVM infrastructure tree,
  compiled ARM JSON, an unreferenced Bicep module library, live azd environment state, three
  checked-in files holding real subscription/resource identifiers or stale live endpoints
  (`.azure/ccsaecomhb/.env`, `infra/vscode_web/.env`, and both `public/config.js` copies -
  row 28a), byte-identical duplicate data, the four scenario-app CRUD routers including
  `cart.py`, the whole `tests/e2e-test/` subtree, the three per-domain React apps and their card
  components (rows 42, 43, 44) superseded by the pattern's generic catalog app, and - restored or
  new in revision 5 - **both BYO paths**: `existing-project-setup.bicep` with its 17 companion
  items (row 50a, section 7.4), the now-orphaned `cross-scope-role-assignment.bicep` (row 52a),
  and the existing-Log-Analytics-workspace branch with its 8 companion items (section 7.5).

## 4. Per-part plan

Every path under the contribution appears in exactly one row. Outcome uses the shared
vocabulary (**Matched** / **Delta/Upgrade** / **New**), assigned by capability comparison
against the live layers rather than by folder name. `TP` abbreviates
`technical-patterns/chat-with-data-voice/`; `SC` abbreviates `stable-cores/agentic-apps/`.

**Pattern source layout (reviewer decision 4).** The contribution's `*/backend/app/...`
nesting collapses by one level when staged: `backend/app/routers/` becomes `TP/src/api/routers/`,
`backend/app/utils/` becomes `TP/src/api/utils/`, `backend/app/services/` becomes
`TP/src/api/services/`, and the loose `backend/app/*.py` modules land directly in `TP/src/api/`.
There is no intermediate `app/` package. The frontend is unaffected and continues to stage under
`TP/src/app/`. Forced rewrites are listed in section 4.8.

### 4.1 Repository root files and scaffolding

| # | Source part | Target layer | Outcome | Action / destination |
|---|---|---|---|---|
| 1 | `.azure/` (`config.json`, `.state-change`, `.gitignore`, `ccsaecomhb/.env`, `.env.lock`) | - | Out of scope | Live azd environment state holding real subscription and resource identifiers. Repo scaffolding, not staged. **Security-flagged** in section 12. |
| 2 | `.devcontainer/` (`devcontainer.json`, `Dockerfile`) | - | Out of scope | Dev-loop scaffolding per the skill's "Decompose, don't clone" rule. Not staged. |
| 3 | `.github/workflows/` (21 workflows) | - | Out of scope | Source-repo CI. The factory owns its own CI. Not staged. Six of them plumb `AZURE_EXISTING_AIPROJECT_RESOURCE_ID`; that variable is now genuinely supported by the core (section 7.4), but the workflows themselves remain out of scope and the factory build supplies the parameter its own way. |
| 4 | `.github/` remainder (`CODEOWNERS`, `dependabot.yml`, `PULL_REQUEST_TEMPLATE.md`, `ISSUE_TEMPLATE/`, `policies/jit.yml`, `acl/access.yml`) | - | Out of scope | Repo governance scaffolding. Not staged. |
| 5 | `.vscode/` (`launch.json`, `settings.json`) | - | Out of scope | Editor scaffolding. Not staged. |
| 6 | `azure.yaml` | - | Out of scope | Solution-level azd manifest, regenerated by the factory build. Its hook bodies inform the pattern `scripts/README.md` only. |
| 7 | `.flake8`, `.gitignore`, `.dockerignore` (repo root) | - | Out of scope | Linter and VCS scaffolding. Per-app `.dockerignore` files travel with their build contexts instead (rows 20 and 36). |
| 8 | `package-lock.json` (repo root) | - | Out of scope | Stray lockfile. There is no root `package.json`; the real lockfiles live in each frontend. |
| 9 | `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `LICENSE`, `SECURITY.md`, `SUPPORT.md`, `TRANSPARENCY_FAQ.md` | - | Out of scope | Repo governance. Explicitly listed by the skill as not staged. Architecture prose is rewritten into the new pattern README rather than copied. |

### 4.2 `chat-app/` (backend)

| # | Source part | Target layer | Outcome | Action / destination |
|---|---|---|---|---|
| 10 | `chat-app/backend/app/routers/{chat,chat_config,voice_live,auth}.py` | Technical Pattern | New | Merge into **`TP/src/api/routers/`**. These are the domain-independent chat, config, voice, and auth surfaces and form the core of the merged API. |
| 11 | `chat-app/backend/app/{main,config,auth,models,cosmos_service,database}.py` | Technical Pattern | New | Merge into **`TP/src/api/`** (no `app/` level). `main.py` becomes the single API entrypoint (see row 35 for router registration). |
| 12 | `chat-app/backend/app/scenario_config.py` | Technical Pattern | New (with mandatory refactor) | Stage to **`TP/src/api/scenario_config.py`** after removing the hardcoded `VALID_SCENARIOS` frozenset, the `_CATALOG_TOOL_NAMES` / `_POLICY_TOOL_NAMES` dictionaries, and the `voice_grounding_config` profiles containing Contoso Paints copy. All of it moves to the scenario manifest. Its scenario-root resolution is superseded by the `SCENARIO_PATH` variable of the composition contract (section 6A.1). Blocking for domain independence. |
| 13 | `chat-app/backend/app/services/{search,user_onboarding}.py` | Technical Pattern | New | Merge into **`TP/src/api/services/`**. `user_onboarding.py` seeds demo transaction history and stays generic once `Order`/`Transaction` vocabulary is neutralized. |
| 14 | `chat-app/backend/app/utils/{auth_utils,azure_credential_utils,event_utils,foundry_agent_utils,voice_utils}.py` | Technical Pattern | New | Merge into **`TP/src/api/utils/`**. All five are referenced and domain independent. |
| 15 | `chat-app/backend/app/utils/{product_catalog,product_text_parser}.py` | Technical Pattern | New (with mandatory refactor) | Referenced by `routers/chat.py` and `routers/voice_live.py`, so not skippable. Stage to **`TP/src/api/utils/`** after replacing the ecommerce product-card field names with the manifest-declared `catalog.cardSchema` (section 6). |
| 16 | `chat-app/backend/app/agent_instructions.py` | - | Out of scope | Dead code and domain content. Zero importers in either backend; superseded by `scenarios/<id>/agents/*.txt`. See section 7.2. |
| 17 | `chat-app/backend/app/foundry_client.py` | - | Out of scope | Dead code. Zero importers in either backend. See section 7.2. |
| 18 | `chat-app/backend/app/util/jsonsafe.py` (and `util/__init__.py`) | - | Out of scope | Dead code. Zero importers in either backend; superseded by the `utils/` package. See section 7.2. |
| 19 | `chat-app/backend/app/{__init__,routers/__init__,services/__init__,utils/__init__}.py` | Technical Pattern | New | Package markers. The top-level `app/__init__.py` disappears with the collapsed layout; `routers/`, `services/`, `utils/` keep theirs under `TP/src/api/`. |
| 20 | `chat-app/backend/{Dockerfile,.dockerignore,requirements.txt,startup.sh,env.sample}` | Technical Pattern | New | Stage into the **`TP/src/api/`** build context. Genuine runtime and build artifacts the pattern needs. `env.sample` gains `SCENARIO_PATH` (section 6A.1). Entrypoint rewrite in section 4.8. |
| 21 | `chat-app/backend/{requirements-dev.txt,pyrightconfig.json,README.md}` | - | Out of scope | Dev-loop scaffolding. The README content is rewritten into `TP/src/api/README.md`. |

### 4.3 `chat-app/` (frontend)

| # | Source part | Target layer | Outcome | Action / destination |
|---|---|---|---|---|
| 22 | `chat-app/frontend/src/{widget.tsx,widget-bootstrap.ts,WidgetApp.tsx,widget-bundle.css}` and `src/lib/embedContext.ts` | Technical Pattern | New | Stage to `TP/src/app/src/widget/`. This is the shadow-DOM widget mount, the API base override, and the host-page auth bridge. |
| 23 | `chat-app/frontend/vite.widget.config.ts` | Technical Pattern | New | Stage to `TP/src/app/vite.widget.config.ts`. Retarget its `entry` to the merged widget path; output stays `dist/widget.js`. |
| 24 | `chat-app/frontend/src/components/{EnhancedChatPanel,EnhancedChatMessageBubble,ChatMessageBubble}.tsx` and `src/lib/{chatMessageUtils,textParsers,api,audioUtils,types,utils}.ts` | Technical Pattern | New | Stage to `TP/src/app/src/`. These are the widget's live dependency chain; the chat-app copies win over the scenario-app copies because the widget consumes them. **Verified: the chat-app `lib/api.ts` contains zero cart references**, so the cart skip (row 33) does not touch this copy. |
| 25 | `chat-app/frontend/public/pcm-processor.js` | Technical Pattern | New | Stage to `TP/src/app/public/pcm-processor.js`. Required by the voice worklet; must survive the merge even though the standalone chat shell does not. |
| 26 | `chat-app/frontend/src/{contexts/AuthContext.tsx,contexts/ThemeContext.tsx,hooks/use-mobile.ts,styles/*,theme/coralTheme.ts,index.css,main.css,ErrorFallback.tsx}` | Technical Pattern | New | Deduplicate against the identical scenario-app copies; keep one set under `TP/src/app/src/`. The new `ScenarioConfigProvider` (section 6A.2) is authored alongside `contexts/`. |
| 27 | `chat-app/frontend/src/components/ui/` (52 shadcn primitives), `components.json`, `tailwind.config.js`, `theme.json`, `tsconfig.json`, `package.json`, `package-lock.json`, `.npmrc` | Technical Pattern | New | Deduplicate against the scenario-app copies; keep one shared set under `TP/src/app/`. |
| 28 | `chat-app/frontend/src/{App.tsx,main.tsx}`, `index.html`, `nginx.conf`, `Dockerfile`, `startup.sh`, `runtime.config.json`, `public/runtime-config.js` | - | Out of scope | Standalone chat-app deployable shell. Only the scenario app is deployable. Removing these drops one App Service and one container image. See section 7.3. `public/config.js` is pulled out of this row into row 28a. |
| 28a | `chat-app/frontend/public/config.js` **and** `scenario-app/frontend/public/config.js` (2 files, 9 lines each, byte-identical) | - | **Out of scope** | **Reviewer decision 2i - explicit skip, verified zero readers.** Both assign `window.APP_CONFIG`; a repo-wide search across `*.ts`, `*.tsx`, `*.js`, `*.html`, `*.sh`, `*.conf`, and `Dockerfile` returns **only these two assignment sites and no reader anywhere**. Neither `index.html` loads `/config.js` - both load `/runtime-config.js`, which `startup.sh` generates at container start - and `hostConfig.ts` reads `window.__RUNTIME_CONFIG__`, not `window.APP_CONFIG`. Both files hardcode a stale live backend URL and OAuth redirect URI. **Security-flagged** in section 12. |
| 29 | `chat-app/frontend/src/components/{ChatPanel,ProductCard,ProductCardSkeleton,ProductGrid,ProductFilters,ProductRecommendation,FigmaProductCard,ChatProductCard,ChatOrderCard,CartDrawer,ThemeToggle,LoginButton,LoginForm}.tsx`, `src/components/Layout/*`, `src/lib/{data,textCleaners}.ts`, `src/vite-env.d.ts`, `src/vite-end.d.ts` | - | Out of scope | Duplicate or unreferenced copies of the scenario-app host UI. The scenario-app copies are the ones that survive (rows 38 and 40). See section 7.2. |
| 30 | `chat-app/frontend/public/{contoso-ai-icon.png,contoso-icon.png}` | Industry Scenario | New | **Amended by revision 6 (section 6B.3).** Brand assets, staged into **all three** scenarios' `assets/` folders - not retail alone. Usage confirmed before moving: all three `manifest.json` files declare `host.iconPath` = `/contoso-icon.png`, and `AppHeader.tsx` in **both** apps hardcodes `src="/contoso-icon.png"`; `contoso-ai-icon.png` is the assistant avatar hardcoded in `EnhancedChatPanel.tsx` in both apps (lines 817 and 848) and is declared in **no** manifest. Both files are byte-identical across the two apps (MD5 `E0EBD9A4...`, 749 B; MD5 `A690ECD2...`, 1290 B), so exactly one copy of each is staged per scenario, as `assets/contoso-icon.png` and `assets/contoso-ai-icon.png`. All three manifests rewrite `host.iconPath` to `assets/contoso-icon.png` and gain a **new `host.assistantIconPath`** key so the second icon stops being a pattern literal. |
| 31 | `chat-app/frontend/{LICENSE,SECURITY.md,README.md,LOCAL_AUTH_SETUP.md,.gitignore,.spark-initial-sha,spark.meta.json,.github/dependabot.yml,vite.config.ts}` | - | Out of scope | Governance, tooling provenance, and the standalone dev-server config. `vite.config.ts` is replaced by the scenario-app one (row 38). |

### 4.4 `scenario-app/` (backend)

| # | Source part | Target layer | Outcome | Action / destination |
|---|---|---|---|---|
| 32 | `scenario-app/backend/app/routers/{products,banking,healthcare}.py` | Technical Pattern | New (single merged router) | **Merge all three into one generic `TP/src/api/routers/catalog.py`.** Verified equivalent - full evidence and the generic design in section 6. The route prefix, OpenAPI tag, and item vocabulary become scenario-supplied configuration. |
| 33 | `scenario-app/backend/app/routers/{cart,orders,banking_transactions,healthcare_appointments}.py` | - | Out of scope | **All four skipped.** `orders`, `banking_transactions` and `healthcare_appointments` have zero callers. `cart.py` is skipped by reviewer direction despite one reachable call path; the full reachability trace and the mandatory companion-removal list are in section 7.1. |
| 34 | `scenario-app/backend/app/{memory_service.py,database.py,cosmos_service.py,models.py,config.py,auth.py}` and `app/routers/{auth,chat,voice_live}.py`, `app/services/*`, `app/utils/*`, `app/util/*` | Technical Pattern | New (deduplicated) | Merge into the single **`TP/src/api/`**. These are near-duplicates of the chat-app modules; reconcile per file, keeping the chat-app variant where it is a strict superset (its `main.py` adds OpenTelemetry span enrichment and session-id tracing) and the scenario-app variant where it adds capability (`memory_service.py` exists only here). Drop the cart models/containers identified in section 7.1. |
| 35 | `scenario-app/backend/app/main.py` | Technical Pattern | New (with mandatory refactor) | Becomes **`TP/src/api/main.py`** together with row 11. Replace the `if _scenario == "healthcare" / elif "banking" / else` branch (lines 93-114) with a single manifest-driven registration of the generic `catalog` router. Delete the `cart`, `orders`, `banking_transactions`, `healthcare_appointments` imports and `include_router` calls, and the "cart management, and order processing" wording in the app `description` at line 62. **Add the `GET /api/scenario/config` endpoint** with the response filtering required by section 6A.2. Collapse the dual `from .X` / `from app.X` try-except import pairs per section 4.8. | **Revision 6:** also register the `GET /api/scenario/assets/{path}` route of section 6B.3, subject to the mandatory traversal and allow-list controls in section 6B.4.
| 36 | `scenario-app/backend/{Dockerfile,.dockerignore,requirements.txt,startup.sh,env.sample}` | Technical Pattern | New (merged) | Reconcile with row 20 into one **`TP/src/api/`** build context and one requirements file. Entrypoint rewrite in section 4.8. |
| 37 | `scenario-app/backend/{pyrightconfig.json,README.md}` | - | Out of scope | Dev-loop scaffolding; README rewritten into the pattern API README. |

### 4.5 `scenario-app/` (frontend)

| # | Source part | Target layer | Outcome | Action / destination |
|---|---|---|---|---|
| 38 | `scenario-app/frontend/src/{main.tsx,App.tsx,embedChatWidget.ts,ErrorFallback.tsx}`, `index.html`, `vite.config.ts`, `nginx.conf`, `Dockerfile`, `startup.sh`, `runtime.config.json` | Technical Pattern | New | Stage to `TP/src/app/`. This is the single deployable app shell. Simplify the `Dockerfile` to a single build context now that the widget source lives in the same tree, replacing the current cross-app `widget-builder` stage. **The resulting container image is scenario-free** (section 6A.2), so one image serves all three industries. `public/config.js` is pulled out of this row into row 28a. **Revision 6:** `public/contoso-ai-icon.png` is pulled out of this row into row 41 and goes to the scenarios, not the pattern - it is Contoso branding, and leaving it in the pattern's public root would have kept a domain asset inside the image this row calls scenario-free. |
| 39 | `scenario-app/frontend/src/scenarios/ScenarioApp.tsx` | Technical Pattern | New (with mandatory refactor) | Stage to `TP/src/app/src/ScenarioApp.tsx` (no `scenarios/` folder survives). **Replace the compile-time three-way ternary and its three static imports** (`BankingApp`, `EcommerceApp`, `HealthcareApp`) with a single generic render path over the fetched config: `<CatalogApp />` selected by `catalog.cardVariant`. `hostAppTitle()` and `hostComplianceBanner()` become reads off the config context (row 40). See section 6A.3. |
| 40 | `scenario-app/frontend/src/components/*`, `src/components/Layout/*`, `src/lib/{api,audioUtils,data,hostConfig,textCleaners,textParsers,types,utils}.ts`, `src/contexts/*`, `src/hooks/*`, `src/styles/*`, `src/theme/*` | Technical Pattern | New (deduplicated, minus cart, minus domain literals) | Stage to `TP/src/app/src/` as the surviving copy of the shared host UI. Reconcile against rows 24, 26, and 27 so nothing is staged twice. **Excludes every cart artifact listed in section 7.1.** **`lib/hostConfig.ts` is rewritten as a typed accessor over the fetched config** - the `HostScenario` union, the three `Contoso*` default titles, the `genericTitles` set, and the two compliance-banner sentences are all deleted and move to scenario config (section 6A.4). This row also gains the newly authored generic `CatalogApp.tsx`, `CatalogItemCard.tsx`, `resolveItemPresentation.ts`, and `ScenarioConfigProvider.tsx` (section 6A). | **Revision 6:** the newly authored `CatalogItemCard.tsx` resolves its image from the catalog item's own `image` value rather than from the `presentation` map (section 6B.2), passing absolute `http(s)://` values through to `<img src>` unchanged and resolving every other value against `GET /api/scenario/assets/{path}`. `AppHeader.tsx` and `EnhancedChatPanel.tsx` lose their hardcoded `/contoso-icon.png` and `/contoso-ai-icon.png` literals and read `host.iconPath` / the new `host.assistantIconPath` from the config context.
| 41 | `scenario-app/frontend/public/{pcm-processor.js,contoso-icon.png,contoso-ai-icon.png}` | Technical Pattern / Industry Scenario | New (deduplicated) | `pcm-processor.js` deduplicates against row 25 into the pattern - it is an audio worklet, genuine pattern mechanism, and stays in the frontend public root. **Revision 6:** both PNGs deduplicate against row 30 (verified byte-identical) and are staged into **all three** scenarios' `assets/` folders, not into retail alone and not into the pattern. `contoso-ai-icon.png` is pulled in here from row 38. Two-layer split row. |
| 42 | `scenario-app/frontend/src/scenarios/banking/{BankingApp,BankingProductCard}.tsx` (41 + 59 lines) | - | **Out of scope (superseded)** | **Reviewer decision 2c/2f.** Superseded by the pattern's generic `CatalogApp` + `CatalogItemCard` selected by `catalog.cardVariant`. Not staged into the pattern (it is domain code) and **not staged into the scenario either** - a scenario must never carry React code (section 6A.6). Its only non-generic content is the intro prose, the error string, the `/api/accounts/` prefix, and the card field layout, all of which become config (section 6). |
| 42a | `scenario-app/frontend/src/scenarios/banking/bankingProductMeta.ts` (84 lines) | Technical Pattern / Industry Scenario | New (split) | **Mechanism to the pattern, data to the scenario.** The resolver (`id` to uppercased `id` to title alias to tags/description fallback) becomes the single generic `TP/src/app/src/lib/resolveItemPresentation.ts`. The data - the eight-entry `BANKING_PRODUCT_META` record of `image` + `highlights` and the `BANKING_PRODUCT_BY_TITLE` alias map - becomes the `presentation` block of `industry-scenarios/banking-customer-support/manifest.json`, delivered in the section 6A.2 config payload. Two-layer split row. See section 6A.5. |
| 42b | `scenario-app/frontend/public/banking/*.svg` (8 icons) | Industry Scenario | New | **Extended in place by revision 6 (section 6B.3) - this row supersedes its revision-4 text and no duplicate row is created.** Destination flattens from `assets/banking/` to `industry-scenarios/banking-customer-support/assets/`: the domain folder level is redundant inside a scenario already named for that domain, and it would leak into every rewritten CSV value. Two things change substantively. The assets are **no longer copied into the app's public root by the Builder** - that revision-4 step is withdrawn because it contradicts section 6A.1 - and they are instead served by `GET /api/scenario/assets/{path}` from `SCENARIO_PATH`. `scenarios/banking/data/catalog.csv`'s `image` column is rewritten from `/banking/<name>.svg` to `assets/<name>.svg` for all 8 rows. Verified: 8 files, and all 8 CSV values map one-for-one onto the 8 filenames. |
| 43 | `scenario-app/frontend/src/scenarios/ecommerce/EcommerceApp.tsx` (66 lines) | - | **Out of scope (superseded)** | **Reviewer decision 2c/2f.** After the section 7.1 cart removal and dropping its no-op client-side filter/sort (`searchQuery`, `selectedCategory`, `sortBy` are `useState` values whose setters are discarded and never called), the only residual difference from `BankingApp`/`HealthcareApp` is the grid layout via `MainContent` + `ProductGrid` versus a stacked card list - exactly what `catalog.cardVariant` expresses. Its richer error panel (heading + message + retry button) is the one thing worth keeping and becomes the generic app's single error state. See section 6A.3. |
| 44 | `scenario-app/frontend/src/scenarios/healthcare/{HealthcareApp,HealthcareServiceCard}.tsx` (41 + 59 lines) | - | **Out of scope (superseded)** | Same as row 42. Its `/api/services/` prefix, intro prose, error string, and card field layout become config. |
| 44a | `scenario-app/frontend/src/scenarios/healthcare/healthcareServiceMeta.ts` (81 lines) | Technical Pattern / Industry Scenario | New (split) | Same split as row 42a: the resolver deduplicates into the single `resolveItemPresentation.ts` (the two files' resolvers are structurally identical), and `HEALTHCARE_SERVICE_META` + `HEALTHCARE_SERVICE_BY_TITLE` become the `presentation` block of `industry-scenarios/healthcare-patient-support/manifest.json`. Two-layer split row. |
| 44b | `scenario-app/frontend/public/healthcare/*.svg` (8 icons) | Industry Scenario | New | **Extended in place by revision 6 (section 6B.3) - supersedes its revision-4 text; no duplicate row is created.** Identical treatment to row 42b: destination flattens to `industry-scenarios/healthcare-patient-support/assets/`, delivery moves from the withdrawn Builder public-root copy to `GET /api/scenario/assets/{path}` over `SCENARIO_PATH`, and `scenarios/healthcare/data/catalog.csv`'s `image` column is rewritten from `/healthcare/<name>.svg` to `assets/<name>.svg` for all 8 rows. Verified: 8 files, and all 8 CSV values map one-for-one onto the 8 filenames. The 16 SVGs of rows 42b and 44b together total 8,389 B. |
| 45 | `scenario-app/frontend/{package.json,package-lock.json,components.json,tailwind.config.js,theme.json,tsconfig.json,.npmrc,src/components/ui/*}` | Technical Pattern | New (deduplicated) | Single surviving copy, reconciled with row 27. |
| 46 | `scenario-app/frontend/{LICENSE,SECURITY.md,README.md,LOCAL_AUTH_SETUP.md,.gitignore,.spark-initial-sha,spark.meta.json,.github/dependabot.yml,src/vite-env.d.ts,src/vite-end.d.ts}` | - | Out of scope | Governance and tooling provenance. `vite-end.d.ts` is an unreferenced typo duplicate of `vite-env.d.ts`. |

### 4.6 `infra/`

| # | Source part | Target layer | Outcome | Action / destination |
|---|---|---|---|---|
| 47 | `infra/main.bicep` (flavor selector), `infra/build_bicep.md` | - | Out of scope | A vanilla-versus-AVM selector. The factory mandates vanilla only, so the selector has no target. Its parameter list informs the pattern and core parameter surfaces, **minus the two BYO toggles**: `existingFoundryProjectResourceId` (lines 145, 223, 254) and `existingLogAnalyticsWorkspaceId` (lines 142, 222, 253) are **not** re-expressed in any staged layer (reviewer decision 5, revision 5 - sections 7.4 and 7.5). |
| 48 | `infra/avm/` (`main.bicep`, `main.json`, 40 modules) | - | Out of scope | Hard no-AVM rule in `references/layer-structures.md`. Never carried into a staged layer. Includes the AVM twin of `existing-project-setup.bicep`; neither copy is staged. |
| 49 | `infra/main.json`, `infra/bicep/main.json`, `infra/avm/main.json` | - | Out of scope | Compiled ARM build output. |
| 50 | `infra/bicep/modules/ai/{ai-foundry-project,ai-foundry-connection,ai-foundry-model-deployment,ai-search,ai-search-identity}.bicep` | **Stable Core** | **New** | **Stage to `SC/infra/bicep/modules/`** as the new `agentic-apps` core. Verified vanilla: no `br/public` or `avm/` reference in any of the five; `ai-foundry-project.bicep` declares both `Microsoft.CognitiveServices/accounts` and `.../accounts/projects`, and `ai-search.bicep` declares `Microsoft.Search/searchServices`. A new `SC/infra/bicep/main.bicep` composes them, **greenfield only** - `existing-project-setup.bicep` is excluded (row 50a). **Bicep only** (accepted deviation, section 12). See sections 5.2, 7.4 and 8. |
| 50a | `infra/bicep/modules/ai/existing-project-setup.bicep` | - | **Out of scope** | **Reviewer decision 5a (revision 5) - the revision-4 restoration is REVERSED and the revision-3 skip is restored.** The bring-your-own / reuse-an-existing-Foundry-project path is excluded **to reduce complexity**; the composed solution provisions the Foundry account and project **greenfield only**. Confirmed present at this path (the `infra/avm/` twin is separately out of scope under row 48). It is **not** part of row 54's 19 unreferenced modules - it is genuinely referenced at `infra/bicep/main.bicep` line 273 - so this is a distinct exclusion, not a double count. **Skipping it is only safe with all 17 companion removals - see section 7.4.** |
| 51 | `infra/bicep/modules/monitoring/{log-analytics,app-insights}.bicep` | Technical Pattern | New | **Resolved decision (see section 13, Q5).** Because `agentic-apps` is scoped to Foundry + Project + Search only, observability has no core owner in this composition and stays in `TP/infra/bicep/modules/monitoring/`. Observability is normally core-owned; this placement follows from the deliberately scoped core. **Both modules are staged and both are still deployed - the pattern provisions Log Analytics and Application Insights greenfield.** Only the *attach-to-an-existing-workspace* branch around `log-analytics.bicep` is removed (section 7.5); the module itself is untouched and its invocation condition simplifies from `if (enableMonitoring && !useExistingLogAnalytics)` to `if (enableMonitoring)`. |
| 52 | `infra/bicep/modules/compute/{container-registry,app-service-plan,app-service}.bicep`, `modules/data/cosmos-db-nosql.bicep`, `modules/identity/role-assignments.bicep` | Technical Pattern | New | Stage to `TP/infra/bicep/modules/` (**Bicep only**). Exactly the app-hosting and app-specific resource set the pattern layer owns, matching the live `chat-with-data` pattern infra precedent. **`role-assignments.bicep` is staged with its `useExistingAIProject` branches removed** (revision-5 restoration of the revision-3 position): the two params, the three `split()` vars, the two `cross-scope-role-assignment.bicep` module blocks, and the four `!useExistingAIProject &&` condition prefixes all go - see section 7.4. |
| 52a | `infra/bicep/modules/identity/cross-scope-role-assignment.bicep` | - | **Out of scope** | **Orphaned again by decision 5a (revision 5).** Its only two callers are `role-assignments.bicep` lines 117 and 140, both of which are removed with the BYO branch, so nothing invokes it. Moved out of row 52 to its own explicit Out-of-scope row so the skip is visible rather than implied. |
| 53 | `infra/bicep/main.bicep` | Technical Pattern | New (reduced) | Stage to `TP/infra/bicep/main.bicep` reduced to the row 51 and 52 modules, with the core-owned resources (row 50) converted into input parameters (Foundry endpoint, Foundry project resource id, Foundry project endpoint, Foundry account name, project principal id, AI Search endpoint and name). App Insights is pattern-owned, so its connection string is a pattern **output**, not an input. Reduce four App Service module invocations to exactly two (`api`, `app`). **The `useExistingAIProject` plumbing at lines 642-644 is removed** (section 7.4) and **the `existingLogAnalyticsWorkspaceId` plumbing at lines 142, 174, 237 and 246-247 is removed** (section 7.5); `enableMonitoring` itself is retained. |
| 54 | `infra/bicep/modules/` remainder: `ai/ai-services.bicep`, `identity/managed-identity.bicep`, `compute/{container-app,container-app-environment,container-instance,function-app,kubernetes}.bicep`, `data/{app-configuration,cosmos-db-mongo,event-grid,event-hub,postgresql-flexible-server,sql-database,storage-account}.bicep`, `fabric/fabric-capacity.bicep`, `monitoring/{portal-dashboard,workbook}.bicep`, `security/key-vault.bicep` | - | Out of scope | Unreferenced module library (19 modules). Verified: `infra/bicep/main.bicep` invokes only the modules in rows 50, 50a, 51, and 52, and the only nested invocations are `ai-search.bicep` to `ai-search-identity.bicep` and `role-assignments.bicep` to `cross-scope-role-assignment.bicep` (row 52a). Rows 50a and 52a are excluded **by reviewer decision, not by unreachability**, and are counted separately from these 19. See section 7.2. |
| 55 | `infra/main.parameters.json`, `infra/main.waf.parameters.json` | - | Out of scope | Solution-level azd parameter files. Pattern-relevant entries (`appServicePlanSku`, `deploymentScenario`, `enableMonitoring`, private-networking toggles) are re-expressed as pattern parameters in row 53; core-relevant entries as core parameters in row 50. **Revision-5 change:** *both* BYO entries are now dropped rather than re-expressed - `existingFoundryProjectResourceId` / `${AZURE_EXISTING_AIPROJECT_RESOURCE_ID}` (`main.parameters.json` lines 38-40, `main.waf.parameters.json` lines 41-43, section 7.4) **and** `existingLogAnalyticsWorkspaceId` / `${AZURE_ENV_EXISTING_LOG_ANALYTICS_WORKSPACE_RID}` (`main.parameters.json` lines 35-37, `main.waf.parameters.json` lines 38-40, section 7.5). The files themselves are not staged either way. |
| 56 | `infra/scripts/post-provision/build_push_images.{ps1,sh}` | Technical Pattern | **Delta/Upgrade** | Target `technical-patterns/.shared/build-and-push-acr.{ps1,sh}`. Reuse with a parameterization delta. Verdict unchanged from revision 1; full detail in section 5.1. |
| 57 | `infra/scripts/post-provision/agent_scripts/{01_create_agents.py,requirements.txt,run_create_agents_scripts.ps1,run_create_agents_scripts.sh}` | Technical Pattern | New | Stage to `TP/scripts/agents/`. Creates the Foundry connected-agent trio from the scenario manifest and agent text files. Distinct from `chat-with-data/scripts/agents/` (which builds MCP tool connections to a Fabric Data Agent). |
| 58 | `infra/scripts/post-provision/data_scripts/{01_create_products_search_index.py,02_create_policies_search_index.py,03_write_products_to_cosmos.py,azure_credential_utils.py,requirements.txt,run_upload_data_scripts.ps1,run_upload_data_scripts.sh}` | Technical Pattern | New | Stage to `TP/scripts/data/`. Already parameterized through `scenario_loader`, satisfying the Composition Readiness "parameterized data loading" rule once row 70 lands. Rename the `products` vocabulary to `catalog`. |
| 59 | `infra/scripts/post-provision/postprovision_data_agents.{ps1,sh}` | Technical Pattern | New | Stage to `TP/scripts/`. Single post-provision orchestrator over rows 57 and 58. |
| 60 | `infra/scripts/pre-provision/preflight_scenario.{ps1,sh}` and `infra/scripts/scenario_bootstrap.py` | Technical Pattern | New | Stage to `TP/scripts/`. Scenario selection and validation is pattern mechanism, not scenario data. **Extended by section 6A.7**: it also validates the scenario manifest against the pattern's published config JSON schema at compose time. |
| 61 | `infra/scripts/utilities/azure_credential_utils.py` | Technical Pattern | New (deduplicated) | One surviving copy at `TP/scripts/shared/azure_credential_utils.py`; the `data_scripts/` copy is a duplicate. |
| 62 | `infra/scripts/post-provision/data/{policies/*.txt,products/products.csv}` | - | Out of scope | Byte-identical duplicate of `scenarios/ecommerce/data/`. Verified by MD5: `AboutContosoPaints.txt` `CEC20BE5...`, `ReturnPolicy.txt` `42C6CC13...`, `Warranty.txt` `CC88B968...`, `products.csv` = `catalog.csv` `F72318C2...` at 5039 bytes. The `scenarios/` copies survive (row 68). **Revision-6 precision note (nothing in this row is reversed).** This duplicate finding covers **only** the `policies/` and `products/` subfolders named in this row's own path. It has never covered `Color Images/`, which has always been a separate row (63) with outcome **New**. Re-verified afresh: `scenarios/ecommerce/data/` contains exactly `catalog.csv` plus `policies/{AboutContosoPaints,ReturnPolicy,Warranty}.txt` and **no image file of any kind**, so the 16 JPGs are unique to `Color Images/` and fall outside this finding entirely. The revision-6 correction is to row 63's **destination only**. |
| 63 | `infra/scripts/post-provision/data/Color Images/*.jpg` (16 files) | Industry Scenario | New | **Destination corrected by revision 6 (section 6B.3); the outcome is unchanged.** This row was already **New** and never Out of scope, so nothing is reversed here - see row 62's precision note for why the MD5 duplicate finding never covered these files. Stage to `industry-scenarios/retail-customer-support/assets/` (was `unstructured_data/images/`) so all three scenarios share one asset convention and one delivery route. Verified: 16 files, 167,556 B total, unique to this folder, and their 16 filenames match the 16 distinct leaf names in retail's `catalog.csv` `image` column one-for-one. That column's 16 absolute `raw.githubusercontent.com/microsoft/customer-chatbot-solution-accelerator/refs/heads/main/infra/scripts/post-provision/data/Color%20Images/<name>.jpg` values are rewritten to `assets/<name>.jpg`, dropping the `%20` escape along with the space in the folder name. |
| 64 | `infra/scripts/pre-provision/{checkquota.sh,quota_check_params.sh,validate_bicep_params.py}` | - | Out of scope | Solution-level azd preflight and repo CI validation tied to the dual-flavor selector. Not staged. Verified: `validate_bicep_params.py` names `AZURE_EXISTING_AIPROJECT_RESOURCE_ID` in its `_ENV_VAR_EXCEPTIONS` set (line 39) and its docstring (line 14); with row 50a out of scope that exception is simply dropped, and the pattern's own preflight (row 60) must **not** carry it. It never referenced the Log Analytics variable at all. |
| 65 | `infra/scripts/post-provision/sync_azd_hook_env.{ps1,sh}` | - | Out of scope | azd hook environment plumbing, regenerated by the factory build. |
| 66 | `infra/vscode_web/` (`.env`, `codeSample.py`, `endpointCodeSample.py`, `index.json`, `install.sh`, `requirements.txt`, `endpoint-requirements.txt`, `README.md`, `README-noazd.md`, `LICENSE`, `.gitignore`) | - | Out of scope | VS Code Web sample harness for the source template. The checked-in `.env` carries a real `AZURE_SUBSCRIPTION_ID`, a Foundry project resource id, and an agent id. **Security-flagged** in section 12. |

### 4.7 `scenarios/`, `documents/`, `tests/`

| # | Source part | Target layer | Outcome | Action / destination |
|---|---|---|---|---|
| 67 | `scenarios/banking/{manifest.json,agents/{catalog,chat,policy}_agent.txt,data/catalog.csv,data/policies/{DigitalBanking,FeeSchedule,FraudReporting}.txt}` | Industry Scenario | New | Stage to `industry-scenarios/banking-customer-support/`. `industry: financial services`, group `fsi`. The manifest gains the `catalog` block (section 6) and the `presentation` block (row 42a). No live scenario matches (see section 5.3). | **Revision 6 (section 6B.3):** the manifest rewrites `host.iconPath` to `assets/contoso-icon.png` and gains `host.assistantIconPath`; `data/catalog.csv`'s `image` column is rewritten to `assets/*.svg` (row 42b); and the scenario gains a flat `assets/` folder holding 8 SVGs plus the two Contoso PNGs - 10 files.
| 68 | `scenarios/ecommerce/{manifest.json,agents/*.txt,data/catalog.csv,data/policies/{AboutContosoPaints,ReturnPolicy,Warranty}.txt}` | Industry Scenario | New | Stage to `industry-scenarios/retail-customer-support/`. `industry: retail and consumer goods`, group `rcg`. The manifest gains `catalog` and `presentation` blocks. **Revision 6 correction (section 6B.2):** retail's `presentation` block no longer carries images at all, because the `image` key is removed from `presentation` entirely and the CSV column becomes the single source of truth. What retail authors fresh (it has no `*Meta.ts`) is therefore `highlights` per item plus a `defaultImage`, not an image map. The manifest also rewrites `host.iconPath` to `assets/contoso-icon.png` and gains `host.assistantIconPath`; `data/catalog.csv`'s 16 absolute `raw.githubusercontent.com` `image` values are rewritten to `assets/*.jpg` (row 63); and the scenario gains a flat `assets/` folder holding the 16 JPGs plus the two Contoso PNGs - 18 files. |
| 69 | `scenarios/healthcare/{manifest.json,agents/*.txt,data/catalog.csv,data/policies/{BillingFAQ,PatientRights,VisitingHours}.txt}` | Industry Scenario | New | Stage to `industry-scenarios/healthcare-patient-support/`. `industry: healthcare and life sciences`, group `hls`. The manifest gains `catalog` and `presentation` blocks (row 44a). | **Revision 6 (section 6B.3):** the manifest rewrites `host.iconPath` to `assets/contoso-icon.png` and gains `host.assistantIconPath`; `data/catalog.csv`'s `image` column is rewritten to `assets/*.svg` (row 44b); and the scenario gains a flat `assets/` folder holding 8 SVGs plus the two Contoso PNGs - 10 files.
| 70 | `scenarios/scenario_loader.py`, `scenarios/__init__.py` | Technical Pattern | New (with mandatory refactor) | Stage to `TP/scripts/shared/scenario_loader.py` with the three de-hardcoding fixes, the first of which is now the `SCENARIO_PATH` variable of the composition contract. Full detail in section 13, Q3, aligned with section 6A.1. |
| 71 | `scenarios/__pycache__/` | - | Out of scope | Build cache. |
| 72 | `documents/{TechnicalArchitecture.md,scenario-deployment-guide.md,LocalDevelopmentSetup.md,ACRBuildAndPushGuide.md,AppAuthentication.md,CreateNewAppRegistration.md}` and the `documents/Images/` files those six reference | Technical Pattern | New (rewritten) | Stage to `TP/docs/` after rewriting to the pattern's extension-point contract, which must now document the full `host`/`welcome`/`catalog`/`presentation`/`cardVariant` config surface and the composition contract (section 6A). |
| 73 | `documents/{DeploymentGuide.md,AzureAccountSetUp.md,AzureGPTQuotaSettings.md,QuotaCheck.md,CustomizingAzdParameters.md,DeleteResourceGroup.md,TroubleShootingSteps.md,AVMPostDeploymentGuide.md,LogAnalyticsReplicationDisable.md,ReuseLogAnalytics.md,ReuseFoundryProject.md,chatplan.md}` and their remaining `documents/Images/` assets | - | Out of scope | Solution-level azd deployment and planning documentation. The factory build generates its own deployment guide. **Revision-5 note (supersedes the revision-4 note):** `ReuseFoundryProject.md` and `ReuseLogAnalytics.md` each document a reuse capability the split **no longer ships** (rows 50a and section 7.5), so both are dropped outright - neither is rewritten into `SC/README.md` or `TP/README.md`. What *is* required instead is a one-line documented limitation in each README (sections 8 and 9). `CustomizingAzdParameters.md` line 24 and `DeploymentGuide.md` line 276 both advertise the Log Analytics reuse path and are dropped with the rest of the file. |
| 74 | `tests/e2e-test/{base/,config/,pages/,tests/,pytest.ini,requirements.txt,README.md,.gitignore}` | - | **Out of scope** | Reviewer decision 6. The whole subtree is out of scope and staged into no layer. Consequence recorded as a risk in section 12 and reflected in the fit score, partially offset by the section 6A.7 config validation. |
| 75 | `tests/e2e-test/testdata/golden_path_data.json` | - | **Out of scope** | Part of the same subtree. Previously proposed for `retail-customer-support/evals/`; now dropped per reviewer decision 6. |
| 76 | `tests/e2e-test/results/6207_reference_count.html` | - | Out of scope | Test run artifact, inside the same out-of-scope subtree. |

### 4.8 Import-path and entrypoint rewrites forced by the collapsed layout

Removing the intermediate `app/` package (reviewer decision 4) forces these mechanical rewrites
during staging. They are listed here so the classifier applies them consistently and the
reviewer can see the blast radius.

| Where | Current | Staged |
|---|---|---|
| `routers/*.py`, `services/*.py`, `utils/*.py` | `from ..database import get_db_service`, `from ..models import Product`, `from ..config import settings` | `from database import get_db_service`, `from models import CatalogItem`, `from config import settings` |
| `main.py` router imports | `from .routers import auth` with an `except ImportError: from app.routers import auth` fallback (lines 31-40, 93-114) | A single `from routers import auth, catalog, chat, chat_config, scenario_config_api, voice_live` - the dual try-except pair is no longer needed because there is only one import shape |
| `main.py` module imports | `from .auth import get_current_user`, `from .config import settings`, `from .scenario_config import current_scenario` (plus the `app.`-prefixed fallbacks) | `from auth import get_current_user`, `from config import settings`, `from scenario_config import current_scenario` |
| `Dockerfile` (both backends) | `WORKDIR /app`, `ENV PYTHONPATH=/app`, `COPY . .` with build context `backend/`, so modules land at `/app/app/`; `CMD ["uvicorn", "app.main:app", ...]` | Build context becomes `TP/src/api/`, so `COPY . .` lands modules directly at `/app/`; `CMD ["uvicorn", "main:app", ...]` |
| `startup.sh` (both backends) | `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000` | `python -m uvicorn main:app --host 0.0.0.0 --port 8000` |
| Package markers | `app/__init__.py` | Removed. `routers/__init__.py`, `services/__init__.py`, `utils/__init__.py` are retained. |
| Build/deploy scripts | Any `scenario-app/backend` or `app.main` reference in `build_push_images` and the azd hooks | Repointed at `src/api` and `main:app`; folded into the row 56 delta against `technical-patterns/.shared/build-and-push-acr.*` |
| Frontend scenario imports (revision 4) | `import { BankingApp } from '@/scenarios/banking/BankingApp'` and the two siblings in `ScenarioApp.tsx` | Deleted. `src/scenarios/` does not exist in the staged pattern; `ScenarioApp.tsx` moves to `src/ScenarioApp.tsx` and renders `<CatalogApp />` from the config context |

The frontend otherwise keeps the `@/` path alias rooted at `TP/src/app/src/`.

## 5. Delta / New detail

### 5.1 Delta/Upgrade parts

**`infra/scripts/post-provision/build_push_images.{ps1,sh}` maps to `technical-patterns/.shared/build-and-push-acr.{ps1,sh}`.** *(Unchanged from revision 1.)*

* Why it is a capability match: both perform an `az acr build` remote build (no local Docker),
  push to the deployment ACR, repoint App Services with `az webapp config container set`, restart
  them, and auto-discover ACR and app names from the resource group. The shared script is already
  shaped for exactly two App Services (`-ApiAppName`, `-WebAppName`), which is precisely the target
  topology.
* Concrete delta needed in the shared script: the image triples are hardcoded at lines 219-228 as
  `da-app` / `$SolutionPath/src/App` / `WebApp.Dockerfile` and `da-api` / `$SolutionPath/src/api/python`
  / `ApiApp.Dockerfile`, and app discovery hardcodes the `api-` / `app-` name prefixes with a
  `python|dotnet` `-BackendRuntime` validate-set. The delta makes the image name, build context, and
  Dockerfile filename configurable (parameters or a small manifest) so a pattern whose layout is
  `src/api` plus `src/app` can reuse it unchanged.
* What the contribution's own script contributes back: nothing reusable beyond confirming the flow.
  Its four-image, four-app-service structure disappears in the target design.

**This is the only Delta in the plan.** The `stable-cores/microsoft-iq` Fabric-capacity delta
proposed in revision 1 is **withdrawn** per reviewer decision 2 (revision 2). No change of any kind
is proposed to `microsoft-iq`.

### 5.2 New parts and destinations

* Stable core to `stable-cores/agentic-apps/` (row 50). **Bicep only** - see section 8.
  **Greenfield only** - row 50a is excluded (section 7.4).
* Technical pattern to `technical-patterns/chat-with-data-voice/` (rows 10-15, 19, 20, 22-27, 32,
  34-36, 38-41, 42a, 44a, 45, 51-53, 57-61, 70, 72). **Bicep only** - see section 9. Row 52a is
  excluded (section 7.4); observability is staged and provisioned greenfield (section 7.5).
* Industry scenario to `industry-scenarios/banking-customer-support/` (rows 30, 41, 42a, 42b, 67).
* Industry scenario to `industry-scenarios/retail-customer-support/` (rows 30, 41, 63, 68).
* Industry scenario to `industry-scenarios/healthcare-patient-support/` (rows 30, 41, 44a, 44b, 69).
  *(Revision 6: rows 30 and 41 now feed all three scenarios, not retail alone - section 6B.3.)*

**Newly authored pattern artifacts (not source paths, so they carry no table row).** These are
created by the classifier as part of decision 2 and must appear in the comparison report's staged
file inventory: `TP/src/app/src/CatalogApp.tsx`, `TP/src/app/src/components/CatalogItemCard.tsx`,
`TP/src/app/src/lib/resolveItemPresentation.ts`,
`TP/src/app/src/contexts/ScenarioConfigProvider.tsx`,
`TP/src/api/routers/scenario_config_api.py`, and `TP/config/scenario-config.schema.json`.
**Revision 7 drops `TP/config/scenario-config.sample.json` from this set** (section 6A.7), leaving
the schema as the only file the pattern's `config/` folder carries - **six** newly authored
artifacts, not seven. Rationale and contracts in section 6A.

### 5.3 Matched parts (not staged)

**None.** Revision 1 recorded the contribution's Foundry/Search and observability modules as
Matched against `microsoft-iq`; reviewer decision 2 reclassifies the Foundry/Search set as **New**
under `agentic-apps` (row 50) and reviewer direction places observability in the pattern
(row 51). No live technical pattern or industry scenario matches either: `client-meeting-prep` is
financial-services meeting preparation, `sales-product-analysis` is retail sales and product
performance analytics, and `supply-chain` is cross-industry inventory and procurement. None is a
customer-support conversational scenario and none supplies a catalog plus policy corpus with agent
instruction text, so all three contributed packs are genuinely New.

**Recorded overlap note (no action).** `stable-cores/microsoft-iq` already deploys a Foundry
account and project with connections (`modules/foundry.bicep`) and Azure AI Search
(`modules/ai-search.bicep`) in both Bicep and Terraform, so the new `agentic-apps` core overlaps
it on those capabilities. **The reviewer has acknowledged and deliberately accepted this overlap.**
This note exists only to record that the comparison was performed. It is not an action, not a
recommendation to reuse `microsoft-iq`, and not a request to reopen the decision. The forward risk
it implies - two cores whose Foundry and Search modules can drift - is carried in section 12.

## 6. The three catalog routers: verification and the generic merge

Reviewer decision 5 asked whether `products.py`, `banking.py`, and `healthcare.py` really call the
same function, and to specify a single generic router. **All three files were read in full.**

### 6.1 What each router actually is

| Router | Prefix | OpenAPI tag | Endpoints | Data access |
|---|---|---|---|---|
| `products.py` | `/api/products` | `products` | 8: `GET /`, `GET /categories`, `GET /featured`, `GET /{product_id}`, `POST /`, `PUT /{product_id}`, `DELETE /{product_id}`, `GET /{product_id}/related` | `get_db_service().get_products(search_params)`, `.get_product_categories()`, `.get_featured_products()`, `.get_product()`, `.create_product()`, `.update_product()`, `.delete_product()`, `.get_related_products()` |
| `banking.py` | `/api/accounts` | `banking` | 1: `GET /` | `get_db_service().get_products(search_params)` - identical call |
| `healthcare.py` | `/api/services` | `healthcare` | 2: `GET /`, `GET /categories` | `get_db_service().get_products(search_params)` and `.get_product_categories()` - identical calls |

### 6.2 Verdict: the reviewer is correct - they are equivalent, and the merge is not forced

* **Same data-access function, confirmed.** All three list endpoints call
  `await get_db_service().get_products(search_params)`. All three declare
  `response_model=List[Product]` and import `Product` from `..models`. There is **no** response
  shaping, no field renaming, no domain-specific filter, and no post-processing in any of the three.
* **Banking and healthcare are strict behavioral subsets of `products.py`.** They expose only
  `category` and `query`, and they hardcode `sort_by="name"` / `sort_order="asc"` - which are
  already the `products.py` defaults (`sort_by: str = Query("name")`,
  `sort_order: str = Query("asc")`). Calling `GET /api/products/?category=X&query=Y` produces an
  identical result to `GET /api/accounts/?category=X&query=Y`.
* **`healthcare.py`'s `GET /categories` is equivalent** to `products.py`'s `GET /categories`: both
  return `await get_db_service().get_product_categories()` with the same
  `"Error fetching categories"` message.
* **What actually differs** is limited to four cosmetic things: the route prefix
  (`products` / `accounts` / `services`), the OpenAPI tag, the operation function names
  (`get_products` / `get_accounts` / `get_services`), and the noun in the 500 error message
  (`products` / `accounts` / `services`). Every one of them is presentation, not behavior.
* **Consumer confirmation.** The three frontends call exactly the three list endpoints and nothing
  else: `lib/api.ts:162` calls `/api/products/`, `BankingApp.tsx:8` calls `/api/accounts/`, and
  `HealthcareApp.tsx:8` calls `/api/services/`. No frontend calls `POST`/`PUT`/`DELETE`,
  `featured`, `{id}`, or `{id}/related`.

### 6.3 The single generic router

**Module:** `technical-patterns/chat-with-data-voice/src/api/routers/catalog.py`.

**Router construction** - prefix and tag come from configuration, never from code:

```python
router = APIRouter(prefix=catalog_config.route_prefix, tags=["catalog"])
```

**Endpoints (retained):**

| Endpoint | Replaces | Note |
|---|---|---|
| `GET {prefix}/` | `products.get_products`, `banking.get_accounts`, `healthcare.get_services` | Keeps the full `products.py` query surface (`category`, `min_price`, `max_price`, `min_rating`, `in_stock_only`, `query`, `sort_by`, `sort_order`, `page`, `page_size`). Banking and healthcare simply never send the extra params, and the defaults reproduce their behavior exactly. |
| `GET {prefix}/categories` | `products.get_product_categories`, `healthcare.get_service_categories` | Equivalent implementations. |
| `GET {prefix}/{item_id}` | `products.get_product` | Retained; generic. |
| `GET {prefix}/featured` | `products.get_featured_products` | Retained; generic. |
| `GET {prefix}/{item_id}/related` | `products.get_related_products` | Retained; generic. |

**Endpoints dropped:** `POST /`, `PUT /{id}`, `DELETE /{id}` (the "Admin only" CRUD write surface).
No frontend, script, or remaining test calls them, and catalog content is loaded by
`TP/scripts/data/03_write_products_to_cosmos.py` at post-provision time, not through the API.
Recorded as an explicit skip in section 7.2.

**Vocabulary neutralization:** `Product` becomes `CatalogItem`, `product_id` becomes `item_id`, and
the error strings become `f"Error fetching {catalog_config.item_plural}: {e}"` so the domain noun is
supplied, not compiled in. `database.get_products()` / `get_product_categories()` and friends are
renamed to `get_catalog_items()` / `get_catalog_categories()` in the same pass (row 34).

**Where the per-industry differences live.** They are scenario-supplied configuration read through
`scenario_loader`/`scenario_config` from the scenario's `manifest.json`, and the scenario's
`metadata.yaml` declares that it supplies them. The `catalog` block below is **extended in
revision 4** with `cardVariant` and `copy` (decision 2c/2f) - this is the single authoritative
`catalog` block; section 6A does not define a competing one.

| Config key (scenario `manifest.json`, `catalog` block) | banking | retail | healthcare |
|---|---|---|---|
| `catalog.routePrefix` | `/api/accounts` | `/api/products` | `/api/services` |
| `catalog.itemSingular` | `account` | `product` | `service` |
| `catalog.itemPlural` | `accounts` | `products` | `services` |
| `catalog.cardSchema` | field map for the account card layout | field map for the product card layout | field map for the service card layout |
| `catalog.enabledEndpoints` | `[list]` | `[list, categories, item, featured, related]` | `[list, categories]` |
| `catalog.cardVariant` (new, revision 4) | `list` | `grid` | `list` |
| `catalog.copy.intro` (new, revision 4) | "Explore personal, business, and wealth products..." | retail intro copy | "Browse departments and clinical programs..." |
| `catalog.copy.loadError` (new, revision 4) | "Unable to load banking products." | "Failed to Load Products" | "Unable to load care services." |

`metadata.yaml` side: each scenario's `requiredPatternCapabilities` gains `catalog-index`, and its
`domainAssets` records the `catalog` block above as the configuration it supplies; the pattern's
`scenarioExtensionPoints` declares `catalog.routePrefix`, `catalog.itemSingular`,
`catalog.itemPlural`, `catalog.cardSchema`, `catalog.enabledEndpoints`, `catalog.cardVariant`, and
`catalog.copy`. Full metadata wiring, including the `host`/`welcome`/`presentation` surface, is in
section 11.2.

**Registration:** `main.py` registers `catalog.router` unconditionally, replacing the
`if healthcare / elif banking / else` branch at lines 93-114 entirely.

## 6A. Composition contract and UI genericization (reviewer decision 2 - DECIDED)

This section records an **approved design**, not an open question. It is the reviewer's answer to
the Technical Pattern domain-independence rule in `SKILL.md`: *"the UI (branding, labels, theme,
layout, which panels/agents appear) is externalized as configurable extension points a scenario
supplies at compose time."* Every item below is decided; section 12 carries only the residual
execution risks.

### 6A.1 The composition contract: copy plus environment, never patch

**The rule.** Composing a solution from the three layers must **never** require editing
technical-pattern source. If a compose step would have to open a `.tsx` or `.py` file in the
pattern and change a literal, the pattern is wrong and needs another config-selected option.

**What the Builder does, and only this:**

1. Copies the pattern's `src/` **verbatim** into `solutions/<slug>/src/`.
2. Copies the industry scenario folder **verbatim** into `solutions/<slug>/src/api/scenario/` -
   **inside the API Docker build context**, not to a sibling `solutions/<slug>/scenario/`. The API
   `Dockerfile` uses `WORKDIR /app` with `COPY . .` over a build context of `src/api`, so a scenario
   staged at `src/api/scenario/` lands in the image at `/app/scenario` with no Dockerfile change. A
   sibling folder outside the build context is never copied, and the container starts with no
   manifest.
3. Sets `SCENARIO_PATH=/app/scenario` **on the API app only**. The web app carries no
   `SCENARIO_PATH` setting - nginx never reads it - and that setting has been removed.
4. Wires the Stable Core's Bicep **outputs** into the pattern's Bicep **parameters**
   (the same mechanism section 7.4 relies on for the BYO Foundry identifiers).

**Ordering constraint.** Step 2 runs **before the container image is built**, not after
provisioning. The scenario is baked into the API image by `COPY . .`, so if the build runs first no
later provisioning step can place the manifest inside the running container.

**`SCENARIO_PATH` supersedes `SCENARIOS_DIR`.** The three `scenario_loader.py` de-hardcoding fixes
already in this plan (section 13, Q3) are the same change viewed from the loader side, not an
additional one:

* Q3 fix 1 (`SCENARIOS_DIR = REPO_ROOT / "scenarios"` replaced by an environment variable with a
  discovery-walk default) **is** this contract's step 3. The variable name is `SCENARIO_PATH`, and
  it points at a **single** scenario folder, not a directory of scenarios - which also removes the
  need for the loader's scenario-id selection logic at compose time.
* Q3 fixes 2 and 3 (drop `VALID_SCENARIOS`, drop the tool-name fallback dictionaries) are unchanged
  and unrelated to the variable rename.
* `chat-app/backend/app/scenario_config.py` (row 12) reads the same `SCENARIO_PATH`; its existing
  `SCENARIOS_DIR` env var and parent-walk are replaced, not kept alongside.

`SCENARIO_PATH` is recorded in the pattern's `configuration` metadata block, in
`TP/src/api/env.sample` (row 20), and in `TP/docs/` (row 72).

### 6A.2 Scenario config is served by the API (Option A)

**Decision: Option A.** The API already loads the manifest through
`scenario_loader.load_manifest()`, so it is the natural owner of the config surface.

**New endpoint:** `GET /api/scenario/config`, implemented in
`TP/src/api/routers/scenario_config_api.py` and registered by `main.py` (row 35).

**It returns only the presentation subset:** `host`, `welcome`, `catalog`, `presentation`.

**It must NOT return** `search.catalogIndex`, `search.policiesIndex`, any `agents.*` prefix or tool
name, or any `data.*` path. Those are server-side deployment details; shipping them to a browser is
needless information disclosure with no functional benefit - it tells an unauthenticated page
reader the exact Azure AI Search index names, the Foundry agent naming scheme, and the on-disk data
layout. **Implement the filter as an explicit allow-list of the four keys, not a deny-list of the
three**, so a future manifest key is excluded by default rather than leaked by omission. This is
recorded as a security requirement in section 12.

**Frontend consumption:** `ScenarioConfigProvider.tsx` fetches the endpoint once at boot and
exposes it through React context. `main.tsx` wraps the app in it; the app renders a skeleton until
it resolves.

**Companion route (revision 6).** The same router also serves `GET /api/scenario/assets/{path}`,
resolving `{path}` against `SCENARIO_PATH`. Config and assets are the only two scenario surfaces the
browser ever sees, and both come from the API rather than from the bundle. Design and mandatory
security controls: **section 6B**.

**The decisive property.** Because no scenario value is compiled into the bundle, **the frontend
container image is completely scenario-free - one image serves all three industries**, switched
purely by which scenario the API was pointed at. This is what makes the pattern honestly
domain-independent rather than domain-independent-by-convention.

### 6A.3 One generic catalog app replaces three (verified)

**Verification performed against the contribution, all three files read in full:**

* `BankingApp.tsx` (41 lines) and `HealthcareApp.tsx` (41 lines) are **structurally identical**:
  same `useQuery` with `staleTime: 5 * 60 * 1000`, same `Array.from({ length: 3 })` skeleton loop
  with the identical `py-14 border-b border-border` wrapper, same one-line
  `<p className="text-destructive">` error state, same `.map` to a card keyed on the item id, same
  outer `h-full overflow-auto bg-background` / `max-w-6xl mx-auto px-6 lg:px-10 py-10 lg:py-14`
  layout. They differ **only** in the query key, the endpoint path, the card component, the intro
  prose, and the error string - all five of which are configuration.
* `EcommerceApp.tsx` (66 lines) differs by **more than the cart, but nothing that resists config**:
  1. the cart wiring that section 7.1 already removes (lines 3, 18-26, 44-46, and the
     `onAddToCart` props at 50 and 68);
  2. a **no-op** client-side filter/sort - `searchQuery`, `selectedCategory`, and `sortBy` are
     `useState` values whose setters are destructured away (`const [searchQuery] = useState('')`)
     and therefore never change, so `filterProducts`/`sortProducts` are called with constants and
     produce the unfiltered list. Dropping them changes nothing observable;
  3. a **grid** layout (`MainContent` + `ProductGrid`) instead of a stacked card list;
  4. a **richer error state** - a heading, the error message, and a retry button.

**Verdict: the reviewer's convergence claim is confirmed, with one correction.** After the cart
removal the three do converge, but not to a byte-identical shape - the residual difference is
layout, which is exactly what `catalog.cardVariant` (section 6A.6) expresses. They converge to
**one generic app parameterized by `cardVariant`**, and the ecommerce retry panel is kept as the
single error state for all three because it is strictly better.

**Staged in the pattern:**

* `TP/src/app/src/CatalogApp.tsx` - one `useQuery` against `catalog.routePrefix`, one skeleton
  state, one error state (the retry panel), and a `cardVariant` switch selecting `grid` or `list`.
* `TP/src/app/src/components/CatalogItemCard.tsx` - a schema-driven card that renders fields named
  by `catalog.cardSchema` and presentation values resolved by `resolveItemPresentation`
  (section 6A.5).

**Removed from the pattern:** the entire `src/scenarios/{banking,ecommerce,healthcare}/` tree. Rows
42, 43 and 44 become **Out of scope (superseded)**; rows 42a and 44a carry the surviving mechanism
and data split.

### 6A.4 `hostConfig.ts` becomes generic config access

**What it hardcodes today** (53 lines, read in full):

* `export type HostScenario = 'ecommerce' | 'healthcare' | 'banking'` - a compile-time enum of
  three industries in pattern code.
* Three default titles: `Contoso`, `Contoso Health`, `Contoso Banking`, plus a `genericTitles`
  deny-set containing `Contoso`, `Contoso Bank`, `Contoso Banking`, `E-commerce Store`,
  `Ecommerce Store`.
* Two compliance-banner sentences, selected by an `if/if` on the scenario name:
  * healthcare: "Not for medical emergencies. This assistant does not provide medical diagnosis or treatment advice."
  * banking: "Not financial advice. Do not share full account numbers, PINs, or passwords in chat."
* `resolveHostScenario()` defaulting to `'ecommerce'`.

**Where it goes.** Every one of those values **already exists in each scenario's
`manifest.json`** - verified in `scenarios/banking/manifest.json`, which supplies
`host.appTitle` = `"Contoso Banking"`, `host.iconPath` = `"/contoso-icon.png"`,
`host.widgetTheme` = `"light"`, and `host.complianceBanner` = the exact banking sentence above. The
pattern is duplicating scenario data it is already being handed.

**What the file becomes.** A typed accessor over the fetched config (section 6A.2) with **no domain
literals and no scenario enum**: `useHostConfig()` returning `{ appTitle, iconPath, widgetTheme,
complianceBanner }`, plus a `HostConfig` type generated from the published JSON schema
(section 6A.7). `resolveHostScenario()`, the defaults map, and the `genericTitles` set are deleted
outright - there is no scenario identity in the frontend at all any more.

**`ScenarioApp.tsx` follows.** Its compile-time three-way ternary
(`scenario === 'healthcare' ? <HealthcareApp/> : scenario === 'banking' ? <BankingApp/> :
<EcommerceApp/>`) and its three static imports are replaced by a **single generic render path**:
`<CatalogApp />`, with the banner rendered from `host.complianceBanner` (falsy means no banner, the
same semantics as today's empty-string return) and `document.title` set from `host.appTitle`.

### 6A.5 `*Meta.ts` split - mechanism stays, data moves

`bankingProductMeta.ts` (84 lines) and `healthcareServiceMeta.ts` (81 lines) were read in full and
are the **same file with different nouns**.

**Mechanism (stays in the pattern, one copy).** Both contain an identical four-step resolver:
exact `id` lookup, then uppercased `id`, then a title-to-id alias map, then a fallback that derives
`highlights` from `tags` or `description` or `category` and substitutes a default image. That is a
generic presentation-lookup algorithm with no domain content. It becomes the single
`TP/src/app/src/lib/resolveItemPresentation.ts`:

```ts
resolveItemPresentation(item: CatalogItem, presentationMap: PresentationMap): ItemPresentation
```

**Amended by revision 6 (section 6B.2) - the `image` key does not survive into `presentation`.**
Only `highlights` and the `titleAliases` map do; the image comes from the catalog item's own `image`
value, which is now the single source of truth. The per-domain default image
(`/banking/checking.svg`, `/healthcare/primary-care.svg`) becomes a single
`presentation.defaultImage` config value. The per-domain path prefix guard
(`product.image?.startsWith('/banking/')`) is **deleted outright** rather than becoming
`presentation.assetPrefix`: with scenario-relative paths and a per-scenario asset route there is
nothing left to guard against, and the tolerant-path rule of section 6B.2 replaces it.

**Data (moves to the scenario).** The eight-entry `BANKING_PRODUCT_META` /
`HEALTHCARE_SERVICE_META` records of `image` + `highlights`, and the `*_BY_TITLE` alias maps, become
the `presentation` block of each scenario's `manifest.json`, delivered in the section 6A.2 payload:

```json
"presentation": {
  "defaultImage": "assets/checking.svg",
  "items": { "BK-0001": { "highlights": ["..."] } },
  "titleAliases": { "Everyday Checking": "BK-0001" }
}
```

**Assets follow the data.** The referenced SVGs move into the scenario's flat `assets/` folder -
rows 42b and 44b - and are served by `GET /api/scenario/assets/{path}`. **The revision-4 sentence
"the Builder copies them into the app's public root at compose time" is withdrawn** (section 6B):
that step would have patched the pattern's build output at compose time, contradicting the
section 6A.1 copy-plus-environment contract, and would have placed a domain asset inside the
container image section 6A.2 requires to be scenario-free.

**Retail has no `*Meta.ts`.** Its `presentation` block is authored fresh, and after revision 6 it
carries only `highlights` per item plus a `defaultImage`. The image itself comes straight from the
rewritten catalog CSV column (row 63), not from `presentation`.

### 6A.6 `cardVariant` enum, not a plugin registry

**Decided: card layout variation is a config enum over layouts the PATTERN owns** - `grid`, `list`,
`detail`. A scenario selects one; it never supplies one.

**Rejected alternative, and why.** A scenario-supplied React component (the "plugin registry" shape
revision 3's row 39 sketched) was considered and is **rejected** on two grounds:

1. It puts reusable UI **mechanism** in the Industry Scenario layer, which the skill's boundary
   rule forbids outright: *"never place the reusable application mechanism in an Industry
   Scenario."* A card renderer is mechanism; only the values it renders are domain content.
2. It re-couples the frontend bundle to a specific scenario, because the scenario's `.tsx` must be
   present at `npm run build` time. That destroys the section 6A.2 property that the frontend
   container image is scenario-free and one image serves all three industries - the single largest
   architectural gain of this decision.

**Standing rule, recorded for every future contribution to this pattern.** When a scenario needs
something the pattern cannot express, **add the capability to the pattern as another
config-selected option** - a new `cardVariant` value, a new `cardSchema` field type, a new
`presentation` key. **Never let a scenario carry code.** If a proposed scenario change requires a
`.tsx`, `.ts`, or `.py` file in the scenario folder, it is a pattern gap, and the correct fix is a
pattern Delta.

This also retires the revision-3 risk *"Scenario UI modules cross a layer boundary at build time"* -
under this decision, no scenario UI module exists to cross it (section 12).

### 6A.7 Config schema and compose-time validation

* The pattern **publishes a JSON schema** for its config surface - `host`, `welcome`, `catalog`,
  `presentation` - at `TP/config/scenario-config.schema.json`, and **names it in
  `scenarioExtensionPoints`** (section 11.2) so a scenario author can find the contract without
  reading pattern source.
* Each scenario's `manifest.json` is **validated against that schema at compose time**, in the
  extended `preflight_scenario` step (row 60). A missing required key **fails loudly at compose**
  rather than rendering a blank panel at runtime - which is the actual failure mode the current
  code has, since `hostAppTitle()` silently falls back to `'Contoso'`.
**Revision 7 - the sample config is dropped; the schema and its validation are not.**

Revision 4 also planned **`TP/config/scenario-config.sample.json`**, a complete default config so
the pattern could run standalone for a smoke test with no scenario attached. **The reviewer has
removed it.** Only the sample *instance* goes. Stated as a table so this section cannot be misread
as dropping validation as well:

| Artifact | Revision 7 status |
|---|---|
| `TP/config/scenario-config.schema.json` - the published JSON schema for `host`, `welcome`, `catalog`, `presentation` | **Kept.** Still authored, still shipped in the pattern's `config/` folder. |
| The schema named in `scenarioExtensionPoints` as `configSchema` | **Kept**, unchanged (section 11.2). |
| Compose-time validation of every scenario `manifest.json` against that schema, in the extended `preflight_scenario` step (row 60), including the section 6B.3 asset-path resolution check | **Kept.** A missing or malformed key still fails loudly at compose rather than rendering a blank panel at runtime. |
| `TP/config/scenario-config.sample.json` - the sample *instance* | **Dropped.** This decision removes this row and nothing else. |

**Precedent basis, verified in this repository before the decision was written down.** The live
`technical-patterns/chat-with-data/` pattern sets the factory convention, and it ships no standalone
fixture of any kind:

* Its top level is exactly `infra/`, `scripts/`, `src/`, `README.md` - **no `config/` folder, no
  `samples/` folder, no `evals/` folder**, and no sample dataset anywhere in the tree.
* `scripts/shared/scenarios.py` resolves `industry-scenarios/scenarios.json` (falling back to
  `ROOT_DIR / "scenarios.json"`), and when that file is absent `_load_scenarios()` prints a
  `scenarios.json not found at: …` warning and **returns an empty registry** rather than
  substituting built-in defaults. The live pattern therefore **assumes a scenario is always
  composed**, and simply degrades with a warning when one is not.
* Two folders in that tree look like counter-examples and are not.
  `src/app/public/config/config.json` is **UI layout configuration** - column-width ratios plus a
  chart list carrying call-center domain labels such as `Total Calls` and `Average Handling Time` -
  nested inside the app's public root, not a pattern-level `config/` folder and not a scenario
  fixture. `src/app/src/configs/StaticData.tsx` is **frontend mock data** (hardcoded Cosmos
  conversation records complete with `_rid` and `_etag` fields) consumed by the UI, not a smoke-test
  fixture. Neither is a standalone sample config, so neither weakens the precedent.

Introducing one here would have made `chat-with-data-voice` the only pattern in the factory with
such a folder - a new convention established unilaterally by a single contribution. That is the
reviewer's rationale, and the plan stage is the right place to apply it.

**Consequence, recorded plainly rather than buried.** With `tests/e2e-test/` out of scope (rows
74-76) **and** no sample fixture, the technical pattern ships **no executable validation
whatsoever**. The schema plus its compose-time validation is the only executable check that
survives, and it runs **only when a scenario is composed** - it cannot be exercised against the
pattern alone. It follows that `chat-with-data-voice` **cannot be deployed meaningfully without a
composed scenario**: the catalog renders empty, because `GET {prefix}/` has no Cosmos content to
return, and **no agents exist at all**, because agent creation reads `agents/*.txt` from the
scenario folder under `SCENARIO_PATH`. This is carried as a prominent risk in section 12, and it is
why Workflow execution fit is re-scored 4 to 3 in section 2. The starter `evals/` recommendation in
section 12 is now the only validation route left, not a nice-to-have.

**The deferred idea is logged as an open question, not a deliverable** - a minimal sample scenario,
raised as a *factory-wide* convention so `chat-with-data` adopts it too. See section 12.

### 6A.8 Net effect on the pattern

| Measure | Value |
|---|---|
| Domain-specific React/TS **deleted** from the pattern | **431 lines** - the whole `src/scenarios/{banking,ecommerce,healthcare}/` tree (41 + 59 + 84 + 66 + 41 + 59 + 81), verified by line count |
| Domain literals removed from `hostConfig.ts` | ~30 of its 53 lines (the `HostScenario` union, three default titles, five-entry `genericTitles` set, two compliance sentences, the `'ecommerce'` default) |
| **Total domain code leaving the pattern** | **~461 lines** |
| Of which re-emerges as scenario **data** (not code) | ~130 lines of `*Meta.ts` records and alias maps, restated as JSON `presentation` blocks in two manifests |
| Generic pattern code to author (estimate, not verified) | ~350 lines across `CatalogApp.tsx`, `CatalogItemCard.tsx`, `resolveItemPresentation.ts`, `ScenarioConfigProvider.tsx`, `scenario_config_api.py`, and the JSON schema. **Revision 7 removed the sample config from this set** (section 6A.7); the schema and its compose-time validation remain |
| Scenario enum references remaining in pattern code | **0** |

## 6B. Scenario image assets are localized and API-served (reviewer decision - DECIDED)

This records an **approved design**, not an open question. It answers the three inconsistent image
conventions the contribution ships, one of which produces dead data and one of which points at a
third-party repository. Every factual claim below was verified against
`C:\GSAs\OG\customer-chatbot-solution-accelerator` before it was written, and the verification
method is stated inline. Section 12 carries the residual security requirement.

### 6B.1 The problem: three conventions, two sources of truth, one dead column

**Convention 1 - retail uses absolute third-party URLs. Verified.** All **16** data rows of
`scenarios/ecommerce/data/catalog.csv` carry an `image` value of the form
`https://raw.githubusercontent.com/microsoft/customer-chatbot-solution-accelerator/refs/heads/main/infra/scripts/post-provision/data/Color%20Images/<name>.jpg`.
Confirmed by parsing the file: 16 rows, **16 of 16** matching that prefix, **0** rows in any other
form, and 16 distinct filenames. Columns are
`productId,title,category,price,description,punchLine,image`.

**Convention 2 - banking and healthcare use root-relative paths. Verified.**
`scenarios/banking/data/catalog.csv` (8 rows) carries `/banking/<name>.svg` for `BK-0001`..`BK-0008`,
and `scenarios/healthcare/data/catalog.csv` (8 rows) carries `/healthcare/<name>.svg` for
`HC-0001`..`HC-0008`. Both resolve out of the **pattern frontend's** public root: the files sit at
`scenario-app/frontend/public/banking/` (8 SVGs) and `scenario-app/frontend/public/healthcare/`
(8 SVGs), 16 SVGs and 8,389 B in total. Each CSV's 8 values map one-for-one onto the 8 filenames in
its folder.

**Convention 3 - the dead column. Verified, including the healthcare case the reviewer asked about.**
`BankingProductCard.tsx` renders `src={meta.image}` at line 53, where `meta` comes from
`resolveBankingProductMeta()` over the hardcoded `bankingProductMeta.ts` map.
**`HealthcareServiceCard.tsx` behaves identically** - the same `src={meta.image}` at the same
line 53, over the structurally identical `healthcareServiceMeta.ts`. Only retail's
`FigmaProductCard.tsx` renders `src={product.image}` (line 15) off the catalog item.

**Precision on exactly how dead it is.** `resolveBankingProductMeta()` tries the item `id`, then the
uppercased `id`, then a title alias, and only in its *fallback* branch (line 83) does it consult
`product.image?.startsWith('/banking/')`. Every one of the 8 shipped banking rows hits the `id`
lookup and returns the hardcoded map entry, and healthcare is the same shape. So **the CSV `image`
column is dead for 8 of 8 banking rows and 8 of 8 healthcare rows as shipped**; it is live only for
a catalog item absent from the hardcoded map, which no shipped scenario has. That is two sources of
truth for one value, with the CSV losing every time.

**Why this matters to the split, not just to the source.** Left alone, all three conventions break
once the layers separate. Retail's absolute URLs would make a factory industry scenario depend on a
third-party repository's moving `main` branch (section 6B.6). Banking's and healthcare's
root-relative paths resolve out of the **pattern's** container - the one section 6A.2 requires to be
scenario-free - so they would either 404 or force the Builder to patch the pattern's public root at
compose time, which section 6A.1 forbids.

### 6B.2 The decided target design

**1. Single source of truth: the CSV `image` column wins.** The `image` key is **removed** from the
`presentation` map defined in section 6A.5. `highlights` and `titleAliases` stay there - they have
no CSV column and are genuine presentation data. The generic `CatalogItemCard` reads the catalog
item's own `image` uniformly for all three scenarios, so banking and healthcare stop carrying two
sources of truth and retail's existing behavior becomes the universal one. **Section 6A.5 has been
amended in place** so the two sections do not contradict each other; `presentation.assetPrefix` is
deleted outright rather than carried forward, because a per-scenario asset route leaves nothing to
prefix-guard.

**2. Scenario-relative paths.** All three CSVs are rewritten to scenario-relative values -
`assets/checking.svg`, `assets/primary-care.svg`, `assets/SnowVeil.jpg`. Assets live in one flat
`assets/` folder per scenario. No leading slash, no repeated domain folder level, no host.

**3. Asset serving.** The merged API gains **`GET /api/scenario/assets/{path}`**, implemented
alongside the `GET /api/scenario/config` endpoint of section 6A.2 in
`TP/src/api/routers/scenario_config_api.py` and resolving `{path}` against `SCENARIO_PATH`
(section 6A.1). This is the point of the decision: the frontend container stays **scenario-free**
and one image serves all three industries, exactly as the Option A decision requires. No image file
is copied into the frontend's public root, ever.

**4. Tolerant card rule.** `CatalogItemCard` passes an `image` value beginning with `http://` or
`https://` through to `<img src>` **unchanged**, and resolves every other value against the asset
route. Recorded now so a future scenario can point at a CDN or a blob endpoint **without a pattern
change** - which is also what makes the section 6B.5 production path a configuration migration
rather than a code migration.

**5. Path string, not bytes - stated explicitly to prevent a build-time misreading.** Cosmos DB
stores the catalog row, and that row's `image` field holds **only the path string**
(e.g. `assets/checking.svg`). **Image bytes are never written to Cosmos, never base64-encoded into a
document, and never returned by the catalog API.** `TP/scripts/data/03_write_products_to_cosmos.py`
copies the CSV column verbatim. The bytes live on disk under `SCENARIO_PATH` and are served only by
the asset route.

### 6B.3 Asset moves to stage

Every move lands in one flat `assets/` folder per scenario. **Note for the classifier:** no live
factory scenario currently has an `assets/` folder or ships an image of any kind - verified, zero
`.jpg`/`.png`/`.svg` files anywhere under `industry-scenarios/` - so this **establishes** the
convention rather than following one, and all three scenario `README.md` files must document it.

| Scenario | Staged into `assets/` | Source | Rows |
|---|---|---|---|
| `banking-customer-support` | 8 SVGs + `contoso-icon.png` + `contoso-ai-icon.png` = **10 files** | `scenario-app/frontend/public/banking/`; both apps' `public/` | 42b, 30, 41 |
| `healthcare-patient-support` | 8 SVGs + `contoso-icon.png` + `contoso-ai-icon.png` = **10 files** | `scenario-app/frontend/public/healthcare/`; both apps' `public/` | 44b, 30, 41 |
| `retail-customer-support` | 16 JPGs + `contoso-icon.png` + `contoso-ai-icon.png` = **18 files** | `infra/scripts/post-provision/data/Color Images/`; both apps' `public/` | 63, 30, 41 |
| **Total** | **38 staged files** from **20 distinct source files** - the 2 PNGs are staged into all 3 scenarios | - | - |

**Reconciliation with rows 42b and 44b - extended, not duplicated.** Both rows already existed from
revision 4 and already carried the 16 SVGs to their scenarios. Revision 6 **rewrites those two rows
in place** and creates no new row for the SVGs. Two things change inside them: the destination
flattens from `assets/banking/` and `assets/healthcare/` to plain `assets/` (the domain folder level
is redundant inside a scenario already named for that domain, and it would leak into every rewritten
CSV value), and the delivery mechanism changes from *"the Builder copies them into the app's public
root at compose time"* to the asset route. That copy step is **withdrawn**, in those two rows and in
section 6A.5.

**Reconciliation with the `Color Images` out-of-scope finding - a narrower correction than the
request assumed.** The request asked whether localizing the 16 JPGs partially reverses their
out-of-scope status. **It does not, because they were never out of scope.** Re-verified: row **62**
is the byte-identical-duplicate row, and its path is
`infra/scripts/post-provision/data/{policies/*.txt,products/products.csv}` - the MD5 finding covers
the `policies/` and `products/` subfolders only. `Color Images/` has always been its own row **63**,
outcome **New**, staged into the retail scenario, annotated *"only copy in the contribution."* That
annotation is now independently re-verified: `scenarios/ecommerce/data/` contains exactly
`catalog.csv` and `policies/{AboutContosoPaints,ReturnPolicy,Warranty}.txt` and **no image file of
any kind**, so the 16 JPGs (167,556 B) are unique to `Color Images/` and were never covered by the
duplicate finding. **The precise adjustment is therefore to row 63's destination only** -
`unstructured_data/images/` becomes `assets/` - plus a precision note appended to row 62 recording
the exact scope of its finding. **No out-of-scope row flips, and the New / Out-of-scope split in
section 15 is unchanged.**

**Brand icons - usage confirmed before moving.** `contoso-icon.png` is declared as
`host.iconPath` = `/contoso-icon.png` in **all three** `manifest.json` files, and is also hardcoded
as `src="/contoso-icon.png"` in `AppHeader.tsx` in **both** apps. `contoso-ai-icon.png` is the
assistant avatar, hardcoded as `src="/contoso-ai-icon.png"` in `EnhancedChatPanel.tsx` in both apps
(lines 817 and 848), and is declared in **no** manifest. Both are byte-identical across the two apps
(MD5 `E0EBD9A4...`, 749 B; MD5 `A690ECD2...`, 1290 B), so exactly one copy of each is staged per
scenario. Manifest updates: `host.iconPath` becomes `assets/contoso-icon.png` in all three, and a
**new `host.assistantIconPath`** key carrying `assets/contoso-ai-icon.png` is added to all three so
the second icon stops being a pattern literal. `AppHeader.tsx` and `EnhancedChatPanel.tsx` read both
from the config context (section 6A.4) and resolve them through the asset route. This also corrects
two revision-4 placements: row 30 sent both icons to **retail only**, even though all three
manifests reference one of them, and row 38 sent `scenario-app`'s `contoso-ai-icon.png` into the
**pattern**, which would have left Contoso branding inside the image section 6A.2 calls scenario-free.

**The CSV rewrite is a required decomposition action, not an optional cleanup.** All three
`data/catalog.csv` files must have their `image` column rewritten during staging: 16 retail rows
from absolute `raw.githubusercontent.com` URLs (dropping the `%20` escape along with the space in
the folder name), 8 banking rows from `/banking/*.svg`, and 8 healthcare rows from
`/healthcare/*.svg`, all to `assets/<filename>`. Skipping it leaves the staged scenarios with 16
dead external links and 16 paths resolving out of a container that no longer holds them. The
`preflight_scenario` schema validation (section 6A.7, row 60) is extended to assert that every
catalog `image` value either matches `^https?://` or resolves to a file that exists under the
scenario's `assets/`, so an unrewritten CSV fails loudly at compose time instead of rendering broken
images in a demo.

### 6B.4 Security requirements for the asset route (mandatory)

`GET /api/scenario/assets/{path}` is a **file-serving endpoint whose path segment is
user-supplied**, sitting on top of a folder that also holds the manifest, the agent instruction
text, and the policy corpus. That is the classic path-traversal shape (OWASP A01, Broken Access
Control). All seven controls below are required; they are not a menu.

1. **Reject `..` and every URL-encoded traversal variant** before any filesystem call - `..`,
   `%2e%2e`, `%2E%2E`, `..%2f`, `%2e%2e%5c`, double-encoded `%252e%252e`, and backslash separators.
   Decode exactly once, then reject; never decode in a loop until stable.
2. **Reject absolute and drive-qualified paths** - `/etc/...`, `C:\...`, UNC `\\host\share`.
3. **Canonicalize, then re-verify containment.** Resolve the candidate to a real absolute path
   (following symlinks) and confirm it is still **under the canonicalized `SCENARIO_PATH`**. A
   `startswith` check on the *unresolved* string is not sufficient.
4. **Reject, never clamp.** On any failure return `404 Not Found`. Do **not** strip the offending
   segments and serve whatever remains, and do not return `403`, which confirms the path shape to an
   attacker. Silent clamping turns a blocked traversal into an unlogged one.
5. **Enforce an image-only extension allow-list** - `.jpg`, `.jpeg`, `.png`, `.svg`, `.webp`,
   `.gif` - matched on the canonicalized path's real extension. Everything else is `404`, so the
   route can never serve `manifest.json`, an agent instruction `.txt`, a policy document, or a
   `.env` that happens to sit under `SCENARIO_PATH`. Set `Content-Type` from the allow-list entry,
   never from the request.
6. **Set `Cache-Control` on every asset response.** `public, max-age=31536000, immutable` is
   appropriate, because a composed solution's scenario folder is immutable for the life of the
   deployment; a shorter `max-age` with `must-revalidate` is acceptable if the reviewer prefers
   invalidation headroom. Assets are public brand content, so `public` is correct. The
   `GET /api/scenario/config` endpoint of section 6A.2 must **not** inherit this header.
7. **Serve `.svg` as an image, not as a document.** SVG can carry script, and 16 of the 20 distinct
   source assets are SVGs, so this is the common case rather than an edge case. Serve with
   `Content-Disposition: inline`, `X-Content-Type-Options: nosniff`, and
   `Content-Security-Policy: default-src 'none'; style-src 'unsafe-inline'; sandbox`, so a hostile
   SVG dropped into a scenario folder cannot execute in the app's origin.

The comparison report must show the handler with the traversal rejection, the canonical containment
check, and the extension allow-list visible. Also recorded in section 12.

### 6B.5 Blob storage plus CDN is the documented production path, not built now

**Documented in `TP/README.md` (and in `TP/docs/`, row 72) as the production-hardening path.
Not implemented in this split.**

**Why it is deferred, concretely.** `infra/bicep/main.bicep` provisions **no storage account** -
verified, zero occurrences of `storage` anywhere in the vanilla template.
`infra/bicep/modules/data/storage-account.bicep` exists but is **unreferenced**, and is already
accounted for inside row 54's 19-module dead-module skip list. Building the blob path would
therefore mean adding a storage account to a staged layer, and **storage is core-layer** in the
factory's boundary - while `agentic-apps` is deliberately scoped by the reviewer to Foundry account
+ Foundry project + AI Search and nothing else (section 3). Adding storage would either widen the
core past its agreed scope or push shared platform infrastructure into the pattern, which the
skill's source-layer-ownership rule forbids outright. Neither is in scope for this pass.

**What a future migration would and would not change.** The CSV convention is **unchanged** by it:
the `image` column still holds a path string, `presentation` still holds no image, and Cosmos still
stores only the string (section 6B.2 item 5). Only the **resolution target** moves - either the
asset route proxies to blob instead of the local filesystem, or the values become absolute CDN URLs,
which the tolerant card rule of section 6B.2 item 4 **already** passes through unchanged. That is
precisely why the tolerant rule is recorded now rather than added later: it makes the migration a
configuration change, not a pattern Delta.

### 6B.6 Rejected alternative: raw GitHub URLs

Considered and **rejected**. Two variants, both fail:

* **Point at the factory repository.** `git remote -v` resolves this repository to
  `https://github.com/mcaps-microsoft/frontier-accelerator-factory.git` - an **internal/private**
  organization repository. `raw.githubusercontent.com` serves private content only with an
  authenticated token in the request, and a browser `<img src>` sends no such token, so every image
  request would 404 for every user. This is not a policy objection; it simply does not render.
* **Point at the upstream public repository.** The contribution's existing retail URLs already do
  this, against `microsoft/customer-chatbot-solution-accelerator` on `refs/heads/main`. It renders
  today, but it would permanently couple factory industry scenarios to a **third-party repository's
  moving `main` branch** - an upstream rename, reorganization, archive, or licence change silently
  breaks a shipped factory scenario, with no version pin and no ownership.

**Supporting evidence that this would set a precedent, not follow one.** Verified across
`industry-scenarios/**`: **zero** CSV/JSON/JSONL values reference `raw.githubusercontent.com` or any
remote image URL. No existing factory scenario depends on a remote image, and this decision keeps it
that way.

## 7. Files proposed to skip

Complete and exhaustive. Nothing is dropped silently. Every row is evidence-backed.

### 7.1 The four scenario-app CRUD routers, including the reviewer-directed `cart.py` skip

All four are registered in `scenario-app/backend/app/main.py` (lines 93-114). Three have no caller
at all. `cart.py` is the exception, and the reviewer asked for a one-level-deeper trace before
applying the skip.

**Cart reachability trace - result: the cart is PARTIALLY reachable. One of the five `api.ts`
call sites is live in the running ecommerce UI; the other four are dead.**

| `api.ts` function | Line | HTTP call | Importers found | Reachable in a rendered component? |
|---|---|---|---|---|
| `addToCart` | 270-276 | `POST /api/cart/add` | **1** - `scenarios/ecommerce/EcommerceApp.tsx:3` | **YES.** `EcommerceApp` wraps it in `addToCartMutation` (lines 18-26), exposes `handleAddToCart` (lines 44-46), and passes it as `onAddToCart` to `MainContent` (line 50) and `ProductGrid` (line 68). `ProductGrid` renders `FigmaProductCard` (line 37), which renders the add-to-cart button. `EcommerceApp` is mounted by `scenarios/ScenarioApp.tsx`. |
| `getCart` | 278-310 | `GET /api/cart/` | **0** | No |
| `updateCartItem` | 312-318 | `PUT /api/cart/update` | **0** | No |
| `removeFromCart` | 320-326 | `DELETE /api/cart/{id}` | **0** | No |
| `checkoutCart` | 328-334 | `POST /api/cart/checkout` | **0** | No |

Component-level findings:

* **`CartDrawer.tsx` is never mounted.** Zero importers anywhere in
  `scenario-app/frontend/src`. It is the only component that would *render* cart contents, so the
  cart is write-only today: an item can be added, but nothing in the UI ever displays it.
* **`ProductCard.tsx` cannot even build.** It imports `useAddToCart` from `../hooks/api`
  (line 4), but `scenario-app/frontend/src/hooks/` contains **only** `use-mobile.ts` - there is no
  `hooks/api` module. `ProductCard` also has zero importers (`ProductGrid` renders
  `FigmaProductCard`, not `ProductCard`). It is unambiguously dead.
* **Two of the four dead functions were already broken.** `api.ts` calls
  `DELETE /api/cart/${productId}` and `POST /api/cart/checkout`, but `cart.py` exposes
  `DELETE /api/cart/remove/{product_id}` (line 174) and `DELETE /api/cart/clear` (line 214) with no
  checkout route at all.
* **The widget path is unaffected.** `chat-app/frontend/src/lib/api.ts` - the copy that survives
  into the pattern (row 24) - contains **zero** cart references.

**Decision applied: skip `cart.py` as directed.** The reviewer's premise ("the cart is unused in
the UI") is correct about everything the user can *see*, since nothing renders a cart. But the add
path is genuinely wired, so the skip is not free - see the prominent risk row in section 12.

**Companion removals required for the skip to be coherent.** Skipping `cart.py` alone leaves a live
button posting to a route that no longer exists. Every item below must be removed in the same pass:

*Backend:*

1. `scenario-app/backend/app/routers/cart.py` - the whole file (5 endpoints: `GET /`, `POST /add`, `PUT /update`, `DELETE /remove/{product_id}`, `DELETE /clear`).
2. `main.py` line 109 - drop `cart` from `from .routers import cart, orders, products`.
3. `main.py` line 111 - drop `cart` from the `from app.routers import cart, orders, products` fallback (the whole try-except pair disappears anyway per section 4.8).
4. `main.py` line 113 - `app.include_router(cart.router)`.
5. `main.py` line 62 - the app `description` string "product browsing, cart management, and order processing".
6. `models.py` - the `Cart`, `CartItem`, and cart request models, once confirmed at staging that `cart.py` is their only consumer.
7. `cosmos_service.py` / `database.py` - the cart container binding and cart CRUD helpers, same confirmation.

*Frontend:*

8. `lib/api.ts` - the `CartItem` interface (line 145) and all five functions: `addToCart` (270-276), `getCart` (278-310), `updateCartItem` (312-318), `removeFromCart` (320-326), `checkoutCart` (328-334).
9. `components/CartDrawer.tsx` - the whole file (unmounted).
10. `components/ProductCard.tsx` - the whole file (broken import, zero importers).
11. `scenarios/ecommerce/EcommerceApp.tsx` - line 3 `addToCart` import (keep `getProducts`); lines 18-26 `addToCartMutation`; lines 44-46 `handleAddToCart`; the `onAddToCart` props at lines 50 and 68; and the then-unused `useMutation` (line 6) and `toast` (line 8) imports. **Revision-4 note:** the whole file is now Out of scope (row 43), so this item is satisfied by not staging it at all - but the trace is retained because it is the evidence that the cart's only live caller disappears with it.
12. The `onAddToCart` prop chain, removed prop-by-prop: `components/Layout/MainContent.tsx` (11, 18, 39), `components/Layout/ChatSidebar.tsx` (19, 31, 72), `components/ProductGrid.tsx` (10, 16, 40), `components/FigmaProductCard.tsx` (6, 9 and its add-to-cart button), `components/ChatProductCard.tsx` (6, 11), `components/EnhancedChatMessageBubble.tsx` (15, 21, 75, 88, 99), `components/EnhancedChatPanel.tsx` (20, 33, 846), `components/ProductRecommendation.tsx` (10, 16, 47, 118).
13. `lib/types.ts` - the `CartItem` interface (line 32) and the `cart: CartItem[]` field of `AppState` (line 67). `AppState` itself has zero importers and is dead regardless.

Items 12 and 13 matter beyond hygiene: `EnhancedChatPanel.tsx`, `EnhancedChatMessageBubble.tsx`,
and `ChatProductCard.tsx` are **pattern** files (rows 24 and 40), so leaving a cart-shaped
`onAddToCart` prop in them would leak retail vocabulary straight into the technical pattern.

**Revision-4 interaction with decision 2c.** The cart removal is what makes the three front ends
converge (section 6A.3): once `EcommerceApp.tsx` loses its cart wiring, the only difference left
from `BankingApp`/`HealthcareApp` is a grid-versus-list layout and a no-op filter/sort. The two
decisions reinforce each other - decision 2c is only clean *because* the cart is already going.
Note that `MainContent.tsx`, `ProductGrid.tsx`, and `FigmaProductCard.tsx` (item 12) are absorbed
into the generic `CatalogApp` / `CatalogItemCard` rather than staged as-is, so their `onAddToCart`
props disappear with the rewrite rather than needing a separate surgical pass.

**The other three routers.**

| File | Registered in `main.py` | Caller found | Verdict |
|---|---|---|---|
| `routers/orders.py` | Yes, lines 109-114 | No. No `/api/orders` string in either frontend or any backend module | Skip. Also delete its import and `include_router` line. |
| `routers/banking_transactions.py` | Yes, lines 102-106 | No. No `/api/banking/transactions` string anywhere outside the router | Skip. Same companion deletions. |
| `routers/healthcare_appointments.py` | Yes, lines 95-99 | No. No `/api/appointments` string anywhere outside the router | Skip. Same companion deletions. |

All three are also domain-shaped (`banking`, `appointments`) and would violate the pattern's
domain-independence rule even if they were used. They are thin Cosmos readers over
`get_orders_by_customer`, so they can be reinstated later as manifest-driven views of a generic
transaction-history endpoint.

### 7.2 Additional dead code found

| File | Reason | Evidence | Risk if wrong |
|---|---|---|---|
| `chat-app/backend/app/agent_instructions.py` | Dead and domain-specific | Zero `import agent_instructions` or `from .agent_instructions` across both backends. Superseded by `scenarios/<id>/agents/*.txt`, which `01_create_agents.py` reads through `scenario_loader.load_agent_instructions` | Low. Prompt text is preserved in the scenario packs. |
| `scenario-app/backend/app/agent_instructions.py` | Same as above | Same search, same result | Low |
| `chat-app/backend/app/foundry_client.py` | Dead | Zero importers across both backends; agent calls go through `utils/foundry_agent_utils.py` | Low |
| `scenario-app/backend/app/foundry_client.py` | Same as above | Same search, same result | Low |
| `chat-app/backend/app/util/jsonsafe.py` and `util/__init__.py` | Dead | Zero importers. The live helpers are in the sibling `utils/` package | Low. The confusing `util/` versus `utils/` split disappears with the skip. |
| `scenario-app/backend/app/util/jsonsafe.py` and `util/__init__.py` | Same as above | Same search, same result | Low |
| `products.py` write surface: `POST /`, `PUT /{product_id}`, `DELETE /{product_id}` | Unused admin CRUD, surfaced by the section 6 router analysis | No frontend, script, or remaining test calls them; catalog content is loaded by `TP/scripts/data/03_write_products_to_cosmos.py` at post-provision | Low. Reinstatable from git history if an admin surface is ever needed. |
| `chat-app/frontend/public/config.js` and `scenario-app/frontend/public/config.js` (row 28a) | Dead **and** stale | `window.APP_CONFIG` is assigned in these two files and read nowhere - repo-wide search over `*.ts`, `*.tsx`, `*.js`, `*.html`, `*.sh`, `*.conf`, `Dockerfile` returns only the two assignment sites. Neither `index.html` references `/config.js`; both load `/runtime-config.js`, generated at container start by `startup.sh`. `hostConfig.ts` reads `window.__RUNTIME_CONFIG__` | None functionally. **Security-relevant**: both hardcode a live deployment's backend hostname and OAuth redirect URI. See section 12. |
| `chat-app/frontend/src/components/{ChatPanel,ProductFilters,ProductRecommendation,LoginForm}.tsx`, `src/components/Layout/{AppShell,BottomNavigation}.tsx`, `src/lib/textCleaners.ts`, `src/vite-end.d.ts` | Unreferenced in the chat-app tree | Import-graph scan of every `.ts`/`.tsx` under `chat-app/frontend/src` found no importing module | Low |
| `scenario-app/frontend/src/components/{ChatPanel,ProductCard,ProductFilters,LoginForm,CartDrawer}.tsx`, `src/components/Layout/{AppShell,BottomNavigation}.tsx`, `src/lib/textCleaners.ts`, `src/ErrorFallback.tsx`, `src/vite-end.d.ts` | Unreferenced in the scenario-app tree | Same scan over `scenario-app/frontend/src`. `CartDrawer` and `ProductCard` are re-confirmed in section 7.1 | Medium for `ErrorFallback.tsx`: it is imported by `main.tsx` under a different casing path and by the widget, so keep the single merged copy from row 26 and skip only the duplicate. |
| `scenario-app/frontend/src/lib/data.ts` (`filterProducts`, `sortProducts`) | Live import, no-op behavior | Its only caller is `EcommerceApp.tsx`, which passes constant filter/sort values whose setters are destructured away and never called. With row 43 out of scope it has zero callers | Low. If client-side filtering is ever wanted, it belongs in `CatalogApp` behind a `catalog.enableClientFilter` config key, not restored as-is. |
| `chat-app/frontend/src/components/ui/{calendar,form,resizable}.tsx` and the same three under `scenario-app` | Unreferenced shadcn primitives | Same scan. Skipping them also drops their `react-day-picker`, `react-hook-form`, and `react-resizable-panels` dependencies | Low |
| `infra/bicep/modules/` unreferenced library (row 54, 19 modules) | Dead IaC | `infra/bicep/main.bicep` invokes only 12 modules; the only nested invocations are `ai-search.bicep` to `ai-search-identity.bicep` and `role-assignments.bicep` to `cross-scope-role-assignment.bicep` (both callers now retained). Everything else is unreachable | Low. A generic copy-paste library, not solution content. |
| `infra/scripts/post-provision/data/{policies,products}` | Byte-identical duplicate | MD5 match against `scenarios/ecommerce/data/` on all four files, verified in row 62 | None. The surviving copy is identical. |
| `infra/scripts/post-provision/data_scripts/azure_credential_utils.py` | Duplicate of `infra/scripts/utilities/azure_credential_utils.py` | Same helper, two copies | Low. Keep one under `TP/scripts/shared/`. |

### 7.3 Deliberate scope reductions (not dead code, dropped by directive)

| File | Reason | Risk if wrong |
|---|---|---|
| `tests/e2e-test/**` (rows 74-76) | **Reviewer decision 6.** The whole Playwright subtree is out of scope | **Medium-High after revision 7.** It was the only automated validation the contribution shipped. Revision 4's offset - the standalone sample config - is now dropped (section 6A.7), so the only executable check left is the compose-time schema validation, which runs **only against a composed scenario** and checks configuration shape, not behavior. The pattern is therefore left with **no executable validation whatsoever**. Reflected in the fit score (Workflow execution fit re-scored 4 to 3) and carried as a **prominent** risk in section 12. |
| `routers/cart.py` and its companion removals (section 7.1) | **Reviewer decision 7.** The cart has no rendered surface | **Medium.** One reachable add-to-cart path is removed with it. See the prominent risk row in section 12. |
| `scenarios/{banking,ecommerce,healthcare}/*.tsx` (rows 42, 43, 44) | **Reviewer decision 2c/2f (revision 4, preserved).** Superseded by the pattern's generic `CatalogApp` + `CatalogItemCard` + `cardVariant`. Not staged into the pattern (domain code) and not into the scenario (a scenario carries no code) | **Low-Medium.** Nothing user-visible is lost - every difference is reproduced by `catalog.copy`, `catalog.cardSchema`, `catalog.cardVariant`, and `presentation`. The risk is that the generic app must actually reproduce three layouts correctly on the first pass; and **revision 7 removes the mitigation previously named here** - the standalone sample config is dropped (section 6A.7), so the generic app cannot be exercised outside a composed solution. Carried as a risk in section 12. |
| `infra/bicep/modules/ai/existing-project-setup.bicep` (row 50a) plus its **17 companion items** and the orphaned `cross-scope-role-assignment.bicep` (row 52a) | **Reviewer decision 5a (revision 5), reversing revision 4 decision 1 and restoring revision 3.** The bring-your-own Foundry project branch is excluded **to reduce complexity**; the core provisions Foundry greenfield only. Full trace in section 7.4 | **High if applied incompletely, low if applied fully.** Removing the module without the 17 companions leaves a dangling `module` reference and a template that will not build. Carried as a dangling-reference risk in section 12. The capability loss (compose onto a customer-owned Foundry project) is real and recorded as a documented limitation in sections 7.4 and 8. |
| The `existingLogAnalyticsWorkspaceId` branch in the pattern infra plus its **8 companion items** (section 7.5) | **Reviewer decision 5b (revision 5), new.** The attach-to-an-existing-Log-Analytics-workspace branch is excluded **to reduce complexity**. Observability is pattern-owned (row 51), so the branch lives in the pattern's infra | **Medium if applied incompletely, low if applied fully.** **This removes the BYO *branch*, not the workspace** - `log-analytics.bicep` and `app-insights.bicep` are both still staged and still deployed greenfield (row 51). Removing the branch without collapsing the `logAnalyticsWorkspaceResourceId` selector ternary leaves an unresolved symbol. The capability loss (attach to a customer's central workspace) is recorded as a documented limitation in sections 7.5 and 9. |
| `chat-app/frontend/{App.tsx,main.tsx,index.html,nginx.conf,Dockerfile,startup.sh,runtime.config.json,public/runtime-config.js}` | The standalone chat app stops being deployable; only the scenario app deploys. Widget functionality is fully preserved through rows 22-25 | Medium. Anyone wanting a standalone chat surface loses it. Mitigation: the widget can be mounted on a blank host page, so the capability is not lost, only the second deployable. |
| `public/config.js` in both frontends (row 28a) | **Reviewer decision 2i (revision 4, preserved).** Zero readers, verified; stale live endpoints | **None functionally.** Verified no reader exists. Security-positive: it removes two files carrying a live deployment hostname and OAuth redirect URI from anything the promoter could commit. |
| `chat-app/frontend/src/components/*` duplicates and `scenario-app` duplicates | Deduplication into a single merged app. Not deletion of capability | Low. Diff each pair during staging rather than assuming byte equality. |
| `infra/avm/**`, `infra/main.bicep` selector, `infra/*/main.json` | Factory rules: vanilla IaC only, no compiled output | Low |
| Repo-root scaffolding rows 1-9, 21, 31, 37, 46, 64, 65, 66, 71, 73 | Skill rule "Decompose, don't clone" | Low |

### 7.4 `existing-project-setup.bicep` - SKIPPED, greenfield Foundry only

> **Revision-5 reversal.** Revision 4 restored this module and kept all 17 companion items.
> **The reviewer has reversed that decision**, restoring the revision-3 position: the module is an
> explicit **Out of scope** row (row 50a), all 17 companion items are **removed**,
> `cross-scope-role-assignment.bicep` is orphaned and out of scope again (row 52a), and
> `stable-cores/agentic-apps` provisions the Foundry account and project **greenfield only**.
> Reason: **complexity reduction.** The retention record written in revision 4 is deleted; what
> follows is the removal trace, with every line reference re-verified against the contribution at
> revision-5 time.

**Confirmed path:** `infra/bicep/modules/ai/existing-project-setup.bicep`. A second copy exists at
`infra/avm/modules/ai/existing-project-setup.bicep`, out of scope under row 48 (hard no-AVM rule).
Neither copy is staged.

**What it is.** The module provisions nothing. It is a pair of `existing` resource references
(`Microsoft.CognitiveServices/accounts` and `.../accounts/projects`) that re-exports the same output
surface as `ai-foundry-project.bicep` (`resourceId`, `name`, `endpoint`,
`cognitiveServicesEndpoint`, `azureOpenAiCuEndpoint`, `principalId`, `projectResourceId`,
`projectName`, `projectEndpoint`, `projectIdentityPrincipalId`). It is the **bring-your-own** half
of a two-branch switch selected by
`var useExistingAIProject = !empty(existingFoundryProjectResourceId)` at `infra/bicep/main.bicep`
line 175, and invoked at line 273:

```bicep
module existing_project_setup './modules/ai/existing-project-setup.bicep' = if (useExistingAIProject) {
  name: take('module.existing-project-setup.${solutionName}', 64)
  scope: resourceGroup(aiFoundrySubscriptionId, aiFoundryResourceGroupName)
  params: { name: aiFoundryResourceName, projectName: aiProjectResourceName }
}
```

**Skipping it is only safe with these 17 companion removals.** Every line reference below was
re-read in the contribution during revision 5 and still holds exactly as stated. A partial removal
leaves an unresolvable `module` reference and a template that will not build - see the
dangling-reference risk in section 12.

*Staged Stable Core `SC/infra/bicep/main.bicep` (extracted from `infra/bicep/main.bicep`):*

1. Line 145 - `param existingFoundryProjectResourceId string = ''`. **Remove.** It is not a core
   parameter any more; the core parameter surface in section 8 does not carry it.
2. Line 175 - `var useExistingAIProject = !empty(existingFoundryProjectResourceId)`. **Remove.**
3. Line 177 - `var aiFoundryResourceName = useExistingAIProject ? split(...)[8] : 'aif-${solutionSuffix}'`.
   **Collapse** to `var aiFoundryResourceName = 'aif-${solutionSuffix}'`.
4. Line 178 - `var aiProjectResourceName = useExistingAIProject ? split(...)[10] : 'proj-${solutionSuffix}'`.
   **Collapse** to `var aiProjectResourceName = 'proj-${solutionSuffix}'`.
5. Line 179 - `var aiFoundrySubscriptionId = useExistingAIProject ? split(...)[2] : subscription().subscriptionId`.
   **Collapse** to `subscription().subscriptionId`.
6. Line 180 - `var aiFoundryResourceGroupName = useExistingAIProject ? split(...)[4] : resourceGroup().name`.
   **Collapse** to `resourceGroup().name`.
7. Line 264 - the `= if (!useExistingAIProject)` condition on `module ai_foundry_project`.
   **Remove the condition**, making the module unconditional. The module itself stays (row 50).
8. Lines 273-280 - the whole `module existing_project_setup` block. **Delete.**
9. Lines 282-287 - the six branch-selection ternaries `aiFoundryName`, `aiProjectName`,
   `projectEndpoint`, `aiFoundryEndpoint`, `aiFoundryResourceId`, `aiProjectPrincipalId`.
   **Collapse each to the greenfield side** and drop the `!` safe-dereference operator, which is no
   longer needed once `ai_foundry_project` is unconditional - for example
   `var aiFoundryName = ai_foundry_project.outputs.name`. These six become the core's outputs.
10. Lines 292 and 324 - the `scope: resourceGroup(aiFoundrySubscriptionId,
    aiFoundryResourceGroupName)` expressions on `module model_deployments` (line 290) and
    `module foundry_search_connection` (line 322). **Collapse, do not delete.** Both modules still
    need a scope; with items 5 and 6 collapsed the expression reduces to `scope: resourceGroup()`
    (equivalently, the deployment's own resource group). Deleting the `scope:` line outright would
    change the deployment target of two modules that are still staged.

*Staged Technical Pattern `TP/infra/bicep/modules/identity/role-assignments.bicep` (row 52):*

11. Line 15 - `param useExistingAIProject bool = false`. **Remove.**
12. Line 18 - `param existingFoundryProjectResourceId string = ''`. **Remove.** Note that line 41's
    `param aiFoundryResourceId string = ''` **stays** - it is the greenfield input.
13. Lines 56-58 - the three `existingAIFoundryName` / `existingAIFoundrySubscription` /
    `existingAIFoundryResourceGroup` `split()` vars. **Delete outright.** This is the change that
    removes a core-owned concern (ARM resource-id segment layout) from the pattern layer.
14. Lines 117-127 - `module assignOpenAIToSearchExisting './cross-scope-role-assignment.bicep' =
    if (useExistingAIProject && ...)`. **Delete the whole block.** It consumes items 12 and 13.
15. Lines 140-150 - `module backendAppCogServicesUserExisting './cross-scope-role-assignment.bicep'
    = if (useExistingAIProject && ...)`. **Delete the whole block.** Items 14 and 15 are the only
    two callers of `cross-scope-role-assignment.bicep`, which is why row 52a is orphaned.
16. Lines 106, 129, 220, 231 - the four `if (!useExistingAIProject && ...)` conditions on
    `assignOpenAIRoleToAISearch`, `backendAppCogServicesUserAssignment`, `deployerAzureAIAccess`,
    and `deployerAzureAIDeveloper`. **Drop only the `!useExistingAIProject &&` prefix** from each,
    keeping the remaining `!empty(...)` guards intact. These four resources are the greenfield half
    and they all stay.

*Staged Technical Pattern `TP/infra/bicep/main.bicep` (row 53):*

17. Lines 642-644 - the three `module role_assignments` params. **Remove all three:**
    `useExistingAIProject: useExistingAIProject` (642) and
    `existingFoundryProjectResourceId: existingFoundryProjectResourceId` (643) are deleted with
    items 11-12, and `aiFoundryResourceId: !useExistingAIProject ? aiFoundryResourceId : ''` (644)
    **collapses to `aiFoundryResourceId: aiFoundryResourceId`**. The deliberate blanking existed
    only to switch the same-resource-group assignments off on the BYO branch; with no BYO branch it
    must not survive, or the greenfield role assignments will never fire.

**Cross-layer implication - simplified, not merely relocated.**

With items 11-13 removed, the pattern no longer re-derives anything about the Foundry account. The
revision-4 finding - that `role-assignments.bicep` lines 56-58 string-split the raw resource id
inside the pattern layer, duplicating logic the core performs at lines 177-180 - is **moot**, because
those three lines are removed wholesale rather than reworked.

**The revision-4 "core emits six identifiers" fix and the `aiFoundryResourceId` double-assign caveat
are deleted from this plan.** They described a repair to a branch that no longer exists. The core
still emits the identifiers the pattern genuinely needs (section 8), but it emits them as plain
greenfield values, and the pattern consumes them as ordinary parameters with no branch logic on
either side. There is no `split()` to delete at staging time and no blanking to preserve.

**References that need no action** (re-verified at revision 5):

| Reference | Row | Revision-5 status |
|---|---|---|
| `infra/main.parameters.json` lines 38-40 and `infra/main.waf.parameters.json` lines 41-43 (`${AZURE_EXISTING_AIPROJECT_RESOURCE_ID}`) | 55 | Out of scope, and **not re-expressed** on the core. The parameter disappears with item 1. |
| `infra/main.bicep` selector lines 145, 223, 254 | 47 | Out of scope. Its parameter list informs the core parameter surface **minus** this toggle. |
| Six `.github/workflows/*.yml` plumbing `AZURE_EXISTING_AIPROJECT_RESOURCE_ID` | 3 | Out of scope. Repo CI for the source template only; nothing to carry. |
| `infra/scripts/pre-provision/validate_bicep_params.py` lines 14 and 39 | 64 | Out of scope. Verified: the variable appears in the docstring and in `_ENV_VAR_EXCEPTIONS`. Both simply disappear; the pattern's own preflight (row 60) must **not** add the exception back. |
| `documents/ReuseFoundryProject.md`, `documents/CustomizingAzdParameters.md` line 25 | 73 | Out of scope and **dropped, not rewritten**. They document a capability the split no longer ships. Replaced by a one-line limitation in `SC/README.md` (section 8). |
| `infra/vscode_web/.env` line 6 | 66 | Out of scope and still **security-flagged** - it holds a real project resource id. Unchanged. |
| `azure.yaml` | 6 | Verified: contains no reference to the parameter or the environment variable. Nothing to do. |

**Capability statement - stated plainly.** `stable-cores/agentic-apps` provisions the AI Foundry
account and Foundry Project **greenfield only**. It does **not** support composing onto a
customer-owned, pre-existing Foundry project. Record this as a **documented limitation** in
`SC/README.md` and `SC/metadata.yaml`, and note the plausible future enhancement: re-introduce
`existing-project-setup.bicep` plus `cross-scope-role-assignment.bicep` behind an
`existingFoundryProjectResourceId` extension point, with the core emitting the account name,
subscription id, and resource group name as outputs so the pattern never re-derives them. That is a
strictly additive follow-up and nothing in this split blocks it.

### 7.5 The existing Log Analytics workspace branch - SKIPPED, greenfield observability only

> **New in revision 5 (reviewer decision 5b).** The attach-to-an-existing-Log-Analytics-workspace
> branch is excluded **to reduce complexity**. Because observability is **pattern-owned** in this
> composition (row 51, section 13 Q5), the branch lives in the Technical Pattern's infra, not the
> Stable Core's.

> **Read this before applying anything below.** This removes the **bring-your-own branch**, not the
> workspace. `technical-patterns/chat-with-data-voice` **still provisions a Log Analytics workspace
> and an Application Insights component, greenfield**, through the staged
> `modules/monitoring/log-analytics.bicep` and `modules/monitoring/app-insights.bicep` (row 51).
> **Both modules remain staged, invoked, and deployed. Neither is orphaned. Observability is not
> dropped.** The `enableMonitoring` parameter is also **retained** - it is a feature toggle, a
> different thing entirely from the BYO branch, and it keeps its existing semantics. The promoter
> must not read this section as removing telemetry.

**Located and confirmed.** The branch is entirely inside the vanilla `infra/bicep/main.bicep` plus
its solution-level parameter files; there is no separate BYO module and no `existing` resource
declaration for the workspace. Verified surface:

| What | Where (verified) |
|---|---|
| Parameter | `infra/bicep/main.bicep` line 142 - `param existingLogAnalyticsWorkspaceId string = ''`, described as *"Optional. Resource ID of an existing Log Analytics workspace. Empty creates a new one when monitoring is enabled."* |
| Use-existing flag | `infra/bicep/main.bicep` line 174 - `var useExistingLogAnalytics = !empty(existingLogAnalyticsWorkspaceId)` |
| Conditional module | `infra/bicep/main.bicep` line 237 - `module log_analytics './modules/monitoring/log-analytics.bicep' = if (enableMonitoring && !useExistingLogAnalytics)` |
| Selection ternary | `infra/bicep/main.bicep` lines 246-248 - `var logAnalyticsWorkspaceResourceId = enableMonitoring ? (useExistingLogAnalytics ? existingLogAnalyticsWorkspaceId : log_analytics!.outputs.resourceId) : ''` |
| Consumer | `infra/bicep/main.bicep` line 255 - `workspaceResourceId: logAnalyticsWorkspaceResourceId` on `module app_insights` (line 250, conditioned only on `enableMonitoring`) |
| azd parameter files | `infra/main.parameters.json` lines 35-37 and `infra/main.waf.parameters.json` lines 38-40 - `"existingLogAnalyticsWorkspaceId": { "value": "${AZURE_ENV_EXISTING_LOG_ANALYTICS_WORKSPACE_RID}" }` |
| Selector template | `infra/main.bicep` lines 142, 222, 253 - the same parameter declared and forwarded to both flavors |
| Workflows | `AZURE_ENV_EXISTING_LOG_ANALYTICS_WORKSPACE_RID` in `deploy-orchestrator.yml`, `deploy-v2.yml`, `job-deploy.yml`, `job-deploy-linux.yml`, `job-deploy-windows.yml` (input declarations, a resource-id regex validation, and `azd env set` plumbing) |
| Docs | `documents/ReuseLogAnalytics.md` (whole file), `documents/CustomizingAzdParameters.md` line 24, `documents/DeploymentGuide.md` line 276 |
| `azure.yaml` | **Verified: no reference.** Nothing to change. |

**Companion removals (8 items).** Applied to `TP/infra/bicep/main.bicep` (row 53) at staging:

1. Line 142 - `param existingLogAnalyticsWorkspaceId string = ''` and its `@description`.
   **Remove.** It is not a pattern parameter; section 9's parameter surface does not carry it.
2. Line 174 - `var useExistingLogAnalytics = !empty(existingLogAnalyticsWorkspaceId)`. **Remove.**
3. Line 237 - the `module log_analytics` condition `if (enableMonitoring && !useExistingLogAnalytics)`.
   **Simplify to `if (enableMonitoring)`.** The module block, its `name`, `params`, and `scope` are
   **kept unchanged** - only the `&& !useExistingLogAnalytics` clause is dropped.
4. Lines 246-248 - the nested selection ternary. **Collapse the inner ternary only**, to
   `var logAnalyticsWorkspaceResourceId = enableMonitoring ? log_analytics!.outputs.resourceId : ''`.
   The outer `enableMonitoring` ternary and the `!` safe-dereference **stay**, because
   `log_analytics` is still a conditional module.
5. Line 255 - `workspaceResourceId: logAnalyticsWorkspaceResourceId` on `module app_insights`.
   **Unchanged.** Listed here only so the classifier confirms the collapsed var still resolves and
   does not "clean up" a line that must survive.
6. `infra/main.parameters.json` lines 35-37 and `infra/main.waf.parameters.json` lines 38-40 -
   the `existingLogAnalyticsWorkspaceId` / `${AZURE_ENV_EXISTING_LOG_ANALYTICS_WORKSPACE_RID}`
   entries. **Not re-expressed** as a pattern parameter (the files themselves are already out of
   scope under row 55).
7. All five `.github/workflows/*.yml` references to `AZURE_ENV_EXISTING_LOG_ANALYTICS_WORKSPACE_RID`
   - input declarations, the resource-id regex validation, and the `azd env set` plumbing. **Not
   carried** (the workflows are already out of scope under row 3). Recorded so the reviewer can see
   the full blast radius rather than discovering it later.
8. `documents/ReuseLogAnalytics.md`, `documents/CustomizingAzdParameters.md` line 24, and
   `documents/DeploymentGuide.md` line 276. **Dropped, not rewritten** into `TP/docs/` (already out
   of scope under row 73). Replaced by the one-line limitation in `TP/README.md` below.

**Newly orphaned modules: none.** `log-analytics.bicep` keeps its single caller (item 3, now
unconditional on the BYO axis) and `app-insights.bicep` is untouched, so both remain reachable and
both are staged under row 51. This is the material difference from decision 5a, which *does* orphan
`cross-scope-role-assignment.bicep` (row 52a). A dangling-reference risk row is still carried in
section 12 for the *incomplete-application* failure mode - if item 4 is skipped while item 1 is
applied, `logAnalyticsWorkspaceResourceId` references a parameter that no longer exists and the
template will not build.

**Lost capability - recorded honestly.** The pattern can no longer attach the solution's
Application Insights component to a customer's **pre-existing central Log Analytics workspace**.
Every deployment gets its own new workspace. For a customer with a consolidated observability
estate - centralized retention policy, cross-workload Kusto queries, existing alert rules,
workspace-scoped RBAC, a negotiated commitment tier - that is a genuine gap, and it is the most
likely of the two excluded BYO paths to be asked for in a real engagement. Record it as a
**documented limitation** in `TP/README.md` and `TP/metadata.yaml`, alongside the **plausible future
enhancement**: re-introduce `existingLogAnalyticsWorkspaceId` as a pattern extension point that
short-circuits the `log_analytics` module and feeds `app-insights.bicep` directly. It is a small,
strictly additive change - roughly the four lines removed above, put back - and nothing in this
split forecloses it.

**Survey only, no action - other reuse or bring-your-own branches in the infra.** The reviewer asked
for a list, not a decision. Every `param` in the vanilla `infra/bicep/main.bicep` was enumerated and
checked:

* **`existingFoundryProjectResourceId`** (line 145) - the decision 5a path, section 7.4.
* **`existingLogAnalyticsWorkspaceId`** (line 142) - the decision 5b path, this section.
* **No others exist.** There is **no** BYO/reuse parameter for Application Insights, App Service
  Plan, Azure Container Registry, Cosmos DB, Azure AI Search, or VNet/subnet. The complete parameter
  list is `solutionName`, `solutionUniqueText`, `location`, `tags`, `azureAiServiceLocation`,
  `deploymentScenario`, `deploymentType`, `gptModelName`, `gptModelVersion`,
  `gptDeploymentCapacity`, `embeddingModel`, `embeddingDeploymentCapacity`, `gptRealtimeModelName`,
  `gptRealtimeModelVersion`, `gptRealtimeDeploymentCapacity`, `azureOpenaiAPIVersion`,
  `azureAiAgentApiVersion`, `appServicePlanSku`, `enableMonitoring`, the two `existing*` parameters
  above, and `deployingUserPrincipalType`. None of the remainder selects between provisioning and
  reusing a resource.
* **`enableMonitoring`** (line 135) is called out explicitly so it is not mistaken for a third BYO
  branch. It is a **feature toggle** - monitoring on or off - not a bring-your-own selector, and it
  is **retained unchanged** in the staged pattern.
* **Open question for the reviewer:** none of the above needs a decision now. If the intent is a
  blanket "greenfield only, everywhere" rule for this pattern and core, it is already satisfied
  after 5a and 5b, and no further exclusions follow from it.

## 8. Stable Core IaC completeness

`stable-cores/agentic-apps/` is a **New** core. The full Stable Core contract from
`references/layer-structures.md` applies to it.

**Canonical shape to stage:**

```text
stable-cores/agentic-apps/
├── infra/
│   ├── bicep/
│   │   ├── main.bicep          # NEW - composes the five modules below
│   │   └── modules/            # from row 50, staged as-is (already vanilla)
│   │       ├── ai-foundry-project.bicep          # CognitiveServices/accounts + .../projects
│   │       ├── ai-foundry-connection.bicep
│   │       ├── ai-foundry-model-deployment.bicep
│   │       ├── ai-search.bicep                   # Microsoft.Search/searchServices
│   │       └── ai-search-identity.bicep
│   └── README.md               # Bicep only; records the deferred Terraform flavor
├── scripts/                    # provisioning / post-provision automation
├── metadata.yaml               # metadata/schemas/stable-core.schema.json
└── README.md
```

`existing-project-setup.bicep` is **not** in this tree - it is Out of scope under row 50a
(section 7.4). Five modules, not six.

**Scope:** AI Foundry account, Foundry Project, and Azure AI Search **only**, as directed. No
storage account, no Fabric capacity, no observability - observability is in the pattern (row 51,
section 13 Q5). **Greenfield provisioning only**; existing-project reuse is excluded (row 50a,
section 7.4).

**Bicep flavor - verified vanilla, no rewrite needed.** All five modules were scanned: zero
`br/public:` references and zero `avm/` references. They declare plain resources directly
(`Microsoft.CognitiveServices/accounts@2025-12-01`,
`Microsoft.CognitiveServices/accounts/projects@2025-12-01`,
`Microsoft.CognitiveServices/accounts/projects/connections@2025-12-01`,
`Microsoft.CognitiveServices/accounts/deployments@2025-12-01`,
`Microsoft.Search/searchServices@2025-05-01`). They can be staged as-is under
`SC/infra/bicep/modules/`. Only `main.bicep` is newly authored, extracted from the core-owned
resource block of `infra/bicep/main.bicep` **with the `useExistingAIProject` switch removed** per
the 17-item trace in section 7.4 - which means `module ai_foundry_project` is unconditional, the
six branch-selection ternaries collapse to direct `ai_foundry_project.outputs.*` reads, and the two
cross-scope `scope:` expressions collapse to the deployment's own resource group rather than being
deleted.

**Terraform flavor - DEFERRED, NOT AUTHORED IN THIS PASS (reviewer decision 1, revision 3).** The
contribution ships no Terraform, and the reviewer has consciously scoped Terraform out of this
split. No `infra/terraform/` tree is staged, and no generated-flavor entry appears in the per-part
table or the roll-up counts. The per-flavor folder `infra/bicep/` is **kept** (with `main.bicep` +
`modules/`) precisely so a Terraform flavor can be added later without restructuring - do not
flatten to a single file and do not move the Bicep up to `infra/`. This deviates from the skill's
Composition Readiness "both IaC flavors" requirement and is recorded as an **accepted deviation** in
section 12. `SC/infra/README.md` and `SC/metadata.yaml` must state **supported IaC flavors: Bicep
only** rather than claiming both. Consequence: `agentic-apps` is not Terraform-composable, so a
Planner/Builder run that selects the Terraform flavor cannot consume it until that flavor is added.
**Revision-5 note:** the eventual Terraform translation is now *smaller* than revision 4 implied -
there is no BYO branch and no cross-scope role assignment to translate.

**Parameter surface (Bicep):** Foundry account name/location/SKU, project name and display name,
model deployment list (including `gpt-realtime-mini` for the voice channel), AI Search
name/SKU/replica-partition counts, and private-networking toggles carried over from
`infra/main.parameters.json`. **`existingFoundryProjectResourceId` is not part of this surface** -
it is removed with the BYO branch (section 7.4, item 1).

**Outputs** (these are exactly the inputs `TP/infra/bicep/main.bicep` declares as parameters, row
53): Foundry endpoint, Foundry account name, Foundry project resource id, Foundry project endpoint,
Foundry project principal id, model deployment names, and AI Search endpoint and name. All are
plain greenfield values with no branch logic; there is no `useExistingAIProject` output and no
`aiFoundrySubscriptionId` / `aiFoundryResourceGroupName` pair, because the pattern no longer places
role assignments outside the deployment's own resource group.

**Also required for a New core:** `metadata.yaml` (schema-valid, `status: proposed`, supported IaC
flavors recorded as **Bicep only**), `README.md` stating scope and composition, and **two documented
limitations**: (1) **Bicep only**, and (2) **greenfield Foundry only - no existing-project reuse**,
with the future-enhancement note from section 7.4. `documents/ReuseFoundryProject.md` is **not**
rewritten into this README; the capability it describes is not shipped. Plus `scripts/` for
provisioning and post-provision automation.

**Naming.** `agentic-apps` is kept as directed. One-line taxonomy note only, no rename proposed:
`docs/design/accelerator-taxonomy.md` reserves `foundry-iq` for the Foundry-plus-Search core shape,
so `agentic-apps` is a new name outside the current taxonomy registry and should be **proposed as a
taxonomy addition** in the promotion PR rather than mapped to an existing entry.

## 9. Technical Pattern IaC completeness

The contribution ships Bicep only, in two competing flavors (vanilla `infra/bicep/` and AVM
`infra/avm/`). The AVM tree is discarded outright. Therefore:

* `technical-patterns/chat-with-data-voice/infra/bicep/` is staged from the vanilla tree
  (`main.bicep` plus `modules/{compute,data,identity,monitoring}`), reduced to the **seven**
  pattern-owned modules (rows 51 and 52): `log-analytics`, `app-insights`, `container-registry`,
  `app-service-plan`, `app-service`, `cosmos-db-nosql`, and `role-assignments`.
  `cross-scope-role-assignment` is **not** among them - it is orphaned and Out of scope under
  row 52a (section 7.4). Seven, not eight.
* **Observability is staged and provisioned, greenfield.** `log-analytics.bicep` and
  `app-insights.bicep` are both pattern modules and both deploy on every run where
  `enableMonitoring` is true. Decision 5b removes only the *attach-to-an-existing-workspace* branch
  (section 7.5), not the workspace, not Application Insights, and not the `enableMonitoring`
  toggle.
* **Terraform flavor - DEFERRED, NOT AUTHORED IN THIS PASS (reviewer decision 1, revision 3).** No
  `infra/terraform/` tree is staged and no generated-flavor entry appears in the per-part table or
  the roll-up counts. The per-flavor folder `infra/bicep/` with `main.bicep` + `modules/` is
  **kept** so a Terraform flavor can be added later without restructuring - not flattened to a
  single file, not moved up to `infra/`. `TP/infra/README.md` and `TP/metadata.yaml` (`deployment` /
  `compatibility.iac`) must state **supported IaC flavors: Bicep only** rather than claiming both.
* Consequence, stated honestly: `chat-with-data-voice` is **not Terraform-composable**. Because the
  Planner picks one flavor for the whole solution and merges every layer in it, a run that selects
  Terraform cannot consume this pattern (or `agentic-apps`) until the flavor is added. Recorded as
  an **accepted deviation** in section 12, tracked as follow-up work, not a blocker.
* The pattern's infra **consumes** the `agentic-apps` outputs (Foundry endpoint, Foundry account
  name, project resource id, project endpoint, project principal id, Search endpoint and name) as
  plain parameters - no branch logic, no `useExistingAIProject`, no re-derived identifiers - and
  **produces** `APPLICATIONINSIGHTS_CONNECTION_STRING` as an output, since observability is
  pattern-owned in this composition. It also consumes `SCENARIO_PATH` indirectly, as an app setting
  on the two App Services (section 6A.1).
* `TP/README.md` and `TP/metadata.yaml` must record **one documented limitation** from decision 5b:
  **the pattern always provisions a new Log Analytics workspace and cannot attach to an existing
  one** (section 7.5), with the future-enhancement note. It must state this in a way that cannot be
  misread as "no observability".

## 10. Stable Core fit risks

The single core dependency for this pattern is the new `stable-cores/agentic-apps`.

| Service the core deploys | Pattern needs it? | Optional in IaC? | Control |
|---|---|---|---|
| Azure AI Foundry account | Yes (`chat`, `voice_live`, connected agents) | Mandatory | None - provisioned greenfield on every deployment (row 50a excluded) |
| Azure AI Foundry project | Yes (agent creation via `TP/scripts/agents/`) | Mandatory | Same |
| Foundry model deployments (chat plus `gpt-realtime-mini`) | Yes | Mandatory | Deployment list is a core parameter |
| Azure AI Search | Yes (catalog and policy indexes) | Mandatory | None needed |

**No unrelated mandatory services.** Because `agentic-apps` is scoped to exactly the three
capabilities the pattern requires, `requiredCoreCapabilities` and the core's deployed services match
one-for-one. There is no unrelated-mandatory-service composition risk to disclose to the Planner -
which is the concrete benefit the reviewer's decision buys, and it replaces the Fabric-capacity risk
that revision 1 carried against `microsoft-iq`.

**Revision-5 change.** The revision-4 note claiming a composition could satisfy the Foundry
capabilities **without provisioning anything** is **deleted** - decision 5a removes that path. Every
composition provisions its own Foundry account and project, always in the deployment's own
subscription and resource group. The pattern therefore never places a role assignment across a
subscription or resource-group boundary, which is exactly why `cross-scope-role-assignment.bicep`
is orphaned (row 52a) and why `role-assignments.bicep` loses its three `split()` derivations
(section 7.4, item 13).

**No change is proposed to `microsoft-iq`.** The observation recorded in revision 1 - that
`microsoft-iq/infra/bicep/main.bicep` references `br/public:avm/res/fabric/capacity`, conflicting
with the vanilla-only rule - remains pre-existing live content and is explicitly **out of scope**
for this split, since no delta targets that file any more.

## 11. Taxonomy alignment and declared cross-layer links

### 11.1 Taxonomy alignment (new components)

Per `docs/design/accelerator-taxonomy.md`. Folder layout stays flat; family and group are recorded
in `metadata.yaml`.

| New component | Layer | Taxonomy placement |
|---|---|---|
| `agentic-apps` | Stable Core | No existing registry entry. The closest is `foundry-iq` (Foundry plus AI Search). Name kept as directed; **propose `agentic-apps` as a new taxonomy entry** in the promotion PR. |
| `chat-with-data-voice` | Technical Pattern | L1 family `chat-with-your-data`, L2 `customer-chat-with-your-data`. Record the proposed `real-time-voice` family as a secondary family because the voice channel is first class. |
| `banking-customer-support` | Industry Scenario | Group `fsi`; `industry: financial services`, segment `retail banking`. Name locked by the reviewer. |
| `retail-customer-support` | Industry Scenario | Group `rcg`; `industry: retail and consumer goods`, segment `specialty retail`. Name locked by the reviewer. |
| `healthcare-patient-support` | Industry Scenario | Group `hls`; `industry: healthcare and life sciences`, segment `provider services`. Name locked by the reviewer. |

### 11.2 Declared cross-layer links and metadata wiring (to populate at staging)

**`stable-cores/agentic-apps`:**

* `capabilities: [ai-foundry-account, ai-foundry-project, ai-model-deployment,
  ai-realtime-model-deployment, ai-search]`. **`existing-foundry-project-reuse` is removed again**
  (revision 5, decision 5a) - the core must not advertise a capability it does not ship.
* `status: proposed`; **Bicep only** in `deployment` / `compatibility.iac` - the metadata must
  reflect the single supported flavor honestly rather than claiming both.
* `extensionPoints` advertises the model-deployment list and the private-networking toggles.
  **`existingFoundryProjectResourceId` is not an extension point** and must not appear.
* `limitations` (or the README equivalent) records both documented limitations: Bicep only, and
  greenfield Foundry only.

**`technical-patterns/chat-with-data-voice`:**

* **Bicep only** in `deployment` / `compatibility.iac`.
* `supportedStableCores: [agentic-apps]`; `requiredCoreCapabilities: [ai-foundry-account,
  ai-foundry-project, ai-model-deployment, ai-realtime-model-deployment, ai-search]`. Observability
  is **not** listed, because the pattern provisions it itself.
* `limitations` records the decision 5b limitation in unambiguous words: *provisions a new Log
  Analytics workspace and Application Insights component on every deployment; cannot attach to an
  existing Log Analytics workspace.* It must **not** be phrased as an observability gap.
* **`scenarioExtensionPoints`** must cover the entire config surface, and must name the published
  schema. Extending - not replacing - the `catalog` block defined in section 6:
  * `host.appTitle`, `host.iconPath`, `host.widgetTheme`, `host.complianceBanner`, and
    **`host.assistantIconPath`** (new in revision 6, section 6B.3)
  * `welcome.title`, `welcome.subtitle`, `welcome.hint`
  * `catalog.routePrefix`, `catalog.itemSingular`, `catalog.itemPlural`, `catalog.cardSchema`,
    `catalog.enabledEndpoints`, `catalog.cardVariant`, `catalog.copy`
  * `presentation.defaultImage`, `presentation.items`, `presentation.titleAliases` - **revision 6
    removes `presentation.image` and `presentation.assetPrefix` from this surface** (section 6B.2);
    `presentation.items` now carries `highlights` only, and the image comes from the catalog row
  * `configSchema: config/scenario-config.schema.json` (section 6A.7) - **unchanged by revision 7:
    the schema is still published and still named here; only the sample instance was dropped, and
    compose-time validation against this schema still runs** - and `SCENARIO_PATH` recorded in the
    `configuration` block (section 6A.1). The pattern's `config/` folder now contains this schema
    and nothing else.
* `application` records the scenario-free frontend image property (section 6A.2) so the Builder
  knows one image serves every scenario. **Revision 6 strengthens this claim rather than qualifying
  it:** with assets served from `SCENARIO_PATH`, the Builder no longer copies anything into the
  frontend's public root, so nothing scenario-specific enters the image at any stage.
* `apiSurface` (or the README equivalent) records **both** scenario-facing routes -
  `GET /api/scenario/config` and `GET /api/scenario/assets/{path}` - and states that the asset route
  resolves against `SCENARIO_PATH` under the section 6B.4 controls.

**Each industry scenario** (`banking-customer-support`, `retail-customer-support`,
`healthcare-patient-support`):

* `compatibleTechnicalPatterns: [chat-with-data-voice]`.
* `requiredPatternCapabilities: [scenario-manifest, connected-agent-handoff, catalog-index,
  policy-index, chat-widget-embed, realtime-voice, scenario-config-api, schema-driven-catalog-ui]` -
  the last two added in revision 4 and **preserved unchanged in revision 5**, naming exactly what
  each scenario needs the pattern to provide now that it carries no code of its own.
* `domainAssets` names what it supplies: the agent instruction texts, the catalog CSV, the policy
  corpus, **the flat `assets/` image folder** (rows 42b, 44b, 63, 30, 41 - 10 files for banking, 10
  for healthcare, 18 for retail, section 6B.3), and the manifest's `host`, `welcome`, `catalog`, and
  `presentation` blocks.
* `requiredPatternCapabilities` gains **`scenario-asset-serving`** (revision 6), naming the asset
  route each scenario now depends on to render any image at all. The pattern's
  `scenarioExtensionPoints` correspondingly documents the `assets/` folder convention and the
  scenario-relative `image` column contract.

## 12. Risks and open questions

**Prominent risk - the cart skip removes a reachable code path.**

> The cart is **not** fully unused. `POST /api/cart/add` is reachable in the running ecommerce UI:
> `EcommerceApp.tsx` to `MainContent`/`ProductGrid` to `FigmaProductCard`'s add-to-cart button to
> `addToCart()` to `POST /api/cart/add`. Applying the skip **as directed** therefore breaks that
> path unless every companion in section 7.1 is removed with it. **What breaks if the companions
> are not removed:** the retail scenario ships a visible "Add to Cart" button that fires a request
> to a route that no longer exists, producing a 404 and a "Failed to add product to cart" toast on
> every click - a demo-visible regression. **What is genuinely lost either way:** nothing the user
> can see today, because `CartDrawer.tsx` (the only component that renders cart contents) is never
> mounted and the remaining four `api.ts` cart functions have zero importers - two of them
> (`DELETE /api/cart/${productId}`, `POST /api/cart/checkout`) were already calling routes that
> `cart.py` does not expose. The cart is write-only and partially broken in the source. Removing it
> is defensible; removing it *incompletely* is not. **Mitigation (revision 4, preserved):**
> decision 2c removes `EcommerceApp.tsx`, `MainContent`, `ProductGrid`, and `FigmaProductCard` as
> staged files altogether, replacing them with the generic `CatalogApp`/`CatalogItemCard`, so the
> `onAddToCart` prop chain disappears by construction rather than by a careful surgical pass. The
> residual risk is now the *backend* companions (items 1-7) only.

**Prominent risk - dangling module references if either BYO removal is applied incompletely.**

> Two removals in this revision take out a `module` invocation and its supporting parameters and
> variables. Each is safe only if applied in full.
> **Decision 5a (section 7.4).** All 17 companion items must go together. Leaving
> `module existing_project_setup` while removing `useExistingAIProject` - or the reverse - produces
> a template that does not build, and `cross-scope-role-assignment.bicep` (row 52a) must **not** be
> staged, because after items 14 and 15 nothing invokes it. Two collapses are especially easy to get
> wrong: item 10, where the `scope:` expressions on `model_deployments` and `foundry_search_connection`
> must be **collapsed to the deployment's own resource group, not deleted** - both modules still
> need a scope; and item 17, where `aiFoundryResourceId: !useExistingAIProject ? aiFoundryResourceId
> : ''` must collapse to `aiFoundryResourceId: aiFoundryResourceId`, because leaving the blanking in
> place would silently switch off every greenfield role assignment.
> **Decision 5b (section 7.5).** All 8 companion items must go together. Removing the parameter
> (item 1) without collapsing the selection ternary (item 4) leaves
> `logAnalyticsWorkspaceResourceId` referencing a symbol that no longer exists. Conversely, item 3
> must **simplify** the `log_analytics` module condition to `if (enableMonitoring)` rather than
> delete the module - **the pattern still provisions Log Analytics and Application Insights
> greenfield**, and item 5 (`workspaceResourceId: logAnalyticsWorkspaceResourceId`) must survive
> untouched.
> **Verification:** `az bicep build` on both staged `main.bicep` files must pass before the
> comparison report is produced, and the report must show the collapsed expressions.

**Accepted deviation - Terraform out of scope (reviewer decision 1, revision 3).**

> **The rule.** The skill's **Composition Readiness** contract (`SKILL.md` and
> `references/layer-structures.md`) requires that every infra-bearing layer ship **both** IaC
> flavors under a per-flavor `infra/<flavor>/` with `main.<ext>` + `modules/`, and that a missing
> flavor be authored vanilla-only/WAF and flagged *generated - human-review*.
> **The deviation.** The reviewer has **consciously scoped Terraform out of this pass**. Both
> infra-bearing components - `stable-cores/agentic-apps` and
> `technical-patterns/chat-with-data-voice` - stage **Bicep only**. The revision-2 *generated
> Terraform* entries for both are withdrawn. The canonical per-flavor path `infra/bicep/` with
> `main.bicep` + `modules/` is **retained** so a Terraform flavor can be added later without
> restructuring; nothing is flattened to a single file and nothing is moved up to `infra/`.
> **The consequence.** The staged components are **not Terraform-composable**. The Planner picks a
> single IaC flavor for the whole solution and merges every layer in it, so any Planner/Builder run
> that selects the Terraform flavor **cannot consume either component** until that flavor is added.
> Each component's `metadata.yaml` (`deployment` / `compatibility.iac`) and `infra/README.md` must
> state **supported IaC flavors: Bicep only** rather than claiming both.
> **Disposition.** Follow-up work, **not a blocker** for this promotion: author
> `agentic-apps/infra/terraform/` and `chat-with-data-voice/infra/terraform/` as faithful vanilla
> translations in a later pass, each flagged *generated - human-review/validate before deployment*.
> **Revision-5 note:** the translation is now **smaller** than revision 4 implied - with both BYO
> branches and the cross-scope role assignments gone, there is a single unconditional provisioning
> path to translate in each layer.

**Security requirement - the scenario config endpoint must filter its response.**

> `GET /api/scenario/config` (section 6A.2) reads the full scenario manifest server-side and must
> return **only** `host`, `welcome`, `catalog`, and `presentation`. It must **never** return
> `search.catalogIndex`, `search.policiesIndex`, any `agents.*` prefix or tool name, or any `data.*`
> path. Those are server-side deployment details, and shipping them to a browser discloses the
> exact Azure AI Search index names, the Foundry agent naming scheme, and the on-disk data layout to
> anyone who can load the page - with no functional benefit whatsoever. **Implement the filter as an
> explicit four-key allow-list, not a three-key deny-list**, so any future manifest key is excluded
> by default rather than leaked by omission. The comparison report must show the endpoint's
> serializer and confirm the allow-list. *(Revision 4, preserved unchanged.)*

**Security requirement - the scenario asset route must reject path traversal.**

> `GET /api/scenario/assets/{path}` (section 6B.3) is a file-serving endpoint whose path segment
> comes straight from the URL, layered over a folder (`SCENARIO_PATH`) that also holds the manifest,
> the agent instruction text, and the policy corpus. Unmitigated, a request for `..%2f..%2f.env`
> reads whatever the app service identity can read. The mandatory controls are enumerated in
> **section 6B.4** and are **all** required, not a menu: reject `..` and every encoded variant before
> touching the filesystem; reject absolute and drive-qualified paths; canonicalize and re-verify
> containment under the canonicalized `SCENARIO_PATH` (a `startswith` on the raw string is not
> sufficient); **reject with `404` rather than clamping** the path; enforce an image-only extension
> allow-list and set `Content-Type` from it; set `Cache-Control` on asset responses; and serve
> `.svg` with `nosniff` plus a locked-down `Content-Security-Policy`, since SVG can carry script and
> 16 of the 20 distinct source assets are SVGs. The comparison report must show the handler with the
> rejection, the containment check, and the allow-list visible. *(New in revision 6.)*

Other risks:

* **Two capability losses, both deliberate, both documented.** `agentic-apps` cannot compose onto a
  customer-owned Foundry project (section 7.4), and `chat-with-data-voice` cannot attach to a
  customer's pre-existing central Log Analytics workspace (section 7.5). Both were reduced away for
  complexity, both are recorded as documented limitations in the owning component's README and
  `metadata.yaml`, and both have a small, strictly additive route back. The Log Analytics one is the
  more likely to be requested in a real engagement, because customers with a consolidated
  observability estate expect workspace reuse. **Neither is an observability or AI capability gap** -
  the solution still provisions Foundry, a project, Log Analytics, and Application Insights on every
  deployment.
* **The generic catalog app must reproduce three layouts on the first pass.** Decision 2c collapses
  431 lines of per-domain React into one config-driven component. The three source apps differ in
  layout (grid versus list), intro copy, error copy, and card field layout; all four are now config,
  but the generic component has to actually honor them. **Revision 7 removes the mitigation this
  bullet used to name:** with no standalone sample config (section 6A.7), the generic app cannot be
  smoke-tested without a scenario. The only remaining check is that the comparison report show the
  generic app rendering all three `cardVariant` values against the three staged scenarios - a
  review-time inspection, not an executable test.
* **Prominent risk (revision 7) - the technical pattern ships no executable validation whatsoever,
  and cannot be deployed meaningfully on its own.** With `tests/e2e-test/` out of scope (rows 74-76)
  **and** the standalone sample config dropped (section 6A.7), no staged component ships an eval
  dataset, harness, behavioral smoke test, or runnable fixture of any kind. The only executable check
  that survives is compose-time validation of a scenario `manifest.json` against
  `config/scenario-config.schema.json` - which validates **configuration shape only** (not agent
  grounding, handoff correctness, voice latency, or safety) **and runs only when a scenario is
  composed**, so it cannot be exercised against the pattern alone. Two concrete consequences, stated
  rather than implied: deploying `chat-with-data-voice` with no scenario attached yields a **catalog
  that renders empty**, because `GET {prefix}/` has no Cosmos content to return; and **no agents
  exist at all**, because agent creation reads `agents/*.txt` from the scenario folder under
  `SCENARIO_PATH`. There is therefore no "does it work?" check available at any point between
  staging and a fully composed solution. This is the accepted, combined cost of reviewer decision 6
  and the revision-7 decision, and it is why Workflow execution fit is 3 rather than 4 (section 2).
  **Recommendation, now the only validation route left:** a starter `TP/evals/` smoke check and a
  starter `evals/dataset.jsonl` per scenario before promotion.
* **Open question (revision 7, deferred - an idea to raise, not a deliverable of this plan).** A
  **minimal sample scenario** - a few generic catalog rows, one or two short policy documents, and
  domain-neutral agent instruction text - would give the pattern standalone smoke-test capability and
  close the risk above without reintroducing a domain-specific fixture inside the pattern. It is
  deliberately **not** proposed as part of this split, because the same gap applies to the live
  `chat-with-data` pattern (section 6A.7, precedent basis). **Raise it as a factory-wide
  convention** so `chat-with-data` adopts it too, rather than letting `chat-with-data-voice` become
  the only pattern in the factory carrying such a folder. Owner: the factory maintainers, not this
  contribution.
* **Two cores now overlap on Foundry and Search.** `agentic-apps` and `microsoft-iq` both deploy a
  Foundry account, project, and AI Search in Bicep (`microsoft-iq` additionally in Terraform, which
  `agentic-apps` deliberately does not ship in this pass). The reviewer has accepted this. The
  forward cost is drift between the two module sets and an ambiguous choice for the Planner when a
  future pattern requires only Foundry plus Search. **Revision-5 note:** with the BYO path removed,
  `agentic-apps` no longer has the differentiator revision 4 claimed for it - it is now a strictly
  narrower, greenfield-only subset of `microsoft-iq`'s Foundry and Search coverage. Recommend the
  `agentic-apps` README state its scope explicitly so the difference is discoverable, and expect the
  overlap question to be raised again at promotion.
* **Observability sits outside its normal layer.** Log Analytics and Application Insights are
  core-owned in the factory's normal boundary. Placing them in the pattern (row 51) is a deliberate
  consequence of the scoped core, not an oversight, but a future solution that composes
  `chat-with-data-voice` onto a *different* core that already ships observability will provision a
  second Application Insights and a second workspace - and, after decision 5b, has no BYO parameter
  to point at the core's existing workspace instead. Recommend the pattern gate its observability
  modules behind an `enableObservability` parameter defaulting to `true`, so such a composition can
  turn them off. This is now the only escape hatch the pattern offers.
* **App Service count.** The contribution deploys four App Services (chat backend, chat frontend,
  scenario backend, scenario frontend). The target is two. This is the single largest piece of merge
  work and it touches `main.bicep`, both Dockerfiles, `azure.yaml` hooks, the ACR script, and the
  CORS allowed-origins configuration.
* **Domain leakage in the API is now the last blocker to pattern reusability.** Decision 2 clears
  the frontend completely (zero scenario enum references remain, section 6A.8), which leaves the
  merged API as the only place domain vocabulary survives: `models.py`, `cosmos_service.py`
  (`get_orders_by_customer`, `transactions_container`), `services/user_onboarding.py`, and
  `scenario_config.py`'s Contoso Paints voice-grounding prose. The section 6 rename pass (`Product`
  to `CatalogItem`, `get_products` to `get_catalog_items`) must extend to all of these.
* **Import rewrites are mechanical but wide.** The collapsed `app/` level (section 4.8) touches
  every router, service, and util module plus both Dockerfiles and both `startup.sh` files, and now
  also the frontend's deleted `@/scenarios/*` imports. A missed rewrite is an import error at
  container start, not a build failure - verify by running the merged API and building the merged
  frontend once before the comparison report.
* **Secrets and environment leakage - flag unchanged from revision 4.** Three checked-in files carry
  real or stale deployment identifiers and **must never reach a staged layer or the promotion PR**:
  `.azure/ccsaecomhb/.env` (real subscription id, Foundry project resource id, agent id - row 1),
  `infra/vscode_web/.env` (same class of values - row 66), and **both `public/config.js` copies**
  (a live backend hostname `ecommerce-backend-202510211322.azurewebsites.net` and an OAuth redirect
  URI `ecommerce-frontend-202510211322.azurewebsites.net/auth/callback` - row 28a). All are Out of
  scope. The promoter must confirm exclusion of all three before opening the PR to `main`.
* **The CSV `image` rewrite must land together with the asset move and the asset route.** Revision 6
  makes three edits interdependent: the assets move into each scenario's `assets/`, the three CSVs
  are rewritten to `assets/<filename>`, and the API gains the asset route. Any one applied without
  the other two is worse than none - moving the assets without rewriting the CSVs leaves banking and
  healthcare pointing at a public root that no longer holds them, and rewriting the CSVs without the
  route leaves all three scenarios requesting a path nothing serves. Mitigation: the extended
  `preflight_scenario` check (section 6B.3) fails compose when a catalog `image` value is neither
  absolute nor resolvable under `assets/`, so an incomplete application surfaces at compose time
  rather than as broken images in a demo. *(New in revision 6.)*
* **Frontend duplication is assumed, not proven byte-identical.** The two frontends share roughly 90
  file names. This plan deduplicates them, but each pair must be diffed during staging; silently
  keeping the wrong copy would lose the widget's API base override or the host's scenario switcher.

**Risk bookkeeping for revision 6** (recorded so nothing looks silently dropped):

* *New:* the asset-route path-traversal security requirement (section 6B.4) and the
  incomplete-CSV-rewrite failure mode above.
* *Deleted as moot:* nothing. Revision 6 retires no risk. The revision-4 *"the Builder copies the
  SVGs into the app's public root"* step is **withdrawn** (sections 6A.5, 42b, 44b), which removes a
  latent contradiction with section 6A.1 rather than a tracked risk.
* *Unchanged:* every revision-5 risk, in full - the cart skip, both dangling-module-reference
  failure modes, the accepted Terraform deviation, the config-endpoint allow-list, both BYO
  capability losses, the generic-catalog-app risk, the no-behavioral-validation risk, the
  core-overlap risk, the observability-placement risk, the App Service count, the API domain
  leakage, the import rewrites, the secrets flag, and the frontend duplication caveat.

**Risk bookkeeping for revision 5** (recorded so nothing looks silently dropped):

* *Restored from revision 3, because decision 5a restores the skip:* the dangling-module-reference
  risk (now covering both BYO removals) and the greenfield-only capability loss for
  `agentic-apps`. Revision 4 had listed both under *"Risks retired in revision 4"*; that retirement
  is cancelled and the section is removed.
* *Deleted as moot:* the revision-4 bullet **"The BYO path's cross-layer identifiers must flow as
  parameters, not re-derivations"**, together with the *"core emits six identifiers"* fix and the
  `aiFoundryResourceId` double-assign caveat. `role-assignments.bicep` lines 56-58 are removed
  wholesale (section 7.4, item 13), so there is nothing left to re-derive and no cross-layer edge to
  repair. The only surviving instruction about line 644 is item 17's *collapse to a direct
  assignment*, which is the opposite of preserving the blanking - there is no contradictory
  guidance left anywhere in this plan.
* *New in revision 5:* the Log Analytics BYO capability loss and its incomplete-application failure
  mode (section 7.5), plus the note that decision 5b leaves the pattern with no way to defer to a
  core-owned workspace.
* *Unchanged:* the cart risk, the generic-catalog-app risk, the no-behavioral-validation risk, the
  core-overlap risk, the observability-placement risk, the App Service count, the API domain
  leakage, the import rewrites, the secrets flag, and the frontend duplication caveat.

## 13. Resolved decisions (carried forward)

### Q1. `agentic-apps` - RESOLVED by reviewer decision 2 (revision 2)

**New stable core, created as directed.** Revision 1 recommended reusing `microsoft-iq` on overlap
grounds. The reviewer has acknowledged the overlap and accepted it deliberately, so
`stable-cores/agentic-apps/` is staged as **New** with AI Foundry account, Foundry Project, and
Azure AI Search only (section 8). `microsoft-iq` is **not modified in any way** - the Fabric
capacity delta proposed in revision 1 is withdrawn, and the comparison against `microsoft-iq`
survives only as the recorded note in section 5.3. Not reopened.

### Q2. `chat-with-data-voice` is a new pattern - RESOLVED, verdict stands

Applying the New-vs-Same decision rule, three of the four "fundamentally different" criteria are met:

* **Data processing model:** live `chat-with-data` grounds on a Fabric Lakehouse plus a Fabric
  Ontology plus a Foundry IQ knowledge base, reached over MCP. The contribution grounds on two Azure
  AI Search indexes built from a catalog CSV and policy text files, plus Cosmos DB for session and
  transaction state. No Fabric anywhere.
* **Agent orchestration:** live is a single Foundry agent with two MCP tool connections. The
  contribution is a three-agent connected-agent topology with explicit handoff routing
  (`chat_agent` to `catalog_agent` or `policy_agent`).
* **Core API behavior:** the contribution adds a bidirectional real-time WebSocket voice channel
  (`routers/voice_live.py`, `/api/voice/config`, `/api/chat/save-voice-message`) and an embeddable
  widget contract (`window.ChatWidget.init`, shadow DOM, host-page auth bridge). Neither exists in
  the live pattern.

Only the fourth criterion (UI, prompts, agent count) would have pointed to Same, and the rule says
those alone never justify a new pattern. **Revision-4 reinforcement:** decision 2 makes that fourth
criterion structurally irrelevant to this pattern - UI is now entirely config, so no future UI
variation can ever argue for a fork.

### Q3. `scenario_loader.py` - RESOLVED, verdict stands, aligned with the composition contract

**Stage it to `TP/scripts/shared/scenario_loader.py` with three mandatory de-hardcoding fixes.**

The file is pure mechanism: it resolves a scenario id, reads `manifest.json`, reads agent
instruction text, and resolves the catalog CSV and policies directory paths. It contains no domain
content of its own. The skill is explicit that loaders and registration machinery are Technical
Pattern material even when the source ships them under a scenario-looking folder. Its five importers
confirm this: `01_create_agents.py`, the three `data_scripts/0{1,2,3}_*.py` loaders, and
`infra/scripts/scenario_bootstrap.py` - all pattern scripts under this plan (rows 57, 58, 60).

Three required fixes:

1. `SCENARIOS_DIR = REPO_ROOT / "scenarios"` hardcodes the source repo layout. **Replace with the
   `SCENARIO_PATH` environment variable of the composition contract (section 6A.1)**, which points
   at a single copied scenario folder. This is the *same* fix as contract step 3, not an additional
   one - `SCENARIO_PATH` supersedes `SCENARIOS_DIR`, and because it names one folder rather than a
   directory of folders, the loader's scenario-id selection also falls away.
2. `VALID_SCENARIOS = frozenset({"ecommerce", "healthcare", "banking"})` hardcodes three domain names
   into pattern code. Delete it - with `SCENARIO_PATH` there is exactly one scenario and nothing to
   validate an id against. Validation moves to the schema check of section 6A.7.
3. The `catalog_tool_name` and `policy_tool_name` fallback dictionaries embed domain vocabulary
   (`product_agent`, `care_policy_agent`, `accounts_agent`). Delete them. Every shipped manifest
   already sets `agents.catalogToolName` and `agents.policyToolName` (verified in
   `scenarios/banking/manifest.json`), so the fallbacks are unreachable and only leak domain names
   into the pattern.

The same three fixes apply to `chat-app/backend/app/scenario_config.py` (row 12), which additionally
hardcodes full Contoso Paints voice-grounding prose. That file is the larger of the two offenders.

**Staging outcome (revision 7a) - implemented, with three corrections to the wording above.**

1. **One loader, not three.** The three duplicate manifest loaders were consolidated into a single
   `TP/src/api/scenario_loader.py`. It must live under `src/api` rather than at the
   `TP/scripts/shared/scenario_loader.py` path named above, because `scripts/` sits **outside** the
   API Docker build context (section 6A.1) and would therefore not exist in the image.
   `load_manifest()` carries `@lru_cache(maxsize=1)`, since one solution composes exactly one
   immutable scenario.
2. **Fix 3 was a real bug, not only a domain-vocabulary leak.** `catalog_tool_name()` and
   `policy_tool_name()` read `manifest['catalog']['toolName']`, a key present in **no** manifest, so
   they silently returned `'catalog-search'` / `'catalog-policy'` while
   `scripts/agents/create_agents.py` registers the tools from `manifest['agents']['catalogToolName']`
   and `['policyToolName']`. `chat.py` therefore requested tool names that were never created, and
   grounding failed silently. Both functions now read `agents.*` and **raise** instead of falling
   back. Verified across all three scenarios: `accounts_agent`/`banking_policy_agent`,
   `product_agent`/`policy_agent`, `services_agent`/`care_policy_agent` - each matching what
   `create_agents.py` registers.
3. **Startup fails fast.** `resolve_scenario_path()` raises `RuntimeError: SCENARIO_PATH is
   required` rather than defaulting to `Path.cwd()`, which previously made a missing scenario look
   healthy.

### Q4. ACR script - RESOLVED, verdict stands unchanged

**Reuse `technical-patterns/.shared/build-and-push-acr.{ps1,sh}` with a parameterization delta.**
The shared script already implements the exact flow, including private-networking handling the
contribution's script lacks, and is already shaped for a two-App-Service topology. The delta lives in
the shared script, not in the new pattern: make the image name, build context, and Dockerfile
filename configurable instead of hardcoding `da-app` / `src/App` / `WebApp.Dockerfile` and `da-api` /
`src/api/python` / `ApiApp.Dockerfile`, and relax the app-name discovery prefixes and the
`python|dotnet` runtime validate-set. Do not stage the contribution's `build_push_images.{ps1,sh}` as
pattern-local scripts; that would fork a shared capability. Full detail in section 5.1.

### Q5. Observability placement - RESOLVED, follows from reviewer decision 2

**Log Analytics and Application Insights stay in the technical pattern's infra** (row 51). This is
no longer an open question. Because `agentic-apps` ships only Foundry account, Foundry Project, and
AI Search, observability has no core owner in this composition, so the reviewer's original direction
stands and the pattern provisions it. One-line note for the record: observability is normally
core-owned in the factory's layer boundary; this placement is a direct consequence of the
deliberately scoped core, not an accidental boundary violation. The mitigation (an
`enableObservability` parameter so the pattern can defer to a core that already ships it) is carried
as a risk in section 12.

**Revision-5 consequence.** Because observability is pattern-owned, the existing-Log-Analytics-workspace
branch excluded by decision 5b is a **pattern-layer** change, traced in section 7.5 - not a Stable
Core change. To be explicit: that decision removes the *bring-your-own branch only*. Both monitoring
modules stay staged under `TP/infra/bicep/modules/monitoring/`, both still deploy, and
`enableMonitoring` is retained with its existing semantics.

### Q6. UI genericization and the composition contract - RESOLVED by reviewer decision 2 (revision 4)

Not an open question. The full decided design - the copy-plus-environment contract, the API-served
config (Option A) with its mandatory response filtering, the single generic catalog app, the
rewritten `hostConfig.ts`, the `*Meta.ts` mechanism/data split, the `cardVariant` enum with its
explicitly rejected plugin-registry alternative, the published config schema with compose-time
validation, and the metadata wiring - is recorded in **section 6A**. The standing rule it
establishes (a scenario never carries code; a pattern gap is closed by adding a config-selected
option to the pattern) governs every future contribution to `chat-with-data-voice`.

## 14. Changelog

### 14.0 Revision 7a - post-approval staging corrections

**These are corrections, not scope changes.** Each was discovered while staging the approved plan or
during an external code review of the staged code, and is recorded here so the plan matches staged
reality. No layer assignment, no per-part verdict, and no fit-score dimension changes.

1. **Section 6A.1 build-context correction.** The Builder copies the composed scenario to
   `solutions/<slug>/src/api/scenario/`, inside the API Docker build context, so the Dockerfile's
   existing `COPY . .` places it at `/app/scenario`. `SCENARIO_PATH=/app/scenario` is set on the
   **API app only**; the web app's `SCENARIO_PATH` setting was removed. The copy must precede the
   image build.
2. **Loader consolidation (section 13, Q3).** Three duplicate manifest loaders became one
   `TP/src/api/scenario_loader.py` - under `src/api` because `scripts/` is outside the build
   context - with `@lru_cache(maxsize=1)` on `load_manifest()`.
3. **Tool-name bug fixed (section 13, Q3).** The catalog and policy tool-name accessors read a
   non-existent `catalog.toolName` key and silently returned placeholder names that
   `create_agents.py` never registered, breaking grounding without an error. They now read
   `agents.*` and raise.
4. **Fail-fast startup (section 13, Q3).** A missing `SCENARIO_PATH` now raises instead of
   defaulting to the current working directory.

### 14.1 Revision 7 vs. revision 6

**One reviewer decision - the sample scenario config is dropped (section 6A.7).**

1. **`TP/config/scenario-config.sample.json` removed everywhere it appeared.** It was never a
   numbered per-part row - it was one of section 5.2's *newly authored pattern artifacts* - so the
   removal touches section 5.2 (seven artifacts to **six**), section 6A.7 (the bullet that
   introduced it), section 6A.8's authoring estimate, the two section 7.3 rows that leaned on it as
   a mitigation, and two section 12 risk bullets. Nothing survives in the pattern's `config/` folder
   except the schema, and no README or metadata text promises standalone runnability any more.
2. **The schema and compose-time validation explicitly survive.** Section 6A.7 now states this in a
   four-row table so the plan cannot be misread as dropping validation too: the published
   `config/scenario-config.schema.json`, its `configSchema` entry in `scenarioExtensionPoints`
   (section 11.2, restated and untouched), and the `preflight_scenario` validation of every scenario
   `manifest.json` - including the section 6B.3 asset-path resolution check - are all kept. Only the
   sample *instance* is dropped.
3. **Precedent verified in this repository before it was written down**, and recorded in section
   6A.7: `technical-patterns/chat-with-data/` has exactly `infra/`, `scripts/`, `src/` and
   `README.md` at top level - **no `config/`, `samples/`, or `evals/` folder** and no sample
   dataset; and `scripts/shared/scenarios.py` resolves `industry-scenarios/scenarios.json`, printing
   a `scenarios.json not found` warning and returning an **empty registry** when it is absent, i.e.
   the pattern assumes a scenario is always composed. The two possible counter-examples were checked
   and rejected: `src/app/public/config/config.json` is UI layout config carrying call-center domain
   labels (`Total Calls`, `Average Handling Time`), and `src/app/src/configs/StaticData.tsx` is
   frontend mock data - neither is a smoke-test fixture.
4. **The consequence is recorded honestly, not buried.** Section 12 gains a **prominent** risk row:
   with `tests/e2e-test/` out of scope and no sample fixture, the technical pattern ships **no
   executable validation whatsoever** and cannot be deployed meaningfully without a composed
   scenario - the catalog renders empty and no agents exist, because agent creation reads
   `agents/*.txt` from the scenario. The same statement appears in the header block, in section
   6A.7, and in the section 7.3 `tests/e2e-test/**` row, whose risk rating rises to Medium-High.
5. **Fit reconfirmation re-run honestly, and the total moved for the first time since revision 4:
   25/35 to 24/35.** **Workflow execution fit 4 to 3.** Revision 4's raise rested partly on *"the
   first executable validation ships"*; that justification is gone, so it was deleted rather than
   reworded, and the dimension was re-scored from the rubric on the merits (the workflow `Must`
   `Requires customization` - score-3 rule, first match). The other six dimensions were re-checked
   and did not move, and section 2 records why for each. **Band unchanged: Proceed with scoped
   conditions (18-27).** The `evals/` scoped condition is hardened, because it is now the only
   validation route left.
6. **The deferred idea is logged as an open question, not a deliverable** (section 12): a minimal
   sample scenario - a few generic catalog rows, one or two policy documents, domain-neutral agent
   instructions - should be raised as a **factory-wide convention** so `chat-with-data` adopts it
   too, rather than this pattern being the only one with such a folder.

**Preserved unchanged from revision 6.**

7. **Everything else stands** - the section 6 router merge, the section 6A UI genericization minus
   the sample config, the section 6B localized image assets with their seven mandatory security
   controls, the section 7.1 cart trace, both BYO removal traces (sections 7.4 and 7.5), the section
   4.8 import rewrites, the accepted Terraform deviation, row 28a, and every security flag including
   the `GET /api/scenario/config` four-key allow-list and the asset-route containment check.

**Housekeeping.**

8. **Roll-up counts refreshed** (section 15) and **unchanged**: 83 numbered rows, New **43**, Delta
   **1**, Matched **0**, Out of scope **39** - because the dropped artifact corresponds to no source
   path and therefore carried no row. The only count that changes is the newly-authored-artifact
   count, seven to **six**. The per-part table was re-verified **exhaustive and mutually exclusive**,
   with the same three intentional two-layer split rows (41, 42a, 44a).

### 14.2 Revision 6 vs. revision 5

**One reviewer decision - all scenario image assets are localized and API-served (section 6B).**

1. **New section 6B in six subsections.** 6B.1 records the verified problem (three conventions, two
   sources of truth, one dead column); 6B.2 the decided target design (CSV column is the single
   source of truth, scenario-relative paths, the asset route, the tolerant `http(s)://` pass-through
   rule, and the explicit *path string never bytes* statement for Cosmos); 6B.3 the asset moves and
   their reconciliation with the existing rows; 6B.4 the seven mandatory security controls; 6B.5 the
   deferred blob-plus-CDN production path with its concrete reason; 6B.6 the rejected raw-GitHub-URL
   alternative with both variants' failure modes.
2. **Every 6B.1 claim verified before it was written.** Retail: 16 of 16 rows on the absolute
   `raw.githubusercontent.com` form, 0 in any other form, 16 distinct filenames. Banking and
   healthcare: 8 root-relative `/banking/*.svg` and 8 `/healthcare/*.svg`, resolving from
   `scenario-app/frontend/public/{banking,healthcare}/` (16 SVGs, 8,389 B). **The dead-column
   finding is confirmed for healthcare as well as banking** - `HealthcareServiceCard.tsx` renders
   `src={meta.image}` at line 53, exactly like `BankingProductCard.tsx`, and only retail's
   `FigmaProductCard.tsx` uses `src={product.image}` (line 15). Refined with precision: the resolver
   consults the CSV only in its *fallback* branch, and every shipped row hits the hardcoded `id`
   lookup first, so the column is dead for **8 of 8 banking and 8 of 8 healthcare rows** as shipped.
3. **Section 6A.5 amended in place, not contradicted.** The `image` key is removed from the
   `presentation` map, `presentation.assetPrefix` is deleted outright (the prefix guard has nothing
   left to guard), the example JSON block is rewritten, and the revision-4 sentence *"the Builder
   copies them into the app's public root at compose time"* is **withdrawn** as a compose-time patch
   that contradicted section 6A.1 and section 6A.2. Section 11.2's `presentation.*` extension-point
   list is updated to match.
4. **Rows 42b and 44b extended in place - no duplicate rows.** Destination flattens from
   `assets/banking/` and `assets/healthcare/` to plain `assets/`, and delivery moves from the
   withdrawn Builder copy to `GET /api/scenario/assets/{path}`.
5. **The `Color Images` reconciliation is narrower than the request assumed, and is recorded as
   such.** The 16 JPGs were **never out of scope**: row 62's MD5 duplicate finding covers only the
   `policies/` and `products/` subfolders it names, and `Color Images/` has always been row **63**
   with outcome **New**. Re-verified that `scenarios/ecommerce/data/` holds no image file of any
   kind, so the JPGs are unique to `Color Images/`. **The adjustment applied is to row 63's
   destination only** (`unstructured_data/images/` to `assets/`), plus a precision note appended to
   row 62. No out-of-scope row flips.
6. **Brand icons corrected in two places, after confirming actual usage.** `contoso-icon.png` is
   declared as `host.iconPath` in **all three** manifests and hardcoded in `AppHeader.tsx` in both
   apps; `contoso-ai-icon.png` is the assistant avatar hardcoded in `EnhancedChatPanel.tsx` in both
   apps (lines 817, 848) and declared in **no** manifest. Both are byte-identical across apps
   (749 B, 1290 B). Row 30 therefore now stages both into **all three** scenarios rather than retail
   alone, and row 41 pulls `contoso-ai-icon.png` **out of the pattern** (row 38), where it would
   have left Contoso branding inside the "scenario-free" image. All three manifests gain a new
   **`host.assistantIconPath`** key.
7. **The three-CSV `image` rewrite is recorded as a required decomposition action**, not optional,
   in rows 42b, 44b, 63, 67, 68, 69 and section 6B.3, with `preflight_scenario` extended to fail
   compose on any `image` value that is neither absolute nor resolvable under `assets/`.
8. **Section 12 gains a security-requirement block** for the asset route (the seven section 6B.4
   controls, including *reject rather than clamp*, the image-only extension allow-list,
   `Cache-Control`, and `nosniff` plus a locked-down CSP for SVG) and an interdependency risk bullet
   for the three-part change. A revision-6 risk-bookkeeping block records that nothing was retired.
9. **Row 68 corrected.** Retail's `presentation` block no longer carries images; it authors
   `highlights` plus a `defaultImage`, and the image comes from the rewritten CSV column.

**Preserved unchanged from revision 5.**

10. **Every revision-5 decision stands** - decision 5a (`existing-project-setup.bicep` and its 17
    companions Out of scope, row 50a, row 52a, section 7.4) and decision 5b (the existing Log
    Analytics workspace branch and its 8 companions Out of scope, section 7.5) - together with the
    section 6 router merge, all of section 6A's decision-2 design, the section 7.1 cart trace, the
    section 4.8 import rewrites, the accepted Terraform deviation, row 28a, and every security flag
    including the `GET /api/scenario/config` four-key allow-list.

**Housekeeping.**

11. **Fit score re-run honestly, dimension by dimension: 25/35, unchanged**, band unchanged
    (Proceed with scoped conditions). No dimension moved, and section 2 now states **why** rather
    than leaving a flat total to look like a skipped re-run: revision 6 improves Data alignment,
    Architecture fit and Connectivity fit on the merits, but each is already pinned by a
    lower-scoring condition revision 6 does not touch (the missing evals, the unmet Terraform
    `Must`, the two BYO removals), and the rubric's *first matching rule* semantics mean an
    improvement above the pinning condition cannot raise the score. Connectivity fit was
    specifically **not** raised to 4 despite the removal of the external-network dependency.
12. **Roll-up counts refreshed** (section 15): still **83 numbered rows**, New **43**, Delta **1**,
    Matched **0**, Out of scope **39** - all unchanged, because revision 6 amends existing rows (30,
    35, 38, 40, 41, 42b, 44b, 62, 63, 67, 68, 69) and adds none. Table re-verified exhaustive and
    mutually exclusive, with the same three intentional two-layer split rows (41, 42a, 44a).

### 14.3 Revision 5 vs. revision 4

**Decision 5a - `existing-project-setup.bicep` skip RESTORED (this reverses revision 4 decision 1).**

1. **Row 50a flipped back from a staged New Stable Core row to Out of scope.** The bring-your-own /
   reuse-an-existing-Foundry-project path is excluded **to reduce complexity**; `agentic-apps`
   provisions Foundry **greenfield only**. This is a straight reversal of revision 4 decision 1 and
   a restoration of the revision-3 position.
2. **Section 7.4 flipped from a retention record back to a 17-item removal trace**, with every line
   reference re-verified against the contribution: core `main.bicep` param (145), the
   `useExistingAIProject` var (175), the four ternary vars (177-180), the
   `if (!useExistingAIProject)` guard (264), the `module existing_project_setup` block (273-280),
   the six branch-selection ternaries (282-287), and the two `scope:` expressions on
   `model_deployments` (292) and `foundry_search_connection` (324) - the last **collapsed, not
   deleted**, because both modules still need a scope. Then, in the pattern:
   `role-assignments.bicep`'s two params (15, 18), the three `split()` vars (56-58), the two
   `cross-scope-role-assignment.bicep` module blocks (117, 140), the four `!useExistingAIProject &&`
   condition prefixes (106, 129, 220, 231), and the three `role_assignments` params in
   `TP/infra/bicep/main.bicep` (642-644), with line 644 **collapsing to a direct assignment**.
3. **Row 52a flipped back to Out of scope.** `cross-scope-role-assignment.bicep` is orphaned again -
   its only two callers are removed by items 14 and 15. Section 9's pattern module count goes back
   from eight to **seven**.
4. **The greenfield-only limitation is restored** in sections 3, 7.4, 8, 11.2 and 12, replacing
   revision 4's positive BYO capability statement. `existing-foundry-project-reuse` is removed from
   `SC/metadata.yaml` `capabilities`, and `existingFoundryProjectResourceId` is removed from the
   core parameter surface and from `extensionPoints`.
5. **The dangling-module-reference risk row is restored** to section 12, now covering both BYO
   removals, and revision 4's *"Risks retired in revision 4"* block is deleted as cancelled.
6. **The revision-4 cross-layer `split()` gap note is DELETED**, along with its *"core emits six
   identifiers"* fix and the `aiFoundryResourceId` double-assign caveat. `role-assignments.bicep`
   lines 56-58 are now removed wholesale, so the finding is moot. Section 8's output list is
   rewritten to plain greenfield values with no `useExistingAIProject`, no `aiFoundrySubscriptionId`
   and no `aiFoundryResourceGroupName`. **No contradictory instruction about line 644 survives** -
   the only guidance is item 17's collapse to a direct assignment.
7. **Sections 8, 9, 11.2 and the no-action reference list restored to revision-3 substance.**
   `ReuseFoundryProject.md` is dropped rather than rewritten into `SC/README.md` (row 73);
   `validate_bicep_params.py`'s `AZURE_EXISTING_AIPROJECT_RESOURCE_ID` exception simply disappears
   and must not be re-added to the pattern preflight (row 64); `main.parameters.json`'s
   `${AZURE_EXISTING_AIPROJECT_RESOURCE_ID}` entry is not re-expressed anywhere (row 55).

**Decision 5b - the existing Log Analytics workspace branch EXCLUDED (new).**

8. **New section 7.5** locates and confirms the branch (no assumptions carried from the request):
   `param existingLogAnalyticsWorkspaceId` at `infra/bicep/main.bicep` line 142,
   `var useExistingLogAnalytics` at line 174, the conditional
   `module log_analytics ... = if (enableMonitoring && !useExistingLogAnalytics)` at line 237, and
   the selection ternary at lines 246-248 feeding `workspaceResourceId` at line 255. There is **no**
   separate BYO module and **no** `existing` resource declaration.
9. **Numbered 8-item companion removal**, in its own subsection, covering the parameter, the flag,
   the module condition (**simplified, not deleted**), the ternary (**inner branch collapsed only**),
   the surviving consumer line, `main.parameters.json` lines 35-37 / `main.waf.parameters.json`
   lines 38-40, all five `.github/workflows/*.yml` files plumbing
   `AZURE_ENV_EXISTING_LOG_ANALYTICS_WORKSPACE_RID`, and `ReuseLogAnalytics.md` /
   `CustomizingAzdParameters.md` line 24 / `DeploymentGuide.md` line 276. `azure.yaml` verified to
   contain **no** reference.
10. **Unambiguous distinction recorded** in sections 3, 7.3, 7.5, 9, 11.2, 12 and 13 Q5: this
    removes the **BYO branch**, not the workspace. The pattern still provisions Log Analytics and
    Application Insights **greenfield** on every deployment, both modules stay staged under row 51,
    and `enableMonitoring` is retained unchanged.
11. **Newly orphaned modules: none from 5b.** `log-analytics.bicep` keeps its caller and
    `app-insights.bicep` is untouched. A dangling-reference risk row is still added for the
    incomplete-application failure mode. (Decision 5a *does* orphan one module - row 52a.)
12. **Lost capability recorded** - cannot attach to a customer's pre-existing central Log Analytics
    workspace - as a documented limitation in `TP/README.md` / `TP/metadata.yaml` with a plausible,
    strictly additive future enhancement.
13. **Survey only, no action:** every parameter in the vanilla `infra/bicep/main.bicep` was
    enumerated. **Exactly two BYO/reuse branches exist** - `existingFoundryProjectResourceId` and
    `existingLogAnalyticsWorkspaceId`. There is **no** BYO parameter for Application Insights, App
    Service Plan, ACR, Cosmos DB, AI Search, or VNet/subnet. `enableMonitoring` is called out as a
    feature toggle, not a third BYO branch. Left as an open question for the reviewer; nothing acted
    on.

**Preserved unchanged from revision 4.**

14. **All of decision 2** - the copy-plus-environment composition contract, section 6A and all eight
    subsections, API-served config with four-key allow-list filtering, the generic catalog app, the
    rewritten `hostConfig.ts`, the `*Meta.ts` mechanism/data split, the `cardVariant` enum plus the
    rejected plugin registry and the standing *"a scenario never carries code"* rule, the config
    schema and compose-time validation, and the metadata wiring. Also preserved: the section 6
    router merge, the section 7.1 cart trace, the section 4.8 import rewrites, the accepted
    Terraform deviation, row 28a, and every security flag.

**Housekeeping.**

15. **Fit score re-run honestly: 26/35 to 25/35**, band unchanged (Proceed with scoped conditions).
    Connectivity fit 5 to **3** - both reuse paths are gone, which is one step below revision 3's 4,
    since revision 3 still had the Log Analytics path. Customization effort 2 to **3** - the two BYO
    surfaces and the revision-4 identifier-flow fix are all removed work. Architecture fit stays 3
    (better reason: no cross-layer leak survives; still capped by the unmet Terraform `Must`). Time
    to value stays 3 - the UI genericization, not the BYO plumbing, is the critical path. Problem
    alignment 5, Data alignment 4, Workflow execution fit 4 unchanged. No dimension scored 1, so no
    halt flag.
16. **Roll-up counts refreshed** (section 15): still **83 numbered rows** - decision 5b adds no new
    source-path row, because its whole surface sits inside rows 53, 55, 3 and 73. New 45 to **43**
    (rows 50a and 52a flip out); Out of scope 37 to **39**. Delta 1 and Matched 0 unchanged. Table
    re-verified exhaustive and mutually exclusive, with the same three intentional two-layer split
    rows (41, 42a, 44a).

### 14.4 Revision 4 vs. revision 3

**Decision 1 - `existing-project-setup.bicep` skip REVERSED.** *(Historical record only. Items 1-8 below were themselves **reversed by revision 5 decision 5a** - see 14.2 and section 7.4. Nothing in this block is an instruction to the classifier.)*

1. **Row 50a flipped from Out of scope to a staged New Stable Core row.** The module is the
   bring-your-own / reuse-an-existing-Foundry-project path, and the core owns Foundry project
   provisioning. Staged to `SC/infra/bicep/modules/ai/`.
2. **All 17 companion items are retained as-is, not removed** - the core `main.bicep` param
   `useExistingAIProject` plumbing, the four ternary vars, the `if (!useExistingAIProject)` guard,
   the module block, the six output ternaries, the two module scopes; and in the pattern,
   `role-assignments.bicep`'s params, vars, two cross-scope module blocks, and four conditions, plus
   the three `role_assignments` params in the pattern `main.bicep`.
3. **Section 7.4 rewritten** from a removal trace into a *"retained - BYO project supported"*
   record. No removal instructions remain anywhere in the plan.
4. **Row 52a flipped from Out of scope to a staged New Technical Pattern row.**
   `cross-scope-role-assignment.bicep` has two live callers again, so it is no longer orphaned.
   Section 9's pattern module count goes from seven to **eight**.
5. **Greenfield-only limitation removed** from sections 7.4, 8 and 12, replaced by a positive
   capability statement: `agentic-apps` supports **both greenfield provisioning and reuse of an
   existing Foundry project**, gated by `useExistingAIProject`.
6. **Two risk rows deleted** - the dangling-module-reference risk and the lost-BYO-capability risk -
   and explicitly listed under *"Risks retired in revision 4"* so the reviewer can see they were
   retired, not dropped.
7. **Cross-layer implication verified and recorded (section 7.4).** The core must emit
   `useExistingAIProject`, `aiFoundryName`, `aiFoundrySubscriptionId`, `aiFoundryResourceGroupName`,
   `aiFoundryResourceId`, and `aiProjectPrincipalId` as outputs, and the pattern must declare them
   as parameters. **Gap found:** `role-assignments.bicep` lines 56-58 currently re-derive the first
   three by string-splitting the raw resource id inside the pattern layer. Fix recorded in row 52
   and carried as a risk. The deliberate `aiFoundryResourceId: !useExistingAIProject ? ... : ''`
   blanking at line 644 must be preserved.
8. **No-action reference list re-checked, not copied.** Rows 3, 47, 55, 64, 66 and 73 were re-read
   in light of the reversal: `main.parameters.json`'s `AZURE_EXISTING_AIPROJECT_RESOURCE_ID` entry is
   now genuinely re-expressed as a core parameter, `validate_bicep_params.py` is *superseded* by the
   pattern preflight rather than merely dropped, and `ReuseFoundryProject.md` documents a shipped
   capability so its content must be rewritten into `SC/README.md`. Sections 8 and 11.2 updated to
   restore the `existing-foundry-project-reuse` capability and the BYO extension point.

**Decision 2 - UI genericization and the composition contract, recorded as decided.** *(Preserved unchanged by revision 5 - items 9-16 below all still stand.)*

9. **New section 6A** carries the whole decided design in eight subsections: the
   copy-plus-environment composition contract (6A.1), API-served scenario config with mandatory
   response filtering (6A.2), the single generic catalog app (6A.3), the rewritten `hostConfig.ts`
   (6A.4), the `*Meta.ts` mechanism/data split (6A.5), the `cardVariant` enum with its rejected
   alternative and the standing "a scenario never carries code" rule (6A.6), the config schema plus
   compose-time validation (6A.7), and the net effect on the pattern (6A.8). Recorded as **decided**,
   and mirrored as resolved decision **Q6**.
10. **`SCENARIO_PATH` aligned with, not duplicated over, the three `scenario_loader.py` fixes.**
    Section 13 Q3 fix 1 is restated as the same change as contract step 3; fixes 2 and 3 are
    unchanged. Row 12 and row 70 updated to match.
11. **Three front ends collapsed into one.** Rows 42, 43 and 44 become **Out of scope
    (superseded)**; the entire `src/scenarios/{banking,ecommerce,healthcare}/` tree leaves the
    pattern. New rows **42a** and **44a** carry the `*Meta.ts` mechanism/data split (two-layer
    splits); new rows **42b** and **44b** carry the SVG brand assets to their scenarios. Rows 39 and
    40 rewritten for the generic render path and the generic `hostConfig.ts`.
12. **Section 6's `catalog` block extended, not replaced** - `cardVariant` and `copy.intro` /
    `copy.loadError` added to the existing table. Section 11.2 rewritten as full metadata wiring
    covering `host`, `welcome`, `catalog`, `presentation`, `cardVariant`, the published
    `configSchema`, `domainAssets`, and two new `requiredPatternCapabilities`.
13. **New row 28a - `public/config.js` skipped in both frontends**, with the zero-reader claim
    verified and a security note. Pulled out of rows 28 and 38.
14. **Section 12 gains a security requirement block** for the `GET /api/scenario/config` allow-list,
    and the secrets flag is extended from two files to three.
15. **Section 7.1's cart trace preserved in full**, with a revision-4 note recording that decision 2c
    makes the frontend companion removals (items 11-13) automatic rather than surgical.
16. **Section 7.2 gains two rows** - the two `config.js` copies, and `lib/data.ts`'s no-op
    `filterProducts`/`sortProducts`, which lose their only caller with row 43.

**Housekeeping.**

17. **Fit score re-run: 25/35 to 26/35**, band unchanged (Proceed with scoped conditions).
    Architecture fit 2 to 3 and Connectivity fit 4 to 5 (capability restored, domain vocabulary
    gone); Workflow execution fit 3 to 4 (first executable validation ships); Customization effort
    3 to 2 and Time to value 4 to 3 (the UI genericization is real, front-loaded authoring). No
    dimension scored 1, so no halt flag.
18. **Roll-up counts refreshed** (section 15): 83 numbered rows (78 plus 28a, 42a, 42b, 44a, 44b);
    New 45 distinct rows, Delta 1, Matched 0, Out of scope 37. Table re-verified exhaustive and
    mutually exclusive, with three intentional two-layer split rows (41, 42a, 44a).

### 14.5 Revision 3 vs. revision 2

1. **Terraform deferred - Bicep only (reviewer decision 1).** Both *generated Terraform* entries
   are removed: the `agentic-apps` Stable Core one (section 8) and the `chat-with-data-voice`
   Technical Pattern one (section 9). No `infra/terraform/` tree is staged, and no generated-flavor
   entry survives in the per-part table or the roll-up counts. Both infra-bearing layers keep the
   canonical per-flavor path `infra/bicep/` with `main.bicep` + `modules/` so a Terraform flavor can
   be added later without restructuring - nothing flattened, nothing moved up to `infra/`.
2. **The deviation is recorded, not hidden.** Section 12 gains an **Accepted deviation - Terraform
   out of scope** block stating the Composition Readiness rule, the reviewer's conscious scoping
   decision, and the concrete consequence (the staged components are not Terraform-composable, so a
   Planner/Builder run selecting the Terraform flavor cannot consume them). Logged as follow-up
   work, **not a blocker**. The old *"Two Terraform flavors must be authored"* risk bullet is
   deleted as superseded.
3. **Metadata and READMEs must claim Bicep only.** Sections 8, 9 and 11.2 now require
   `deployment` / `compatibility.iac` and each `infra/README.md` to record **supported IaC flavors:
   Bicep only** rather than claiming both.
4. **`existing-project-setup.bicep` skipped (reviewer decision 2).** *(Reversed in revision 4 -
   see 14.2.)* Confirmed at `infra/bicep/modules/ai/existing-project-setup.bicep`. It moved out of
   row 50 into a new explicit **Out of scope** row **50a**. It was **not** in the revision-2 list of
   19 unreferenced Bicep modules (row 54) - it is genuinely referenced - so it was a new skip, not a
   double count.
5. **New section 7.4** traced the reference (`infra/bicep/main.bicep` line 273, gated on
   `useExistingAIProject`), listed the **17 companion removals**, and named the references that
   needed no action. *(Rewritten in revision 4 as a retention record.)*
6. **New row 52a** - `cross-scope-role-assignment.bicep` orphaned by the skip and moved out of row
   52 to its own **Out of scope** row. *(Reversed in revision 4.)*
7. **Two new risks in section 12** - a dangling-module-reference risk and the greenfield-only
   capability loss. *(Both retired in revision 4.)*
8. **Rows 50, 52, 53 and 55 updated** for both decisions; sections 3, 5.2, 8, 9, 11.2 updated for
   Bicep-only staging.
9. **Fit score re-run: 24/35 to 25/35**, band unchanged (Proceed with scoped conditions).
   Architecture and constraints fit 3 to 2 (a Composition Readiness `Must` is now knowingly unmet);
   Customization effort 2 to 3 and Time to value 3 to 4 (two Terraform trees and the BYO plumbing
   no longer have to be authored). No dimension scored 1, so no halt flag.
10. **Roll-up counts refreshed** (section 15): 78 numbered rows, Out of scope 33 to 35, New
    unchanged at 43 once the two withdrawn generated-flavor entries are removed.

### 14.6 Revision 2 vs. revision 1

1. **Base branch `dev` changed to `main`** throughout. Verified `dev` does not exist; `main` exists
   at `f3e56db5` with all three layer roots present. Recorded in section 1 for the promoter and
   restated in the closing note.
2. **Stable Core outcome changed from Matched to New.** `stable-cores/agentic-apps/` is now staged
   from row 50 with the full Stable Core contract (canonical shape, both flavors, generated
   Terraform flagged, `metadata.yaml`, `README.md`, `scripts/`). Sections 3, 5.2, 8, 10, 11
   rewritten.
3. **All proposed `microsoft-iq` modifications removed.** The Fabric-capacity-toggle delta is
   withdrawn; section 5.1 now contains exactly one Delta (the ACR script). `microsoft-iq` survives
   only as the recorded overlap note in section 5.3.
4. **Scenario names locked** - `banking-customer-support` (fsi), `retail-customer-support` (rcg),
   `healthcare-patient-support` (hls). The revision-1 naming discussion is deleted.
5. **Pattern source layout collapsed** - every `TP/src/api/app/...` path became `TP/src/api/...`
   across rows 10-15, 19, 20, 32, 34-36. New section 4.8 enumerates the forced import and entrypoint
   rewrites (relative imports, the dual try-except import pairs, `uvicorn app.main:app` to
   `uvicorn main:app`, Dockerfile build context).
6. **Three catalog routers verified and merged** - new section 6 with the endpoint inventory, the
   equivalence proof, the generic `catalog.py` design, and the scenario `manifest.json` /
   `metadata.yaml` keys carrying the per-industry differences.
7. **`tests/e2e-test/` moved to Out of scope** (rows 74, 75, 76). Row 75 previously staged into
   `retail-customer-support/evals/`; that destination is removed.
8. **`cart.py` skipped**, with the reachability trace, the "cart is write-only" finding, and the
   13-item companion-removal list in section 7.1, plus a prominent risk row in section 12. Rows 33,
   34, 40, 43 updated accordingly.
9. **Observability moved from Matched-against-core to pattern-owned** (row 51); Q5 changed from an
   open question to a resolved decision.
10. **The `products.py` write surface (`POST`/`PUT`/`DELETE`) added as an explicit skip** in section
    7.2, surfaced by the section 6 router analysis.
11. **Fit score re-run: 26/35 to 24/35**, band unchanged (Proceed with scoped conditions).
    Customization effort 3 to 2 (second core plus second Terraform flavor); Workflow execution fit 4
    to 3 (no validation ships at all after decision 6).
12. **Roll-up counts refreshed** (section 15); the per-part table re-checked for exhaustiveness and
    mutual exclusivity - all 76 rows accounted for, row 41 the only intentional two-layer split.

## 15. Roll-up counts

| Layer | New | Delta/Upgrade | Matched | Out of scope |
|---|---|---|---|---|
| Stable Core | 1 row (50) | 0 | 0 | 0 |
| Technical Pattern | 35 rows | 1 (row 56) | 0 | 0 |
| Industry Scenario | 10 rows (across 3 scenarios) | 0 | 0 | - |
| Cross-cutting skill | 0 | 0 | 0 | - |
| Out of scope / Solution-only | - | - | - | 39 rows |
| **Total** | **43 distinct rows** | **1** | **0** | **39** |

* **83 numbered rows**, unchanged from revision 4 - the 78 of revision 3 plus **28a**
  (`public/config.js` in both frontends), **42a** / **44a** (the two `*Meta.ts` mechanism/data
  splits), and **42b** / **44b** (the two SVG asset sets). **Decision 5b adds no row**, because its
  entire surface lives inside existing rows: the parameter, flag, module condition and ternary are
  in `infra/bicep/main.bicep` (row 53); the azd parameter files are row 55; the workflows are row 3;
  the docs are row 73.
* **Distinct-row arithmetic.** The per-layer New column sums to 46 layer entries (1 + 35 + 10), but
  **three rows are intentional two-layer splits** - row 41 (`pcm-processor.js` to the pattern,
  `contoso-icon.png` to retail), row 42a, and row 44a (resolver to the pattern, presentation data to
  the scenario). Subtracting those three gives **43 distinct New rows**. Check:
  43 + 1 + 0 + 39 = **83**, matching the row count exactly.
* **Movement from revision 4.** New 45 to 43: `-1` (row 50a back to Out of scope, decision 5a),
  `-1` (row 52a back to Out of scope, orphaned by decision 5a). Out of scope 37 to 39: `+2` for the
  same two rows. Delta and Matched unchanged. This restores exactly the revision-3 distribution.
* **Revision 6 changes no count.** It amends twelve existing rows (30, 35, 38, 40, 41, 42b, 44b, 62,
  63, 67, 68, 69) and adds none: rows 42b and 44b are extended in place rather than duplicated, and
  row 63 keeps its **New** outcome with only its destination corrected. Because the 16 `Color Images`
  JPGs were never covered by row 62's duplicate finding, **no row moves between New and Out of
  scope** - the distribution is identical to revision 5. The two Contoso PNGs of rows 30 and 41 now
  stage into all three scenarios, which increases the *staged file* count (38 files from 20 distinct
  sources, section 6B.3) without changing the *row* count; row 41 remains one of the three
  intentional two-layer splits.
* **Revision 7 changes no count either.** The dropped `scenario-config.sample.json` was never a
  numbered row - it was one of section 5.2's newly authored artifacts, which correspond to no source
  path. New **43**, Delta **1**, Matched **0**, Out of scope **39**, 83 rows: all identical to
  revision 6, and no row moves between New and Out of scope. The only count that moves is the
  newly-authored-artifact count, **seven to six**.
* **No generated-flavor entries remain.** Revision 2's two *generated Terraform* entries stay
  withdrawn (reviewer decision 1), so the New column counts table rows only. The **six** newly
  authored pattern artifacts of section 5.2 also carry no row, because they correspond to no source
  path; they are inventoried in the comparison report instead.
* The table is re-verified **exhaustive and mutually exclusive** over the whole contribution: every
  path under `C:\GSAs\OG\customer-chatbot-solution-accelerator` appears in exactly one row, no path
  is staged under two layers except the three deliberate splits above, and nothing is dropped
  silently. Rows 50a and 52a are Out of scope by **reviewer decision**, and are counted separately
  from row 54's 19 modules that are Out of scope by **unreachability** - no double count.
* **Percentage New or Delta, excluding out-of-scope:** 44 of 44 in-scope parts = **100%** (nothing
  is Matched). Per layer: Stable Core 100%, Technical Pattern 100%, Industry Scenario 100%.
  Unchanged across revisions 2 through 7 - the reversals, supersessions and removals moved rows
  between New and Out of scope without introducing a single Matched part.
* Excluded from the percentage: 39 Out-of-scope rows. Unclassified: 0.

---

> _**Promotion note (revision 7):** the promoter's pre-PR IaC validation covers **Bicep only** -
> `az bicep build` on `stable-cores/agentic-apps/infra/bicep/main.bicep` and on
> `technical-patterns/chat-with-data-voice/infra/bicep/main.bicep`. Both must build clean **with
> both BYO branches fully removed**, which means `existing-project-setup.bicep` and
> `cross-scope-role-assignment.bicep` must be **absent** from the staged module folders (section
> 7.4), while `log-analytics.bicep` and `app-insights.bicep` must be **present** and still invoked
> (section 7.5) - the pattern provisions observability greenfield. The comparison report must show:
> the two collapsed `scope:` expressions and the collapsed `aiFoundryResourceId` assignment
> (section 7.4 items 10 and 17); the simplified `if (enableMonitoring)` module condition and the
> collapsed `logAnalyticsWorkspaceResourceId` ternary (section 7.5 items 3 and 4); the
> `GET /api/scenario/config` serializer's four-key allow-list (section 12); the
> `GET /api/scenario/assets/{path}` handler's traversal rejection, canonical containment check and
> image-only extension allow-list (section 6B.4); the three rewritten `catalog.csv` `image` columns
> and the three scenario `assets/` folders (section 6B.3); the generic catalog
> app rendering all three `cardVariant` values; and that the pattern's `config/` folder contains
> **`scenario-config.schema.json` and nothing else** - no `scenario-config.sample.json`, which
> revision 7 dropped, while the `preflight_scenario` validation against that schema must still be
> present (section 6A.7). There is no Terraform to validate, by accepted
> deviation (section 12); `python metadata/validate.py` and the catalog/README registration checks
> are unaffected._

> _Nothing has been staged or written to the live layers. `stable-cores/`,
> `technical-patterns/`, and `industry-scenarios/` were read for comparison only. Explicit
> human approval of this exact revised plan is required before any classifier is dispatched.
> After the split is staged, the **FDE Split Comparison Reporter** produces
> `comparison-report.md` (the promotion plan) for the second review gate, and the **FDE Split
> Promoter** branches from **`main`** and raises the PR to **`main`**._
