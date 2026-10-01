---
name: audit-privacy
description: Privacy and data-protection audit (LGPD, GDPR) of a codebase covering the personal data inventory, minimization, personal data in logs, third-party sharing, consent, data subject rights, retention, and protection of sensitive data, delivered as a PDF/HTML report with ready-to-paste GitHub issues. Use when the user asks for a privacy, LGPD, or GDPR audit, or wants to know what personal data an application collects and where it goes.
---

# Audit: privacy

Audit how the application collects, stores, shares, and deletes personal data,
and deliver the report defined by the `audit-report` skill.

This audit reads code and configuration; it is not legal advice. Whether a
legal basis is valid, or a disclosure is sufficient, is a question for counsel.
Record such points as `info` findings marked "for legal review" instead of
judging them.

Access-control flaws that expose personal data belong to `audit-webserver`;
mention them here only to point at that audit.

Copy this checklist and track it:

```
- [ ] 1. Load audit-report
- [ ] 2. Build the personal data inventory
- [ ] 3. Check every category
- [ ] 4. Write findings.json and render
```

## 1. Load audit-report

Invoke the `audit-report` skill now. It defines the findings file you fill in
as you go. The area is `privacy`; the issue title prefix is `[Privacy]`.

## 2. Build the personal data inventory

Personal data is any information about an identified or identifiable person:
names, emails, phone numbers, documents (CPF, passport), addresses, IP
addresses, device and advertising identifiers, location, photos, free-text
fields users fill in. Sensitive data, under LGPD art. 5 II and GDPR art. 9,
covers health, biometric and genetic data, racial or ethnic origin, religion,
political opinion, union membership, and sex life or orientation; children's
data also needs special care.

Find personal data in database schemas and migrations, ORM models, API request
and response types, forms, file uploads, analytics events, and log statements.
Record one row per data item in `inventory`: data item, where it is stored
(`table.column` or file), source, purpose found in code, sensitive (yes/no),
third parties that receive it, and retention.

## 3. Categories

### 1. Minimization (`minimization`)

Personal data collected or stored but never used for any purpose the code
shows; full documents or birth dates kept where a check or a year would do;
whole user objects returned by APIs that need two fields.

### 2. Personal data in logs and telemetry (`logs`)

Personal data or secrets written to logs, error trackers (Sentry and similar),
analytics events, URLs and query strings, and caches. Check request logging
middleware and exception handlers, which often dump entire bodies.

### 3. Third-party sharing (`sharing`)

SDKs and services that receive personal data: analytics, advertising, email
and SMS providers, payment processors, support widgets, LLM and AI APIs. For
each one record what data it receives. Flag trackers and SDKs loaded before the
user consents, and personal data sent to services that do not need it.

### 4. Consent (`consent`)

How consent is captured, stored (with timestamp and the version of the text
accepted), and withdrawn; whether non-essential cookies and trackers wait for
consent; whether withdrawing consent stops the processing in code.

### 5. Data subject rights (`rights`)

Whether the code supports access and portability (export a user's data),
correction, and deletion. For deletion, follow the data: soft deletes that
keep everything, related tables, uploaded files, search indexes, caches,
analytics, and third parties that keep a copy.

### 6. Retention (`retention`)

Cleanup jobs, TTLs, or archival for personal data; data kept forever by
default; logs and backups with no retention configured where the configuration
is in the repository.

### 7. Protection of personal data (`protection`)

Encryption in transit and, for sensitive data, at rest or per field; personal
data exposed in admin and support tools to more staff than need it; real
personal data in seeds, fixtures, test dumps, or non-production environments.

### 8. International transfer (`transfer`)

Personal data stored or processed outside the user's jurisdiction, as shown by
cloud regions and third-party providers in the configuration. Record these as
`info` for legal review.

## Severity

| Level | Meaning |
|---|---|
| `critical` | Sensitive personal data exposed publicly or to parties with no reason to receive it. |
| `high` | Personal data sent to third parties without consent or a purpose in code, personal data in logs shipped to external services, or no way to delete a user's data. |
| `medium` | Incomplete deletion or export, missing retention for personal data, collection beyond what the code uses. |
| `low` | Minor minimization gaps, such as an API returning a non-sensitive field it does not need. |
| `info` | Points for legal review, and observations with no risk on their own. |

## 4. Write findings.json and render

Fill `findings.json` as `audit-report` defines, with all eight categories in
`categories`, and render it. Mask personal data in snippets and screenshots.
