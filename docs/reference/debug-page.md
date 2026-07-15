# Debug Page

ExpertGPTs ships a hidden diagnostics page for developers and operators. It
surfaces the running environment, dependency versions, app health, configuration
status and live session state, plus a few cache-maintenance actions.

## How to open it

The debug page is **not** linked in the sidebar navigation. Reach it by
appending `/debug` to the app URL:

```
http://localhost:8501/debug
```

(Use whatever host and port your app runs on — `8501` is the Streamlit default.)

Because it is only added to the navigation while you are on that URL, it never
appears in the sidebar during normal use. Navigating to any other page removes
it again.

> **Security note:** The page is *unlisted*, not *access-controlled* — anyone who
> can reach the app and knows the URL can open it. API keys and other
> secret-like values are always masked (only the last 4 characters are shown),
> and no raw secret is ever rendered. Still, treat `/debug` like any other
> operator tool and don't expose the app publicly without authentication.

## What each tab shows

The page is organized into six tabs:

### Dependencies

Every package declared in `requirements.txt` and `requirements-dev.txt`, shown
next to the version that is **actually installed** in the running environment:

| Column | Meaning |
|--------|---------|
| Package | Package name as declared |
| Required | The version specifier from the requirements file (e.g. `~=1.59.0`) |
| Installed | The resolved installed version, or `—` if missing |
| Status | `✅ ok`, `⚠️ mismatch` (installed version doesn't satisfy the spec), or `❌ not installed` |
| Source | `prod` (`requirements.txt`) or `dev` (`requirements-dev.txt`) |

A banner at the top summarizes whether everything is installed and satisfies its
declared spec. This is the quickest way to spot a drifted or missing dependency.

### Runtime

Python version and executable, Streamlit version, platform/OS, the current
working directory, the project root, and the active Git branch.

### App status

- Number of expert pages and expert config files
- Chat-history files with their size and usage against the 1 MB per-file limit
- Streaming-cache files currently on disk

### Config

- Per-provider API-key status: present (masked, e.g. `••••1234`) or `not set`
- The current default provider, default model, and language preference

### Session state

A live dump of `st.session_state` keys, their types, and a short value preview.
Values under secret-like keys (anything containing `key`, `secret`, `token`,
`password`, or `credential`) are masked. Handy for debugging state-related
issues.

### Actions

Three **cache-only** maintenance buttons. None of them delete chat history or
expert configs:

| Action | Effect |
|--------|--------|
| **Clear data cache** | Drops all `@st.cache_data` results — the cached expert list, theme settings and UI translations. Re-read from disk on next use. Run after editing files in `configs/` outside the app. |
| **Clear resource cache** | Drops all `@st.cache_resource` singletons — the pooled LLM client connections and the tiktoken encoder. Rebuilt on the next request. Run after changing API keys or if a connection is stale. |
| **Clean streaming cache** | Deletes finished response files in `streaming_cache/` (completed or errored). In-progress streams are preserved, so a running generation is never interrupted — it just frees leftover disk space. |

## When to use it

- Confirming which dependency versions are actually installed vs. declared
- Checking that API keys are configured (without revealing them)
- Verifying default provider/model/language after changing settings
- Inspecting session state while debugging a state issue
- Clearing caches after editing configs or rotating API keys

## Related

- [Troubleshooting](troubleshooting.md) — common issues and fixes
- [API Keys](../configuration/api-keys.md) — how keys are stored and validated
- [Configuration Overview](../configuration/overview.md) — configuration files
