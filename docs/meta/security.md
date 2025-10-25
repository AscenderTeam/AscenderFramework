---
title: Security Policy — Ascender Framework
---

# 🔒 Security Policy — Ascender Framework

> **Last updated:** 2025-10-21  
> **Maintained by:** Ascender Framework Core Team (Ascender Team)   
> **Repository source:** [https://github.com/AscenderTeam/AscenderFramework](https://github.com/ascenderteam/ascenderframework)

---

## 1. Overview

The **Ascender Framework** and its associated packages are maintained with a strict security posture.
This document defines the **mandatory protocols** for vulnerability handling, responsible disclosure,
dependency integrity, and internal security governance.

Security is treated as **a first-class runtime concern**, not an afterthought.

---

## 2. Reporting a Vulnerability

If you believe you’ve discovered a security vulnerability in any Ascender Framework repository or
Ascender-based library, **do not open a public issue**.

### 📩 Confidential Report Channel

- **Email:** `security@ascender-framework.com`
- **PGP Key:** Available on request via email
- **Response SLA:** Within **72 hours** (business days)
- **Fix Target SLA:** Within **14 days** for critical issues, **30 days** for moderate issues

### Your Report Must Include:
1. A clear and reproducible description of the issue.
2. Proof of concept (if possible) - do **not** include harmful payloads.
3. Affected version(s) and environment (Python, OS, runtime, use `ascender version --raw` and provide its output).
4. Potential impact and suggested mitigation (if known).

---

## 3. Security Severity Levels

| Level | Description | Expected Response |
|-------|--------------|-------------------|
| **Critical** | Remote code execution, data leak, privilege escalation | Fix within 14 days, immediate advisory |
| **High** | Auth bypass, injection vectors, dependency exploit | Fix within 21 days |
| **Moderate** | Local DoS, misconfiguration vulnerability | Fix within 30 days |
| **Low** | Information disclosure, logging detail leakage | Fix within 45 days |

---

## 4. Disclosure Protocol

1. Reports are triaged **privately** by the Ascender Security Maintainers.
2. A confirmation will be sent to the reporter within 72 hours.
3. A fix or mitigation plan will be created and tracked privately.
4. Public disclosure happens **only after the fix has been released** and validated.
5. Reporters will be credited unless they request anonymity.

---

## 5. Dependency Integrity

All dependencies are vetted for:
- License compatibility (MIT / Apache 2.0 / BSD-3 preferred)
- Supply chain safety (verified via hash pinning)
- CVE scanning (automated via GitHub Actions security scanner)

If you maintain an Ascender extension or plugin, you **must**:
- Avoid dynamic imports from untrusted sources.
- Verify all third-party dependencies with pinned versions.
- Use `requirements.lock` or Poetry lock files under version control.

---

## 6. Runtime Security Guidelines

Ascender Framework enforces runtime security across all layers:

| Domain | Enforcement |
|--------|--------------|
| **Dependency Injection (DI)** | All providers are sandboxed by scope and resolved through verified injectors. |
| **Guards & Middleware** | Guard chains are executed with strict context isolation. |
| **Logging** | Sensitive data (tokens, passwords, API keys) must never appear in logs. |
| **Network IO** | HTTP clients and other custom endpoints must validate TLS and sanitize payloads. |
| **Serialization** | Only use Ascender Core’s internal serializers. Do not eval() or unpickle unknown data. |

---

## 7. Version Support Policy

Only the following releases receive security updates:

| Branch | Status | End of Support |
|---------|---------|----------------|
| `2.0.x` | ✅ Active (LTS) | April 2026 |
| `1.3.x` | ⚠️ Security-only | December 2025 |
| `<1.2`  | ❌ Unsupported | N/A |

---

## 8. Responsible Research

We welcome ethical security research under the following conditions:
- Testing must **never** impact production systems or user data.
- Do not publicly exploit vulnerabilities before coordinated disclosure.
- Do not use exploits to gain access to non-public data or repositories.

Violations of these rules may result in a permanent ban from all Ascender projects.

---

## 9. Contact

For any security-related inquiries:

**Ascender Framework Security Team**  
📧 security@ascender-framework.com  
🌐 https://ascender-framework.com/meta/security  

---

**Ascender Framework** is committed to maintaining enterprise-grade security practices
and transparent communication with the open-source community.

> “Reliability is not a feature — it’s the foundation.” — *Ascender Team*
