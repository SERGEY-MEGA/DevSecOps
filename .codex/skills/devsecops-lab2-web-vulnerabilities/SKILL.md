---
name: devsecops-lab2-web-vulnerabilities
description: Use this skill when working on DevSecOps lab 2: analyzing and exploiting the eight training web vulnerability stands on 10.0.0.40, preparing a Russian report with payloads, evidence, root cause, OWASP Top 10:2025/CWE mapping, and remediation notes.
---

# DevSecOps Lab 2: Web Vulnerabilities

## Goal

Help complete laboratory work number 2: analyze eight prepared web vulnerability stands, prove exploitation where practical, and prepare a Russian report.

The stands are training targets at `http://10.0.0.40:<port>`. Do not use unrelated infrastructure credentials in the report unless the user explicitly asks.

## Workflow

For each chosen stand:

1. Recon: `curl -i`, `OPTIONS`, cookies, visible stack.
2. Read the vulnerable code displayed by the stand page.
3. Identify input points and the flawed check.
4. Prepare a minimal payload with `curl`, a small HTML PoC, or a browser action.
5. Record concise evidence from the response.
6. Explain root cause mechanically.
7. Add a remediation that fixes the class of bug.

Prefer exploit evidence, but a precise analysis with theoretical payload and fix is acceptable when the stand is unavailable.

## Stands

| Stand | URL | Class | OWASP/CWE |
|---|---|---|---|
| `csrf-change-email` | `http://10.0.0.40:1331` | CSRF | A06:2025, CWE-352 |
| `file-upload-extension-blacklist` | `http://10.0.0.40:1332` | Unrestricted File Upload -> RCE | A02:2025, CWE-434 |
| `idor-basic-role` | `http://10.0.0.40:1333` | IDOR/client-side role | A01:2025, CWE-639/CWE-602 |
| `idor-invalid-if-statement` | `http://10.0.0.40:1334` | Broken Access Control | A01:2025, CWE-697/CWE-285 |
| `pathTraversal-improper-regex` | `http://10.0.0.40:1335` | Path Traversal | A01:2025, CWE-22 |
| `sqli-blind-variable-mixup` | `http://10.0.0.40:1336` | SQL Injection | A05:2025, CWE-89 |
| `ssrf-regex-bypass` | `http://10.0.0.40:1337` | SSRF | CWE-918, outside OWASP Top 10:2025 |
| `xss-christmas` | `http://10.0.0.40:1338` | Reflected XSS / Type Confusion | A05:2025, CWE-79/CWE-843 |

## Report Structure

Create a `.md` or `.docx` report with:

1. Header: full name, group, lab number, date.
2. One subsection per solved stand:
   - address and vulnerability class;
   - recon/visible stack/input points;
   - code review evidence;
   - exploitation command or theoretical payload;
   - why the protection failed;
   - remediation.

Detailed theory, OWASP mapping, defense questions, and fix principles: see `references/lab2-theory.md`.
