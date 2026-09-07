---
title: Infrastructure
description: App hosting and app-specific resources for the chat-with-data-voice technical pattern.
---

## Infrastructure

This split stages the pattern's application infrastructure in Bicep only. The pattern owns the API and web app hosting, the application registry, Cosmos DB, role assignments, and greenfield observability resources.

## Notes

* Bicep only in this staging slice.
* Terraform support is deferred.
* Log Analytics and Application Insights are retained and provisioned greenfield.
* The existing-workspace branch is intentionally excluded.
