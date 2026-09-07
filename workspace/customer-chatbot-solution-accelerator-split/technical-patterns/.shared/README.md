# `.shared` delta — build-and-push-acr (staged, do not promote as an overwrite)

**Live target:** `technical-patterns/.shared/build-and-push-acr.ps1` and `.sh`
(not modified — those files stay live/read-only; this folder stages the
delta for a surgical merge by the promoter).

## What changed

Both scripts previously hardcoded the image name / build-context / Dockerfile
triple per app (`da-app` + `src/App` + `WebApp.Dockerfile` for the frontend,
`da-api` + `src/api/python` + `ApiApp.Dockerfile` for the python backend, plus
the `da-api-dotnet` + `src/api/dotnet` + `CsApi.Dockerfile` dotnet variant),
and hardcoded the `api-` / `app-` / `api-cs-` App Service name prefixes used
for auto-discovery.

`technical-patterns/chat-with-data-voice` uses a different layout
(`src/api` + `src/app`, each with its own `Dockerfile`), so this delta turns
every one of those hardcoded values into a parameter/flag with a default
that matches the **original** `chat-with-data` layout — no existing caller
of the live script needs to change.

New parameters/flags (defaults preserve current behavior):

| PowerShell | Bash | Default |
|---|---|---|
| `-WebImageName` | `--web-image-name` | `da-app` |
| `-WebContext` | `--web-context` | `src/App` |
| `-WebDockerfile` | `--web-dockerfile` | `WebApp.Dockerfile` |
| `-ApiImageName` | `--api-image-name` | `da-api` |
| `-ApiContext` | `--api-context` | `src/api/python` |
| `-ApiDockerfile` | `--api-dockerfile` | `ApiApp.Dockerfile` |
| `-ApiDotnetImageName` | `--api-dotnet-image-name` | `da-api-dotnet` |
| `-ApiDotnetContext` | `--api-dotnet-context` | `src/api/dotnet` |
| `-ApiDotnetDockerfile` | `--api-dotnet-dockerfile` | `CsApi.Dockerfile` |
| `-ApiAppPrefix` | `--api-app-prefix` | `api-` |
| `-WebAppPrefix` | `--web-app-prefix` | `app-` |
| `-ApiDotnetAppPrefix` | `--api-dotnet-app-prefix` | `api-cs-` |

`chat-with-data-voice` would invoke the script with
`-ApiContext src/api -ApiDockerfile Dockerfile -WebContext src/app -WebDockerfile Dockerfile`
(prefixes unchanged, since it already uses `api-`/`app-`).

Preserved unchanged: the private-networking (`-PrivateNetworking` /
`--private-networking`) enable/build/disable flow, and the two-app-service
(frontend + backend) shape.

## Promotion note

Apply this as a surgical diff against the live files — the only changes are
the new parameters/flags and replacing the hardcoded triples/prefixes with
references to them. No behavioral change when the new parameters are left
at their defaults.
