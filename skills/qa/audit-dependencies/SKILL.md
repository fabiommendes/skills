---
name: audit-dependencies
description: Supply-chain audit of a project's dependencies covering known vulnerabilities, pinning and lockfiles, install-time code, package provenance, maintenance health, unused dependencies, and licenses, delivered as a PDF/HTML report with ready-to-paste GitHub issues. Use when the user asks to audit dependencies, check for vulnerable or outdated packages, or review the supply chain.
---

# Audit: dependencies

Audit everything the project pulls in from outside (packages, base images, CI
actions, vendored code) and deliver the report defined by the `audit-report`
skill.

Copy this checklist and track it:

```
- [ ] 1. Load audit-report
- [ ] 2. Build the dependency inventory
- [ ] 3. Run the vulnerability scanners
- [ ] 4. Check every category
- [ ] 5. Write findings.json and render
```

## 1. Load audit-report

Invoke the `audit-report` skill now. It defines the findings file you fill in
as you go. The area is `dependencies`; the issue title prefix is `[Deps]`.

## 2. Build the dependency inventory

Find every manifest and lockfile: `package.json` with `package-lock.json`,
`pnpm-lock.yaml`, or `yarn.lock`; `pyproject.toml` with `uv.lock` or
`poetry.lock`; `requirements*.txt`; `Cargo.toml`/`Cargo.lock`;
`go.mod`/`go.sum`; `Gemfile.lock`; `pom.xml`; `build.gradle`; `composer.lock`;
Dockerfiles (`FROM` lines); CI workflows (`uses:` lines); and vendored or
copied third-party code.

Record one row per manifest in `inventory`: path, ecosystem, lockfile present
and in sync, number of direct production and development dependencies.

## 3. Run the vulnerability scanners

Run the scanner for each ecosystem, from the project directory:

| Ecosystem | Command |
|---|---|
| any (preferred, covers most lockfiles) | `osv-scanner scan source -r .` |
| npm / pnpm / yarn | `npm audit --json`, `pnpm audit --json`, `yarn npm audit --json` |
| Python | `uvx pip-audit` (add `-r requirements.txt` or run inside the project environment) |
| Rust | `cargo audit` |
| Go | `govulncheck ./...` |

Report vulnerabilities only from scanner output or an advisory you looked up.
Never cite a CVE from memory. If no scanner can run (no network, no tool), say
so in `methodology` and mark the category's coverage as partial.

For each vulnerability, check reachability: is the vulnerable package used in
production code, and is the vulnerable function or feature called? Record the
evidence in `conditions`.

## 4. Categories

### 1. Known vulnerabilities (`vulnerabilities`)

Scanner results, deduplicated by advisory, with the installed version, the
fixed version, and reachability.

### 2. Pinning and lockfiles (`pinning`)

Applications without a committed lockfile, or with one out of sync with the
manifest; `latest` or floating tags in `FROM` lines; GitHub Actions referenced
by tag or branch instead of a commit SHA; `curl ... | sh` and unpinned
downloads in Dockerfiles, CI, and setup scripts.

### 3. Install-time code (`install-scripts`)

Packages that run code on install (`preinstall`/`postinstall` scripts in npm,
`setup.py` builds, build scripts), and dependencies installed from git URLs,
tarballs, or local paths.

### 4. Provenance (`provenance`)

Names one typo away from a popular package; internal package names that would
also resolve from the public registry (dependency confusion) when the registry
configuration does not scope them; packages from personal forks or accounts
with no history.

### 5. Maintenance health (`maintenance`)

Deprecated packages, packages archived upstream, and runtimes or base images
past end of life (Node.js, Python, distribution releases). Check release
history in the registry when network access exists; otherwise report only what
the lockfile and deprecation notices show.

### 6. Footprint (`footprint`)

Dependencies declared but never imported, several libraries for the same job,
heavy dependencies used for one trivial function, and development dependencies
that end up in the production bundle or image.

### 7. Licenses (`licenses`)

Dependencies with copyleft licenses (GPL, AGPL) in a product that is
distributed or offered as a service, packages with no license, and licenses
incompatible with the project's own. Ask the user how the product is
distributed before rating these; without an answer, rate them `info`.

## Severity

| Level | Meaning |
|---|---|
| `critical` | A malicious or compromised package, or a reachable vulnerability allowing code execution, authentication bypass, or data theft in production. |
| `high` | A reachable high-severity vulnerability, or install-time code from an unpinned or untrusted source. |
| `medium` | A vulnerability that is not reachable as used, missing lockfiles or unpinned actions, or an end-of-life runtime. |
| `low` | Unused or duplicated dependencies, deprecated packages without known vulnerabilities. |
| `info` | License observations and maintenance notes. |

## 5. Write findings.json and render

Fill `findings.json` as `audit-report` defines, with all seven categories in
`categories`, and render it. For vulnerabilities, put the advisory ID, installed
version, and fixed version in the finding's `title` or `description`, and the
manifest path in `location`. Group upgrades that one command fixes into a
single issue.
