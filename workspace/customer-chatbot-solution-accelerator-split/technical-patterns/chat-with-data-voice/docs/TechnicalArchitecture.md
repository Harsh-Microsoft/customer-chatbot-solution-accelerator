---
title: Technical Architecture
description: Overview of the generic catalog chat pattern, its config surface, and its guarded asset route.
---

## Architecture

Chat with Data Voice exposes a generic catalog UI, a catalog API, and a scenario config API. The browser receives only the safe manifest subset and the frontend stays scenario-free; scenario assets are resolved on demand through the API with containment checks.

## Extension Points

* Host copy and branding.
* Welcome copy.
* Catalog route and presentation schema.
* Card layout selection through `cardVariant`.
* Scenario assets and presentation mappings.

## Composition Notes

* Compose with the `agentic-apps` stable core.
* Keep scenario values in the composed manifest and asset folder.
* Do not hardcode domain values, search index names, or data paths in pattern code.
* The pattern provisions its own app infrastructure, Log Analytics, and Application Insights in Bicep.
