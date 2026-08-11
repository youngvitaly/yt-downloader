from __future__ import annotations

import os
import json
import queue
import re
import shutil
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import Any

try:
    import yt_dlp
except ImportError:
    yt_dlp = None


APP_TITLE = "YouTube Downloader"
DEFAULT_OUTPUT_DIR = Path.home() / "Downloads"
DEFAULT_SETTINGS = {
    "language": "en",
    "theme": "light",
    "output_dir": str(DEFAULT_OUTPUT_DIR),
    "mode": "video",
    "audio_format": "MP3",
    "geometry": "720x520",
}

LANGUAGE_LABELS = {"en": "English", "ru": "Русский"}
THEME_LABELS = {
    "en": {"light": "Light", "dark": "Dark"},
    "ru": {"light": "Светлая", "dark": "Тёмная"},
}

TEXT = {
    "en": {
        "heading": "Video and audio downloader",
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
        "paste_video": "Paste a video link.",
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
        "save": "Save",
        "close": "Close",
        "per_second": "/s",
        "remaining": "left",
        "progress_details": "{downloaded}  •  {speed}  •  {remaining} {eta}",
        "not_bot": "YouTube asked to confirm that you are not a bot. "
        "Try updating yt-dlp or using browser cookies.\n\n{text}",
        "ffmpeg_processing": "FFmpeg could not process the file.\n\n{text}",
    },
    "ru": {
        "heading": "Загрузка видео и аудио",
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
        "paste_video": "Вставьте ссылку на видео.",
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
        "save": "Сохранить",
        "close": "Закрыть",
        "per_second": "/с",
        "remaining": "осталось",
        "progress_details": "{downloaded}  •  {speed}  •  {remaining} {eta}",
        "not_bot": "YouTube запросил подтверждение, что вы не бот. "
        "Попробуйте обновить yt-dlp или использовать cookies браузера.\n\n{text}",
        "ffmpeg_processing": "Не удалось обработать файл через FFmpeg.\n\n{text}",
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


class DownloaderApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.settings = load_settings()
        language = self.settings.get("language", "en")
        self.language = language if isinstance(language, str) and language in TEXT else "en"
        theme = self.settings.get("theme", "light")
        self.theme = theme if isinstance(theme, str) and theme in THEME_LABELS["en"] else "light"

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
        self.download_button = ttk.Button(
            actions,
            text=self.t("download"),
            command=self.start_download,
            style="Accent.TButton",
        )
        self.download_button.grid(row=0, column=1, sticky="e", padx=(8, 0))
        self.cancel_button = ttk.Button(
            actions,
            text=self.t("cancel"),
            command=self.cancel_download,
            state="disabled",
        )
        self.cancel_button.grid(row=0, column=2, sticky="e", padx=(8, 0))
        self.open_folder_button = ttk.Button(
            actions,
            text=self.t("open_folder"),
            command=self.open_output_dir,
        )
        self.open_folder_button.grid(row=0, column=3, sticky="e", padx=(8, 0))

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

        dialog = tk.Toplevel(self.root)
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

        buttons = ttk.Frame(frame)
        buttons.grid(row=2, column=0, columnspan=2, sticky="e", pady=(12, 0))

        def close_dialog() -> None:
            try:
                dialog.grab_release()
            except tk.TclError:
                pass
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

    def _check_dependency(self) -> bool:
        if yt_dlp is None:
            messagebox.showerror(
                APP_TITLE,
                self.t("dependency_error"),
            )
            return False
        return True

    def _get_url(self) -> str:
        return self.url_var.get().strip()

    def inspect_url(self) -> None:
        if not self._check_dependency():
            return

        url = self._get_url()
        if not url:
            messagebox.showwarning(APP_TITLE, self.t("paste_video"))
            return

        self._set_busy(True, inspecting=True)
        self.status_var.set(self.t("fetching"))
        self.details_var.set("")
        self._log(self.t("checking", url=url))
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

    def start_download(self) -> None:
        if not self._check_dependency():
            return

        url = self._get_url()
        if not url:
            messagebox.showwarning(APP_TITLE, self.t("paste_video"))
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
        if mode == "video":
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

        args = (url, output_dir, mode, selector, ffmpeg)
        self.worker = threading.Thread(target=self._download_worker, args=args, daemon=True)
        self.worker.start()

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

        try:
            with yt_dlp.YoutubeDL(options) as downloader:
                downloader.download([url])
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

        if self.worker and self.worker.is_alive():
            self.status_var.set(self.t("stopping"))
            self.details_var.set(self.t("close_wait"))
            self._set_busy(True)
            self.cancel_button.configure(state="disabled")
            self.root.after(100, self._wait_for_worker)
        else:
            self.root.destroy()

    def _wait_for_worker(self) -> None:
        if self.worker and self.worker.is_alive():
            self.root.after(100, self._wait_for_worker)
            return
        self.root.destroy()

    def _process_events(self) -> None:
        try:
            while True:
                event, payload = self.events.get_nowait()
                if event == "progress":
                    if not self.is_closing:
                        self._update_progress(payload)
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
