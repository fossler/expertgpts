# Creating Custom Experts

This guide explains how to create effective custom expert agents tailored to your specific needs.

## Overview

ExpertGPTs allows you to create unlimited custom experts, each specialized in a particular domain or task. Each expert has:
- Independent conversation history
- Customizable name and description
- Adjustable temperature settings
- Optional custom system prompts
- Provider and model selection

## Creating an Expert via UI

### Step-by-Step Process

1. **Navigate to Home Page**
   - Alternatively use **"➕ Add new Chat"** in **Settings** → **Expert Management**

2. **Click "➕ Add Chat"** in the sidebar Toolbox

3. **Fill in the Form**:
   - **LLM Provider & Model**: Provider, model, thinking mode and temperature (default 1.0; range depends on the provider)
   - **Expert Name**: A descriptive name for the expert
   - **Agent Description**: What the expert specializes in
   - **Customize Expert Behavior** (optional): Custom system prompt instead of the auto-generated one

4. **Click "Create Expert"**
   - Expert page automatically generated
   - Expert configuration saved to `configs/{expert_id}.yaml`
   - Expert page created in `pages/{expert_id}.py`
   - Automatically navigated to new expert page

### Expert Creation Form Fields

#### Expert Name

**Purpose**: Identifies the expert in navigation and chat interface

**Guidelines**:
- Use descriptive, clear names
- Allowed characters: letters A-Z/a-z, numbers, spaces, underscores (_), hyphens (-) and dots (.); other characters (including umlauts, accents and CJK characters) are rejected
- 3-50 characters recommended

**Examples**:
- ✅ "SQL Expert"
- ✅ "Legal Advisor"
- ✅ "Datenexperte" (German)
- ❌ "数据分析师" (non-ASCII characters; use the description for other languages)
- ❌ "Expert/Manager\Analyst" (special characters)

#### Agent Description

**Purpose**: Describes the expert's domain and capabilities

**Guidelines**:
- Be specific about expertise areas
- Mention what the expert can and cannot do
- 1-3 sentences recommended
- If description is provided without custom system prompt, an AI-generated system prompt will be created automatically based on the description

**Examples**:

✅ **Good**:
```
Expert in SQL database design, query optimization, and database administration.
Specializes in PostgreSQL, MySQL, and SQLite. Helps with schema design, complex
queries, performance tuning, and database best practices.
```

✅ **Good**:
```
Career coach specializing in tech industry transitions. Provides guidance on
resume building, interview preparation, salary negotiation, and career path
planning for software developers.
```

❌ **Too vague**:
```
An expert that helps with stuff.
```

#### Temperature

**Purpose**: Controls response creativity and randomness

**Provider limits**: Z.AI accepts at most 1.0; DeepSeek ignores the temperature while thinking is enabled (the field is disabled); OpenAI models are fixed at 1.0 and KIMI models use a fixed temperature.

**Quick Reference**:
- **0.0 - 0.3**: Highly focused, deterministic (coding, math)
- **0.4 - 0.7**: Balanced, informative (general advice, explanations)
- **0.8 - 1.2**: Creative, exploratory (brainstorming, analysis)
- **1.3 - 2.0**: Highly creative (creative writing, ideation)

**Recommendations by Expert Type**:

| Expert Type | Suggested Temperature | Rationale |
|-------------|----------------------|-----------|
| **Code Expert** | 0.2 - 0.4 | Factual, accurate code |
| **Data Analyst** | 0.3 - 0.5 | Balanced analysis |
| **Writing Editor** | 0.4 - 0.6 | Helpful but conservative |
| **Helpful Assistant** | 0.8 - 1.2 | Flexible for various tasks |
| **Creative Writer** | 1.0 - 1.5 | Original, creative content |
| **Brainstormer** | 1.2 - 1.8 | Diverse ideas |

**See also**: [Temperature Guide](temperature-guide.md) for detailed explanations

#### Customize Expert Behavior (Optional)

**Purpose**: Override the auto-generated system prompt with specific instructions

**When to Use**:
- You need precise control over expert behavior
- Auto-generated prompt doesn't capture your requirements
- Expert requires specific formatting or constraints
- Expert needs to follow strict guidelines

**Guidelines**:
- Be explicit about behavior and constraints
- Include formatting requirements if needed
- Specify what the expert should and shouldn't do
- Use clear, professional language

**Example Custom Prompts**:

**Code Review Expert**:
```
You are a Code Review Expert specializing in Python.

Your role:
- Review code for bugs, security issues, and best practices
- Suggest improvements for readability and performance
- Follow PEP 8 style guidelines
- Provide specific, actionable feedback

Your responses should:
- Start with a summary of findings
- List issues by severity (critical, major, minor)
- Provide code examples for improvements
- Be constructive and educational

If you're unsure about something, acknowledge it honestly.
```

**Legal Expert** (with disclaimers):
```
You are a Legal Information Expert specializing in contract law.

Your role:
- Explain legal concepts in plain language
- Identify common clauses and their implications
- Highlight potential risks in contracts

Important constraints:
- You provide information, not legal advice
- Always recommend consulting a qualified attorney
- Do not interpret specific documents for real-world use
- Cite general legal principles when applicable

Your responses should be clear, accurate, and include appropriate disclaimers.
```

**Creative Writing Expert**:
```
You are a Creative Writing Expert specializing in short fiction.

Your expertise:
- Narrative structure and pacing
- Character development
- Dialogue writing
- Show, don't tell techniques

When helping with writing:
- Ask about the intended tone and audience
- Provide specific examples from the text
- Suggest revisions that maintain the author's voice
- Offer multiple approaches when appropriate

Be encouraging while providing constructive feedback.
```

## Multilingual Experts

You can describe experts in any language! The expert will automatically respond in the user's selected language. Note that the expert name itself is limited to ASCII letters, numbers, spaces, `_`, `-` and `.`.

### Creating a Multilingual Expert

**Example: German Expert**

1. **Expert Name**: "Datenexperte"
2. **Description**: "Experte für Datenanalyse und Visualisierung mit Python, SQL und Excel."
3. **Temperature**: 0.7

When users with German selected chat with this expert, responses will be in German.

**Example: Chinese Expert**

1. **Expert Name**: "SQL Expert CN"
2. **Description**: "SQL数据库设计、查询优化和数据库管理专家。专长于PostgreSQL、MySQL和SQLite。"
3. **Temperature**: 0.5

### Language Behavior

**Expert Creation Language**:
- The description (and custom system prompt) can be in any language; the name must use the allowed ASCII characters
- This sets the "identity" of the expert

**User Interaction Language**:
- Experts automatically respond in user's selected language
- A German expert can respond in English if the user has English selected
- A Chinese expert can respond in German if the user has German selected

**Why this works**:
The app injects a language prefix at runtime:
```
You must respond in German (Deutsch).

You are SQL Expert CN, a domain-specific expert AI assistant...
```

## Expert Creation Best Practices

### 1. Start with a Balanced Temperature

**Recommended**: Begin with 0.7 (balanced; the form's default is 1.0), then adjust based on results.

**Rationale**:
- Easier to adjust later than to redesign the expert
- 0.7 works well for most use cases
- Can fine-tune after testing

### 2. Write Specific Descriptions

**❌ Too vague**:
```
An expert that helps with technology.
```

**✅ Specific**:
```
Expert in Python web development using FastAPI and Flask. Specializes in API design,
authentication, database integration, and deployment best practices.
```

### 3. Test and Iterate

**Workflow**:
1. Create expert with initial settings
2. Test with typical questions
3. Adjust temperature if responses are too focused or too creative
4. Refine description or add custom prompt if needed
5. Edit expert configuration via Settings → Expert Management if needed (model, thinking mode and temperature can also be changed directly below the chat input)

### 4. Use Temperature Appropriately

**Technical domains** (coding, math, data analysis):
- Lower temperature (0.2 - 0.5)
- Prioritizes accuracy over creativity

**Advisory domains** (career, life coaching):
- Medium temperature (0.6 - 0.8)
- Balances expertise with engagement

**Creative domains** (writing, brainstorming):
- Higher temperature (0.9 - 1.5)
- Encourages originality and variety

### 5. Consider Custom Prompts for Complex Experts

**Use custom prompts when**:
- Expert needs to follow specific formats
- Expert requires disclaimers (legal, medical, financial)
- Expert has strict behavioral guidelines
- Auto-generated prompt isn't specific enough

**Skip custom prompts when**:
- Description is sufficient for general guidance
- You want flexibility in expert responses
- You're still exploring the expert's capabilities

## Examples: Effective Expert Configurations

### Example 1: Technical Expert

**Git Expert**

```
Name: Git Expert
Description: Expert in Git version control, branching strategies, merge conflicts,
and collaboration workflows. Specializes in Git best practices and CI/CD integration.
Temperature: 0.3
Custom Prompt: None (let description guide)
```

### Example 2: Advisory Expert

**Interview Coach**

```
Name: Interview Coach
Description: Career coach specializing in technical interview preparation. Helps with
behavioral questions (STAR method), system design, coding interviews, and salary
negotiation for software engineering roles.
Temperature: 0.7
Custom Prompt: None (let description guide)
```

### Example 3: Creative Expert

**Storyteller**

```
Name: Storyteller
Description: Creative writing assistant specializing in short fiction. Expert in
narrative structure, character development, dialogue, and literary techniques.
Temperature: 1.2
Custom Prompt: Custom prompt provided for specific style guidelines
```

### Example 4: Multilingual Expert

**Traductor Espanol**

```
Name: Traductor Espanol
Description: Experto en traducción inglés-español, gramática español, y matices
culturales en la traducción.
Temperature: 0.5
Custom Prompt: None (let description guide)
```

## Editing Existing Experts

### Via UI

1. Go to **Settings** → **Expert Management**
2. Find the expert in the list
3. Click **Edit** button
4. Modify name, description, provider/model, thinking mode, temperature, or expert behavior (the Expert ID cannot be changed)
5. Click **Save Changes**

Model, thinking mode and temperature can also be changed directly in the toolbox below the chat input on the expert's page; changes there are saved immediately.

### Via Configuration Files

Advanced users can edit YAML configs directly:

**Location**: `configs/{expert_id}.yaml`

**Example**:
```yaml
expert_id: "1001_python_expert"
expert_name: "Python Expert"
description: "Expert in Python programming, software development..."
temperature: 0.7
system_prompt: |
  You are Python Expert...
created_at: "2025-01-17T12:00:00.000000"
metadata:
  version: "2.0"
  provider: "deepseek"
  model: "deepseek-flash"
  thinking_level: "high"
```

**Note**: After editing YAML, you may need to restart the app or increment cache version.

## Deleting Experts

### Via UI

1. Go to **Settings** → **Expert Management**
2. Find the expert in the list
3. Click **Delete** button
4. Confirm with **Yes, Delete**

**What gets deleted**:
- Expert configuration: `configs/{expert_id}.yaml`
- Expert page: `pages/{expert_id}.py`
- The chat history file `chat_history/{expert_id}.json` (and images in `chat_attachments/{expert_id}/`) is **not** deleted; remove it manually or use **Clear Chat History** before deleting

**Warning**: Deletion is irreversible. Backup important conversations before deletion.

## Expert Creation Workflow Summary

```
┌─────────────────────────────────────────────────────────────┐
│  1. Plan Your Expert                                         │
│     - Define purpose and domain                              │
│     - Determine appropriate temperature                     │
│     - Decide if custom prompt needed                         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  2. Create Expert                                            │
│     - Go to Home page (or Settings → Expert Management)     │
│     - Click "➕ Add Chat"                                    │
│     - Fill form with details                                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  3. Test and Refine                                          │
│     - Chat with expert using typical questions              │
│     - Adjust temperature if needed                           │
│     - Edit description or add custom prompt                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  4. Use and Iterate                                          │
│     - Use expert for intended purpose                        │
│     - Monitor response quality                               │
│     - Continue refining as needed                            │
└─────────────────────────────────────────────────────────────┘
```

## Advanced: Custom System Prompt Templates

### Template 1: Code Review Expert

```
You are {EXPERT_NAME}, specializing in {LANGUAGE/Framework} code review.

Your responsibilities:
- Identify bugs, security vulnerabilities, and performance issues
- Suggest improvements following {STYLE_GUIDE} guidelines
- Provide specific, actionable feedback with examples

Review process:
1. Summarize the code's purpose
2. List findings by severity (critical, major, minor)
3. Provide code examples for improvements
4. Highlight positive aspects

Always be constructive and educational in your feedback.
```

### Template 2: Learning Assistant

```
You are {EXPERT_NAME}, an educational expert in {DOMAIN}.

Teaching approach:
- Start with assessing the learner's current level
- Explain concepts step-by-step with examples
- Check understanding with questions
- Provide practice problems when appropriate

Adapt your explanations to:
- The learner's knowledge level
- Their learning goals
- Their preferred pace

Encourage questions and make learning engaging.
```

### Template 3: Professional Consultant

```
You are {EXPERT_NAME}, a professional consultant in {FIELD}.

Your expertise includes:
- {AREA_1}
- {AREA_2}
- {AREA_3}

Consultation approach:
- Ask clarifying questions to understand needs
- Provide options with pros and cons
- Recommend best practices
- Highlight potential risks

Maintain professional, objective language.
Acknowledge limitations of expertise when appropriate.
```

## Troubleshooting Expert Creation

### Expert Not Appearing in Navigation

**Problem**: Created expert but not visible in sidebar

**Solutions**:
1. Wait a moment for page discovery
2. Refresh the browser
3. Check if expert page exists: `ls pages/`
4. Verify expert config exists: `ls configs/`

### Auto-Generated System Prompt Not Working

**Problem**: Expert not behaving as expected based on description

**Solutions**:
1. Use a custom system prompt for precise control
2. Make description more specific
3. Adjust temperature
4. Edit config directly and restart app

### Multilingual Expert Not Responding in Language

**Problem**: Expert created in one language but responds in another

**Explanation**: This is expected behavior! Experts respond in the user's selected language, not the language used to create them.

**Solution**: If you want experts to respond in a specific language, users should select that language in Settings.

### Cannot Edit Expert

**Problem**: Edit button not working or changes not saving

**Solutions**:
1. Check file permissions on `configs/` directory
2. Ensure config file is not locked
3. Try restarting the application
4. Edit YAML config directly as fallback

## Next Steps

- **[Temperature Guide](temperature-guide.md)** - Master temperature settings
- **[Configuration Guide](../configuration/expert-configs.md)** - Understand YAML config structure
- **[Customization Guide](customization.md)** - Personalize themes and settings
- **[Development - Adding Features](../development/adding-features.md)** - Contribute new features

---

**Back to**: [Documentation Home](../README.md) | [User Guide - Basics](basics.md)
