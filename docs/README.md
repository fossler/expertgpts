# ExpertGPTs Documentation

Welcome to the ExpertGPTs documentation. This guide helps you find information quickly and efficiently.

## Quick Navigation

### For New Users

1. **[Quick Start](getting-started/quickstart.md)** - Get up and running in 5 minutes
2. **[First Use Guide](getting-started/first-use.md)** - Learn the basics
3. **[User Guide - Basics](user-guide/basics.md)** - Using experts

### For All Users

- **[Installation Guide](getting-started/installation.md)** - Detailed setup instructions
- **[Creating Experts](user-guide/creating-experts.md)** - Create custom experts
- **[Customization](user-guide/customization.md)** - Themes and settings
- **[Troubleshooting](reference/troubleshooting.md)** - Common issues and solutions

### For Developers

- **[Development Setup](development/setup.md)** - Development environment
- **[Architecture Overview](architecture/overview.md)** - System architecture
- **[Project Structure](development/project-structure.md)** - File organization
- **[Adding Features](development/adding-features.md)** - Feature development
- **[Testing Guide](development/testing.md)** - Testing documentation

## Documentation Structure

### Getting Started

Comprehensive guides for new users:

- **[Installation](getting-started/installation.md)** - Prerequisites, setup, verification
- **[Quick Start](getting-started/quickstart.md)** - 5-minute setup
- **[First Use](getting-started/first-use.md)** - Initial configuration and basics

### User Guide

Documentation for using ExpertGPTs:

- **[Basics](user-guide/basics.md)** - Chatting, navigation, provider selection
- **[Creating Experts](user-guide/creating-experts.md)** - Custom expert creation
- **[Customization](user-guide/customization.md)** - Themes, language, defaults
- **[Temperature Guide](user-guide/temperature-guide.md)** - Temperature settings

### Configuration

Technical configuration documentation:

- **[Overview](configuration/overview.md)** - Configuration system
- **[Expert Configs](configuration/expert-configs.md)** - YAML expert configurations
- **[API Keys](configuration/api-keys.md)** - API key management
- **[App Defaults](configuration/app-defaults.md)** - User preferences

### Architecture

System architecture and design:

- **[Overview](architecture/overview.md)** - High-level architecture
- **[Template System](architecture/template-system.md)** - Page generation
- **[Multi-Provider LLM](architecture/multi-provider-llm.md)** - LLM integration
- **[State Management](architecture/state-management.md)** - Session state

### Internationalization

- **[I18N Guide](internationalization/I18N_GUIDE.md)** - Comprehensive i18n documentation

### Development

Developer documentation:

- **[Setup](development/setup.md)** - Development environment
- **[Project Structure](development/project-structure.md)** - File organization
- **[Adding Features](development/adding-features.md)** - Feature development
- **[Testing](development/testing.md)** - Testing guide

### Reference

Reference documentation:

- **[Scripts](reference/scripts.md)** - Script documentation
- **[Troubleshooting](reference/troubleshooting.md)** - Common issues

### API

- **[Providers](api/providers.md)** - LLM provider APIs

## How to Use This Documentation

### By Role

**End Users**:
Start with → Quick Start → First Use → User Guide

**Administrators**:
Start with → Installation → Configuration → API Keys

**Developers**:
Start with → Architecture → Development Setup → Adding Features

**Contributors**:
Start with → Development Setup → Project Structure → Adding Features

### By Task

**I want to...**:

- **Get started**: [Quick Start](getting-started/quickstart.md)
- **Install the app**: [Installation](getting-started/installation.md)
- **Create an expert**: [Creating Experts](user-guide/creating-experts.md)
- **Customize the theme**: [Customization](user-guide/customization.md)
- **Set up API keys**: [API Keys](configuration/api-keys.md)
- **Understand the architecture**: [Architecture Overview](architecture/overview.md)
- **Contribute code**: [Development Setup](development/setup.md)
- **Fix an issue**: [Troubleshooting](reference/troubleshooting.md)

## Key Concepts

### Template-Based Architecture

ExpertGPTs uses a single template to generate all expert pages. See [Template System](architecture/template-system.md).

### Multi-Provider Support

ExpertGPTs integrates with DeepSeek, OpenAI, and Z.AI. See [Multi-Provider LLM](architecture/multi-provider-llm.md).

### Internationalization

Full support for 13 languages with automatic detection. See [I18N Guide](internationalization/I18N_GUIDE.md).

## Contributing to Documentation

When adding documentation:

1. Place in appropriate section (getting-started/, user-guide/, etc.)
2. Use consistent formatting
3. Add links to related docs
4. Update this README if adding new sections

## File Links

All documentation uses relative links:

- **To docs in same section**: `[filename](filename.md)`
- **To docs in other sections**: `[section/filename](section/filename.md)`
- **To root README**: `[../../README.md](../../README.md)`

## External Resources

- **GitHub Repository**: [https://github.com/fossler/expertgpts](https://github.com/fossler/expertgpts)
- **CLAUDE.md**: Project instructions for AI development
- **README.md**: Project overview and quick start

---

**Return to**: [Main README](../README.md)
