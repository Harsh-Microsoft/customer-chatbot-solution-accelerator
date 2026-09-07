---
title: Scripts
description: Post-provision automation for agent creation, data loading, and scenario bootstrap.
---

## Scripts

This folder contains the mechanism that consumes a composed scenario at deployment time.

* `scripts/agents` creates the connected agents from the scenario manifest and instruction files.
* `scripts/data` loads scenario catalog rows and policy documents into the backing store and search indexes.
* `scripts/shared/scenario_loader.py` resolves the composed scenario folder through `SCENARIO_PATH`.

## ACR Delta Note

The build-and-push behavior is staged as a delta against the shared helper at `technical-patterns/.shared/build-and-push-acr.ps1` and `technical-patterns/.shared/build-and-push-acr.sh`. This pattern does not fork that helper.
