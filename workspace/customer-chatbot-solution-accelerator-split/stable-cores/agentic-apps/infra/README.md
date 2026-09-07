# Infrastructure

This stable core is implemented in Bicep only for the approved split. The staged tree intentionally omits Terraform because the human-approved plan recorded that as a deviation.

## Deployment shape

- `bicep/main.bicep` is the entrypoint.
- `bicep/modules/` contains the reusable vanilla Bicep modules.
- No AVM modules or registry references are staged.

## Included services

- Azure AI Foundry account and project
- Foundry project connections
- Foundry model deployments
- Azure AI Search
