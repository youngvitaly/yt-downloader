from __future__ import annotations

import os
import json
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import Any
from urllib.parse import unquote, urlparse

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

try:
    import instaloader
except ImportError:
    instaloader = None


APP_TITLE = "YouTube & Instagram Downloader"
DEFAULT_OUTPUT_DIR = Path.home() / "Downloads"
DEFAULT_SETTINGS = {
    "language": "en",
    "theme": "light",
    "output_dir": str(DEFAULT_OUTPUT_DIR),
    "mode": "video",
    "audio_format": "MP3",
    "geometry": "720x520",
    "instagram_username": "",
}

LANGUAGE_LABELS = {"en": "English", "ru": "Русский"}
THEME_LABELS = {
    "en": {"light": "Light", "dark": "Dark"},
    "ru": {"light": "Светлая", "dark": "Тёмная"},
}

TEXT = {
    "en": {
        "heading": "Video, audio and social media downloader",
        "url": "Link:",
        "paste": "Paste",
        "mode": "Mode:",
        "video": "Video",
        "audio": "Audio",
        "quality": "Quality:",
        "inspect": "Get qualities",
        "audio_format": "Audio format:",
        "folder": "Folder:",
        "browse": "Browse…",
        "settings": "Settings",
        "download": "Download",
        "instagram_saved": "Saved Instagram",
        "cancel": "Cancel",
        "open_folder": "Open folder",
        "ready": "Ready",
        "fetching": "Getting available qualities…",
        "checking": "Checking: {url}",
        "downloading_log": "Downloading: {url}",
        "qualities_updated": "Quality list updated.",
        "ready_download": "Ready to download",
        "available_formats": "{title}  •  available formats: {count}",
        "untitled": "Untitled",
        "best_available": "Best available",
        "up_to": "Up to",
        "paste_video": "Paste a YouTube or Instagram link.",
        "clipboard_empty": "The clipboard does not contain text.\n"
        "Copy a link in the browser and press “Paste” again.",
        "clipboard_no_link": "The clipboard does not contain a link.",
        "folder_error": "Could not open the folder:\n{error}",
        "dependency_error": "The yt-dlp package was not found.\n\nRun run.bat.",
        "ffmpeg_error": "ffmpeg.exe is required for video merging and audio conversion.\n\n"
        "Put ffmpeg.exe next to app.py or next to the .exe.",
        "starting": "Starting download…",
        "downloading": "Downloading: {percent:.1f}%",
        "processing": "File downloaded, processing…",
        "done": "Done",
        "saved": "The file was saved to the selected folder.",
        "download_complete": "Download complete.",
        "canceling": "Canceling…",
        "cancelled": "Cancelled",
        "download_cancelled": "Download cancelled.",
        "error": "Error",
        "error_log": "Error: {text}",
        "stopping": "Stopping the download…",
        "close_wait": "The window will close after the worker stops.",
        "settings_title": "Settings",
        "language": "Language:",
        "theme": "Theme:",
        "instagram_account": "Instagram account",
        "instagram_status_logged_in": "Logged in as {username}",
        "instagram_status_logged_out": "Not logged in",
        "instagram_status_missing": "Session file is missing. Log in again.",
        "instagram_login": "Log in",
        "instagram_logout": "Log out",
        "instagram_login_title": "Instagram login",
        "instagram_username": "Username:",
        "instagram_password": "Password:",
        "instagram_two_factor": "2FA code:",
        "instagram_login_submit": "Log in",
        "instagram_verify": "Verify code",
        "instagram_login_starting": "Signing in to Instagram…",
        "instagram_login_2fa": "Instagram requested a two-factor authentication code.",
        "instagram_login_success": "Logged in as {username}. The local session was saved.",
        "instagram_login_error": "Instagram login failed:\n\n{text}",
        "instagram_logout_confirm": "Delete the saved Instagram session for {username}?",
        "instagram_logout_error": "Could not delete the Instagram session:\n\n{text}",
        "instagram_no_session": "Log in to Instagram in Settings before downloading private content or saved posts.",
        "instagram_session_error": "The saved Instagram session could not be loaded. Log in again in Settings.\n\n{text}",
        "instagram_session_note": "Only Instaloader's session file is kept locally; your password is not saved. Protect this folder like a login credential.",
        "instagram_private_note": "Login unlocks private media and stories visible to this account, plus saved posts.",
        "instagram_saved_starting": "Downloading saved Instagram posts…",
        "instagram_saved_log": "Downloading saved Instagram posts for {username}.",
        "instagram_saved_no_media": "No downloadable saved Instagram media was found.",
        "save": "Save",
        "close": "Close",
        "per_second": "/s",
        "remaining": "left",
        "progress_details": "{downloaded}  •  {speed}  •  {remaining} {eta}",
        "not_bot": "YouTube asked to confirm that you are not a bot. "
        "Try updating yt-dlp or using browser cookies.\n\n{text}",
        "ffmpeg_processing": "FFmpeg could not process the file.\n\n{text}",
        "instagram_detected": "Instagram link detected.",
        "instagram_quality_note": "Instagram uses the best available media quality.",
        "instagram_ytdlp_primary": "Trying yt-dlp for Instagram first.",
        "instagram_fallback_log": "yt-dlp failed: {text}",
        "instagram_fallback": "yt-dlp could not download Instagram media. "
        "Trying the Instaloader fallback…",
        "instagram_fallback_unavailable": "yt-dlp could not download this Instagram link:\n\n"
        "{primary}\n\nInstaloader is not installed. Run run.bat to install all dependencies.",
        "instagram_fallback_error": "Instagram download failed.\n\n"
        "yt-dlp: {primary}\n\nInstaloader: {fallback}",
        "instagram_invalid": "This Instagram link is not a supported post, profile, story, or saved-post URL.",
        "instagram_no_media": "No Instagram media was found.",
        "instagram_no_audio": "The Instagram content does not contain a video or audio track.",
        "instagram_processing": "Converting Instagram video to audio…",
        "instagram_login_required": "Instagram requires a logged-in session for this content. "
        "Log in from Settings and make sure the account can view it.",
        "instagram_dependency_error": "The Instaloader package was not found.\n\nRun run.bat.",
    },
    "ru": {
        "heading": "Загрузка видео, аудио и соцмедиа",
        "url": "Ссылка:",
        "paste": "Вставить",
        "mode": "Режим:",
        "video": "Видео",
        "audio": "Аудио",
        "quality": "Качество:",
        "inspect": "Получить качества",
        "audio_format": "Формат аудио:",
        "folder": "Папка:",
        "browse": "Обзор…",
        "settings": "Настройки",
        "download": "Скачать",
        "instagram_saved": "Сохранённое Instagram",
        "cancel": "Отмена",
        "open_folder": "Открыть папку",
        "ready": "Готово",
        "fetching": "Получаю список доступных качеств…",
        "checking": "Проверка: {url}",
        "downloading_log": "Скачивание: {url}",
        "qualities_updated": "Список качеств обновлён.",
        "ready_download": "Готово к скачиванию",
        "available_formats": "{title}  •  доступно форматов: {count}",
        "untitled": "Без названия",
        "best_available": "Лучшее доступное",
        "up_to": "До",
        "paste_video": "Вставьте ссылку на YouTube или Instagram.",
        "clipboard_empty": "В буфере обмена нет текста.\n"
        "Скопируйте ссылку в браузере и нажмите «Вставить» ещё раз.",
        "clipboard_no_link": "В буфере обмена нет ссылки.",
        "folder_error": "Не удалось открыть папку:\n{error}",
        "dependency_error": "Не найден пакет yt-dlp.\n\nЗапустите run.bat.",
        "ffmpeg_error": "Для объединения видео и конвертации аудио нужен ffmpeg.exe.\n\n"
        "Положите ffmpeg.exe рядом с app.py или рядом с .exe.",
        "starting": "Начинаю скачивание…",
        "downloading": "Скачивание: {percent:.1f}%",
        "processing": "Файл скачан, выполняю обработку…",
        "done": "Готово",
        "saved": "Файл сохранён в выбранную папку.",
        "download_complete": "Скачивание завершено.",
        "canceling": "Отмена…",
        "cancelled": "Отменено",
        "download_cancelled": "Скачивание отменено.",
        "error": "Ошибка",
        "error_log": "Ошибка: {text}",
        "stopping": "Останавливаю загрузку…",
        "close_wait": "Окно закроется после остановки рабочего потока.",
        "settings_title": "Настройки",
        "language": "Язык:",
        "theme": "Тема:",
        "instagram_account": "Аккаунт Instagram",
        "instagram_status_logged_in": "Выполнен вход: {username}",
        "instagram_status_logged_out": "Вход не выполнен",
        "instagram_status_missing": "Файл сессии отсутствует. Войдите снова.",
        "instagram_login": "Войти",
        "instagram_logout": "Выйти",
        "instagram_login_title": "Вход в Instagram",
        "instagram_username": "Имя пользователя:",
        "instagram_password": "Пароль:",
        "instagram_two_factor": "Код 2FA:",
        "instagram_login_submit": "Войти",
        "instagram_verify": "Проверить код",
        "instagram_login_starting": "Выполняю вход в Instagram…",
        "instagram_login_2fa": "Instagram запросил код двухфакторной аутентификации.",
        "instagram_login_success": "Вход выполнен: {username}. Локальная сессия сохранена.",
        "instagram_login_error": "Не удалось войти в Instagram:\n\n{text}",
        "instagram_logout_confirm": "Удалить сохранённую сессию Instagram для {username}?",
        "instagram_logout_error": "Не удалось удалить сессию Instagram:\n\n{text}",
        "instagram_no_session": "Сначала войдите в Instagram через Настройки, чтобы скачивать приватный контент или сохранённые посты.",
        "instagram_session_error": "Не удалось загрузить сохранённую сессию Instagram. Войдите снова через Настройки.\n\n{text}",
        "instagram_session_note": "Локально хранится только файл сессии Instaloader; пароль не сохраняется. Защитите эту папку как данные для входа.",
        "instagram_private_note": "Вход открывает приватные медиа и stories, доступные этому аккаунту, а также сохранённые посты.",
        "instagram_saved_starting": "Скачиваю сохранённые посты Instagram…",
        "instagram_saved_log": "Скачиваю сохранённые посты Instagram для {username}.",
        "instagram_saved_no_media": "Скачиваемые сохранённые медиа Instagram не найдены.",
        "save": "Сохранить",
        "close": "Закрыть",
        "per_second": "/с",
        "remaining": "осталось",
        "progress_details": "{downloaded}  •  {speed}  •  {remaining} {eta}",
        "not_bot": "YouTube запросил подтверждение, что вы не бот. "
        "Попробуйте обновить yt-dlp или использовать cookies браузера.\n\n{text}",
        "ffmpeg_processing": "Не удалось обработать файл через FFmpeg.\n\n{text}",
        "instagram_detected": "Обнаружена ссылка Instagram.",
        "instagram_quality_note": "Для Instagram используется лучшее доступное качество.",
        "instagram_ytdlp_primary": "Сначала пробую скачать Instagram через yt-dlp.",
        "instagram_fallback_log": "yt-dlp завершился с ошибкой: {text}",
        "instagram_fallback": "yt-dlp не смог скачать медиа Instagram. "
        "Пробую запасной вариант Instaloader…",
        "instagram_fallback_unavailable": "yt-dlp не смог скачать эту ссылку Instagram:\n\n"
        "{primary}\n\nInstaloader не установлен. Запустите run.bat для установки зависимостей.",
        "instagram_fallback_error": "Не удалось скачать Instagram.\n\n"
        "yt-dlp: {primary}\n\nInstaloader: {fallback}",
        "instagram_invalid": "Это не поддерживаемая ссылка Instagram на пост, профиль, story или сохранённые посты.",
        "instagram_no_media": "Медиа Instagram не найдено.",
        "instagram_no_audio": "В контенте Instagram нет видео или аудиодорожки.",
        "instagram_processing": "Конвертирую видео Instagram в аудио…",
        "instagram_login_required": "Для этого контента Instagram требует авторизованную сессию. "
        "Войдите через Настройки и проверьте, что аккаунту доступен этот контент.",
        "instagram_dependency_error": "Не найден пакет Instaloader.\n\nЗапустите run.bat.",
    },
}

VIDEO_PRESETS = [
    ("best", "bestvideo+bestaudio/best"),
    ("2160", "bestvideo[height<=2160]+bestaudio/best[height<=2160]"),
    ("1440", "bestvideo[height<=1440]+bestaudio/best[height<=1440]"),
    ("1080", "bestvideo[height<=1080]+bestaudio/best[height<=1080]"),
    ("720", "bestvideo[height<=720]+bestaudio/best[height<=720]"),
    ("480", "bestvideo[height<=480]+bestaudio/best[height<=480]"),
    ("360", "bestvideo[height<=360]+bestaudio/best[height<=360]"),
]

AUDIO_PRESETS = [
    ("best", "bestaudio/best"),
    ("320", "bestaudio[abr<=320]/bestaudio/best"),
    ("256", "bestaudio[abr<=256]/bestaudio/best"),
    ("192", "bestaudio[abr<=192]/bestaudio/best"),
    ("128", "bestaudio[abr<=128]/bestaudio/best"),
]

AUDIO_FORMATS = [
    ("MP3", "mp3"),
    ("M4A", "m4a"),
    ("Opus", "opus"),
]

INSTAGRAM_RESERVED_PATHS = {
    "accounts",
    "direct",
    "directory",
    "emails",
    "explore",
    "legal",
    "reels",
    "session",
    "settings",
    "about",
    "your_activity",
}


def app_directory() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def resource_path(filename: str) -> Path:
    bundled_dir = getattr(sys, "_MEIPASS", None)
    candidates = []
    if bundled_dir:
        candidates.append(Path(bundled_dir) / filename)
    candidates.append(app_directory() / filename)
    return next((path for path in candidates if path.is_file()), candidates[-1])


SETTINGS_PATH = app_directory() / "settings.json"
INSTAGRAM_SESSION_PATH = app_directory() / "instagram.session"


def load_settings() -> dict[str, Any]:
    try:
        data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return {**DEFAULT_SETTINGS, **data}
    except (OSError, json.JSONDecodeError):
        pass
    return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict[str, Any]) -> None:
    try:
        SETTINGS_PATH.write_text(
            json.dumps(settings, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError:
        pass


class DownloadCancelled(Exception):
    """Raised by the progress hook when the user cancels a download."""


def find_ffmpeg() -> str | None:
    """Find ffmpeg next to the app first, then in PATH."""
    locations: list[Path] = []

    if getattr(sys, "frozen", False):
        locations.append(Path(sys.executable).resolve().parent / "ffmpeg.exe")

    locations.append(Path(__file__).resolve().parent / "ffmpeg.exe")

    path_entry = shutil.which("ffmpeg")
    if path_entry:
        locations.append(Path(path_entry))

    for location in locations:
        if location.is_file():
            return str(location)
    return None


def format_bytes(value: float | int | None) -> str:
    if not value:
        return "0 B"

    amount = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if amount < 1024 or unit == "TB":
            return f"{amount:.1f} {unit}"
        amount /= 1024
    return f"{amount:.1f} TB"


def format_speed(value: float | int | None, suffix: str = "/s") -> str:
    return f"{format_bytes(value)}{suffix}" if value else "—"


def format_eta(value: float | int | None) -> str:
    if value is None:
        return "—"

    seconds = max(0, int(value))
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def safe_float(value: Any) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def is_instagram_url(url: str) -> bool:
    try:
        hostname = (urlparse(url).hostname or "").lower().rstrip(".")
    except ValueError:
        return False
    return hostname == "instagram.com" or hostname.endswith(".instagram.com")


def parse_instagram_url(url: str) -> tuple[str, str] | None:
    if not is_instagram_url(url):
        return None

    try:
        parts = [
            unquote(part).strip()
            for part in urlparse(url).path.split("/")
            if part.strip()
        ]
    except ValueError:
        return None

    if not parts:
        return None

    section = parts[0].lower()
    lower_parts = [part.lower() for part in parts]
    if section == "saved" or (
        section == "your_activity" and "saved" in lower_parts[1:]
    ):
        return "saved", "saved"
    if section in {"p", "reel", "tv"} and len(parts) > 1:
        return "post", parts[1]
    if section == "stories":
        return "story", parts[1] if len(parts) > 1 else ""
    if section in INSTAGRAM_RESERVED_PATHS:
        return None
    return "profile", parts[0]


class DownloaderApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.settings = load_settings()
        language = self.settings.get("language", "en")
        self.language = language if isinstance(language, str) and language in TEXT else "en"
        theme = self.settings.get("theme", "light")
        self.theme = theme if isinstance(theme, str) and theme in THEME_LABELS["en"] else "light"
        instagram_username = self.settings.get("instagram_username", "")
        self.instagram_username = (
            instagram_username.strip()
            if isinstance(instagram_username, str)
            else ""
        )

        self.root.title(APP_TITLE)
        try:
            self.root.geometry(str(self.settings.get("geometry", "720x520")))
        except tk.TclError:
            self.root.geometry("720x520")
        self.root.minsize(640, 460)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.events: queue.Queue[tuple[str, Any]] = queue.Queue()
        self.worker: threading.Thread | None = None
        self.auth_worker: threading.Thread | None = None
        self.auth_loader: Any = None
        self.auth_login_username = ""
        self.auth_pending_2fa = False
        self.auth_dialog: tk.Toplevel | None = None
        self.auth_status_var: tk.StringVar | None = None
        self.auth_code_frame: ttk.Frame | None = None
        self.auth_action_button: ttk.Button | None = None
        self.settings_dialog: tk.Toplevel | None = None
        self.settings_account_status_var: tk.StringVar | None = None
        self.settings_login_button: ttk.Button | None = None
        self.settings_logout_button: ttk.Button | None = None
        self.cancel_event = threading.Event()
        self.current_title = ""
        self.is_closing = False

        self.url_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(
            value=str(self.settings.get("output_dir") or DEFAULT_OUTPUT_DIR)
        )
        mode = self.settings.get("mode", "video")
        self.mode_var = tk.StringVar(value=mode if mode in ("video", "audio") else "video")
        self.quality_var = tk.StringVar()
        audio_format = self.settings.get("audio_format", "MP3")
        if not isinstance(audio_format, str) or audio_format not in dict(AUDIO_FORMATS):
            audio_format = "MP3"
        self.audio_format_var = tk.StringVar(value=audio_format)
        self.progress_var = tk.DoubleVar(value=0)
        self.status_var = tk.StringVar(value=self.t("ready"))
        self.details_var = tk.StringVar(value="")

        self.video_options: list[tuple[str, str]] = list(VIDEO_PRESETS)
        self.audio_options: list[tuple[str, str]] = list(AUDIO_PRESETS)
        self.quality_selectors: dict[str, str] = {}
        self.audio_quality_selectors: dict[str, str] = {}

        self._configure_dpi()
        self._build_ui()
        self._apply_theme()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.bind_all("<Control-KeyPress>", self._handle_control_shortcut, add="+")
        self.root.bind_all("<Shift-KeyPress-Insert>", self.paste_url, add="+")
        self._on_mode_changed()
        self.root.after(100, self._process_events)

    def t(self, key: str, **values: Any) -> str:
        text = TEXT.get(self.language, TEXT["en"]).get(key, TEXT["en"].get(key, key))
        return text.format(**values) if values else text

    def _language_label(self, language: str) -> str:
        return LANGUAGE_LABELS.get(language, language)

    def _theme_label(self, theme: str) -> str:
        return THEME_LABELS[self.language].get(theme, theme)

    def _instagram_session_available(self) -> bool:
        return bool(self.instagram_username and INSTAGRAM_SESSION_PATH.is_file())

    def _instagram_session_status(self) -> str:
        if self._instagram_session_available():
            return self.t("instagram_status_logged_in", username=self.instagram_username)
        if self.instagram_username:
            return self.t("instagram_status_missing")
        return self.t("instagram_status_logged_out")

    def _refresh_account_status(self) -> None:
        if self.settings_account_status_var is not None:
            self.settings_account_status_var.set(self._instagram_session_status())
        if self.settings_login_button is not None:
            self.settings_login_button.configure(
                state="disabled"
                if self.auth_worker and self.auth_worker.is_alive()
                else "normal"
            )
        if self.settings_logout_button is not None:
            self.settings_logout_button.configure(
                state="normal" if self._instagram_session_available() else "disabled"
            )

    def _apply_theme(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        if self.theme == "dark":
            colors = {
                "background": "#202124",
                "surface": "#292a2d",
                "entry": "#303134",
                "foreground": "#f1f3f4",
                "muted": "#bdc1c6",
                "accent": "#8ab4f8",
                "select": "#3c5a86",
            }
        else:
            colors = {
                "background": "#f4f4f4",
                "surface": "#ffffff",
                "entry": "#ffffff",
                "foreground": "#202124",
                "muted": "#666666",
                "accent": "#d9e8fb",
                "select": "#c7dcf5",
            }

        self.root.configure(background=colors["background"])
        style.configure("TFrame", background=colors["background"])
        style.configure(
            "TLabel",
            background=colors["background"],
            foreground=colors["foreground"],
        )
        style.configure(
            "TButton",
            background=colors["surface"],
            foreground=colors["foreground"],
            bordercolor=colors["muted"],
            lightcolor=colors["surface"],
            darkcolor=colors["surface"],
        )
        style.map(
            "TButton",
            background=[("active", colors["accent"]), ("disabled", colors["background"])],
            foreground=[("disabled", colors["muted"])],
        )
        style.configure(
            "Accent.TButton",
            background=colors["accent"],
            foreground=colors["foreground"],
        )
        style.configure(
            "TEntry",
            fieldbackground=colors["entry"],
            foreground=colors["foreground"],
            insertcolor=colors["foreground"],
        )
        style.configure(
            "TCombobox",
            fieldbackground=colors["entry"],
            background=colors["surface"],
            foreground=colors["foreground"],
            arrowcolor=colors["foreground"],
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", colors["entry"])],
            foreground=[("readonly", colors["foreground"])],
        )
        style.configure(
            "TRadiobutton",
            background=colors["background"],
            foreground=colors["foreground"],
        )
        style.map(
            "TRadiobutton",
            background=[("active", colors["background"])],
            foreground=[("disabled", colors["muted"])],
        )
        style.configure(
            "Horizontal.TProgressbar",
            troughcolor=colors["entry"],
            background="#20a464" if self.theme == "light" else "#81c995",
            bordercolor=colors["muted"],
            lightcolor="#20a464" if self.theme == "light" else "#81c995",
            darkcolor="#20a464" if self.theme == "light" else "#81c995",
        )

        if hasattr(self, "log"):
            self.log.configure(
                background=colors["entry"],
                foreground=colors["foreground"],
                insertbackground=colors["foreground"],
                selectbackground=colors["select"],
                selectforeground=colors["foreground"],
            )
        if hasattr(self, "details_label"):
            self.details_label.configure(foreground=colors["muted"])

    def _handle_control_shortcut(self, event: Any) -> str | None:
        keysym = str(getattr(event, "keysym", "")).lower()
        keycode = getattr(event, "keycode", None)
        # keycode 86 is the physical V key on Windows. The keycode check
        # also handles Ctrl+V when the Russian keyboard layout is active.
        if str(keycode) == "86" or keysym in {"v", "м", "cyrillic_em"}:
            if str(self.url_entry.cget("state")) != "disabled":
                return self.paste_url(event)
        return None

    def _configure_dpi(self) -> None:
        if sys.platform != "win32":
            return
        try:
            import ctypes

            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except (AttributeError, OSError):
            pass

    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding=16)
        main.grid(row=0, column=0, sticky="nsew")
        main.columnconfigure(1, weight=1)
        main.rowconfigure(7, weight=1)

        self.heading_label = ttk.Label(
            main,
            text=self.t("heading"),
            font=("Segoe UI", 16, "bold"),
        )
        self.heading_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 14))
        self.settings_button = ttk.Button(
            main,
            text=self.t("settings"),
            command=self.open_settings,
        )
        self.settings_button.grid(row=0, column=2, sticky="e", pady=(0, 14))

        self.url_label = ttk.Label(main, text=self.t("url"))
        self.url_label.grid(row=1, column=0, sticky="w", padx=(0, 8), pady=4)
        self.url_entry = ttk.Entry(main, textvariable=self.url_var)
        self.url_entry.grid(row=1, column=1, sticky="ew", pady=4)
        self.paste_button = ttk.Button(
            main,
            text=self.t("paste"),
            command=self.paste_url,
        )
        self.paste_button.grid(row=1, column=2, sticky="e", padx=(8, 0), pady=4)
        self.url_entry.bind("<Control-v>", self.paste_url)
        self.url_entry.bind("<Control-V>", self.paste_url)
        self.url_entry.bind("<Shift-Insert>", self.paste_url)
        self.url_entry.focus_set()

        self.mode_label = ttk.Label(main, text=self.t("mode"))
        self.mode_label.grid(row=2, column=0, sticky="w", padx=(0, 8), pady=4)
        mode_frame = ttk.Frame(main)
        mode_frame.grid(row=2, column=1, columnspan=2, sticky="w", pady=4)
        self.video_radio = ttk.Radiobutton(
            mode_frame,
            text=self.t("video"),
            value="video",
            variable=self.mode_var,
            command=self._on_mode_changed,
        )
        self.video_radio.pack(side="left", padx=(0, 14))
        self.audio_radio = ttk.Radiobutton(
            mode_frame,
            text=self.t("audio"),
            value="audio",
            variable=self.mode_var,
            command=self._on_mode_changed,
        )
        self.audio_radio.pack(side="left")

        self.quality_label = ttk.Label(main, text=self.t("quality"))
        self.quality_label.grid(row=3, column=0, sticky="w", padx=(0, 8), pady=4)
        self.quality_combo = ttk.Combobox(
            main,
            textvariable=self.quality_var,
            state="readonly",
        )
        self.quality_combo.grid(row=3, column=1, sticky="ew", pady=4)
        self.inspect_button = ttk.Button(
            main,
            text=self.t("inspect"),
            command=self.inspect_url,
        )
        self.inspect_button.grid(row=3, column=2, sticky="e", padx=(8, 0), pady=4)

        self.audio_frame = ttk.Frame(main)
        self.audio_frame.grid(row=4, column=1, columnspan=2, sticky="ew", pady=(2, 4))
        self.audio_frame.columnconfigure(1, weight=1)
        self.audio_format_label = ttk.Label(
            self.audio_frame,
            text=self.t("audio_format"),
        )
        self.audio_format_label.grid(
            row=0, column=0, sticky="w", padx=(0, 8)
        )
        self.audio_format_combo = ttk.Combobox(
            self.audio_frame,
            textvariable=self.audio_format_var,
            values=[label for label, _ in AUDIO_FORMATS],
            state="readonly",
            width=12,
        )
        self.audio_format_combo.grid(row=0, column=1, sticky="w")
        self.audio_frame.grid_remove()

        self.folder_label = ttk.Label(main, text=self.t("folder"))
        self.folder_label.grid(row=5, column=0, sticky="w", padx=(0, 8), pady=4)
        self.output_entry = ttk.Entry(main, textvariable=self.output_dir_var)
        self.output_entry.grid(row=5, column=1, sticky="ew", pady=4)
        self.browse_button = ttk.Button(
            main,
            text=self.t("browse"),
            command=self.choose_output_dir,
        )
        self.browse_button.grid(row=5, column=2, sticky="e", padx=(8, 0), pady=4)

        actions = ttk.Frame(main)
        actions.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(12, 8))
        actions.columnconfigure(0, weight=1)
        self.saved_button = ttk.Button(
            actions,
            text=self.t("instagram_saved"),
            command=self.start_saved_download,
        )
        self.saved_button.grid(row=0, column=1, sticky="e", padx=(8, 0))
        self.download_button = ttk.Button(
            actions,
            text=self.t("download"),
            command=self.start_download,
            style="Accent.TButton",
        )
        self.download_button.grid(row=0, column=2, sticky="e", padx=(8, 0))
        self.cancel_button = ttk.Button(
            actions,
            text=self.t("cancel"),
            command=self.cancel_download,
            state="disabled",
        )
        self.cancel_button.grid(row=0, column=3, sticky="e", padx=(8, 0))
        self.open_folder_button = ttk.Button(
            actions,
            text=self.t("open_folder"),
            command=self.open_output_dir,
        )
        self.open_folder_button.grid(row=0, column=4, sticky="e", padx=(8, 0))

        self.progressbar = ttk.Progressbar(
            main,
            variable=self.progress_var,
            maximum=100,
            mode="determinate",
        )
        self.progressbar.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(4, 2))
        self.status_label = ttk.Label(main, textvariable=self.status_var)
        self.status_label.grid(
            row=8, column=0, columnspan=3, sticky="w"
        )
        self.details_label = ttk.Label(
            main,
            textvariable=self.details_var,
        )
        self.details_label.grid(
            row=9, column=0, columnspan=3, sticky="w", pady=(2, 8)
        )

        self.log = scrolledtext.ScrolledText(
            main,
            height=7,
            wrap=tk.WORD,
            state="disabled",
            font=("Consolas", 9),
        )
        self.log.grid(row=10, column=0, columnspan=3, sticky="nsew", pady=(4, 0))
        main.rowconfigure(10, weight=1)

    def _on_mode_changed(self) -> None:
        if self.mode_var.get() == "audio":
            self.audio_frame.grid()
        else:
            self.audio_frame.grid_remove()
        self._set_quality_options()

    def _quality_label(self, value: str, mode: str) -> str:
        if value == "best":
            return self.t("best_available")
        if value.isdigit():
            if mode == "audio":
                return f"{self.t('up_to')} {value} kbps"
            suffix = " (4K)" if value == "2160" else ""
            return f"{value}p{suffix}"
        return value

    def _set_quality_options(self) -> None:
        if self.mode_var.get() == "video":
            localized = [
                (self._quality_label(label, "video"), selector)
                for label, selector in self.video_options
            ]
            self.quality_selectors = dict(localized)
            labels = list(self.quality_selectors)
        else:
            localized = [
                (self._quality_label(label, "audio"), selector)
                for label, selector in self.audio_options
            ]
            self.audio_quality_selectors = dict(localized)
            labels = list(self.audio_quality_selectors)

        self.quality_combo["values"] = labels
        if labels:
            self.quality_var.set(labels[0])

    def _log(self, message: str) -> None:
        self.log.configure(state="normal")
        self.log.insert(tk.END, message.rstrip() + "\n")
        self.log.see(tk.END)
        self.log.configure(state="disabled")

    def paste_url(self, _event: Any = None) -> str:
        if str(self.url_entry.cget("state")) == "disabled":
            return "break"
        try:
            clipboard = str(self.root.clipboard_get())
        except tk.TclError:
            messagebox.showwarning(
                APP_TITLE,
                self.t("clipboard_empty"),
            )
            return "break"

        lines = [line.strip() for line in clipboard.splitlines() if line.strip()]
        if not lines:
            messagebox.showwarning(APP_TITLE, self.t("clipboard_no_link"))
            return "break"

        self.url_var.set(lines[0])
        self.url_entry.focus_set()
        self.url_entry.icursor(tk.END)
        return "break"

    def open_settings(self) -> None:
        if self.is_closing:
            return
        if self.settings_dialog is not None:
            try:
                if self.settings_dialog.winfo_exists():
                    self.settings_dialog.focus_set()
                    return
            except tk.TclError:
                pass

        dialog = tk.Toplevel(self.root)
        self.settings_dialog = dialog
        dialog.title(self.t("settings_title"))
        dialog.transient(self.root)
        dialog.resizable(False, False)

        frame = ttk.Frame(dialog, padding=16)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(1, weight=1)

        language_var = tk.StringVar(value=self._language_label(self.language))
        theme_var = tk.StringVar(value=self._theme_label(self.theme))
        language_by_label = {
            self._language_label(language): language
            for language in ("en", "ru")
        }
        theme_by_label = {
            self._theme_label(theme): theme
            for theme in ("light", "dark")
        }

        ttk.Label(frame, text=self.t("language")).grid(
            row=0, column=0, sticky="w", padx=(0, 12), pady=4
        )
        language_combo = ttk.Combobox(
            frame,
            textvariable=language_var,
            values=list(language_by_label),
            state="readonly",
            width=18,
        )
        language_combo.grid(row=0, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text=self.t("theme")).grid(
            row=1, column=0, sticky="w", padx=(0, 12), pady=4
        )
        theme_combo = ttk.Combobox(
            frame,
            textvariable=theme_var,
            values=list(theme_by_label),
            state="readonly",
            width=18,
        )
        theme_combo.grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Separator(frame, orient="horizontal").grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(10, 6),
        )
        ttk.Label(
            frame,
            text=self.t("instagram_account"),
            font=("Segoe UI", 10, "bold"),
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 2))

        self.settings_account_status_var = tk.StringVar(
            value=self._instagram_session_status()
        )
        ttk.Label(frame, textvariable=self.settings_account_status_var).grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="w",
            pady=2,
        )
        ttk.Label(
            frame,
            text=self.t("instagram_private_note"),
            wraplength=360,
            justify="left",
        ).grid(
            row=5,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 2),
        )
        ttk.Label(
            frame,
            text=self.t("instagram_session_note"),
            wraplength=360,
            justify="left",
        ).grid(
            row=6,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 4),
        )

        account_buttons = ttk.Frame(frame)
        account_buttons.grid(row=7, column=0, columnspan=2, sticky="e", pady=4)
        self.settings_logout_button = ttk.Button(
            account_buttons,
            text=self.t("instagram_logout"),
            command=self.logout_instagram,
            state="normal" if self._instagram_session_available() else "disabled",
        )
        self.settings_logout_button.pack(side="right", padx=(8, 0))
        self.settings_login_button = ttk.Button(
            account_buttons,
            text=self.t("instagram_login"),
            command=lambda: self.open_instagram_login(dialog),
        )
        self.settings_login_button.pack(side="right")

        buttons = ttk.Frame(frame)
        buttons.grid(row=8, column=0, columnspan=2, sticky="e", pady=(12, 0))

        def close_dialog() -> None:
            try:
                dialog.grab_release()
            except tk.TclError:
                pass
            self.settings_dialog = None
            self.settings_account_status_var = None
            self.settings_login_button = None
            self.settings_logout_button = None
            dialog.destroy()

        def apply_settings() -> None:
            self.language = language_by_label.get(language_var.get(), "en")
            self.theme = theme_by_label.get(theme_var.get(), "light")
            self._apply_theme()
            self._refresh_texts()
            self._set_quality_options()
            self._save_settings()
            close_dialog()

        ttk.Button(
            buttons,
            text=self.t("close"),
            command=close_dialog,
        ).pack(side="right", padx=(8, 0))
        ttk.Button(
            buttons,
            text=self.t("save"),
            command=apply_settings,
            style="Accent.TButton",
        ).pack(side="right")

        dialog.protocol("WM_DELETE_WINDOW", close_dialog)
        dialog.grab_set()
        language_combo.focus_set()

    def open_instagram_login(self, parent: tk.Toplevel | None = None) -> None:
        if self.is_closing:
            return
        if instaloader is None:
            messagebox.showerror(APP_TITLE, self.t("instagram_dependency_error"))
            return
        if self.auth_dialog is not None:
            try:
                if self.auth_dialog.winfo_exists():
                    self.auth_dialog.focus_set()
                    return
            except tk.TclError:
                pass

        dialog = tk.Toplevel(parent or self.root)
        self.auth_dialog = dialog
        dialog.title(self.t("instagram_login_title"))
        dialog.transient(parent or self.root)
        dialog.resizable(False, False)

        frame = ttk.Frame(dialog, padding=16)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(1, weight=1)

        username_var = tk.StringVar(value=self.instagram_username)
        password_var = tk.StringVar()
        code_var = tk.StringVar()
        status_var = tk.StringVar()
        self.auth_username_var = username_var
        self.auth_password_var = password_var
        self.auth_code_var = code_var
        self.auth_status_var = status_var
        self.auth_pending_2fa = False

        ttk.Label(frame, text=self.t("instagram_username")).grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 12),
            pady=4,
        )
        username_entry = ttk.Entry(frame, textvariable=username_var, width=28)
        username_entry.grid(row=0, column=1, sticky="ew", pady=4)
        self.auth_username_entry = username_entry

        ttk.Label(frame, text=self.t("instagram_password")).grid(
            row=1,
            column=0,
            sticky="w",
            padx=(0, 12),
            pady=4,
        )
        password_entry = ttk.Entry(frame, textvariable=password_var, show="*", width=28)
        password_entry.grid(row=1, column=1, sticky="ew", pady=4)
        self.auth_password_entry = password_entry

        self.auth_code_frame = ttk.Frame(frame)
        self.auth_code_frame.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=4,
        )
        self.auth_code_frame.columnconfigure(1, weight=1)
        ttk.Label(self.auth_code_frame, text=self.t("instagram_two_factor")).grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 12),
        )
        code_entry = ttk.Entry(self.auth_code_frame, textvariable=code_var, width=28)
        code_entry.grid(row=0, column=1, sticky="ew")
        self.auth_code_entry = code_entry
        self.auth_code_frame.grid_remove()

        ttk.Label(
            frame,
            textvariable=status_var,
            wraplength=360,
            justify="left",
        ).grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(8, 4),
        )

        buttons = ttk.Frame(frame)
        buttons.grid(row=4, column=0, columnspan=2, sticky="e", pady=(8, 0))

        def close_dialog() -> None:
            if self.auth_worker and self.auth_worker.is_alive():
                return
            self._close_auth_dialog()

        def submit() -> None:
            if self.auth_pending_2fa:
                code = code_var.get().strip()
                if not code:
                    status_var.set(self.t("instagram_two_factor"))
                    return
                self._set_auth_busy(True)
                self.auth_worker = threading.Thread(
                    target=self._instagram_two_factor_worker,
                    args=(code,),
                    daemon=True,
                )
                self.auth_worker.start()
                return

            username = username_var.get().strip()
            password = password_var.get()
            if not username or not password:
                status_var.set(self.t("instagram_login_error", text=self.t("instagram_username")))
                return
            self.auth_login_username = username
            status_var.set(self.t("instagram_login_starting"))
            self._set_auth_busy(True)
            self.auth_worker = threading.Thread(
                target=self._instagram_login_worker,
                args=(username, password),
                daemon=True,
            )
            self.auth_worker.start()

        self.auth_action_button = ttk.Button(
            buttons,
            text=self.t("instagram_login_submit"),
            command=submit,
            style="Accent.TButton",
        )
        self.auth_action_button.pack(side="right")
        ttk.Button(
            buttons,
            text=self.t("close"),
            command=close_dialog,
        ).pack(side="right", padx=(8, 0))

        dialog.protocol("WM_DELETE_WINDOW", close_dialog)
        dialog.grab_set()
        username_entry.focus_set()

    def _set_auth_busy(self, busy: bool) -> None:
        state = "disabled" if busy else "normal"
        for entry_name in (
            "auth_username_entry",
            "auth_password_entry",
            "auth_code_entry",
        ):
            entry = getattr(self, entry_name, None)
            if entry is not None:
                try:
                    entry_state = state
                    if (
                        not busy
                        and self.auth_pending_2fa
                        and entry_name in {"auth_username_entry", "auth_password_entry"}
                    ):
                        entry_state = "disabled"
                    entry.configure(state=entry_state)
                except tk.TclError:
                    pass
        if self.auth_action_button is not None:
            try:
                self.auth_action_button.configure(state=state)
            except tk.TclError:
                pass

    def _close_auth_dialog(self) -> None:
        dialog = self.auth_dialog
        self.auth_dialog = None
        self.auth_status_var = None
        self.auth_code_frame = None
        self.auth_action_button = None
        self.auth_loader = None
        self.auth_login_username = ""
        self.auth_pending_2fa = False
        password_var = getattr(self, "auth_password_var", None)
        if password_var is not None:
            password_var.set("")
        for attribute in (
            "auth_username_entry",
            "auth_password_entry",
            "auth_code_entry",
            "auth_username_var",
            "auth_password_var",
            "auth_code_var",
        ):
            setattr(self, attribute, None)
        if dialog is not None:
            try:
                dialog.grab_release()
            except tk.TclError:
                pass
            try:
                dialog.destroy()
            except tk.TclError:
                pass

    def _save_instagram_session(self, loader: Any, username: str) -> None:
        INSTAGRAM_SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = INSTAGRAM_SESSION_PATH.with_name(
            INSTAGRAM_SESSION_PATH.name + ".tmp"
        )
        try:
            loader.save_session_to_file(filename=str(temporary_path))
            temporary_path.replace(INSTAGRAM_SESSION_PATH)
        finally:
            try:
                temporary_path.unlink()
            except OSError:
                pass

    def _instagram_login_worker(self, username: str, password: str) -> None:
        try:
            loader = self._create_instaloader()
            try:
                loader.login(username, password)
            except Exception as error:
                two_factor_error = getattr(
                    instaloader,
                    "TwoFactorAuthRequiredException",
                    None,
                )
                if two_factor_error and isinstance(error, two_factor_error):
                    self.auth_loader = loader
                    self.events.put(("auth_2fa", None))
                    return
                raise
            self._save_instagram_session(loader, username)
        except Exception as error:
            self.auth_loader = None
            self.events.put(("auth_error", self._friendly_error(error)))
            return
        self.events.put(("auth_done", username))

    def _instagram_two_factor_worker(self, code: str) -> None:
        loader = self.auth_loader
        if loader is None:
            self.events.put(
                ("auth_error", self.t("instagram_login_error", text="No pending login."))
            )
            return
        username = self.auth_login_username
        try:
            loader.two_factor_login(code)
            self._save_instagram_session(loader, username)
        except Exception as error:
            self.auth_loader = None
            self.events.put(("auth_error", self._friendly_error(error)))
            return
        self.events.put(("auth_done", username))

    def logout_instagram(self) -> None:
        if not INSTAGRAM_SESSION_PATH.is_file():
            self.instagram_username = ""
            self._save_settings()
            self._refresh_account_status()
            return
        username = self.instagram_username or "Instagram"
        if not messagebox.askyesno(
            APP_TITLE,
            self.t("instagram_logout_confirm", username=username),
        ):
            return
        try:
            INSTAGRAM_SESSION_PATH.unlink()
        except OSError as error:
            messagebox.showerror(
                APP_TITLE,
                self.t("instagram_logout_error", text=error),
            )
            return
        self.instagram_username = ""
        self.auth_loader = None
        self._save_settings()
        self._refresh_account_status()

    def _refresh_texts(self) -> None:
        self.root.title(APP_TITLE)
        self.heading_label.configure(text=self.t("heading"))
        self.settings_button.configure(text=self.t("settings"))
        self.url_label.configure(text=self.t("url"))
        self.paste_button.configure(text=self.t("paste"))
        self.mode_label.configure(text=self.t("mode"))
        self.video_radio.configure(text=self.t("video"))
        self.audio_radio.configure(text=self.t("audio"))
        self.quality_label.configure(text=self.t("quality"))
        self.inspect_button.configure(text=self.t("inspect"))
        self.audio_format_label.configure(text=self.t("audio_format"))
        self.folder_label.configure(text=self.t("folder"))
        self.browse_button.configure(text=self.t("browse"))
        self.saved_button.configure(text=self.t("instagram_saved"))
        self.download_button.configure(text=self.t("download"))
        self.cancel_button.configure(text=self.t("cancel"))
        self.open_folder_button.configure(text=self.t("open_folder"))
        if not self.worker or not self.worker.is_alive():
            self.status_var.set(self.t("ready"))

    def _save_settings(self) -> None:
        self.settings.update(
            {
                "language": self.language,
                "theme": self.theme,
                "output_dir": self.output_dir_var.get(),
                "mode": self.mode_var.get(),
                "audio_format": self.audio_format_var.get(),
                "geometry": self.root.geometry(),
                "instagram_username": self.instagram_username,
            }
        )
        save_settings(self.settings)

    def choose_output_dir(self) -> None:
        selected = filedialog.askdirectory(
            title=self.t("folder"),
            initialdir=self.output_dir_var.get() or str(Path.home()),
        )
        if selected:
            self.output_dir_var.set(selected)
            self._save_settings()

    def open_output_dir(self) -> None:
        output_dir = Path(self.output_dir_var.get()).expanduser()
        output_dir.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(output_dir)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            os.system(f'open "{output_dir}"')
        else:
            os.system(f'xdg-open "{output_dir}"')

    def _check_dependency(self, url: str = "") -> bool:
        if yt_dlp is None and not (is_instagram_url(url) and instaloader is not None):
            messagebox.showerror(
                APP_TITLE,
                self.t("dependency_error"),
            )
            return False
        return True

    def _get_url(self) -> str:
        return self.url_var.get().strip()

    def inspect_url(self) -> None:
        url = self._get_url()
        if not url:
            messagebox.showwarning(APP_TITLE, self.t("paste_video"))
            return
        if not self._check_dependency(url):
            return

        self._set_busy(True, inspecting=True)
        self.status_var.set(self.t("fetching"))
        self.details_var.set("")
        self._log(self.t("checking", url=url))
        if is_instagram_url(url):
            self._set_instagram_quality_options()
            self.status_var.set(self.t("ready_download"))
            self.details_var.set(self.t("instagram_quality_note"))
            self._log(self.t("instagram_detected"))
            self._set_busy(False)
            return

        self.worker = threading.Thread(
            target=self._inspect_worker,
            args=(url,),
            daemon=True,
        )
        self.worker.start()

    def _inspect_worker(self, url: str) -> None:
        try:
            options = {
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "skip_download": True,
                "socket_timeout": 15,
            }
            with yt_dlp.YoutubeDL(options) as downloader:
                info = downloader.extract_info(url, download=False)
            self.events.put(("inspection_done", info))
        except Exception as error:
            self.events.put(("error", self._friendly_error(error)))

    def _set_instagram_quality_options(self) -> None:
        self.video_options = [("best", "bestvideo+bestaudio/best")]
        self.audio_options = [("best", "bestaudio/best")]
        self._set_quality_options()

    def _apply_inspection(self, info: dict[str, Any]) -> None:
        title = info.get("title") or self.t("untitled")
        self.current_title = str(title)

        video_heights: set[int] = set()
        audio_rates: set[int] = set()
        for item in info.get("formats") or []:
            if item.get("vcodec") not in (None, "none"):
                height = item.get("height")
                if isinstance(height, int) and height > 0:
                    video_heights.add(height)
            if item.get("acodec") not in (None, "none"):
                abr = safe_float(item.get("abr"))
                if abr and abr > 0:
                    audio_rates.add(round(abr))

        if video_heights:
            ordered_heights = sorted(video_heights, reverse=True)
            self.video_options = [("best", "bestvideo+bestaudio/best")]
            self.video_options.extend(
                (
                    str(height),
                    f"bestvideo[height<={height}]+bestaudio/best[height<={height}]",
                )
                for height in ordered_heights
            )
        else:
            self.video_options = list(VIDEO_PRESETS)

        if audio_rates:
            ordered_rates = sorted(audio_rates, reverse=True)
            self.audio_options = [("best", "bestaudio/best")]
            self.audio_options.extend(
                (
                    str(rate),
                    f"bestaudio[abr<={rate}]/bestaudio/best",
                )
                for rate in ordered_rates
            )
        else:
            self.audio_options = list(AUDIO_PRESETS)

        self._set_quality_options()
        self.details_var.set(
            self.t(
                "available_formats",
                title=self.current_title,
                count=len(info.get("formats") or []),
            )
        )
        self._log(self.t("qualities_updated"))
        self.status_var.set(self.t("ready_download"))

    def start_saved_download(self) -> None:
        if instaloader is None:
            messagebox.showerror(APP_TITLE, self.t("instagram_dependency_error"))
            return
        if not self._instagram_session_available():
            messagebox.showwarning(APP_TITLE, self.t("instagram_no_session"))
            return

        output_dir = Path(self.output_dir_var.get()).expanduser()
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            messagebox.showerror(APP_TITLE, self.t("folder_error", error=error))
            return

        ffmpeg = find_ffmpeg()
        if not ffmpeg:
            messagebox.showerror(
                APP_TITLE,
                self.t("ffmpeg_error"),
            )
            return

        mode = self.mode_var.get()
        self.cancel_event.clear()
        self.progress_var.set(0)
        self.details_var.set("")
        self._set_busy(True)
        self.status_var.set(self.t("instagram_saved_starting"))
        self._log(
            self.t(
                "instagram_saved_log",
                username=self.instagram_username,
            )
        )
        self.worker = threading.Thread(
            target=self._saved_download_worker,
            args=(output_dir, mode, ffmpeg),
            daemon=True,
        )
        self.worker.start()

    def start_download(self) -> None:
        url = self._get_url()
        if not url:
            messagebox.showwarning(APP_TITLE, self.t("paste_video"))
            return
        if not self._check_dependency(url):
            return
        instagram_target = parse_instagram_url(url) if is_instagram_url(url) else None
        if instagram_target and instagram_target[0] == "saved":
            self.start_saved_download()
            return

        output_dir = Path(self.output_dir_var.get()).expanduser()
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            messagebox.showerror(APP_TITLE, self.t("folder_error", error=error))
            return

        ffmpeg = find_ffmpeg()
        if not ffmpeg:
            messagebox.showerror(
                APP_TITLE,
                self.t("ffmpeg_error"),
            )
            return

        mode = self.mode_var.get()
        if is_instagram_url(url) and mode == "video":
            selector = "bestvideo+bestaudio/best"
        elif is_instagram_url(url):
            selector = "bestaudio/best"
        elif mode == "video":
            selector = self.quality_selectors.get(
                self.quality_var.get(),
                "bestvideo+bestaudio/best",
            )
        else:
            selector = self.audio_quality_selectors.get(
                self.quality_var.get(),
                "bestaudio/best",
            )

        self.cancel_event.clear()
        self.progress_var.set(0)
        self.details_var.set("")
        self._set_busy(True)
        self.status_var.set(self.t("starting"))
        self._log(self.t("downloading_log", url=url))
        if is_instagram_url(url):
            self._log(self.t("instagram_ytdlp_primary"))

        args = (url, output_dir, mode, selector, ffmpeg)
        self.worker = threading.Thread(target=self._download_worker, args=args, daemon=True)
        self.worker.start()

    def _saved_download_worker(
        self,
        output_dir: Path,
        mode: str,
        ffmpeg: str,
    ) -> None:
        try:
            self._download_saved_instagram(output_dir, mode, ffmpeg)
            if self.cancel_event.is_set():
                self.events.put(("cancelled", None))
            else:
                self.events.put(("done", None))
        except DownloadCancelled:
            self.events.put(("cancelled", None))
        except Exception as error:
            if self.cancel_event.is_set():
                self.events.put(("cancelled", None))
            else:
                self.events.put(("error", self._friendly_error(error)))

    def _download_worker(
        self,
        url: str,
        output_dir: Path,
        mode: str,
        selector: str,
        ffmpeg: str,
    ) -> None:
        def progress_hook(data: dict[str, Any]) -> None:
            if self.cancel_event.is_set():
                raise DownloadCancelled()
            self.events.put(("progress", data))

        try:
            if is_instagram_url(url):
                self._download_instagram(
                    url,
                    output_dir,
                    mode,
                    selector,
                    ffmpeg,
                    progress_hook,
                )
            else:
                self._download_with_yt_dlp(
                    url,
                    output_dir,
                    mode,
                    selector,
                    ffmpeg,
                    progress_hook,
                )
            if self.cancel_event.is_set():
                self.events.put(("cancelled", None))
            else:
                self.events.put(("done", None))
        except DownloadCancelled:
            self.events.put(("cancelled", None))
        except Exception as error:
            if self.cancel_event.is_set():
                self.events.put(("cancelled", None))
            else:
                self.events.put(("error", self._friendly_error(error)))

    def _create_instaloader(
        self,
        output_dir: Path | None = None,
        mode: str = "video",
    ) -> Any:
        if instaloader is None:
            raise RuntimeError(self.t("instagram_dependency_error"))

        options: dict[str, Any] = {
            "sleep": False,
            "quiet": True,
            "download_pictures": mode == "video",
            "download_videos": True,
            "download_video_thumbnails": False,
            "download_geotags": False,
            "download_comments": False,
            "save_metadata": False,
            "compress_json": False,
            "post_metadata_txt_pattern": "",
            "storyitem_metadata_txt_pattern": "",
            "max_connection_attempts": 3,
            "request_timeout": 15,
            "sanitize_paths": True,
        }
        if output_dir is not None:
            options.update(
                {
                    "dirname_pattern": str(output_dir / "{target}"),
                    "filename_pattern": "{date_utc}_UTC",
                }
            )
        return instaloader.Instaloader(**options)

    def _load_instagram_session(self, loader: Any) -> bool:
        if not self.instagram_username or not INSTAGRAM_SESSION_PATH.is_file():
            return False
        try:
            loader.load_session_from_file(
                self.instagram_username,
                filename=str(INSTAGRAM_SESSION_PATH),
            )
        except Exception as error:
            raise RuntimeError(
                self.t(
                    "instagram_session_error",
                    text=self._friendly_error(error),
                )
            ) from error
        return True

    def _instagram_http_headers(self) -> dict[str, str]:
        loader = self._create_instaloader()
        if not self._load_instagram_session(loader):
            return {}

        session = getattr(loader.context, "_session", None)
        cookies = getattr(session, "cookies", None)
        if cookies is None:
            return {}
        cookie_values = [
            f"{cookie.name}={cookie.value}"
            for cookie in cookies
            if "instagram.com" in (cookie.domain or "")
        ]
        if not cookie_values:
            return {}

        headers = {"Cookie": "; ".join(cookie_values)}
        user_agent = getattr(loader.context, "user_agent", "")
        if user_agent:
            headers["User-Agent"] = str(user_agent)
        return headers

    def _download_with_yt_dlp(
        self,
        url: str,
        output_dir: Path,
        mode: str,
        selector: str,
        ffmpeg: str,
        progress_hook: Any,
        http_headers: dict[str, str] | None = None,
    ) -> None:
        if yt_dlp is None:
            raise RuntimeError(self.t("dependency_error"))

        options: dict[str, Any] = {
            "format": selector,
            "outtmpl": str(output_dir / "%(title)s [%(id)s].%(ext)s"),
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "progress_hooks": [progress_hook],
            "ffmpeg_location": ffmpeg,
            "windowsfilenames": True,
            "retries": 3,
            "fragment_retries": 3,
            "file_access_retries": 3,
            "socket_timeout": 15,
        }
        if http_headers:
            options["http_headers"] = http_headers

        if mode == "video":
            options["merge_output_format"] = "mp4"
        else:
            audio_format = dict(AUDIO_FORMATS).get(self.audio_format_var.get(), "mp3")
            audio_quality = self._audio_postprocess_quality()
            options["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": audio_format,
                    "preferredquality": audio_quality,
                }
            ]

        with yt_dlp.YoutubeDL(options) as downloader:
            downloader.download([url])

    def _download_instagram(
        self,
        url: str,
        output_dir: Path,
        mode: str,
        selector: str,
        ffmpeg: str,
        progress_hook: Any,
    ) -> None:
        primary_error: Exception
        if yt_dlp is None:
            primary_error = RuntimeError(self.t("dependency_error"))
        else:
            try:
                http_headers = self._instagram_http_headers()
            except Exception as error:
                http_headers = None
                self.events.put(
                    (
                        "log",
                        self.t(
                            "instagram_session_error",
                            text=self._friendly_error(error),
                        ),
                    )
                )
            try:
                self._download_with_yt_dlp(
                    url,
                    output_dir,
                    mode,
                    selector,
                    ffmpeg,
                    progress_hook,
                    http_headers,
                )
                return
            except DownloadCancelled:
                raise
            except Exception as error:
                primary_error = error
                self.events.put(
                    (
                        "log",
                        self.t(
                            "instagram_fallback_log",
                            text=self._friendly_error(error),
                        ),
                    )
                )

        if self.cancel_event.is_set():
            raise DownloadCancelled()
        if instaloader is None:
            raise RuntimeError(
                self.t(
                    "instagram_fallback_unavailable",
                    primary=self._friendly_error(primary_error),
                )
            )

        self.events.put(("status", self.t("instagram_fallback")))
        try:
            self._download_with_instaloader(url, output_dir, mode, ffmpeg)
        except DownloadCancelled:
            raise
        except Exception as fallback_error:
            raise RuntimeError(
                self.t(
                    "instagram_fallback_error",
                    primary=self._friendly_error(primary_error),
                    fallback=self._friendly_error(fallback_error),
                )
            ) from fallback_error

    def _download_saved_instagram(
        self,
        output_dir: Path,
        mode: str,
        ffmpeg: str,
    ) -> None:
        loader = self._create_instaloader(output_dir, mode)
        self._load_instagram_session(loader)
        self._raise_if_cancelled()

        target = "instagram_saved"
        media_root = output_dir / target
        profile = instaloader.Profile.own_profile(loader.context)
        saved_posts = profile.get_saved_posts()
        post_count = 0

        def post_filter(_post: Any) -> bool:
            nonlocal post_count
            self._raise_if_cancelled()
            post_count += 1
            return True

        loader.posts_download_loop(
            saved_posts,
            target=target,
            post_filter=post_filter,
            total_count=getattr(saved_posts, "count", None),
        )
        self._raise_if_cancelled()
        if post_count == 0 or not any(path.is_file() for path in media_root.rglob("*")):
            raise RuntimeError(self.t("instagram_saved_no_media"))
        if mode == "audio":
            self._convert_instagram_audio(media_root, ffmpeg)

    def _download_with_instaloader(
        self,
        url: str,
        output_dir: Path,
        mode: str,
        ffmpeg: str,
    ) -> None:
        if instaloader is None:
            raise RuntimeError(self.t("instagram_fallback_unavailable", primary=""))

        target_info = parse_instagram_url(url)
        if not target_info:
            raise RuntimeError(self.t("instagram_invalid"))

        target_kind, identifier = target_info
        if target_kind == "story" and not identifier:
            raise RuntimeError(self.t("instagram_invalid"))

        target = re.sub(r"[^A-Za-z0-9._-]+", "_", identifier).strip("._") or "instagram"
        media_root = output_dir / target
        loader = self._create_instaloader(output_dir, mode)
        self._load_instagram_session(loader)

        self._raise_if_cancelled()
        post_count = 0
        if target_kind == "post":
            post = instaloader.Post.from_shortcode(loader.context, identifier)
            self._raise_if_cancelled()
            loader.download_post(post, target=target)
            post_count = 1
        elif target_kind == "profile":
            profile = instaloader.Profile.from_username(loader.context, identifier)
            for post in profile.get_posts():
                self._raise_if_cancelled()
                loader.download_post(post, target=target)
                post_count += 1
        else:
            profile = instaloader.Profile.from_username(loader.context, identifier)
            loader.download_stories(
                userids=[profile],
                filename_target=target,
                storyitem_filter=lambda _item: not self.cancel_event.is_set(),
            )

        self._raise_if_cancelled()
        if target_kind != "story" and post_count == 0:
            raise RuntimeError(self.t("instagram_no_media"))
        if target_kind == "story" and not any(path.is_file() for path in media_root.rglob("*")):
            raise RuntimeError(self.t("instagram_no_media"))

        if mode == "audio":
            self._convert_instagram_audio(media_root, ffmpeg)

    def _convert_instagram_audio(self, media_root: Path, ffmpeg: str) -> None:
        media_files = sorted(
            path
            for path in media_root.rglob("*")
            if path.is_file() and path.suffix.lower() in {".mp4", ".webm", ".mkv", ".mov"}
        )
        if not media_files:
            raise RuntimeError(self.t("instagram_no_audio"))

        audio_format = dict(AUDIO_FORMATS).get(self.audio_format_var.get(), "mp3")
        audio_quality = self._audio_postprocess_quality()
        bitrate = audio_quality if audio_quality != "0" else "192"
        codec = {
            "mp3": "libmp3lame",
            "m4a": "aac",
            "opus": "libopus",
        }.get(audio_format, "libmp3lame")

        for source in media_files:
            self._raise_if_cancelled()
            destination = source.with_suffix(f".{audio_format}")
            self.events.put(("status", self.t("instagram_processing")))
            process = subprocess.Popen(
                [
                    ffmpeg,
                    "-y",
                    "-i",
                    str(source),
                    "-vn",
                    "-codec:a",
                    codec,
                    "-b:a",
                    f"{bitrate}k",
                    str(destination),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            while process.poll() is None:
                if self.cancel_event.is_set():
                    process.terminate()
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    raise DownloadCancelled()
                time.sleep(0.1)

            _stdout, stderr = process.communicate()
            if process.returncode != 0:
                details = (stderr or "").strip()
                raise RuntimeError(details or self.t("ffmpeg_processing", text=""))
            try:
                source.unlink()
            except OSError:
                pass

    def _raise_if_cancelled(self) -> None:
        if self.cancel_event.is_set():
            raise DownloadCancelled()

    def _audio_postprocess_quality(self) -> str:
        selected = self.quality_var.get()
        match = re.search(r"(\d+)", selected)
        if match:
            return match.group(1)
        return "0"

    def cancel_download(self) -> None:
        if self.worker and self.worker.is_alive():
            self.cancel_event.set()
            self.cancel_button.configure(state="disabled")
            self.status_var.set(self.t("canceling"))

    def _on_close(self) -> None:
        if self.is_closing:
            return

        self._save_settings()
        self.is_closing = True
        self.cancel_event.set()

        if (
            (self.worker and self.worker.is_alive())
            or (self.auth_worker and self.auth_worker.is_alive())
        ):
            self.status_var.set(self.t("stopping"))
            self.details_var.set(self.t("close_wait"))
            self._set_busy(True)
            self.cancel_button.configure(state="disabled")
            self.root.after(100, self._wait_for_workers)
        else:
            self.root.destroy()

    def _wait_for_workers(self) -> None:
        if (
            (self.worker and self.worker.is_alive())
            or (self.auth_worker and self.auth_worker.is_alive())
        ):
            self.root.after(100, self._wait_for_workers)
            return
        self.root.destroy()

    def _process_events(self) -> None:
        try:
            while True:
                event, payload = self.events.get_nowait()
                if event == "auth_2fa":
                    self.auth_pending_2fa = True
                    if not self.is_closing:
                        self._set_auth_busy(False)
                        if self.auth_code_frame is not None:
                            self.auth_code_frame.grid()
                        if self.auth_action_button is not None:
                            self.auth_action_button.configure(
                                text=self.t("instagram_verify")
                            )
                        if self.auth_status_var is not None:
                            self.auth_status_var.set(self.t("instagram_login_2fa"))
                        auth_code_entry = getattr(self, "auth_code_entry", None)
                        if auth_code_entry is not None:
                            auth_code_entry.focus_set()
                    self.root.after(100, self._refresh_account_status)
                elif event == "auth_done":
                    self.instagram_username = str(payload)
                    self.auth_loader = None
                    self.auth_pending_2fa = False
                    self._save_settings()
                    self._refresh_account_status()
                    if not self.is_closing:
                        success_text = self.t(
                            "instagram_login_success",
                            username=self.instagram_username,
                        )
                        self._close_auth_dialog()
                        messagebox.showinfo(APP_TITLE, success_text)
                    self.root.after(100, self._refresh_account_status)
                elif event == "auth_error":
                    self.auth_loader = None
                    self.auth_pending_2fa = False
                    if not self.is_closing:
                        self._set_auth_busy(False)
                        if self.auth_status_var is not None:
                            self.auth_status_var.set(
                                self.t("instagram_login_error", text=str(payload))
                            )
                        messagebox.showerror(
                            APP_TITLE,
                            self.t("instagram_login_error", text=str(payload)),
                        )
                    self.root.after(100, self._refresh_account_status)
                elif event == "progress":
                    if not self.is_closing:
                        self._update_progress(payload)
                elif event == "status":
                    if not self.is_closing:
                        self.status_var.set(str(payload))
                        self.details_var.set("")
                elif event == "log":
                    if not self.is_closing:
                        self._log(str(payload))
                elif event == "inspection_done":
                    if not self.is_closing:
                        self._apply_inspection(payload)
                    self._set_busy(False)
                elif event == "done":
                    if not self.is_closing:
                        self.progress_var.set(100)
                        self.status_var.set(self.t("done"))
                        self.details_var.set(self.t("saved"))
                        self._log(self.t("download_complete"))
                    self._set_busy(False)
                elif event == "cancelled":
                    if not self.is_closing:
                        self.status_var.set(self.t("cancelled"))
                        self.details_var.set("")
                        self._log(self.t("download_cancelled"))
                    self._set_busy(False)
                elif event == "error":
                    if not self.is_closing:
                        self.status_var.set(self.t("error"))
                        self.details_var.set("")
                        self._log(self.t("error_log", text=payload))
                        messagebox.showerror(APP_TITLE, str(payload))
                    self._set_busy(False)
        except queue.Empty:
            pass
        self.root.after(100, self._process_events)

    def _update_progress(self, data: dict[str, Any]) -> None:
        status = data.get("status")
        if status == "finished":
            self.status_var.set(self.t("processing"))
            self.details_var.set("")
            return

        if status != "downloading":
            return

        downloaded = data.get("downloaded_bytes") or 0
        total = data.get("total_bytes") or data.get("total_bytes_estimate")
        if total:
            self.progress_var.set(min(100, downloaded * 100 / total))

        percent = self.progress_var.get()
        speed = format_speed(data.get("speed"), self.t("per_second"))
        eta = format_eta(data.get("eta"))
        self.status_var.set(self.t("downloading", percent=percent))
        self.details_var.set(
            self.t(
                "progress_details",
                downloaded=format_bytes(downloaded),
                speed=speed,
                remaining=self.t("remaining"),
                eta=eta,
            )
        )

    def _set_busy(self, busy: bool, inspecting: bool = False) -> None:
        state = "disabled" if busy else "normal"
        self.url_entry.configure(state=state)
        self.output_entry.configure(state=state)
        self.browse_button.configure(state=state)
        self.paste_button.configure(state=state)
        self.settings_button.configure(state=state)
        self.saved_button.configure(state=state)
        self.download_button.configure(state=state)
        self.inspect_button.configure(state=state)
        self.quality_combo.configure(state="disabled" if busy else "readonly")
        self.audio_format_combo.configure(state="disabled" if busy else "readonly")
        self.video_radio.configure(state=state)
        self.audio_radio.configure(state=state)
        self.cancel_button.configure(state="normal" if busy and not inspecting else "disabled")

    def _friendly_error(self, error: Exception) -> str:
        text = str(error).strip()
        text = re.sub(r"^\s*ERROR:\s*", "", text, flags=re.IGNORECASE)
        lower_text = text.lower()
        if any(
            marker in lower_text
            for marker in (
                "loginrequiredexception",
                "login required",
                "privateprofilenotfollowedexception",
                "private profile",
            )
        ):
            return self.t("instagram_login_required")
        if "Sign in to confirm" in text or "not a bot" in text.lower():
            return self.t("not_bot", text=text)
        if "ffmpeg" in text.lower():
            return self.t("ffmpeg_processing", text=text)
        return text or error.__class__.__name__


def main() -> None:
    root = tk.Tk()
    icon_path = resource_path("icon.ico")
    if icon_path.is_file():
        try:
            root.iconbitmap(default=str(icon_path))
        except tk.TclError:
            pass
    try:
        root.iconname(APP_TITLE)
    except tk.TclError:
        pass
    DownloaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
