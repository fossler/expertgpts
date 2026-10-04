# Streamlit 1.59 → 1.65 Upgrade Notes

Review of the Streamlit release notes from 1.60.0 to 1.65.0 (2026-07-21 to 2026-10-02),
checked against the ExpertGPTs code base (`app.py`, `lib/`, `pages/`, `templates/`).

Sources: GitHub release notes
[1.60.0](https://github.com/streamlit/streamlit/releases/tag/1.60.0) ·
[1.61.0](https://github.com/streamlit/streamlit/releases/tag/1.61.0) ·
[1.62.0](https://github.com/streamlit/streamlit/releases/tag/1.62.0) ·
[1.63.0](https://github.com/streamlit/streamlit/releases/tag/1.63.0) ·
[1.64.0](https://github.com/streamlit/streamlit/releases/tag/1.64.0) ·
[1.65.0](https://github.com/streamlit/streamlit/releases/tag/1.65.0)

## Upgrade Status

Upgraded to `streamlit~=1.65.0` on 2026-10-04 (installed: 1.65.0). No code changes were
needed. Verification:

- `pytest`: 49 passed.
- `ruff format --check`: clean.
- Headless browser walkthrough (Playwright/Chromium) of all 13 navigation pages (Home,
  10 experts, Settings, Help) and all 6 Settings sections: no `st.exception`, no browser
  console errors, no failed requests, no warnings or deprecations in the server log.
- End-to-end chat on the Spell Checker expert (DeepSeek V4 Flash): the message is sent,
  the response streams through the background-streaming cache and is rendered completely.

Known non-issues (behave the same on 1.59.2):

- Opening a page by deep link (e.g. `/spell_checker`) produces two 404s for
  `/<page>/_stcore/health` and `/<page>/_stcore/host-config`. The frontend probes the
  page path as a possible base path before falling back to the root.
- Under `AppTest`, `st.context.url` is `None`, so `app.py` fails at
  `urllib.parse.urlparse(st.context.url)` in the `/debug` routing check. This only
  matters if `AppTest` tests are added for `app.py`.

## Breaking Changes

None of the breaking changes require code changes in ExpertGPTs.

| Version | Change | Impact on ExpertGPTs |
|---|---|---|
| 1.61 | `use_column_width` removed from `st.image` (accepted as no-op again in 1.65) | Not used |
| 1.61 | String file paths in `st.html` / `st.iframe` deprecated in favour of `pathlib.Path` | Neither command is used |
| 1.62 | Legacy `st.cache` removed | Not used (only `st.cache_data` / `st.cache_resource`) |
| 1.62 | `st.pyplot`: global-figure support removed, savefig kwargs deprecated | No Matplotlib |
| 1.64 | `mapbox.token` config option removed | Not in `.streamlit/config.toml` |
| 1.60 | New `server.maxWidgetStateSize` config option (size limit for widget state) | **Verify** with long text areas (see below) |
| 1.60 | Client-supplied query string size and field count limited | `st.query_params` not used in app code |
| 1.60 | Host messages from child frames rejected | No custom components / iframes |
| 1.61 | `disabled=` enforced server-side | Unlikely to matter (Settings uses `disabled=` for display only) |

### Things to verify after upgrading

- **Long `st.text_area` values**: custom system prompts in `lib/ui/dialogs.py` and
  `pages/9998_Settings.py` could hit the new widget state size limit. The release notes
  don't state the default value.
- **Rerun semantics**: `st.rerun()` now works inside widget callbacks (1.63), and widget
  values are kept after a body-level `st.rerun()` (1.64). The app calls `st.rerun()` ~76
  times, none of them from a callback. Still worth clicking through the chat flow and the
  add/edit expert flows.
- `AppTest` changed a lot, but the test suite doesn't use it.

## New Features Worth Adopting

### Good fit

1. **Real dialogs via `st.dialog(position=...)` (1.65)**
   The "Add Chat" and "Edit Expert" dialogs are rendered inline using
   `show_*_dialog` session state flags (`lib/ui/dialogs.py:render_add_chat_dialog`,
   `pages/9998_Settings.py:render_edit_expert_dialog`). A real `@st.dialog` — as a modal
   or a side drawer — would remove that flag handling. Several dialog bugs were fixed in
   1.62–1.65 (color picker in dialogs, popovers in dialogs, dialogs closing on reruns).

2. **`st.tabs` with query param binding (1.65) and `height` (1.60)**
   Settings emulates tabs with `st.segmented_control` plus `settings_active_tab` in
   session state. `st.tabs` with query param binding gives deep links such as
   `/settings?tab=api` and keeps the active tab across reloads.
   Trade-off: `st.tabs` executes the code of *all* tabs on every rerun, while the
   segmented control only renders the active section.

3. **`required` and client-side validation for `st.text_input` (1.62 / 1.65)**
   Mandatory fields in the add/edit expert forms (name, description) could be validated
   in the browser before submitting, replacing part of the custom validation.

4. **`icon=` for `st.title` / `st.header` / `st.subheader` (1.63) and `st.metric` (1.61)**
   Headings currently embed emojis in the string (e.g. `f"➕ {i18n.t(...)}"`). Material
   icons would be consistent with the navigation, which already uses `:material/...`.
   Cosmetic only.

### Nice to have

5. **Background refresh for `st.cache_data` (1.61, TTL multiplier configurable in 1.63)**
   Serves the stale value while refreshing in the background. Fits
   `list_experts_lightweight` (ttl=60) and `translate_expert_names_batch` (ttl=300) to
   avoid latency spikes when the TTL expires.

6. **`on_change="ignore"` for almost all widgets (1.63–1.65)**
   Changing the widget doesn't trigger a rerun. Useful for the theme selection, which
   only takes effect on "Save & Apply".

7. **Async support and async-aware caches (1.64)**
   Not a real win for streaming: the background thread + file cache design exists so
   streams survive page navigation, which in-script async can't provide.

### Bug fixes that help indirectly

- 1.62: toasts are preserved when `st.rerun()` follows `st.toast`.
- 1.62: color picker interaction works inside dialogs again (relevant for item 1).
- 1.61: reconnect to the existing session after an unclean websocket close.
- 1.65: `st.query_params` stays in sync on browser back/forward.
