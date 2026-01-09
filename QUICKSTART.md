# Quick Start Guide

Get ExpertGPTs up and running in minutes!

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- A DeepSeek API key ([Get one here](https://platform.deepseek.com/))

## Installation

1. **Install dependencies**:
   ```bash
   # For development (includes watchdog for faster reloading)
   pip install -r requirements-dev.txt

   # For production only
   pip install -r requirements.txt
   ```

## Running the Application

Start the app with:
```bash
streamlit run app.py
```

**First run?** The app will automatically create 7 example expert agents:
- Python Expert
- Data Scientist
- Writing Assistant
- Linux System Admin
- Career Coach
- Translation Expert
- Spell Checker

The application will open at `http://localhost:8501`

**Features**:
- Modern navigation with Material Design icons
- Wide mode enabled by default
- Expert pages generated from templates for consistency

## First Use

1. **Set up your API key**:
   - Navigate to **Settings** → **API Key** tab
   - Enter your DeepSeek API key
   - Click **"Save API Key"**
   - The key is automatically saved to `.streamlit/secrets.toml` with secure permissions
2. **Select an expert**: Click on any expert in the navigation menu
3. **Start chatting**: Type your question and get expert responses!

## Creating Your Own Expert

1. Navigate to the **Home** page
2. Click **"➕ Add Chat"** in the sidebar
3. Fill in the details:
   - Name: e.g., "Legal Advisor"
   - Description: What this expert specializes in
   - Temperature: 0.7 (balanced) or customize
4. Click **"Create Expert"**
5. You'll automatically navigate to your new expert and can start chatting immediately!

> **Note**: The "Add Chat" button is only available on the Home page sidebar

## Temperature Guide

- **0.0 - 0.3**: Highly focused, deterministic (coding, math)
- **0.4 - 0.7**: Balanced, informative (general advice, explanations)
- **0.8 - 1.2**: Creative, exploratory (brainstorming, analysis)
- **1.3 - 2.0**: Highly creative (creative writing, ideation)

## Troubleshooting

**App won't start?**
- Ensure all dependencies are installed: `pip install -r requirements.txt`

**API errors?**
- Verify your DeepSeek API key is valid
- Check that you have sufficient API credits

**Import errors?**
- Make sure you're running from the project root directory
- Check that `utils/` directory contains all three Python files

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize expert pages by editing `templates/template.py`
- Explore the config files in `configs/` to understand expert settings
- Create custom experts for your specific use cases!

## Support

For issues or questions, visit the [GitHub repository](https://github.com/fossler/expertgpts).
