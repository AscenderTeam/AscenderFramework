---
title: Contributing
---

# Contributing to Ascender Framework

## 1. GITFLOW POLICY (MANDATORY)

The repository follows a strict GitFlow branching model.
Direct commits to `main` or `dev` are **forbidden**.
All work must be performed through feature branches and merged via Pull Requests.

### 1.1 Branch Structure

| Branch       | Purpose                                             | Rules              |
| ------------ | --------------------------------------------------- | ------------------ |
| `main`       | Production-ready code. Only maintainers merge here. | Protected.         |
| `dev`        | Active development branch.                          | Protected.         |
| `feature/*`  | New features.                                       | Branch from `dev`. |
| `fix/*`      | Bug fixes.                                          | Branch from `dev`. |
| `refactor/*` | Structural or performance refactors.                | Branch from `dev`. |
| `docs/*`     | Documentation updates.                              | Branch from `dev`. |
| `test/*`     | Testing or SpecTest modifications.                  | Branch from `dev`. |
| `release/*`  | Pre-release staging.                                | Maintainers only.  |

#### Example

```bash
git checkout dev
git pull
git checkout -b feature/core-di-lazy-injection
# work
git push origin feature/core-di-lazy-injection
```

Pull Requests must always target `dev`.

---

## 2. COMMIT MESSAGE FORMAT

All commits must use **Conventional Commits** with explicit scopes.

```
<type>(<scope>): <summary>
```

### 2.1 Allowed Types

| Type     | Description                              |
| -------- | ---------------------------------------- |
| feat     | Introduces a new feature                 |
| fix      | Fixes a bug                              |
| refactor | Refactors code without changing behavior |
| docs     | Documentation updates                    |
| test     | Adds or updates tests                    |
| chore    | Build / config / CI changes              |
| style    | Code style or formatting only            |
| perf     | Performance optimization                 |

### 2.2 Allowed Scopes

`core`, `common`, `testing`, `contrib`, `guards`, `schematics`, followed by submodules if applicable.

**Examples**

```
feat(core.di): add lazy injection mode
fix(core.logger): resolve circular dependency
refactor(schematics.controller): clean CLI structure
docs(core.applications): update app bootstrap example
```

Improperly formatted commits will be rejected during review.

---

## 3. PULL REQUEST FORMAT

Pull Requests must follow `.github/PULL_REQUEST_TEMPLATE.md`.
All sections are required unless explicitly marked optional.

### 3.1 Example of Properly Filled PR

```
## Pull Request Checklist
- [x] I have read the CONTRIBUTING guidelines
- [x] My code follows the code style
- [x] I added documentation
- [x] I added tests
- [x] All tests passed

## Pull Request Type
Feature

## Description of current behavior
Dependency Injection eagerly instantiates all services, increasing boot time.

## Description of changes
Added `lazy=True` parameter to `@Injectable()` decorator. Updated injector and SpecTests.

## Affected Packages
core.di, testing

## Breaking Changes
- [ ] No

## Additional Context
Boot time reduced by ~30%.
```

Pull Requests missing information or containing mixed concerns will be closed.

---

## 4. CODE STYLE AND RULES

### 4.1 General

* Code must be formatted with `black` and `isort`.
* Use `mypy --strict`.
* Use explicit imports only. `from x import *` is prohibited.
* Use full type hints. Bare parameters or return types are not accepted.
* Maintain SRP (Single Responsibility Principle).
  Each class or module must handle one concern only.
* Public classes and functions must include a one-line docstring.
* Keep files under 800 lines unless technically unavoidable.

### 4.2 Prohibited Patterns

* `print()` statements — use `ASC_LOGGER`.
* Commented-out code.
* Mixed commits (features + fixes + refactor in one).
* Manual dependency injection (`service = SomeService()`).
  Always use the DI container and decorators.
* Runtime modifications of providers.

### 4.3 Required Practices

* Run `poetry run black . && poetry run isort .` before committing.
* Write deterministic tests.
* Follow naming conventions:

  * Classes: `PascalCase`
  * Functions: `snake_case`
  * Private fields: `_field`
  * Constants: `UPPER_CASE`
* Avoid side effects in module scope.

---

## 5. TESTING REQUIREMENTS

Ascender Framework uses **Specification Tests** (SpecTests).

### 5.1 Running Tests

```bash
ascender spec-tests start
```

### 5.2 Requirements

* Every new feature must include corresponding SpecTests.
* Existing tests must pass before submission.
* Tests must not rely on network or random behavior.
* CI runs all tests; failing builds are automatically rejected.

---

## 6. ENVIRONMENT

* Python **3.13+** required.
* Dependency management via Poetry only.
* No third-party DI, ORM, or logging libraries allowed.
* Linting: `black`, `flake8`, `isort`.
* Type checking: `mypy --strict`.
* Supported OS: macOS, Linux, Windows (partial).

---

## 7. SECURITY

Security vulnerabilities or data leaks must be reported privately to maintainers.
Do **not** open public issues for security-sensitive topics.
See `SECURITY.md` for reporting procedure.

---

## 8. WHEN NOT TO WRITE CODE

Do **not** submit new code when:

* The functionality already exists.
* The change is cosmetic or stylistic without functional benefit.
* The same effect can be achieved through configuration or refactor.
* The proposal breaks modular boundaries (e.g., core logic in `schematics`).

Instead, open a **Feature Request** issue describing the problem, rationale, and impact.
Code contributions for unapproved concepts will be closed.

---

## 9. REVIEW AND MERGE POLICY

1. All PRs require successful CI checks (lint, type, test).
2. Each PR is reviewed for:

   * Code quality and adherence to standards.
   * Correct commit and branch naming.
   * Documentation completeness.
   * Absence of unrelated modifications.
3. Approved PRs are squashed and merged into `dev`.
4. Only maintainers merge `dev` into `main`.

Unreviewed or failing PRs are not merged under any condition.

---

## 10. CONTRIBUTOR CONDUCT

* Maintain professionalism in all discussions.
* Respect maintainers’ final decisions.
* Follow all policies stated in this document.

Failure to comply with any rule in this document may result in PR rejection or contributor suspension.

---

## 11. CONTRIBUTOR COMMANDS REFERENCE

| Task                | Command                                    |
| ------------------- | ------------------------------------------ |
| Generate components | `ascender g controller <name>`             |
| Run server          | `ascender run serve`                       |
| Run SpecTests       | `ascender run tests run -m framework`      |
| Format code         | `poetry run black . && poetry run isort .` |
| Type check          | `poetry run mypy --strict`                 |


