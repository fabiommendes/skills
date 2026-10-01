---
name: audit-webserver
description: Security audit of a whole web application or API codebase covering tenant isolation, function- and property-level authorization (mass assignment), IDOR, authentication, injection, XSS, SSRF, CSRF/CORS, secrets, resource limits, and security configuration, delivered as a PDF/HTML report with ready-to-paste GitHub issues. Use when the user asks for a security audit or security review of a web app, API, or backend.
---

# Audit: web server

Audit a web application's codebase for security flaws and deliver the report
defined by the `audit-report` skill. This is a whole-codebase audit; to review
a single change or pull request, use the `security-reviewer` agent instead.
Vulnerable dependencies belong to `audit-dependencies`.

Work from the code. Evidence from reading the source is enough for every
finding; do not send exploit payloads to a running server unless the user asks
for it and names a test environment.

Copy this checklist and track it:

```
- [ ] 1. Load audit-report
- [ ] 2. Detect the stack
- [ ] 3. Build the route inventory
- [ ] 4. Check every category
- [ ] 5. Write findings.json and render
```

## 1. Load audit-report

Invoke the `audit-report` skill now. It defines the findings file you fill in
as you go. The area is `webserver`; the issue title prefix is `[Security]`.

## 2. Detect the stack

Identify the language, framework, ORM or query builder, authentication
mechanism, frontend, and deploy files (Docker, CI, Helm, Terraform). Map each
category below onto the stack's equivalent, and record the mapping in
`methodology`. When a category does not apply, such as XSS in a project with no
frontend, mark it not applicable with the reason instead of forcing a finding.

## 3. Build the route inventory

List every route the server registers: method, path, handler `file:line`,
authentication required, role or permission checked, and ownership or tenant
check. Find routes where the framework registers them, not by sampling files:
router calls and decorators in code, or the specification file for spec-first
frameworks (OpenAPI `operationId` in Connexion, API gateway configs). Count the
registrations to confirm the inventory is complete. Store it as `inventory` in
`findings.json`. Categories 1 to 4 are checked against it, row by row.

## 4. Categories

### 1. Tenant and owner isolation (`isolation`)

In Supabase this is missing RLS. In hand-written APIs it is list, search,
aggregate, report, and export queries that do not filter by the authenticated
user or their organization, workspace, or tenant. First identify which
isolation mechanism the project uses (RLS, tenant middleware, manual `user_id`
filtering), then show where it is absent or leaky.

### 2. Function-level authorization (`function-authz`)

Privileged operations (admin, settings, user management, maintenance, debug,
database reset, write actions) that the server exposes without checking the
caller's role, including:

- Operations the frontend hides by role (`isAdmin`, `canEdit`, `role`) while
  the endpoint performs no equivalent check. Match every frontend role gate
  with its endpoint.
- Admin, debug, and maintenance endpoints reachable without authentication or
  by any authenticated user.

### 3. IDOR (`idor`)

Routes that fetch, modify, or delete an object by an ID from the path, query,
or body without verifying the object belongs to the caller or their tenant.
Check every handler in the inventory. A foreign object must look exactly like a
missing one (404), so the response does not reveal which IDs exist.

### 4. Property-level authorization (`property-authz`)

Request bodies bound to models without an allowlist (mass assignment), so a
caller sets fields such as `admin`, `role`, `owner_id`, `tenant_id`, `price`,
or `verified`; and responses that serialize whole models, returning fields
the caller must not see (password hashes, tokens, internal flags, other
users' emails).

### 5. Authentication and sessions (`authn`)

Password hashing (argon2, bcrypt, or scrypt, never a fast hash); rate limiting
or lockout on login, reset, and MFA endpoints; session cookies with `HttpOnly`,
`Secure`, and `SameSite`; session and token expiry and revocation on logout and
password change; JWT verification that pins the algorithm and rejects `none`;
password reset tokens that are random, single-use, and expiring.

### 6. Injection (`injection`)

User input reaching an interpreter: SQL built by string concatenation or
formatting, NoSQL operator injection, shell commands (`shell=True`, `exec`,
backticks), file paths (path traversal, archive extraction), server-side
templates rendered from user input, and deserialization of untrusted data
(`pickle`, `yaml.load`, Java serialization).

### 7. Unsanitized input and XSS (`xss`)

Frontend: `innerHTML`, `dangerouslySetInnerHTML` and framework equivalents
(`v-html`, `[innerHTML]`), markdown or HTML rendered without sanitization,
user-controlled URLs in `href` or `src` (`javascript:`), `eval`, `new Function`.
Backend: user input reaching email HTML, templates, or responses without
escaping. Check whether the project has a sanitization library and whether it
is applied at each point found.

### 8. SSRF (`ssrf`)

The server fetching a URL the user controls: webhooks, URL previews, image or
file imports, PDF generators. Check for an allowlist, blocking of private and
link-local addresses (including the cloud metadata endpoint `169.254.169.254`),
and redirect handling that re-checks the destination.

### 9. CSRF and CORS (`csrf-cors`)

State-changing routes authenticated by cookies without a CSRF token or a
`SameSite` cookie that blocks cross-site requests. CORS configurations that
reflect any `Origin` or allow `*` together with credentials.

### 10. Exposed secrets (`secrets`)

API keys, tokens, passwords, signing secrets (JWT, webhooks), private keys, and
default credentials in source, configs, `docker-compose`, charts, CI, scripts,
and documentation. Pay particular attention to:

- Public defaults that become real secrets when not overridden, such as
  `${VAR:-default-value}`, and missing startup validation that would reject
  them.
- Secrets in git history: run `gitleaks detect` or `trufflehog git file://.`
  when available, otherwise `git log -p -S '<pattern>'` for each secret pattern
  found in the current tree. When the history is incomplete (a shallow clone,
  `git rev-parse --is-shallow-repository` prints `true`) or absent, record in
  `methodology` that history was not checked.
- Keys bundled into the frontend build.

### 11. Resource limits (`limits`)

Request body and upload size limits, upload type checks, maximum page sizes on
list endpoints, rate limits on expensive or abusable endpoints (search, export,
email sending), regular expressions with catastrophic backtracking on user
input, and loops or allocations sized by user input.

### 12. Security configuration (`config`)

Debug mode or verbose error pages reachable in production, stack traces in
responses, missing security headers (`Content-Security-Policy`,
`Strict-Transport-Security`, `X-Content-Type-Options`, `frame-ancestors`),
admin panels and API docs exposed without authentication, and directory
listing.

## Severity

| Level | Meaning |
|---|---|
| `critical` | Exploitable by anyone who can reach the server or create an account, to read or change other users' or tenants' data, take over accounts, gain admin rights, execute code, or obtain production secrets. |
| `high` | The same impact, but the attacker needs a specific role, an invited account, or a common non-default configuration; or a flaw that turns another breach into a worse one (passwords stored in plain text or with a fast hash). |
| `medium` | Exploitable only under specific conditions (configuration, user interaction, timing), or exposes limited data. |
| `low` | A defense-in-depth gap with no direct exploit path. |
| `info` | An observation with no risk on its own. |

## 5. Write findings.json and render

Rate each finding by its own exploit path, with the conditions in
`conditions`. Fill `findings.json` as `audit-report` defines, with all twelve
categories in `categories`, and render it. Deliver as `audit-report` describes.
