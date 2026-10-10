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

1. **Real dialogs via `st.dialog(position=...)` (1.65)** — *done (2026-10-10)*
   "Add Chat", "Edit Expert", the delete confirmation and the reset confirmation are now
   blocking modal `st.dialog`s (`dismissible=False`, closed only by their own buttons;
   `lib/ui/dialogs.py:open_add_chat_dialog`,
   `pages/9998_Settings.py:open_edit_expert_dialog` / `open_delete_expert_dialog` /
   `open_reset_dialog`). The `show_*_dialog`, `editing_expert_*`, `confirm_delete_*` and
   `confirm_reset` session state flags and `ensure_dialog_state()` are gone. Success
   messages use `st.toast`, which survives the closing `st.rerun()` (1.62).

2. **`st.tabs` with query param binding (1.65) and `height` (1.60)** — *done differently (2026-10-10)*
   Goal: deep links to a Settings section and keeping it across reloads. The built-in
   `bind="query-params"` (on `st.tabs` and `st.segmented_control`) writes the displayed
   label to the URL (`?tab=🔑+API-Schlüssel`), even with `format_func`, so links break on a
   language change. Settings therefore keeps its `st.segmented_control` (only the active
   section renders) and binds it manually to a stable key via `st.query_params`:
   `/Settings?tab=api_key` (`SETTINGS_SECTIONS` in `pages/9998_Settings.py`, parameter
   name `SETTINGS_TAB_PARAM`). Deep links, reloads and browser back/forward work; the
   default section has no parameter, unknown values fall back to it. The
   `settings_active_tab` session state is gone. "Go to Settings" in the Add Chat dialog
   opens the API Key section.

3. **`required` and client-side validation for `st.text_input` (1.62 / 1.65)** — *not adopted (2026-10-10)*
   Name and description are already mandatory and validated in Python after submitting;
   the error shows inside the open dialog. `required` / `validate` exist only on
   `st.text_input`, not on `st.text_area`, so only the expert name would gain browser-side
   checks, and the server-side check has to stay anyway. Too little gain for now.

4. **`icon=` for `st.title` / `st.header` / `st.subheader` (1.63) and `st.metric` (1.61)** — *done (2026-10-10)*
   Page titles, section headings and the Settings tab bar use Material icons via `icon=`
   instead of emojis in the string: Home `smart_toy`, expert pages and the expert list
   `psychology_alt`, Settings `settings` (tabs: `palette`, `vpn_key`, `smart_toy`,
   `manage_accounts`, `warning`, `info`; sections also `language`, `library_books`,
   `backup`), Help `menu_book`, dialog sub-headings `memory` and `psychology_alt`.
   Emojis in buttons, alerts and captions are unchanged.

### Nice to have

5. **Background refresh for `st.cache_data` (1.61, TTL multiplier configurable in 1.63)** — *not adopted (2026-10-10)*
   Serves the stale value while refreshing in the background. Measured uncached cost:
   `list_experts_lightweight` (10 YAML files) ~10 ms, `translate_expert_names_batch`
   ~0.01 ms, so there is no latency spike to hide. Serving stale values could instead show
   an expert list without a just-created expert.

6. **`on_change="ignore"` for almost all widgets (1.63–1.65)** — *not adopted (2026-10-10)*
   Changing the widget doesn't trigger a rerun. The theme selection needs the rerun: it
   updates the color preview immediately and enables the color pickers for "Custom". No
   other widget where a rerun is a problem.

7. **Async support and async-aware caches (1.64)** — *not adopted (2026-10-10)*
   Async only helps when a page run waits for several slow things at once; none does.
   The chat stream runs in a background thread so it survives page navigation (an
   in-script coroutine would be cancelled), transcription and system prompt generation
   are single calls, and the rest takes milliseconds (git branch ~4 ms). Library imports
   can't be made async and happen once per server process (~0.3 s, mostly `openai`).

### Bug fixes that help indirectly

- 1.62: toasts are preserved when `st.rerun()` follows `st.toast`.
- 1.62: color picker interaction works inside dialogs again (relevant for item 1).
- 1.61: reconnect to the existing session after an unclean websocket close.
- 1.65: `st.query_params` stays in sync on browser back/forward.
