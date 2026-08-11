<div align="center">
  <img src="icon.png" width="128" alt="YouTube Downloader icon">
  <h1>YouTube Downloader</h1>
  <p>A small, focused Windows desktop downloader powered by <a href="https://github.com/yt-dlp/yt-dlp">yt-dlp</a>.</p>
  <p>
    <img src="https://img.shields.io/badge/platform-Windows-0078D4?style=flat-square" alt="Windows">
    <img src="https://img.shields.io/badge/python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11+">
    <img src="https://img.shields.io/badge/powered%20by-yt--dlp-111111?style=flat-square" alt="Powered by yt-dlp">
  </p>
</div>

## English

### Overview

YouTube Downloader provides a clean native Windows interface for downloading one YouTube
video at a time. It works with both regular YouTube videos and YouTube Shorts.

Choose a video resolution or extract audio in the format and quality you need, without
having to remember command-line options.

### Download a ready-to-run release

Open the [Latest release](https://github.com/youngvitaly/yt-downloader/releases/latest)
and download `YouTubeDownloader-windows-x64.zip`.

The portable archive contains both `YouTubeDownloader.exe` and `ffmpeg.exe`. Python,
Tkinter, and `yt-dlp` are already bundled into the executable, so end users do not need
to install Python.

### Features

- Regular YouTube videos and YouTube Shorts.
- Video mode with available resolutions from 360p up to 4K when provided by the source.
- Audio mode with quality selection and MP3, M4A, or Opus output.
- Optional format inspection before downloading.
- Download progress, speed, ETA, cancellation, and retry handling.
- Light and dark themes.
- English and Russian interface; English is the default.
- Paste by button, `Ctrl+V`, or `Shift+Insert`, including Russian keyboard layouts.
- Settings persisted in `settings.json`.
- Graceful shutdown: closing the window stops the worker before the process exits.
- Custom application icon embedded in the executable and loaded by the window.

The application processes one video per link. It does not download entire playlists.

### Quick start with the executable

1. Download or build `YouTubeDownloader.exe`.
2. Put a Windows `ffmpeg.exe` next to it.
3. Double-click `YouTubeDownloader.exe`.
4. Paste a YouTube video or Shorts link, select the mode and quality, then click **Download**.

Releases are built automatically by GitHub Actions when a version tag such as `v1.0.0` is
published.

The current build expects this layout:

```text
dist/
├── YouTubeDownloader.exe
└── ffmpeg.exe
```

### Get FFmpeg

For Windows x64, use a non-shared GPL build such as
[`ffmpeg-n8.1-latest-win64-gpl-8.1.zip`](https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-n8.1-latest-win64-gpl-8.1.zip).

Extract `bin\ffmpeg.exe` and place it next to the executable. The non-shared build does not
need additional FFmpeg DLLs for this application.

### Run from source

Requirements:

- Windows;
- Python 3.11 or newer;
- `ffmpeg.exe` next to `app.py`.

Run:

```bat
run.bat
```

The script creates `.venv` and installs the current `yt-dlp` package automatically.

### Build the executable

```bat
build.bat
```

The result is written to `dist\YouTubeDownloader.exe`. The build embeds the application icon
and bundles the icon resource used by the window at runtime.

### Settings and project layout

Settings are saved next to the running application:

- source run: `settings.json` next to `app.py`;
- packaged run: `dist\settings.json` next to the executable.

The file stores language, theme, output folder, audio format, selected mode, and window
geometry. It is local user configuration and is excluded from Git.

### Project structure

```text
app.py          Windows GUI and yt-dlp integration
requirements.txt Runtime dependency
run.bat         Easy source launch
build.bat       PyInstaller build
icon.png        Clean source icon
icon.ico        Multi-size Windows icon
```

### Legal note

Use this tool only for content you are allowed to download. Respect YouTube's Terms of
Service, copyright, and the rights of content creators.

---

## Русская версия

### О приложении

YouTube Downloader — небольшое нативное приложение для Windows на базе
[`yt-dlp`](https://github.com/yt-dlp/yt-dlp).

Оно работает и с обычными видео YouTube, и с YouTube Shorts. Можно выбрать разрешение
видео или скачать только аудио в нужном формате и качестве.

### Скачать готовый релиз

Откройте страницу [Latest release](https://github.com/youngvitaly/yt-downloader/releases/latest)
и скачайте `YouTubeDownloader-windows-x64.zip`.

В portable-архив уже входят `YouTubeDownloader.exe` и `ffmpeg.exe`. Python, Tkinter и
`yt-dlp` встроены в исполняемый файл, поэтому пользователю не нужно устанавливать Python.

### Возможности

- обычные видео YouTube и Shorts;
- видео от 360p до 4K, если такое качество доступно у источника;
- аудио в MP3, M4A или Opus;
- предварительный просмотр доступных качеств;
- прогресс, скорость, оставшееся время и отмена загрузки;
- автоматические повторы при временных сетевых ошибках;
- светлая и тёмная тема;
- английский и русский интерфейс, по умолчанию английский;
- вставка кнопкой, `Ctrl+V` или `Shift+Insert`, в том числе при русской раскладке;
- сохранение настроек в `settings.json`;
- корректная остановка загрузки при закрытии окна;
- пользовательская иконка встроена в `.exe` и используется самим окном.

Приложение обрабатывает одну ссылку как один ролик и не скачивает плейлисты целиком.

### Быстрый запуск `.exe`

1. Скачайте или соберите `YouTubeDownloader.exe`.
2. Положите рядом с ним файл `ffmpeg.exe`.
3. Запустите `.exe` двойным кликом.
4. Вставьте ссылку на обычное видео или Shorts, выберите режим и качество, нажмите
   **Download**.

Релизы собираются автоматически через GitHub Actions после публикации тега версии,
например `v1.0.0`.

Структура папки:

```text
dist/
├── YouTubeDownloader.exe
└── ffmpeg.exe
```

### Где взять FFmpeg

Для обычной 64-битной Windows скачайте
[`ffmpeg-n8.1-latest-win64-gpl-8.1.zip`](https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-n8.1-latest-win64-gpl-8.1.zip).

Распакуйте архив, возьмите `bin\ffmpeg.exe` и положите его рядом с `.exe`. Выбранная
несвязанная (`non-shared`) сборка не требует дополнительных DLL FFmpeg.

### Запуск из исходников

Нужны Windows, Python 3.11+ и `ffmpeg.exe` рядом с `app.py`.

Запустите:

```bat
run.bat
```

Скрипт автоматически создаст `.venv` и установит актуальный `yt-dlp`.

### Сборка `.exe`

```bat
build.bat
```

Готовый файл появится в `dist\YouTubeDownloader.exe`. Иконка встраивается в `.exe`, а
ресурс иконки также упаковывается внутрь приложения для отображения в окне.

### Настройки

Настройки сохраняются рядом с запущенным приложением:

- при запуске из исходников: `settings.json` рядом с `app.py`;
- при запуске `.exe`: `dist\settings.json` рядом с исполняемым файлом.

Сохраняются язык, тема, папка загрузки, формат аудио, режим и размер/позиция окна.
Файл является локальной конфигурацией пользователя и исключён из Git.

### Структура проекта

```text
app.py          Windows-интерфейс и интеграция с yt-dlp
requirements.txt Зависимость приложения
run.bat         Простой запуск из исходников
build.bat       Сборка через PyInstaller
icon.png        Обработанная иконка
icon.ico        Иконка Windows в нескольких размерах
```

### Важно

Используйте приложение только для материалов, которые вам разрешено скачивать.
Соблюдайте правила YouTube, авторские права и права создателей контента.
