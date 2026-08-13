<div align="center">
  <img src="icon.png" width="128" alt="YouTube and Instagram Downloader icon">
  <h1>YouTube &amp; Instagram Downloader</h1>
  <p>A small, focused Windows desktop downloader powered by <a href="https://github.com/yt-dlp/yt-dlp">yt-dlp</a>, with an <a href="https://instaloader.github.io/">Instaloader</a> fallback for public Instagram media.</p>
  <p>
    <img src="https://img.shields.io/badge/platform-Windows-0078D4?style=flat-square" alt="Windows">
    <img src="https://img.shields.io/badge/python-3.11.9-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11.9">
    <img src="https://img.shields.io/badge/powered%20by-yt--dlp-111111?style=flat-square" alt="Powered by yt-dlp">
    <img src="https://img.shields.io/badge/Instagram-public%20media-E4405F?style=flat-square&logo=instagram&logoColor=white" alt="Instagram public media">
  </p>
</div>

## English

### Overview

YouTube & Instagram Downloader provides a clean native Windows interface for downloading
media from regular YouTube videos, YouTube Shorts, and public Instagram links.

Choose a video resolution or extract audio in the format and quality you need, without
having to remember command-line options.

For Instagram, the application tries `yt-dlp` first. If that extractor cannot handle the
link, Instaloader is used as a fallback for public posts, Reels, carousels, and profiles.
Private content and login-protected stories are intentionally outside the current scope.

### Download a ready-to-run release

Open the [Latest release](https://github.com/youngvitaly/yt-downloader/releases/latest)
and download `YouTubeDownloader-windows-x64.zip`.

The portable archive contains `YouTubeDownloader.exe`, its support folder, and `ffmpeg.exe`.
Python, Tkinter, `yt-dlp`, and Instaloader are bundled in the portable folder, so end users
do not need to install Python. Keep the complete folder contents together.

### Features

- Regular YouTube videos and YouTube Shorts.
- Public Instagram posts, Reels, carousels, and profiles.
- Automatic Instagram fallback: `yt-dlp` first, Instaloader second.
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
- SHA-256 checksums published with every release.

The application processes one link at a time. A public Instagram profile may contain
multiple posts, so the Instaloader fallback downloads the profile's public media.

### Quick start with the executable

1. Download and extract `YouTubeDownloader-windows-x64.zip`.
2. Keep `YouTubeDownloader.exe`, `_internal`, and `ffmpeg.exe` in the same folder.
3. Double-click `YouTubeDownloader.exe`.
4. Paste a YouTube, Shorts, or public Instagram link, select the mode and quality, then
   click **Download**.

Releases are built automatically by GitHub Actions when a version tag such as `v1.0.0` is
published.

The portable release expects this layout:

```text
release/
├── YouTubeDownloader.exe
├── _internal/
└── ffmpeg.exe
```

`SHA256SUMS.txt` is published beside the ZIP. Use it to verify the downloaded archive
before extracting it.

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

The script creates `.venv` and installs the current `yt-dlp` and Instaloader packages
automatically.

### Build the executable

```bat
build.bat
```

The result is written to `dist\YouTubeDownloader\YouTubeDownloader.exe`. This is an
`onedir` build: keep the entire `YouTubeDownloader` folder together. The build embeds the
application icon and bundles the icon resource used by the window at runtime.

### Settings and project layout

Settings are saved next to the running application:

- source run: `settings.json` next to `app.py`;
- packaged run: `dist\YouTubeDownloader\settings.json` next to the executable.

The file stores language, theme, output folder, audio format, selected mode, and window
geometry. It is local user configuration and is excluded from Git.

### Project structure

```text
app.py          Windows GUI, yt-dlp integration, and Instagram fallback
requirements.txt Runtime dependency
build-requirements.txt Pinned build dependency
run.bat         Easy source launch
build.bat       PyInstaller build
icon.png        Clean source icon
icon.ico        Multi-size Windows icon
```

### Legal note

Use this tool only for content you are allowed to download. Respect YouTube's and
Instagram's Terms of Service, copyright, and the rights of content creators.

The release workflow can add an Authenticode signature when the repository secrets
`WINDOWS_CERTIFICATE_BASE64` and `WINDOWS_CERTIFICATE_PASSWORD` are configured. Without
those secrets, the executable remains unsigned.

---

## Русская версия

### О приложении

YouTube & Instagram Downloader — небольшое нативное приложение для Windows на базе
[`yt-dlp`](https://github.com/yt-dlp/yt-dlp) с запасным вариантом через
[Instaloader](https://instaloader.github.io/) для публичного Instagram-контента.

Оно работает и с обычными видео YouTube, и с YouTube Shorts. Можно выбрать разрешение
видео, скачать только аудио в нужном формате и качестве, а также скачать публичные
посты, Reels, карусели и профили Instagram.

Для Instagram сначала используется `yt-dlp`. Если он не справляется со ссылкой,
приложение автоматически пробует Instaloader. Приватный контент и stories, требующие
авторизации, пока намеренно не входят в область поддержки.

### Скачать готовый релиз

Откройте страницу [Latest release](https://github.com/youngvitaly/yt-downloader/releases/latest)
и скачайте `YouTubeDownloader-windows-x64.zip`.

В portable-архив входят `YouTubeDownloader.exe`, папка поддержки и `ffmpeg.exe`. Python,
Tkinter, `yt-dlp` и Instaloader уже находятся внутри portable-папки, поэтому пользователю
не нужно устанавливать Python. Не отделяйте `.exe` и папку `_internal`.

### Возможности

- обычные видео YouTube и Shorts;
- публичные посты, Reels, карусели и профили Instagram;
- автоматический fallback для Instagram: сначала `yt-dlp`, затем Instaloader;
- видео от 360p до 4K, если такое качество доступно у источника;
- аудио в MP3, M4A или Opus;
- предварительный просмотр доступных качеств;
- прогресс, скорость, оставшееся время и отмена загрузки;
- автоматические повторы при временных сетевых ошибках;
- SHA-256 контрольные суммы публикуются вместе с каждым релизом;
- светлая и тёмная тема;
- английский и русский интерфейс, по умолчанию английский;
- вставка кнопкой, `Ctrl+V` или `Shift+Insert`, в том числе при русской раскладке;
- сохранение настроек в `settings.json`;
- корректная остановка загрузки при закрытии окна;
- пользовательская иконка встроена в `.exe` и используется самим окном.

Приложение обрабатывает одну ссылку за раз. Публичная ссылка на профиль Instagram может
содержать несколько публикаций — в этом случае fallback Instaloader скачает публичное
медиа профиля.

### Быстрый запуск `.exe`

1. Скачайте и распакуйте `YouTubeDownloader-windows-x64.zip`.
2. Оставьте `YouTubeDownloader.exe`, `_internal` и `ffmpeg.exe` в одной папке.
3. Запустите `YouTubeDownloader.exe` двойным кликом.
4. Вставьте ссылку на YouTube, Shorts или публичный Instagram, выберите режим и
   качество, нажмите **Download**.

Релизы собираются автоматически через GitHub Actions после публикации тега версии,
например `v1.0.0`.

Структура portable-папки:

```text
release/
├── YouTubeDownloader.exe
├── _internal/
└── ffmpeg.exe
```

Файл `SHA256SUMS.txt` публикуется рядом с ZIP-архивом. С его помощью можно проверить
скачанный архив до распаковки.

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

Скрипт автоматически создаст `.venv` и установит актуальные `yt-dlp` и Instaloader.

### Сборка `.exe`

```bat
build.bat
```

Готовый файл появится в `dist\YouTubeDownloader\YouTubeDownloader.exe`. Это сборка
`onedir`: всю папку `YouTubeDownloader` нужно сохранять целиком. Иконка встраивается
в `.exe`, а ресурс иконки также упаковывается внутрь приложения.

### Настройки

Настройки сохраняются рядом с запущенным приложением:

- при запуске из исходников: `settings.json` рядом с `app.py`;
- при запуске `.exe`: `dist\YouTubeDownloader\settings.json` рядом с исполняемым файлом.

Сохраняются язык, тема, папка загрузки, формат аудио, режим и размер/позиция окна.
Файл является локальной конфигурацией пользователя и исключён из Git.

### Структура проекта

```text
app.py          Windows-интерфейс, yt-dlp и fallback Instagram
requirements.txt Зависимость приложения
build-requirements.txt Фиксированные зависимости сборки
run.bat         Простой запуск из исходников
build.bat       Сборка через PyInstaller
icon.png        Обработанная иконка
icon.ico        Иконка Windows в нескольких размерах
```

### Важно

Используйте приложение только для материалов, которые вам разрешено скачивать.
Соблюдайте правила YouTube и Instagram, авторские права и права создателей контента.

Workflow релиза умеет добавлять Authenticode-подпись, если в настройках репозитория
заданы секреты `WINDOWS_CERTIFICATE_BASE64` и `WINDOWS_CERTIFICATE_PASSWORD`. Без этих
секретов `.exe` остаётся неподписанным.
