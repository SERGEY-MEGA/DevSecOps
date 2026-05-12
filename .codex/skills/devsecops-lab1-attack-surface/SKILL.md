---
name: devsecops-lab1-attack-surface
description: Use this skill when working on DevSecOps lab 1: deploying a vulnerable web app, inventorying attack surface, mapping ports/endpoints/assets/secrets/trust boundaries, and preparing a Russian report for the course. The current chosen candidate project is https://github.com/vulnerable-apps/vuln_django_play, but verify facts from the local repo and running stand before writing conclusions.
---

# DevSecOps Lab 1: Attack Surface

## Goal

Help prepare laboratory work number 1: deploy a vulnerable web application locally and produce an attack surface inventory report. Focus on inventory, not exploitation.

Candidate upstream: `https://github.com/vulnerable-apps/vuln_django_play`.

Do not assume project internals from the repository name. Verify via README, configs, code, and the running stand.

## Expected Result

By defense time, the user needs:

- A local stand that can be started from scratch in under 10 minutes.
- A working repository with the app and the report.
- A report in Russian, `.md` or `.docx`.
- A clear explanation of attack surface vs attack vector vs vulnerability.
- A short live demo of the running stand.
- A concise oral defense script: what was deployed, how it was inspected, what the attack surface contains, and which evidence supports the conclusions.

## Workflow

1. Read the upstream/local README and identify what the app does.
2. Inspect declarative config: `docker-compose.yml`, `Dockerfile`, `.env*`, `settings.py`, web server config, dependency files.
3. Start or verify the stand.
4. Compare declared state with actual state:
   - `docker compose ps`
   - `docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}"`
   - `ss -tlnp` or macOS alternative `lsof -iTCP -sTCP:LISTEN -P`
   - `curl -i` against key URLs
5. Inspect routes and input points in code.
6. Inventory assets, secrets names, roles/auth, trust boundaries.
7. Draft report sections with evidence and commands.

Use `rg` instead of `grep` when searching locally.

## Report Sections

The report must contain:

1. Header: full name, group, lab number, GitLab repo link, upstream link, date.
2. Source data: selected project and why, one-to-two sentence app functionality.
3. Setup and deployment: required software, versions, launch commands, typical errors and fixes.
4. Research process: sources used and commands performed.
5. Attack surface analysis:
   - 5.1 Deployment conditions and scope boundaries.
   - 5.2 System components and technologies.
   - 5.3 Network access points: addresses, ports, protocols, external availability.
   - 5.4 Application entry points: paths/pages, methods, auth, accepted data.
   - 5.5 Access, roles, valuable data, and secrets names without secret values.
   - 5.6 Trust boundaries.

Each subsection 5.2-5.6 should usually contain 4-6 key elements, not an exhaustive dump.

## Important Definitions

- Asset: anything valuable that needs protection: data, business logic, infrastructure, reputation.
- Vulnerability: a property that enables a threat; not the same as a generic bug.
- Threat: a potential event that can violate security properties.
- Attack: a concrete action exploiting a weakness.
- Risk: roughly likelihood multiplied by impact.
- Attack surface: all points where an untrusted subject can enter data, interact, or receive responses.
- Attack vector: a concrete method and path for delivering a payload through an entry point.
- Trust boundary: a place where data/control crosses from a less trusted zone to a more trusted zone.

## Commands Cheat Sheet

Network and runtime:

```bash
docker compose ps
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}"
ss -tlnp
lsof -iTCP -sTCP:LISTEN -P
docker network ls
curl -i http://localhost:<port>/
curl -I http://localhost:<port>/
curl -i -X OPTIONS http://localhost:<port>/<path>
```

Django route and input search:

```bash
rg "path\(|re_path\(|url\(" -g "*.py"
rg "request\.GET|request\.POST|request\.body|request\.FILES" -g "*.py"
rg "FileField|ImageField|multipart|upload" -g "*.py"
rg "execute\(|raw\(|cursor\.execute" -g "*.py"
```

Secrets and sensitive config:

```bash
rg -n "(password|passwd|secret|api[_-]?key|token|private[_-]?key)\s*[=:]" -g "*.py" -g "*.yml" -g "*.yaml" -g "*.env*"
find . -name "*.key" -o -name "*.pem" -o -name "*.p12"
git log --all --full-history -- .env
```

Dependencies:

```bash
cat requirements.txt
cat package.json
cat package-lock.json
pip list 2>/dev/null | wc -l
npm ls --all 2>/dev/null | wc -l
```

## Reporting Rules

- Never include real secret values in the report. Mention only names, storage location, and whether they are hardcoded or example-like.
- Distinguish facts from observations and risks.
- Record commands and representative outputs, but keep the report readable.
- If config says one thing and the running stand shows another, report the running stand separately.

Detailed report skeleton and tables: see `references/lab1-report-template.md`.
