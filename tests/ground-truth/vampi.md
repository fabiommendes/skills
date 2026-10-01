---
type: spec
status: active
tags: [audit-skills, skill-validation, audit-webserver, ground-truth]
relatedTo: [audit-skills-validation, audit-webserver]
---

# Ground truth: VAmPI for audit-webserver

Fixture `vampi` at commit `f16052dc` (see `tests/fixtures/external.tsv`).
Every row was checked against the source. `vuln` is the `vulnerable`
environment variable, which defaults to 1 (`app.py:9`), so the vulnerable
branches are the default; a finding should say so in `conditions`.

## Route inventory

The routes are registered in `openapi_specs/openapi3.yml` through
`operationId`, not in Python. 14 operations on 10 paths:

| Method | Path | Handler | Auth |
|---|---|---|---|
| GET | /createdb | `api_views/main.py:6` | none |
| GET | / | `api_views/main.py:14` | none |
| GET | /users/v1 | `api_views/users.py:19` | none |
| GET | /users/v1/_debug | `api_views/users.py:24` | none |
| POST | /users/v1/register | `api_views/users.py:52` | none |
| POST | /users/v1/login | `api_views/users.py:85` | none |
| GET | /me | `api_views/users.py:28` | bearer |
| GET | /users/v1/{username} | `api_views/users.py:45` | none |
| DELETE | /users/v1/{username} | `api_views/users.py:206` | bearer, admin |
| PUT | /users/v1/{username}/email | `api_views/users.py:132` | bearer |
| PUT | /users/v1/{username}/password | `api_views/users.py:179` | bearer |
| GET | /books/v1 | `api_views/books.py:12` | none |
| POST | /books/v1 | `api_views/books.py:17` | bearer |
| GET | /books/v1/{book_title} | `api_views/books.py:45` | bearer |

T4 passes when the inventory has these 14 rows. Watch for an inventory built
from the README table, which lists the same routes but no handlers.

## Defects listed by the project (README)

Recall (T2) is measured mainly on these nine. "Expected" is the level the
severity table in `audit-webserver/SKILL.md` gives; a level in parentheses is
also defensible.

| ID | Defect | Category | Location | Expected |
|---|---|---|---|---|
| G1 | SQL injection via username | `injection` | `models/user_model.py:72-73`, reached from `GET /users/v1/{username}` | critical |
| G2 | Password change of any user: the path username is used instead of the token subject | `idor` | `api_views/users.py:186-190` | critical |
| G3 | BOLA: any authenticated user reads any book's secret | `idor` | `api_views/books.py:50-58` | critical |
| G4 | Mass assignment: `admin` accepted at registration | `property-authz` | `api_views/users.py:60-66` | critical |
| G5 | Unauthenticated debug endpoint returns every password | `function-authz` (or `property-authz`, `config`) | `api_views/users.py:24-26`, `models/user_model.py:58-59` | critical |
| G6 | User and password enumeration on login | `authn` | `api_views/users.py:101-106` | medium (low) |
| G7 | ReDoS in the email regex | `limits` | `api_views/users.py:143-146` | medium (high) |
| G8 | No rate limit on login (or anywhere) | `authn` and `limits` | no code; whole app | medium |
| G9 | Hard-coded weak JWT signing key `random`: anyone can forge an admin token | `secrets` | `config.py:13` | critical |

## Other real defects

Not in the README but present in the code. Finding them counts toward recall
as a bonus; missing them is not a failure.

| ID | Defect | Category | Location | Expected |
|---|---|---|---|---|
| X1 | Passwords stored and compared in plain text | `authn` | `models/user_model.py:15,24`, `api_views/users.py:93` | high |
| X2 | `GET /createdb` drops and recreates the database without authentication | `function-authz` | `api_views/main.py:6-12` | critical |
| X3 | `debug=True` on `0.0.0.0` when run with `python app.py` | `config` | `app.py:17` | high (medium) |
| X4 | `GET /users/v1` and `GET /users/v1/{username}` list emails without authentication | `property-authz` or `isolation` | `api_views/users.py:19-21,45-47` | medium |
| X5 | JSON built by string formatting (injection into the response) | `injection` | `api_views/users.py:12-16`, `models/user_model.py:28,76` | low |
| X6 | Deleted user's token makes `delete_user` and `update_email` crash (`None.admin`) | `authn` | `api_views/users.py:142,211-212` | low |
| X7 | No token revocation on password change | `authn` | `api_views/users.py:179-201` | low |
| X8 | Container runs as root | `config` | `Dockerfile:8-17` | low |

## Expected "not applicable" and strengths

- `isolation`: no tenants; not applicable, or applicable only to the user-owned
  books (which is G3). Either is fine with a reason.
- `function-authz`: applies (G5, X2), even without a frontend.
- `xss`: JSON API with no HTML; not applicable or `info`.
- `ssrf`: no outbound HTTP; not applicable.
- `csrf-cors`: bearer tokens in a header, no cookies; not applicable or a
  strength.
- Plausible strengths: JWT decoding pins `HS256` (`models/user_model.py:48`);
  ORM queries elsewhere use `filter_by`; jsonschema validation on bodies.

## Out of scope

- Outdated pinned packages in `requirements.txt` belong to
  `audit-dependencies`. A finding that cites a CVE for them fails T3 unless it
  came from a scanner run recorded in `methodology`.

## History

- Run 1 (2026-10-01, skill before `function-authz` and `property-authz`
  existed) exposed two gaps, now fixed: no category for mass assignment or
  unauthenticated admin endpoints, and a severity table where G2 fit both
  `critical` and `high`. Expected levels above follow the revised table.
