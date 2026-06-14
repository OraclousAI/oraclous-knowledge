---
title: "Journey — Connections & credentials: from a buried BYOM form to OAuth auto-connect"
owner: experience-architect
status: signed
signed-by: experience-architect
surface: Connections (new /app/connections — lifted from ConnectionsSection in SettingsPage; CredentialSlot in the agent builder)
grounds-in: capability-surface-inventory.md §3 (credential-broker + auth OAuth)
legacy-divergence: the legacy app had a BYOM-key form in Settings; the real backend models every credential type (model key, api_key, connection_string, oauth) with providers + data-sources, and OAuth tokens captured at login. We expose a first-class Connections surface ending in one-click connect.
backend-gaps: G1 (OAuth-connect bridge — blocks increment 5)
---

# Journey — Connections & credentials

**Persona.** The operator / org admin who wants to manage every credential in one place and **stop pasting
keys** for providers they could just connect (personas: operator, org-admin).

**Today (the problem).** Credentials live in `ConnectionsSection` at the bottom of `SettingsPage` — a
BYOM-key-shaped add form that only creates an `api_key` under the model sentinel; tool credentials appear
read-only but can only be added inside the agent builder. No rename (though `PUT /credentials/{id}` exists),
no providers/data-sources view, and OAuth dead-ends ("add it from the tool instance page"). The backend
(inventory §3) supports the full lifecycle; only OAuth auto-connect is a genuine backend gap (**G1**).

## Design constraints
Mint `#10D88A` = a connected/healthy provider dot only, never a button fill. Secrets are `type=password`,
`autoComplete=off`, send-only (never read back). Reuse the design-system sheet + `useDrawerA11y` (focus
trap/Esc/return) exactly like the Tools detail drawer; keep the two-step destructive confirm. Sentence case,
second-person imperative ("Add a credential", "Connect with Google"); no emoji; AA floor.

## Increments (small, vertical, each testable on the app)

| # | Increment | Gateway capability | Test on the app | Blocked |
| --- | --- | --- | --- | --- |
| 1 | First-class **Connections page** (lift the list out of the BYOM form) + nav entry | `POST /credentials/retrieve/` (existing client) | `/app/connections` lists every credential type with provider/type/name + two-step Remove; BYOM add still works | no |
| 2 | **Add any credential type** from a single sheet (model key / API key / connection string) | `POST /credentials/` (existing client) | "Add a credential" sheet → add each kind → appears with correct type chip; BYOM model dropdown unaffected | no |
| 3 | **Rename a credential** (close the update gap) | `PUT /credentials/{id}` — **new api-client `update()`** (route exists; not a backend gap) | "Rename" → sheet prefilled → new name persists across reload | no |
| 4 | **Connected providers** panel — what each provider unlocks | `GET /credentials/{providers,available-data-sources}` — **new api-client GETs** | panel lists connected providers (mint dot + text label) + the data sources they unlock | no |
| 5 | OAuth **"Connect with…"** auto-connect | **needs G1 bridge** (login token → broker tool credential) | "Connect with Google" → authorize → connected dot, no key pasted; tool's oauth_token slot offers it | **G1** |

## Increment 1 — build brief (the first issue)

**Goal.** Promote credential management out of the BYOM form in Settings into a routed, first-class
`/app/connections` page that lists **every** credential type (not just model keys).

**Scope (in).** New `/app/connections` route + nav entry; lift the credential roster out of
`ConnectionsSection` into a `ConnectionsPage`; compose the existing card + `role="table"` list + type chip +
the two-step danger Remove + `SkeletonList`/empty/error callouts. Render model keys, api_key,
connection_string, and oauth rows with provider/type/name. Keep the secret send-only contract (list returns
metadata only). Link Settings → Connections so nothing is orphaned.

**Scope (out).** No add/edit/rename yet; the BYOM add form stays where it is for now; no providers panel; no
OAuth; no api-client changes.

**How to test on the app.** `pnpm -r build && VITE_API_BASE_URL=<gateway> pnpm --filter @oraclous/console dev`,
open `/app/connections`: every credential the user holds is listed with provider/type/name + Remove (arms on
first click, deletes on Confirm). Keyboard: nav item + each Remove reachable, predictable focus, axe-core AA
clean. No regression: BYOM add still works; Settings still renders.

## Backend gap G1 (Contract → solution-architect, oraclous-backend)
Expose, through the gateway, an in-app "connect a provider" flow that turns a Google/GitHub/Notion OAuth
grant (the same auth-service performs at login) into a broker-stored, resolvable **tool credential** for the
signed-in user, **without minting a new app session**. Today `/oauth/{provider}/login|callback` only re-issue
a session, the broker resolver consumes provider tokens only on the internal plane, and `/credentials/*` CRUD
accepts only manual secrets. The Contract defines: begin-connect / complete-connect gateway endpoints
(distinct from login), the `cred_type=oauth` credential shape the broker persists so it surfaces in
`/credentials/retrieve/` and resolves at tool-execution time, and the relation to the providers/data-sources
reads. **User-facing requirement:** one-click connect Google/GitHub/Notion and it immediately works as a
tool's credential — agents stop asking users to paste keys for providers they could connect.
