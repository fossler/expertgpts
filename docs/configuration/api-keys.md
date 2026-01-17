# API Keys Management Guide

This guide explains how to securely manage API keys for LLM providers in ExpertGPTs.

## Overview

ExpertGPTs supports multiple LLM providers, each requiring an API key for authentication. API keys are stored securely using Streamlit's secrets management system.

## Supported Providers

| Provider | API Key Name | Base URL | Documentation |
|----------|--------------|----------|---------------|
| **DeepSeek** | `DEEPSEEK_API_KEY` | `https://api.deepseek.com` | [DeepSeek API Docs](https://api-docs.deepseek.com/) |
| **OpenAI** | `OPENAI_API_KEY` | `https://api.openai.com/v1` | [OpenAI API Docs](https://platform.openai.com/docs/api-reference) |
| **Z.AI** | `ZAI_API_KEY` | `https://api.z.ai/v1` | [Z.AI Documentation](https://z.ai/) |

## Setting API Keys

### Via Settings Page (Recommended)

The Settings page provides a secure, user-friendly interface for API key management.

**Steps**:

1. Navigate to **Settings** in the app
2. Go to the **API Keys** tab
3. Select the provider tab (DeepSeek, OpenAI, or Z.AI)
4. Enter your API key in the input field
5. Click **"Save API Key"**

**What Happens**:
- Key is validated for minimum length (20 characters)
- Key is saved to `.streamlit/secrets.toml`
- File permissions automatically set to 600 (owner read/write only)
- Key available for use immediately

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
- o3-mini offers reasoning capabilities
- Check platform for current rates

### Z.AI API Key

**URL**: [https://z.ai/](https://z.ai/)

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
- Minimum 20 characters enforced
- Format validation via UI
- Clear error messages

**4. Secure Storage**
- Only accessed via Streamlit secrets API
- Never logged or printed
- Not included in error messages

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
1. Go to Settings → API Keys tab
2. Enter DeepSeek key in DeepSeek tab
3. Enter OpenAI key in OpenAI tab
4. Enter Z.AI key in Z.AI tab
5. Each saved independently

**Manual Configuration**:
```toml
DEEPSEEK_API_KEY = "sk-deepseek-key"
OPENAI_API_KEY = "sk-openai-key"
ZAI_API_KEY = "zai-key"
```

### Switching Between Providers

Once configured, you can use different providers per expert:

1. Go to expert's page
2. Use "Provider" dropdown in sidebar
3. Select desired provider
4. Expert uses that provider's API key

**Use Cases**:
- Use **DeepSeek** for cost-effective daily tasks
- Use **OpenAI** for complex reasoning tasks
- Use **Z.AI** for Chinese language optimization

## Troubleshooting API Keys

### "Invalid API Key" Error

**Symptoms**: Error message when trying to chat with expert

**Possible Causes**:
1. API key entered incorrectly
2. API key expired or revoked
3. Insufficient credits/quota
4. Wrong key for provider

**Solutions**:
1. **Verify key**: Re-check key in Settings → API Keys
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

**Symptoms**: Error when trying to access Settings → API Keys

**Possible Cause**: `secrets.toml` file doesn't exist

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
- Ensure key starts with `sk-`
- Minimum 20 characters
- Check platform status

**OpenAI**:
- Ensure key starts with `sk-`
- Check organization settings if applicable
- Verify billing is set up

**Z.AI**:
- Check key format
- Verify account is active
- Contact Z.AI support if issues persist

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

### Environment Variables (Advanced)

For containerized deployments:

```bash
# Set environment variables
export DEEPSEEK_API_KEY="sk-key"
export OPENAI_API_KEY="sk-key"

# Or in .env file (gitignored)
echo "DEEPSEEK_API_KEY=sk-key" > .env
echo "OPENAI_API_KEY=sk-key" >> .env
```

**Note**: ExpertGPTs primarily uses `secrets.toml` for local development.

## API Key Monitoring

### Monitoring Usage

**Provider Dashboards**:
- DeepSeek: [https://platform.deepseek.com/](https://platform.deepseek.com/)
- OpenAI: [https://platform.openai.com/usage](https://platform.openai.com/usage)
- Z.AI: Check provider dashboard

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
4. ✅ Use secrets API, not environment variables
5. ✅ Test with free/low-cost tiers first

## File Reference

### secrets.toml Example

**Location**: `.streamlit/secrets.toml.example`

```toml
# ExpertGPTs API Keys Configuration
#
# Copy this file to secrets.toml and add your actual API keys
#
# IMPORTANT: Never commit secrets.toml to version control!
# The .gitignore file is configured to ignore secrets.toml
#
# Security: File permissions should be 600 (owner read/write only)
# Set with: chmod 600 .streamlit/secrets.toml

# DeepSeek API Key
# Get your key at: https://platform.deepseek.com/
DEEPSEEK_API_KEY = ""

# OpenAI API Key
# Get your key at: https://platform.openai.com/api-keys
OPENAI_API_KEY = ""

# Z.AI API Key
# Get your key at: https://z.ai/
ZAI_API_KEY = ""
```

## Next Steps

- **[Configuration Overview](overview.md)** - Configuration system overview
- **[User Guide - Customization](../user-guide/customization.md)** - Settings page usage
- **[API Documentation](../api/providers.md)** - Provider-specific details

---

**Back to**: [Documentation Home](../README.md) | [Configuration Overview](overview.md)
