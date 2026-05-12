# Lab 2 Theory Reference

## OWASP Top 10:2025 Notes

- A03:2025 is Software Supply Chain Failures.
- A05:2025 is Injection and includes SQL injection and XSS.
- A10:2025 is Mishandling of Exceptional Conditions.
- SSRF is not a separate OWASP Top 10:2025 category, but remains important through CWE-918 and OWASP WSTG.
- A07:2025 is Authentication Failures.
- A09:2025 is Security Logging and Alerting Failures.

## Stand Mapping

- A01 Broken Access Control: `idor-basic-role`, `idor-invalid-if-statement`, `pathTraversal-improper-regex`.
- A02 Security Misconfiguration: `file-upload-extension-blacklist`.
- A05 Injection: `sqli-blind-variable-mixup`, `xss-christmas`.
- A06 Insecure Design: `csrf-change-email`.
- A10 Mishandling of Exceptional Conditions: fail-open elements in `pathTraversal-improper-regex`.
- Outside Top 10:2025: `ssrf-regex-bypass` as CWE-918.

## Universal Vulnerability Analysis Flow

1. Reconnaissance: identify app behavior, stack, endpoints, headers, cookies.
2. Code review: find untrusted input sources, checks, and sinks.
3. Hypothesis: state the expected vulnerability and reason.
4. Exploitation: confirm with a minimal payload, or document a precise theoretical payload.
5. Root cause: explain why the protection failed mechanically.
6. Impact: state worst-case attacker outcome.
7. Remediation: fix the vulnerability class, not one payload.

## Principles Behind the Lab Bugs

- Whitelist beats blacklist: especially for upload extensions and SSRF hosts.
- Never trust client-controlled authority: cookies, roles, hidden fields, and request origin are attacker-controlled.
- Validate canonicalized data, not raw strings: path traversal filters must resolve paths before checking boundaries.
- Parsers and type coercion matter: `Array.prototype.includes` differs from `String.prototype.includes`; PHP variable mixups can leave tainted values alive.
- Authorization belongs on the server and should be centralized through middleware/decorators/policies.

## Remediation Patterns

- CSRF: use synchronizer token or double-submit cookie, set `SameSite`, validate method semantics, and avoid state-changing GET requests.
- File upload: use allowlisted extensions and MIME/content checks, generate server-side filenames, store outside executable web roots, disable script execution in upload directories.
- IDOR/access control: use server-side sessions and object-level authorization checks for every resource.
- Path traversal: resolve `realpath()` against a fixed base directory and reject paths outside it.
- SQL injection: use prepared statements with bound parameters; avoid SQL string concatenation.
- SSRF: prefer allowlisted destinations, resolve and pin IPs, block private/link-local ranges, enforce egress controls and timeouts.
- XSS: enforce expected input types, context-aware output encoding, safe templating, CSP, and Trusted Types where available.

## Minimal Tooling

- `curl` for HTTP requests and evidence.
- Browser DevTools for cookies, forms, and network requests.
- Small HTML files for CSRF PoCs.
- `base64` for forged cookie values.
- Burp/ZAP and `sqlmap` may help, but manual understanding should be documented first.
