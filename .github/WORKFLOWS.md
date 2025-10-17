# GitHub Workflows Documentation

This document provides an overview of all GitHub Actions workflows configured for the Audiobook Creator TTS project.

## 📋 Table of Contents

- [Overview](#overview)
- [Workflows](#workflows)
  - [CI Pipeline](#ci-pipeline-ciyml)
  - [Dependency Security Check](#dependency-security-check-dependency-checkyml)
  - [Code Quality](#code-quality-code-qualityyml)
  - [Release Automation](#release-automation-releaseyml)
  - [Stale Issue Management](#stale-issue-management-staleyml)
  - [PR Labeler](#pr-labeler-pr-labeleryml)
  - [Welcome Bot](#welcome-bot-welcomeyml)
- [Dependabot Configuration](#dependabot-configuration)
- [Issue & PR Templates](#issue--pr-templates)
- [Badges](#badges)

---

## Overview

Our GitHub Actions workflows provide automated testing, quality checks, security scanning, and project management features. All workflows are designed to maintain high code quality and streamline development processes.

### Workflow Triggers

| Workflow | Push (main) | Pull Request | Schedule | Manual |
|----------|-------------|--------------|----------|--------|
| CI Pipeline | ✅ | ✅ | ❌ | ❌ |
| Dependency Check | ✅ | ✅ | ✅ Weekly | ✅ |
| Code Quality | ✅ | ✅ | ✅ Weekly | ✅ |
| Release | ❌ (tags only) | ❌ | ❌ | ✅ |
| Stale Management | ❌ | ❌ | ✅ Daily | ✅ |
| PR Labeler | ❌ | ✅ | ❌ | ❌ |
| Welcome Bot | ❌ (issues/PRs) | ❌ | ❌ | ❌ |

---

## Workflows

### CI Pipeline (ci.yml)

**Purpose:** Automated testing and validation on every push and pull request.

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Jobs:**

#### 1. Test Matrix
- **Python Versions:** 3.11, 3.12
- **Runs on:** Ubuntu Latest
- **Steps:**
  - Checkout code
  - Set up Python with pip caching
  - Install system dependencies (ffmpeg)
  - Install Python dependencies
  - Install Playwright browsers
  - Run Black formatting check
  - Run Flake8 linting (non-blocking)
  - Run unit tests with coverage
  - Run integration tests (non-blocking)
  - Upload coverage to Codecov
  - Generate coverage badge (main branch only)

#### 2. Code Quality Checks
- **Runs on:** Ubuntu Latest
- **Steps:**
  - Run Pylint analysis (non-blocking)
  - Run MyPy type checking (non-blocking)

#### 3. Build Verification
- **Runs on:** Ubuntu Latest
- **Steps:**
  - Verify requirements files
  - Check for Python syntax errors
  - Validate JSON files (voices.json)

**Exit Codes:**
- ✅ Success: All required checks pass
- ⚠️ Warning: Linting/type checking issues (non-blocking)
- ❌ Failure: Tests fail or syntax errors

---

### Dependency Security Check (dependency-check.yml)

**Purpose:** Monitor and audit dependencies for security vulnerabilities.

**Triggers:**
- Weekly schedule (Mondays at 9:00 UTC)
- Push to `main` (if requirements files change)
- Pull requests (if requirements files change)
- Manual dispatch

**Jobs:**

#### 1. Security Audit
- Run `safety` check for known vulnerabilities
- Run `pip-audit` for comprehensive security scanning
- Generate vulnerability reports

#### 2. Dependency Review (PR only)
- Review dependency changes in pull requests
- Fail on moderate+ severity vulnerabilities
- Block GPL-3.0 and AGPL-3.0 licenses

#### 3. Check Outdated Packages
- List all outdated dependencies
- Generate markdown report
- Upload as artifact

#### 4. License Compliance Check
- Scan all package licenses
- Generate license report with URLs
- Upload as artifact

**Artifacts:**
- `dependency-report.md` - Outdated packages report
- `licenses.md` - License compliance report

---

### Code Quality (code-quality.yml)

**Purpose:** Comprehensive code quality analysis and metrics.

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Weekly schedule (Sundays at 12:00 UTC)
- Manual dispatch

**Jobs:**

#### 1. Complexity Analysis
- **Tools:** Radon, Xenon, McCabe
- **Metrics:**
  - Cyclomatic complexity
  - Maintainability index
  - Complexity thresholds (max B, modules A, average A)

#### 2. Security Scanning
- **Tool:** Bandit
- **Output:** JSON and text reports
- **Scope:** Recursive scan of all Python files

#### 3. Code Duplication Check
- **Tool:** Pylint duplicate-code
- **Purpose:** Detect copy-paste code patterns

#### 4. Documentation Coverage
- **Tools:** Interrogate, pydocstyle
- **Requirements:**
  - Minimum 60% docstring coverage
  - PEP 257 compliance

#### 5. Code Metrics Report
- Lines of code (LOC)
- Cyclomatic complexity distribution
- Maintainability index scores

#### 6. Static Analysis
- Comprehensive Pylint analysis with reports
- Uploaded as artifact

**Artifacts:**
- `bandit-security-report.json` - Security scan results
- `code-metrics-report.md` - Comprehensive metrics
- `pylint-report.txt` - Static analysis results

---

### Release Automation (release.yml)

**Purpose:** Automated release creation and asset management.

**Triggers:**
- Push tags matching `v*.*.*` (e.g., v1.0.0)
- Manual dispatch with version input

**Jobs:**

#### 1. Create Release
- **Steps:**
  - Run all tests before release
  - Extract version from tag
  - Generate changelog from commits
  - Create release archive (tar.gz)
  - Generate requirements file hashes (SHA256)
  - Create GitHub Release with:
    - Release notes
    - Source archive
    - Requirements files with checksums
    - voices.json

#### 2. Publish Documentation
- Update release badges
- Trigger documentation updates

#### 3. Release Notification
- Create summary in GitHub Actions UI
- Link to new release

**Release Assets:**
- `audiobook-creator-tts-vX.X.X.tar.gz` - Source archive
- `requirements.txt` + SHA256 checksum
- `requirements-test.txt` + SHA256 checksum
- `voices.json` - Voice library configuration

---

### Stale Issue Management (stale.yml)

**Purpose:** Automated issue and PR lifecycle management.

**Triggers:**
- Daily schedule (00:00 UTC)
- Manual dispatch

**Jobs:**

#### 1. Close Stale Issues and PRs
- **Configuration:**
  - Issues: Stale after 60 days, close after 7 more days
  - PRs: Stale after 30 days, close after 14 more days
  - Labels: `stale` for marked items
  - Exempt: `keep-open`, `bug`, `enhancement`, etc.
  - Operations limit: 50 per run

#### 2. Label Inactive Issues
- Mark issues as `awaiting-response` after 30 days
- Add friendly reminder comment

#### 3. Organize and Triage Issues (Manual only)
- Auto-label based on keywords:
  - `bug` - for bug reports
  - `enhancement` - for feature requests
  - `documentation` - for doc issues
  - `question` - for questions
  - `security` - for security issues

---

### PR Labeler (pr-labeler.yml)

**Purpose:** Automatic pull request labeling based on changed files and PR size.

**Triggers:**
- Pull request opened, synchronized, or reopened

**Jobs:**

#### Auto-label Pull Requests
- **File-based labels:**
  - `documentation` - README, docs changes
  - `tests` - Test file changes
  - `dependencies` - Requirements changes
  - `ci` - GitHub Actions changes
  - `core` - Main application code
  - See `.github/labeler.yml` for full configuration

- **Size labels:**
  - `size/XS` - < 10 changes
  - `size/S` - < 50 changes
  - `size/M` - < 200 changes
  - `size/L` - < 500 changes
  - `size/XL` - ≥ 500 changes

- **Special labels:**
  - `breaking-change` - Breaking changes detected
  - `needs-review` - Automatic review request

---

### Welcome Bot (welcome.yml)

**Purpose:** Welcome new contributors with helpful information.

**Triggers:**
- New issue opened
- New pull request opened

**Jobs:**

#### 1. Welcome New Issue Contributors
- Detect first-time issue creators
- Post welcome message with:
  - Friendly greeting
  - What to expect next
  - Useful resources
- Add `first-time-contributor` label

#### 2. Welcome New PR Contributors
- Detect first-time PR creators
- Post welcome message with:
  - Contribution appreciation
  - Review process explanation
  - PR checklist
  - Useful resources
- Add `first-time-contributor` label

---

## Dependabot Configuration

**File:** `.github/dependabot.yml`

### Python Dependencies
- **Schedule:** Weekly (Mondays at 9:00 UTC)
- **PR Limit:** 5 open PRs max
- **Grouping:**
  - Production dependencies grouped by minor/patch
  - Development dependencies grouped by minor/patch
- **Labels:** `dependencies`, `python`
- **Commit prefix:** `deps` (production), `deps-dev` (development)

### GitHub Actions
- **Schedule:** Weekly (Mondays at 9:00 UTC)
- **PR Limit:** 3 open PRs max
- **Labels:** `dependencies`, `github-actions`
- **Commit prefix:** `ci`

---

## Issue & PR Templates

### Issue Templates

#### 🐛 Bug Report (`bug_report.yml`)
- Bug description
- Mode identification (Document/Text/Manual)
- Steps to reproduce
- Expected vs. actual behavior
- Environment details
- Error logs
- Checklist for common requirements

#### ✨ Feature Request (`feature_request.yml`)
- Problem statement
- Proposed solution
- Alternatives considered
- Category selection
- Priority level
- Use case description
- Implementation willingness

#### ❓ Question (`question.yml`)
- Question description
- Category selection
- What has been tried
- Environment (if relevant)
- Additional context
- Documentation checklist

### Pull Request Template

**File:** `.github/PULL_REQUEST_TEMPLATE.md`

**Sections:**
- Description
- Type of change (bug fix, feature, breaking change, etc.)
- Related issues
- Changes made
- Testing environment and test cases
- Comprehensive checklist
- Screenshots (if applicable)
- Additional notes

---

## Badges

Add these badges to your README for at-a-glance status:

```markdown
![CI Pipeline](https://github.com/[owner]/[repo]/workflows/CI%20Pipeline/badge.svg)
![Code Quality](https://github.com/[owner]/[repo]/workflows/Code%20Quality/badge.svg)
![Dependencies](https://github.com/[owner]/[repo]/workflows/Dependency%20Security%20Check/badge.svg)
![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)
```

---

## Workflow Maintenance

### Regular Tasks
- **Weekly:** Review Dependabot PRs
- **Monthly:** Review code quality metrics reports
- **Quarterly:** Update workflow versions and dependencies

### Customization
- Modify workflow triggers in each `.yml` file
- Adjust timeout values and retry logic as needed
- Update labeler rules in `.github/labeler.yml`
- Customize welcome messages in `welcome.yml`

### Debugging Workflows
- View workflow runs: Actions tab in GitHub
- Check individual job logs for details
- Use `workflow_dispatch` for manual testing
- Enable workflow debugging: Set `ACTIONS_STEP_DEBUG` secret to `true`

---

## Best Practices

1. **Keep workflows fast:** Use caching and parallel jobs
2. **Fail early:** Place critical checks first
3. **Use continue-on-error:** For informational checks
4. **Cache dependencies:** Speed up builds with pip caching
5. **Monitor workflow usage:** Review Actions usage in Settings
6. **Update regularly:** Keep actions versions current
7. **Test locally:** Use `act` to test workflows locally

---

## Support

For questions or issues with workflows:
1. Check workflow run logs in GitHub Actions
2. Review this documentation
3. See [.github/INDEX.md](INDEX.md) for configuration overview
4. Open an issue with the `ci` label
5. Consult [GitHub Actions documentation](https://docs.github.com/en/actions)

---

**Last Updated:** January 2025

*This documentation is generated from the actual workflow configurations. Keep it in sync with workflow changes.*
