"""Hidden diagnostics page for ExpertGPTs.

Reachable only via the ``/debug`` URL path (see ``app.py``); it is never linked
in the sidebar navigation. Developer/operator convenience page: surfaces the
runtime environment, declared vs. installed dependencies, app health, config
status and session state. Secrets (API keys) are always masked.
"""

import platform
import sys
from importlib import metadata
from pathlib import Path

import streamlit as st

from lib.shared.session_state import initialize_shared_session_state
from lib.shared.helpers import render_git_branch_footer, get_git_branch
from lib.shared.constants import LLM_PROVIDERS
from lib.shared.page_generator import PageGenerator
from lib.storage.chat_history_manager import DEFAULT_MAX_FILE_SIZE_MB
from lib.storage.streaming_cache import STREAMING_CACHE_DIR, StreamingCache
from lib.config.app_defaults_manager import (
    get_llm_defaults,
    get_language_preference,
)

PROJECT_ROOT = Path(__file__).parent.parent
REQUIREMENTS_FILES = [
    ("requirements.txt", "prod"),
    ("requirements-dev.txt", "dev"),
]

# Session-state keys whose values must never be rendered in the inspector.
_SECRET_HINTS = ("key", "secret", "token", "password", "credential")


def _human_size(num_bytes: int) -> str:
    """Format a byte count as a short human-readable string."""
    value = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{value:.1f} GB"


def _is_secret_key(name: str) -> bool:
    """Return True if a session-state key name looks like it holds a secret."""
    lowered = str(name).lower()
    return any(hint in lowered for hint in _SECRET_HINTS)


# --- Dependencies ----------------------------------------------------------


def _parse_requirements(path: Path):
    """Yield ``(package, spec)`` tuples from a requirements file.

    Skips blanks, comments and ``-r``/``-c`` include lines. Splits inline
    comments and separates the package name from its version specifier.
    """
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        for sep in ("~=", ">=", "<=", "==", "!=", ">", "<", "==="):
            if sep in line:
                name, spec = line.split(sep, 1)
                yield name.strip(), f"{sep}{spec.strip()}"
                break
        else:
            yield line.strip(), ""


def _normalize_name(name: str) -> str:
    """Strip extras (e.g. ``pkg[extra]``) and lower-case for lookup."""
    return name.split("[", 1)[0].strip()


def _installed_version(name: str):
    """Return the installed version string, or None if not installed."""
    try:
        return metadata.version(_normalize_name(name))
    except metadata.PackageNotFoundError:
        return None


def _spec_satisfied(spec: str, installed: str):
    """Return True/False if ``installed`` satisfies ``spec``, or None if unknown."""
    if not spec or installed is None:
        return None
    try:
        from packaging.specifiers import SpecifierSet
        from packaging.version import Version

        return Version(installed) in SpecifierSet(spec)
    except Exception:
        return None


def render_dependencies():
    st.subheader(":material/inventory_2: Dependencies")
    st.caption("Declared in requirements*.txt vs. actually installed.")

    rows = []
    mismatches = 0
    for filename, source in REQUIREMENTS_FILES:
        for name, spec in _parse_requirements(PROJECT_ROOT / filename):
            installed = _installed_version(name)
            satisfied = _spec_satisfied(spec, installed)
            if installed is None:
                status = "❌ not installed"
                mismatches += 1
            elif satisfied is False:
                status = "⚠️ mismatch"
                mismatches += 1
            else:
                status = "✅ ok"
            rows.append(
                {
                    "Package": name,
                    "Required": spec or "(any)",
                    "Installed": installed or "—",
                    "Status": status,
                    "Source": source,
                }
            )

    if mismatches:
        st.warning(
            f"{mismatches} package(s) missing or not matching the declared spec."
        )
    else:
        st.success("All declared dependencies are installed and satisfy their specs.")

    st.dataframe(rows, width="stretch", hide_index=True)


# --- Runtime & system ------------------------------------------------------


def render_runtime():
    st.subheader(":material/monitor_heart: Runtime & system")

    col1, col2, col3 = st.columns(3)
    col1.metric("Python", platform.python_version())
    col2.metric("Streamlit", st.__version__)
    branch = get_git_branch() or "—"
    col3.metric("Git branch", branch)

    st.code(
        "\n".join(
            [
                f"Python executable : {sys.executable}",
                f"Python version    : {sys.version}",
                f"Platform          : {platform.platform()}",
                f"Working directory : {Path.cwd()}",
                f"Project root      : {PROJECT_ROOT}",
            ]
        ),
        language="text",
    )


# --- App status ------------------------------------------------------------


def render_app_status():
    st.subheader(":material/health_and_safety: App status")

    expert_count = len(PageGenerator().list_pages())
    config_count = len(list((PROJECT_ROOT / "configs").glob("*.yaml")))
    col1, col2 = st.columns(2)
    col1.metric("Expert pages", expert_count)
    col2.metric("Config files", config_count)

    # Chat history files and their usage vs the 1 MB limit.
    limit_bytes = DEFAULT_MAX_FILE_SIZE_MB * 1024 * 1024
    history_dir = PROJECT_ROOT / "chat_history"
    history_files = sorted(history_dir.glob("*.json")) if history_dir.exists() else []
    st.markdown(f"**Chat history** (limit {DEFAULT_MAX_FILE_SIZE_MB} MB per file)")
    if history_files:
        st.dataframe(
            [
                {
                    "File": f.name,
                    "Size": _human_size(f.stat().st_size),
                    "Usage": f"{f.stat().st_size / limit_bytes * 100:.1f}%",
                }
                for f in history_files
            ],
            width="stretch",
            hide_index=True,
        )
    else:
        st.caption("No chat history files.")

    # Streaming cache files.
    cache_dir = PROJECT_ROOT / STREAMING_CACHE_DIR
    cache_files = sorted(cache_dir.glob("*_latest.*")) if cache_dir.exists() else []
    st.markdown("**Streaming cache**")
    if cache_files:
        st.dataframe(
            [
                {"File": f.name, "Size": _human_size(f.stat().st_size)}
                for f in cache_files
            ],
            width="stretch",
            hide_index=True,
        )
    else:
        st.caption("No streaming cache files.")


# --- Config & API keys -----------------------------------------------------


def _mask_key(value: str) -> str:
    """Mask a secret, keeping only the last 4 characters as a hint."""
    if not value:
        return "—"
    tail = value[-4:] if len(value) >= 4 else ""
    return f"••••{tail}"


def render_config():
    st.subheader(":material/key: Config & API keys")

    api_keys = st.session_state.get("api_keys", {})
    st.dataframe(
        [
            {
                "Provider": cfg["name"],
                "Key": (
                    ("✅ " + _mask_key(api_keys[provider]))
                    if api_keys.get(provider)
                    else "❌ not set"
                ),
            }
            for provider, cfg in LLM_PROVIDERS.items()
        ],
        width="stretch",
        hide_index=True,
    )

    defaults = get_llm_defaults()
    col1, col2, col3 = st.columns(3)
    col1.metric("Default provider", defaults.get("provider", "—"))
    col2.metric("Default model", defaults.get("model", "—"))
    col3.metric("Language", get_language_preference() or "auto")


# --- Session state ---------------------------------------------------------


def render_session_state():
    st.subheader(":material/data_object: Session state")
    st.caption("Secret-like values are masked. Never share raw secrets.")

    rows = []
    for key, value in st.session_state.items():
        if _is_secret_key(key):
            if isinstance(value, dict):
                shown = {k: _mask_key(str(v)) for k, v in value.items()}
                repr_str = repr(shown)
            else:
                repr_str = "••••"
        else:
            repr_str = repr(value)
        if len(repr_str) > 300:
            repr_str = repr_str[:300] + "…"
        rows.append({"Key": str(key), "Type": type(value).__name__, "Value": repr_str})

    st.dataframe(
        sorted(rows, key=lambda r: r["Key"]),
        width="stretch",
        hide_index=True,
    )


# --- Maintenance actions ---------------------------------------------------


def _clean_completed_streams() -> int:
    """Delete completed/error streaming-cache files, preserving in-progress ones.

    Reuses ``StreamingCache._cleanup_old_cache_files`` per expert so the
    "only completed/error" safety logic lives in one place.
    """
    cache_dir = PROJECT_ROOT / STREAMING_CACHE_DIR
    if not cache_dir.exists():
        return 0
    removed = 0
    for meta in list(cache_dir.glob("*_latest.meta")):
        expert_id = meta.name[: -len("_latest.meta")]
        StreamingCache(expert_id)._cleanup_old_cache_files()
        if not meta.exists():
            removed += 1
    return removed


def render_actions():
    st.subheader(":material/build: Maintenance")
    st.caption(
        "Cache-only. None of these delete chat history or expert configs on disk."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Clear data cache", width="stretch"):
            st.cache_data.clear()
            st.toast("Data cache cleared", icon="✅")
        st.caption(
            "Drops all `@st.cache_data` results — the cached expert list, theme "
            "settings and UI translations. They are re-read from disk on next "
            "use. Run this after editing files in `configs/` outside the app."
        )

    with col2:
        if st.button("Clear resource cache", width="stretch"):
            st.cache_resource.clear()
            st.toast("Resource cache cleared", icon="✅")
        st.caption(
            "Drops all `@st.cache_resource` singletons — the pooled LLM client "
            "connections and the tiktoken encoder. They are rebuilt on the next "
            "request. Run this after changing API keys or if a connection is stale."
        )

    with col3:
        if st.button("Clean streaming cache", width="stretch"):
            removed = _clean_completed_streams()
            st.toast(f"Removed {removed} completed stream(s)", icon="🧹")
        st.caption(
            "Deletes finished response files in `streaming_cache/` (completed or "
            "errored). In-progress streams are kept, so this never interrupts a "
            "running generation — it just frees leftover disk space."
        )


def main():
    initialize_shared_session_state()

    st.title(":material/bug_report: Debug")
    st.caption("Diagnostics — reachable only via /debug, hidden from navigation.")

    tabs = st.tabs(
        ["Dependencies", "Runtime", "App status", "Config", "Session state", "Actions"]
    )
    with tabs[0]:
        render_dependencies()
    with tabs[1]:
        render_runtime()
    with tabs[2]:
        render_app_status()
    with tabs[3]:
        render_config()
    with tabs[4]:
        render_session_state()
    with tabs[5]:
        render_actions()

    render_git_branch_footer()


main()
