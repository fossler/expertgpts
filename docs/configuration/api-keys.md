# API Keys Management Guide

This guide explains how to securely manage API keys for LLM providers in ExpertGPTs.

## Overview

ExpertGPTs supports multiple LLM providers, each requiring an API key for authentication. API keys are stored securely using Streamlit's secrets management system.

## Supported Providers

| Provider | API Key Name | Base URL | Documentation |
|----------|--------------|----------|---------------|
| **DeepSeek** | `DEEPSEEK_API_KEY` | `https://api.deepseek.com` | [DeepSeek API Docs](https://api-docs.deepseek.com/) |
| **OpenAI** | `OPENAI_API_KEY` | `https://api.openai.com/v1` | [OpenAI API Docs](https://platform.openai.com/docs/api-reference) |
| **Z.AI** | `ZAI_API_KEY` | `https://api.z.ai/api/paas/v4` | [Z.AI Documentation](https://docs.z.ai/) |
| **KIMI** | `MOONSHOT_API_KEY` | `https://api.moonshot.ai/v1` | [KIMI API Docs](https://platform.kimi.ai/docs) |

**Voice input**: the chat toolbox transcribes voice messages with OpenAI's `gpt-transcribe` (experts using OpenAI, needs `OPENAI_API_KEY`) or Z.AI's `glm-asr-2512` (all other experts, needs `ZAI_API_KEY`). See `lib/audio/transcription.py`.

## Setting API Keys

### Via Settings Page (Recommended)

The Settings page provides a secure, user-friendly interface for API key management.

**Steps**:

1. Navigate to **Settings** in the app
2. Go to the **API Key** tab
3. Select the provider in the **Select LLM Provider** dropdown (DeepSeek, OpenAI, Z.AI, or KIMI)
4. Enter your API key in the input field
5. Click **"Save API Key"**

**What Happens**:
- Key format is validated per provider (see `validate_api_key()` in `lib/shared/helpers.py`)
- Key is saved to `.streamlit/secrets.toml`
- File permissions automatically set to 600 (owner read/write only)
- The app reruns and the key is available immediately

**Benefits**:
- Automatic validation
- Secure file permissions
- No manual file editing
- Immediate feedback

### Manual Configuration

For advanced users or automated setup.

**Steps**:

1. **Copy the example file**:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

2. **Edit the file**:
   ```bash
   vim .streamlit/secrets.toml
   # or use your preferred editor
   ```

3. **Add your API keys**:
   ```toml
   DEEPSEEK_API_KEY = "sk-your-deepseek-key-here"
   OPENAI_API_KEY = "sk-your-openai-key-here"
   ZAI_API_KEY = "your-zai-key-here"
   MOONSHOT_API_KEY = "sk-your-kimi-key-here"
   ```

4. **Set secure permissions**:
   ```bash
   chmod 600 .streamlit/secrets.toml
   ```

5. **Verify permissions**:
   ```bash
   ls -la .streamlit/secrets.toml
   # Should show: -rw-------
   ```

## Getting API Keys

### DeepSeek API Key

**URL**: [https://platform.deepseek.com/](https://platform.deepseek.com/)

**Steps**:
1. Sign up or log in to DeepSeek platform
2. Navigate to API Keys section
3. Create new API key
4. Copy key (starts with `sk-`)
5. Paste into ExpertGPTs Settings

**Pricing** (as of 2025):
- Very cost-effective
- Suitable for development and production
- Check platform for current rates

### OpenAI API Key

**URL**: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

**Steps**:
1. Sign up or log in to OpenAI platform
2. Navigate to API Keys section
3. Create new API key
4. Copy key (starts with `sk-`)
5. Paste into ExpertGPTs Settings

**Pricing** (as of 2025):
- Higher cost but advanced capabilities
- gpt-6.1-sol (default) offers advanced reasoning capabilities (1.05M context)
- Check platform for current rates

### Z.AI API Key

**URL**: [https://z.ai/manage-apikey/subscription](https://z.ai/manage-apikey/subscription)

**Steps**:
1. Sign up or log in to Z.AI platform
2. Navigate to API section
3. Generate API key
4. Copy key
5. Paste into ExpertGPTs Settings

**Characteristics**:
- GLM models optimized for Chinese
- Competitive pricing
- Good for multilingual applications
- Also used for voice input (`glm-asr-2512`) for all non-OpenAI experts

### KIMI API Key

**URL**: [https://platform.kimi.ai/console](https://platform.kimi.ai/console)

**Steps**:
1. Sign up or log in to the KIMI (Moonshot AI) platform
2. Navigate to API Keys section
3. Create new API key
4. Copy key (starts with `sk-`)
5. Paste into ExpertGPTs Settings

## API Key Security

### Security Features

ExpertGPTs implements multiple security layers:

**1. File Permissions**
- Automatically set to 600 (owner read/write only)
- Verified on every save operation
- Manual setup requires chmod

**2. Git Ignore**
- `.streamlit/secrets.toml` is gitignored
- Never committed to version control
- Example file provided instead

**3. Validation**
- Provider-specific format check (regex) before saving
- Clear error messages with an example of the expected format

**4. Secure Storage**
- Read directly from `.streamlit/secrets.toml` (`lib/config/secrets_manager.py`)
- Never logged or printed
- Redacted from error messages (`sanitize_error_message()`)

### Verifying Security

**Check file permissions**:
```bash
ls -la .streamlit/secrets.toml
# Expected: -rw------- (600 permissions)
```

**If permissions are incorrect**:
```bash
chmod 600 .streamlit/secrets.toml
```

**Check git status**:
```bash
git status
# secrets.toml should NOT appear in untracked files
```

### Security Best Practices

**Do ✅**:
- Set file permissions to 600
- Use environment-specific keys (dev vs prod)
- Rotate keys periodically
- Monitor usage on provider platforms
- Revoke unused keys

**Don't ❌**:
- Commit keys to version control
- Share keys in chat/email
- Use production keys in development
- Log keys in plain text
- Ignore permission warnings

## Using Multiple Providers

### Configuring All Providers

You can configure API keys for all providers simultaneously:

**Via Settings Page**:
1. Go to Settings → API Key tab
2. Select a provider in the dropdown
3. Enter its key and click **"Save API Key"**
4. Repeat for the other providers
5. Each saved independently

**Manual Configuration**:
```toml
DEEPSEEK_API_KEY = "sk-deepseek-key"
OPENAI_API_KEY = "sk-openai-key"
ZAI_API_KEY = "zai-key"
MOONSHOT_API_KEY = "sk-kimi-key"
```

### Switching Between Providers

Once configured, you can use different providers per expert:

1. Go to expert's page
2. Open the model dropdown in the chat toolbox below the chat input (it lists all models of providers with an API key)
3. Select a model of the desired provider
4. The choice is saved to the expert's config right away; the expert uses that provider's API key

**Use Cases**:
- Use **DeepSeek** for cost-effective daily tasks
- Use **OpenAI** for complex reasoning tasks
- Use **Z.AI** or **KIMI** for Chinese language optimization

## Troubleshooting API Keys

### "Invalid API Key" Error

**Symptoms**: Error message when trying to chat with expert

**Possible Causes**:
1. API key entered incorrectly
2. API key expired or revoked
3. Insufficient credits/quota
4. Wrong key for provider

**Solutions**:
1. **Verify key**: Re-check key in Settings → API Key
2. **Check provider dashboard**: Ensure key is active
3. **Check credits**: Verify sufficient balance
4. **Regenerate key**: Create new key if needed

**Diagnostic Steps**:
```bash
# Check key exists
cat .streamlit/secrets.toml

# Verify permissions
ls -la .streamlit/secrets.toml

# Test key manually (curl)
curl https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer YOUR_KEY"
```

### Key Not Saving

**Symptoms**: Click "Save API Key" but changes don't persist

**Possible Causes**:
1. Insufficient file permissions
2. Disk full
3. File locked by another process

**Solutions**:
1. **Check directory permissions**:
   ```bash
   ls -la .streamlit/
   # Should be drwxr-xr-x (755) or drwx------ (700)
   ```

2. **Check disk space**:
   ```bash
   df -h
   ```

3. **Manual configuration** (fallback):
   ```bash
   vim .streamlit/secrets.toml
   chmod 600 .streamlit/secrets.toml
   ```

### "Configuration Not Found" Error

**Symptoms**: Error when trying to access Settings → API Key

**Possible Cause**: `secrets.toml` file doesn't exist (saving a key via the Settings page also creates it)

**Solution**:
```bash
# Create from example
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Set permissions
chmod 600 .streamlit/secrets.toml

# Edit and add keys
vim .streamlit/secrets.toml
```

### Provider-Specific Issues

**DeepSeek**:
- Ensure key starts with `sk-` followed by lowercase hex characters
- Check platform status

**OpenAI**:
- Ensure key starts with `sk-` (e.g. `sk-proj-...`)
- Check organization settings if applicable
- Verify billing is set up

**Z.AI**:
- Expected format: 32 hex characters, a dot, 16 alphanumeric characters
- Verify account is active
- Contact Z.AI support if issues persist

**KIMI**:
- Ensure key starts with `sk-`
- Check balance in the KIMI console

## API Key Rotation

### When to Rotate Keys

**Recommended rotation**:
- **Every 90 days** for production environments
- **Immediately** if key is compromised
- **Periodically** for security best practices

### Rotation Steps

1. **Generate new key** on provider platform
2. **Update in ExpertGPTs**:
   - Via Settings page (recommended)
   - Or manually edit `secrets.toml`
3. **Test new key** by sending a message
4. **Revoke old key** on provider platform (after testing)

**Zero-Downtime Rotation**:
1. Add new key to `secrets.toml` (don't remove old yet)
2. Test with new key
3. Remove old key only after confirming new key works

## Environment-Specific Keys

### Development vs Production

**Best Practice**: Use different API keys for different environments

**Development Key**:
- Lower limits
- Separate usage tracking
- Easy to revoke if compromised

**Production Key**:
- Higher limits as needed
- Monitored closely
- Restricted access

**Implementation**:
```bash
# Development
cp .streamlit/secrets.toml.example .streamlit/secrets.toml.dev
# Add development keys

# Production
cp .streamlit/secrets.toml.example .streamlit/secrets.toml.prod
# Add production keys

# Use appropriate file for environment
```

### Environment Variables

ExpertGPTs does **not** read API keys from environment variables or `.env` files. Keys are loaded only from `.streamlit/secrets.toml` (no env var fallback, see `initialize_shared_session_state()` in `lib/shared/session_state.py`). For containerized deployments, mount or generate `secrets.toml` instead.

## API Key Monitoring

### Monitoring Usage

**Provider Dashboards**:
- DeepSeek: [https://platform.deepseek.com/usage](https://platform.deepseek.com/usage)
- OpenAI: [https://platform.openai.com/usage](https://platform.openai.com/usage)
- Z.AI: [https://z.ai/manage-apikey/subscription](https://z.ai/manage-apikey/subscription)
- KIMI: [https://platform.kimi.ai/console](https://platform.kimi.ai/console)

**What to Monitor**:
- Request count
- Token usage
- Cost accumulation
- Error rates

### Setting Alerts

**Recommended Alerts**:
- **Unusual usage spikes** (possible key compromise)
- **Budget thresholds** (cost control)
- **Error rate increases** (service issues)

## Best Practices Summary

### Security

1. ✅ Set file permissions to 600
2. ✅ Never commit to version control
3. ✅ Rotate keys regularly
4. ✅ Use different keys per environment
5. ✅ Monitor usage for anomalies

### Operational

1. ✅ Test keys after configuration
2. ✅ Have backup keys ready
3. ✅ Document rotation schedule
4. ✅ Use Settings page for management
5. ✅ Keep keys secure but accessible

### Development

1. ✅ Use example file as template
2. ✅ Validate before committing
3. ✅ Don't hardcode keys in code
4. ✅ Use `secrets.toml`, not environment variables (they are not read)
5. ✅ Test with free/low-cost tiers first

## File Reference

### secrets.toml Example

**Location**: `.streamlit/secrets.toml.example`

```toml
# Streamlit Secrets Configuration Example
#
# Copy this file to secrets.toml and add your actual API keys:
# cp .streamlit/secrets.toml.example .streamlit/secrets.toml
#
# IMPORTANT: secrets.toml is gitignored and should never be committed!
#
# You can also set your API key through the Settings page in the app,
# which will automatically save it to secrets.toml

# DeepSeek API Key
# Get your API key from: https://platform.deepseek.com/
DEEPSEEK_API_KEY = "your_deepseek_api_key_here"

# OpenAI API Key
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY = "your_openai_api_key_here"

# Z.AI API Key
# Get your API key from: https://z.ai/manage-apikey/subscription
ZAI_API_KEY = "your_zai_api_key_here"

# KIMI API Key (Moonshot AI)
# Get your API key from: https://platform.kimi.ai/console
MOONSHOT_API_KEY = "your_moonshot_api_key_here"
```

## Next Steps

- **[Configuration Overview](overview.md)** - Configuration system overview
- **[User Guide - Customization](../user-guide/customization.md)** - Settings page usage
- **[API Documentation](../api/providers.md)** - Provider-specific details

---

**Back to**: [Documentation Home](../README.md) | [Configuration Overview](overview.md)
