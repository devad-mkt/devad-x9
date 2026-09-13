# X9 Dokploy Direct API Guide

Use this only for careful Dokploy reads, safe fixes, and owner-approved deploys
for Devad CORE. This is not a general Dokploy admin manual and not permission
to delete infrastructure.

## Current Safe Facts

- Dokploy base: `https://dok2.devad.me`
- OpenAPI endpoint: `/api/trpc/settings.getOpenApiDocument`
- CORE app name: `core`
- CORE app slug: `core-0vmpid`
- CORE internal `applicationId`: `FMgiOT89JU7bVD1shTPxX`
- CORE branch observed in the old dry test: `feature/post-v105-native-migration-2026-06-18`
- CORE app status observed in dry test: `done`
- Latest deployment observed in dry test: `done`, title `fix(post): stabilize workspace api key ux`

Fresh Git and Dokploy API responses beat these notes. Verify the current
configured Dokploy branch and latest deployment before deciding whether work
belongs on X9 or the live deploy branch.

## Secret Source

The owner-approved local source for the Dokploy API key is currently:

```text
<private-env-file>
```

If the owner names a newer key file, use that instead. Find the row whose first
column starts with `dokploy api`. Keep the value only in process memory. Do not
print it, commit it, paste it into chat, copy it into `.env`, or save full API
responses that may contain secrets.

## Absolute No

Never do these from Codex unless the owner gives an explicit, task-specific
request and rollback plan:

- Delete, remove, or recreate the CORE app.
- Delete, remove, or recreate Redis, PostgreSQL, databases, volumes, mounts,
  networks, domains, certificates, registries, or compose services.
- Clear, replace, bulk edit, or blindly remove environment variables.
- Rotate secrets, provider keys, Stripe keys, OAuth credentials, webhooks, or
  database credentials.
- Run destructive deploy cleanup, prune, reset, rollback, force-push, or branch
  changes without explicit approval.
- Save full `application.one`, `deployment.all`, logs, or env responses into
  `.devad`, reports, or chat.

## Allowed Without Extra Approval

These are safe when scoped to CORE and projected to non-secret fields:

- Check OpenAPI availability.
- Search for the CORE application id.
- Read CORE app status, branch, repository, source type, and auto-deploy flag.
- Read latest deployment status and short safe title/id/time.
- Check `https://devad.io/health`.
- Inspect short non-secret error summaries.
- Prepare deploy commands but stop before triggering them.

## Deploy Rule

A deploy is allowed only after the current user request clearly asks to deploy
or fix-and-deploy this specific slice. Before triggering:

1. Confirm repo path, branch, HEAD, dirty files, and remote branch HEAD.
2. Confirm GitHub remote heads for X9 and the live deploy branch.
3. Confirm Dokploy app branch/latest deployment safe fields.
4. Confirm the pushed commit is the intended deploy commit.
5. Confirm the internal application id through `application.search`.
6. Confirm no migration/env/queue/worker risk is hidden in the diff.
7. Trigger `application.deploy`, not `application.redeploy`, for CORE.
8. Poll deployment status until terminal: `done`, `failed`, `error`, or
   `cancelled`.
9. Verify `/health` and any task-specific browser/API proof.

Record only safe fields: app name, branch, commit/title, deployment id, status,
health result, and timestamp.

## Read-Only Dry Test

PowerShell pattern. This keeps the key out of output:

```powershell
$csv = Import-Csv -LiteralPath '<private-env-file>' -Header c1,c2,c3,c4,c5,c6
$key = (($csv | Where-Object { $_.c1 -like 'dokploy api*' } | Select-Object -First 1).c2).Trim()
$headers = @{ 'x-api-key' = $key; Accept = 'application/json' }

Invoke-WebRequest `
  -Uri 'https://dok2.devad.me/api/trpc/settings.getOpenApiDocument' `
  -Headers $headers `
  -UseBasicParsing

$search = Invoke-RestMethod `
  -Uri 'https://dok2.devad.me/api/application.search?q=core' `
  -Headers $headers

$app = Invoke-RestMethod `
  -Uri 'https://dok2.devad.me/api/application.one?applicationId=FMgiOT89JU7bVD1shTPxX' `
  -Headers $headers

[ordered]@{
  applicationId = $app.applicationId
  name = $app.name
  appName = $app.appName
  status = $app.applicationStatus
  branch = $app.branch
  autoDeploy = $app.autoDeploy
  repository = $app.repository
}
```

## Deployment Status Read

Normalize response shape before trusting it:

```powershell
function Get-DokployItems($value) {
  if ($null -eq $value) { return @() }
  if ($value -is [array]) { return @($value) }
  if ($value.items) { return @($value.items) }
  if ($value.deployments) { return @($value.deployments) }
  if ($value.result -and $value.result.data -and $value.result.data.json) {
    $json = $value.result.data.json
    if ($json.items) { return @($json.items) }
    if ($json -is [array]) { return @($json) }
    return @($json)
  }
  return @($value)
}

$deployments = Invoke-RestMethod `
  -Uri 'https://dok2.devad.me/api/deployment.all?applicationId=FMgiOT89JU7bVD1shTPxX' `
  -Headers $headers

$latest = Get-DokployItems $deployments |
  Sort-Object { if ($_.createdAt) { [datetime]$_.createdAt } elseif ($_.updatedAt) { [datetime]$_.updatedAt } else { [datetime]'1900-01-01' } } -Descending |
  Select-Object -First 1

[ordered]@{
  deploymentId = $latest.deploymentId
  status = $latest.status
  title = $latest.title
  createdAt = $latest.createdAt
}
```

## Swagger Note

`https://dok2.devad.me/swagger` redirects with HTTP 308 to `/` and then returns
the Dokploy UI HTML. Treat `/api/trpc/settings.getOpenApiDocument` as the
machine-readable API source.

## X9 Routing

For deploy work, first read:

```text
.devad/X9.md
.devad/rules/devad-deploy-dokploy.md
.devad/tooling/dokploy/HOW-TO-USE.md
```

Do not read `.devad/features/**` or old deployment reports unless the current
task names a specific file or requires historical proof.
