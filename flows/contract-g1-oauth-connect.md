---
title: "Contract G1 — OAuth-connect bridge (provider grant → resolvable broker tool credential)"
owner: solution-architect
status: delivered
consumes: oraclous-frontend#108 (FE "Connect with…"), unblocks Connections increment 5
backend-issue: oraclous-backend#339
delivered-by: oraclous-backend#344 (broker bridge), #345 (auth connect flow), #346 (deploy wiring)
---

# Contract G1 — OAuth-connect bridge

**Goal.** A signed-in user clicks "Connect with Google / GitHub / Notion" once, and that connection becomes
a usable **tool credential** — resolvable at tool-execution time — *without* re-pasting a key and *without*
minting a new app session.

## As-built (delivered 2026-06-14) — authoritative; supersedes the design below where they differ

Shipped in #344/#345, deployed, and verified live end-to-end (connect → resolve round-trip; wrong internal
key → 401; reachable through the gateway with auth enforced). **The FE (oraclous-frontend#108) builds against
this shape, not the superseded design narrative below.**

**One deliberate simplification vs the design:** connect-complete is an **authenticated POST**, not a public
`GET /connect/callback`. The principal is taken from the **bearer**, so there was **no `oauth_states` schema
migration** (no `user_id`/`org`/`mode` fields added to the state row — the riskiest part of the original
design is avoided). The connect handshake stays single-use + TTL-bound + provider-matched as before.

### auth-service — two authenticated endpoints under the existing `/oauth` prefix (gateway-proxied)
- **`POST /oauth/{provider}/connect`** — authenticated (user bearer). Body `{ redirect_uri, scopes: [] }`
  (empty `scopes` → the provider's default login scopes). Returns `{ authorize_url }` (PKCE, requesting the
  given **tool** scopes). Send the user there for consent.
- **`POST /oauth/{provider}/connect/complete`** — authenticated (user bearer). Body `{ code, state }` (the
  `code`+`state` the provider returned to your `redirect_uri`). Returns `{ provider, credential_id }`. The
  `organisation_id`/`user_id` come from the bearer, **never the body or the state row**. Mints no session,
  creates no user. Errors: bad/expired state → 400; provider unconfigured → 503; **broker bridge failure
  (down/rejecting) → 502** (deliberate, no broker detail leaked).

### credential-broker — internal bridge (internal-only, X-Internal-Key, never edge)
- **`POST /internal/oauth-connect`** — `{ organisation_id, user_id, provider, name, token: {access_token,
  refresh_token, scopes, expires_at} }` → `{ credential_id }`. **Upserts** by `(org, user, provider,
  cred_type='oauth')` (re-connecting rotates the token in place; same `credential_id`). The landed credential
  then (a) lists via `POST /credentials/retrieve/` and (b) resolves via `get_provider_token` unchanged.

### frontend (oraclous-frontend#108) — the "Connect with…" affordance (gateway-only)
1. "Connect with Google/GitHub/Notion" → `POST /oauth/{provider}/connect` (authenticated, via the gateway) →
   open the returned `authorize_url`.
2. Provider consent → redirects the browser back to your `redirect_uri` with `?code=&state=`.
3. A connect-callback page reads `code`+`state` from the URL and calls `POST /oauth/{provider}/connect/complete`
   **authenticated** (the user's bearer) → `{ credential_id }`. This is the bridge call — **not**
   `auth.oauthCallback` (which would re-issue a session).
4. Refresh the credential list; the connected provider's credential is now selectable for a tool's
   `oauth_token` requirement (replacing the dead-end note in the `oauth_token` branch of `CredentialSlot`).

`redirect_uri` is a FE-owned connect-callback route; nothing in the token ever touches the client — the FE
only ever sees the opaque `credential_id`.

---

_The sections below are the original design narrative, kept for history. Where they differ from **As-built**
above (notably: the public `GET /connect/callback` + the `oauth_states` field additions), **As-built wins.**_

## Current state (verified)
- **auth-service** owns the OAuth machinery. `GET /oauth/{provider}/login` → authorize URL (PKCE); the
  `callback` (`oauth_service.complete_callback`) does **two** things — stores the provider tokens to its own
  `oauth_accounts` table (encrypted with auth's `OAUTH_ENC_KEY`) **and** mints an app JWT. The reusable
  pieces are `begin_login`, the state handshake (`_states.consume`), `exchange_code`, and `_store_tokens`;
  the **login-only** pieces are `_upsert_user` and `issue_for_user`.
- **credential-broker** owns the runtime resolver. `get_provider_token(org, user, provider)` looks up its own
  `user_credentials` table `WHERE provider=X AND cred_type='oauth'`, decrypts `encrypted_cred`, refreshes
  near-expiry via `RefreshClient`, and validates scopes against `DATA_SOURCE_CAPABILITIES`. It expects the
  decrypted dict `{access_token, refresh_token, scopes, expires_at}`. The broker's store is encrypted with
  its **own** per-org KMS envelope (separate from auth's key).
- **The gap:** the resolver's oauth-credential store has **no producer** — only manual `POST /credentials/`
  exists. Auth's `oauth_accounts` (login tokens) is a *different* store the resolver never reads.

## The design — a dedicated *connect* flow, distinct from login

A connect flow reuses auth's OAuth machinery but, on callback, **skips user-creation and JWT issuance** and
instead lands a **broker** oauth credential. The broker is the resolver's source of truth; auth's
`oauth_accounts` stays login-only (no second source of truth for tool tokens).

### 1. auth-service — new connect endpoints (edge-exposed under the existing `/oauth` prefix)
- **`GET /oauth/{provider}/connect`** — **authenticated** (principal from the session). Inputs: the desired
  `data_source`(s) or `scopes` + `redirect_uri`. Resolves the tool scopes (from the broker catalogue, e.g.
  Google → `drive.readonly`), creates a **state row carrying `(user_id, organisation_id, provider,
  code_verifier, redirect_uri, mode=connect, requested_scopes)`**, and returns `{authorize_url}` (PKCE,
  requesting the **tool** scopes — broader than login's `openid email profile`).
- **`GET /oauth/{provider}/connect/callback`** — public (the provider's browser redirect carries no session;
  the user is resolved from the **single-use state row**, not a header). Inputs: `code`, `state`. Consumes
  the state → `(user_id, org)`; `exchange_code` → token set; **does NOT** upsert a user or issue a JWT; calls
  the broker bridge (below) to persist the credential; then redirects the browser back to the FE
  (`<redirect_uri>?connected=<provider>` / `?error=…`).

State model gains `user_id`, `organisation_id`, `mode`, `requested_scopes` (nullable for login rows).

### 2. credential-broker — new internal bridge endpoint (internal-only, never edge)
- **`POST /internal/oauth-connect`** (X-Internal-Key gated, same trusted plane as `/internal/runtime-token`).
  Input: `(organisation_id, user_id, provider, name, token: {access_token, refresh_token, scopes,
  expires_at})`. **Upserts** a `user_credentials` row keyed by `(org, user, provider, cred_type='oauth')` —
  re-connecting updates the token — with `tool_id = <OAUTH connect sentinel UUID>` (the resolver matches by
  provider, not tool_id) and `encrypted_cred = envelope({access_token, refresh_token, scopes, expires_at})`.
  Returns `{credential_id}`.
- The created credential then (a) appears in `POST /credentials/retrieve/` (so the FE lists/selects it in
  `CredentialSlot`) and (b) resolves via the existing `get_provider_token` unchanged.

### 3. frontend (oraclous-frontend#108) — the "Connect with…" affordance
- On the Connections page (and the `oauth_token` branch of `CredentialSlot`, replacing the "coming soon"
  note): "Connect with Google/GitHub/Notion" calls `GET /oauth/{provider}/connect` (via the gateway,
  authenticated) → opens the `authorize_url` → provider consent → redirect to `/oauth/{provider}/connect/
  callback` → a new FE connect-callback route reads the `?connected=` status and refreshes the credential
  list; the connected provider's credential is now selectable for a tool's `oauth_token` requirement.
- It routes to a **connect**-callback (calls the connect flow), **not** `auth.oauthCallback` (which re-issues
  a session).

## Security notes (security-architect lens)
- `connect/callback` is public (provider redirect) but **cannot be abused**: it creates a credential only for
  the user bound into the single-use, expiring state row created by an authenticated `connect` begin. No
  unauthenticated party can mint a credential.
- The token crosses auth → broker over the **internal X-Internal-Key plane** (the same trusted channel the
  resolver already uses), never the edge.
- Scopes are explicit (the user consents to the tool scopes at the provider); the credential is org+user
  scoped; the existing single-use encrypted state covers CSRF.
- auth's `oauth_accounts` and the broker's `user_credentials` keep separate encryption; the connect flow
  writes only the broker credential (the resolver's source).

## Gateway routing
No new gateway route — `/oauth/*` is already proxied to auth-service. The broker `/internal/oauth-connect`
stays internal-only (auth → broker), consistent with the existing internal plane.

## Implementation breakdown (oraclous-backend#339 — one coherent feature, may be 1–2 PRs)
1. **broker:** `POST /internal/oauth-connect` (upsert oauth credential, sentinel tool_id) + the OAUTH-connect
   sentinel constant. (Lands the resolver-ready shape; independently testable against the resolver.)
2. **auth:** the `connect` + `connect/callback` endpoints + the state-model fields (`user_id`/`org`/`mode`/
   `requested_scopes`) + a `connect_provider` service method reusing `exchange_code`, calling the broker bridge.
3. **FE (oraclous-frontend#108):** the "Connect with…" affordance + the connect-callback route (separate PR,
   after the backend lands).

**Done = a user connects a provider once and a tool needing that provider's `oauth_token` resolves it at
execution time with no key pasting** (verify: connect Google → a `cred_type=oauth` credential appears in
`/credentials/retrieve/` → `get_provider_token` returns a valid token → a Drive-tool instance validates ready).
