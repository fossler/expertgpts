"""Application-wide constants for ExpertGPTs.

This module centralizes all magic numbers, thresholds, and configuration
values used throughout the application.
"""

# DeepSeek API Constants
DEEPSEEK_MAX_CONTEXT_TOKENS = 128000
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_TEMPERATURE = 1.0

# Example Experts Configuration
EXAMPLE_EXPERTS_COUNT = 7  # Number of default/example experts created during setup

# Context Usage Thresholds (percentages)
CONTEXT_USAGE_SAFE_THRESHOLD = 50
CONTEXT_USAGE_WARNING_THRESHOLD = 75
CONTEXT_USAGE_ALERT_THRESHOLD = 90

# Context Usage Colors (emojis for UI display)
CONTEXT_USAGE_COLORS = {
    "safe": "🟢",
    "warning": "🟡",
    "alert": "🟠",
    "critical": "🔴"
}

# Cache TTLs (seconds)
CONFIG_CACHE_TTL = 300
TOKEN_COUNT_CACHE_TTL = 60
SYSTEM_PROMPT_CACHE_TTL = 300


# Documentation Content
EXPERT_BEHAVIOR_DOCS = """
### 🎯 Why This Field Matters Most

The behavior instructions define your expert's entire approach:
- **Tone**: Friendly, professional, casual, formal?
- **Expertise**: General overview or deep technical details?
- **Format**: Code examples, step-by-step, conversational?
- **Constraints**: What should the expert NOT do?
- **Guidelines**: Specific requirements for responses

### 📝 Example: Python Expert

```
You are a Python expert with 15 years of experience.
- Provide clean, PEP 8-compliant code with type hints and docstrings
- Explain concepts clearly with practical examples
- Warn about common pitfalls and best practices
- Suggest helpful libraries when appropriate
```

### 📝 Example: Legal Advisor

```
You are a legal assistant providing general legal information.
- Always include a disclaimer: "I am not a lawyer, this is not legal advice"
- Be thorough but cautious in recommendations
- Suggest consulting a qualified attorney for specific legal matters
- Provide general legal concepts and frameworks
```

### 📝 Example: Writing Coach

```
You are an encouraging writing coach.
- Ask questions to understand the writer's goals
- Provide specific, actionable feedback
- Balance praise with constructive criticism
- Suggest resources for improvement
- Be patient and supportive
```
"""

EXPERT_BEHAVIOR_DOCS_EDIT = """
### 🎯 Why This Field Matters Most

The behavior instructions define your expert's entire approach:
- **Tone**: Friendly, professional, casual, formal?
- **Expertise**: General overview or deep technical details?
- **Format**: Code examples, step-by-step, conversational?
- **Constraints**: What should the expert NOT do?
- **Guidelines**: Specific requirements for responses

### 💡 Tip
Leaving this empty will keep the expert's current behavior. Only edit if you want to change how they respond!
"""
