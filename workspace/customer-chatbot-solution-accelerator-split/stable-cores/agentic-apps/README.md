# Agentic Apps Stable Core

`agentic-apps` is the stable-core foundation for agentic applications that need an Azure AI Foundry account, a Foundry project, and Azure AI Search. It provides the shared control plane that technical patterns compose against, without shipping any application compute or domain content.

## What it provides

This core provisions the Foundry and search baseline used by reusable agent patterns:

- Azure AI Foundry account and project
- Foundry project connections for scenario-managed resources
- Azure AI Search for grounded retrieval and indexing
- Role assignments granting the Search service and Foundry project the access they need to work together

This core deploys no models by default. It accepts an optional `modelDeployments` array parameter (empty by default); consumers pass the model deployments they need, and the core provisions them onto its own Foundry account via `modules/ai-foundry-model-deployment.bicep`.

## What it does not provide

- App Service, Container Apps, Functions, or any other application hosting
- Domain data, prompts, business rules, or evaluation datasets
- A bring-your-own Foundry project reuse path
- Terraform implementation files; this approved split stages Bicep only

## Composition

This core is intended to compose with agentic technical patterns that require Foundry project access and search-backed retrieval. The pattern layer must supply its own application infrastructure and any domain-specific configuration.

## Deployment

Use `infra/bicep/main.bicep` as the deployment entrypoint. The staged Bicep implementation is greenfield-only and keeps the Foundry project creation path as the only supported path in this split.
