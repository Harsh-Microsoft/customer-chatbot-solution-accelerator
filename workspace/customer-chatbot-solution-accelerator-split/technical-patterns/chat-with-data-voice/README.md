---
title: Chat with Data Voice
description: Technical pattern for a generic catalog chat application with optional real-time voice, scenario-configured UI, and scenario-served assets.
---

## Overview

Chat with Data Voice is a reusable technical pattern for a conversational catalog experience. It provides the generic web application, API surface, asset-serving contract, and post-provision automation that an industry scenario supplies with domain configuration and data.

## What It Includes

* A generic catalog UI with a configurable card layout.
* A scenario config API that exposes only the browser-safe manifest surface.
* A scenario asset API that serves local scenario files with traversal controls.
* Application infrastructure for the pattern's API and web app.
* Post-provision scripts for agent creation, data loading, and scenario bootstrap.

## Composition

This pattern is designed to compose with [agentic-apps](../../stable-cores/agentic-apps/README.md).

### Required Core Capabilities

* `ai-foundry-account`
* `ai-foundry-project`
* `ai-model-deployment`
* `ai-realtime-model-deployment`
* `ai-search`

### Scenario Extension Points

* `host.appTitle`
* `host.iconPath`
* `host.widgetTheme`
* `host.complianceBanner`
* `host.assistantIconPath`
* `welcome.title`
* `welcome.subtitle`
* `welcome.hint`
* `catalog.routePrefix`
* `catalog.itemSingular`
* `catalog.itemPlural`
* `catalog.cardSchema`
* `catalog.enabledEndpoints`
* `catalog.cardVariant`
* `catalog.copy`
* `presentation.defaultImage`
* `presentation.items`
* `presentation.titleAliases`
* `configSchema`
* `SCENARIO_PATH`

## Limitations

* Bicep only in this split; Terraform support is deferred.
* The pattern provisions a new Log Analytics workspace and Application Insights component on every deployment.
* No standalone sample config or evaluation dataset ships in this staging slice.
* Scenario-specific values must be supplied through the manifest and its assets, not hardcoded into pattern code.

## Interfaces

* `src/app` - generic catalog web application.
* `src/api` - FastAPI surface for catalog, config, and scenario assets.
* `scripts` - post-provision automation and loaders.
* `infra/bicep` - application hosting and app-specific resources.

## Notes

The ACR build-and-push delta is staged as a documentation-only dependency on the shared helper at `technical-patterns/.shared/build-and-push-acr.ps1`; this pattern does not fork that script.
