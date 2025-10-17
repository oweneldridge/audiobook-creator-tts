# GitHub Configuration

This directory contains all GitHub-specific configurations for the Audiobook Creator TTS project.

## 📁 Directory Structure

```
.github/
├── workflows/              # GitHub Actions workflows
│   ├── ci.yml             # CI/CD pipeline
│   ├── code-quality.yml   # Code quality checks
│   ├── dependency-check.yml # Security and dependency auditing
│   ├── pr-labeler.yml     # Automatic PR labeling
│   ├── release.yml        # Release automation
│   ├── stale.yml          # Stale issue management
│   └── welcome.yml        # Welcome new contributors
├── ISSUE_TEMPLATE/        # Issue templates
│   ├── bug_report.yml     # Bug report template
│   ├── feature_request.yml # Feature request template
│   └── question.yml       # Question template
├── PULL_REQUEST_TEMPLATE.md # PR template
├── dependabot.yml         # Dependabot configuration
├── labeler.yml           # Auto-labeling rules
├── WORKFLOWS.md          # Workflow documentation
└── README.md             # This file
```

## 🚀 Quick Links

- **[Workflows Documentation](WORKFLOWS.md)** - Detailed workflow information
- **[Actions Tab](../../actions)** - View workflow runs
- **[Issues](../../issues)** - Project issues
- **[Pull Requests](../../pulls)** - Open pull requests

## 🔧 Workflows Overview

### Automated Testing & Quality

| Workflow | Purpose | Trigger |
|----------|---------|---------|
| **CI Pipeline** | Run tests, linting, formatting checks | Push, PR |
| **Code Quality** | Complexity, security, documentation analysis | Push, PR, Weekly |
| **Dependency Check** | Security audits, license compliance | Weekly, PR |

### Project Management

| Workflow | Purpose | Trigger |
|----------|---------|---------|
| **Stale Management** | Close inactive issues/PRs | Daily |
| **PR Labeler** | Auto-label PRs by size and files | PR events |
| **Welcome Bot** | Greet first-time contributors | New issues/PRs |

### Release Management

| Workflow | Purpose | Trigger |
|----------|---------|---------|
| **Release Automation** | Create releases with assets | Tag push |

## 📋 Issue & PR Templates

### Issue Templates

- **🐛 Bug Report** - Report bugs with structured format
- **✨ Feature Request** - Suggest new features
- **❓ Question** - Ask questions about the project

### Pull Request Template

Comprehensive template with:
- Change description
- Type classification
- Testing checklist
- Related issues linking

## 🤖 Dependabot

Automated dependency updates for:
- **Python packages** (weekly)
- **GitHub Actions** (weekly)

Grouped updates by:
- Production dependencies
- Development dependencies

## 🏷️ Auto-labeling

PRs are automatically labeled based on:
- **Files changed** (tests, docs, dependencies, etc.)
- **PR size** (XS, S, M, L, XL)
- **Content** (breaking changes, etc.)

## 📊 Status Badges

Add these to your README:

```markdown
![CI](https://github.com/owner/repo/workflows/CI%20Pipeline/badge.svg)
![Quality](https://github.com/owner/repo/workflows/Code%20Quality/badge.svg)
![Security](https://github.com/owner/repo/workflows/Dependency%20Security%20Check/badge.svg)
```

## 🛠️ Customization

### Modify Workflows
Edit files in `workflows/` directory. Each workflow is well-commented.

### Update Templates
Modify templates in `ISSUE_TEMPLATE/` or `PULL_REQUEST_TEMPLATE.md`.

### Configure Dependabot
Edit `dependabot.yml` to change:
- Update schedule
- PR limits
- Grouping rules

### Adjust Labels
Edit `labeler.yml` to customize auto-labeling rules.

## 📖 Documentation

For detailed workflow documentation, see [WORKFLOWS.md](WORKFLOWS.md).

## 🙏 Credits

These workflows follow GitHub Actions best practices and community standards.

---

**Last Updated:** January 2025
