from __future__ import annotations

import argparse
import ctypes
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import urlparse
import urllib.request
import zipfile


APP_TITLE = "YouTube & Instagram Downloader"
PACKAGE_NAME = "YouTubeDownloader-windows-x64.zip"
USER_FILES = {"settings.json", "instagram.session"}
DOWNLOAD_TIMEOUT = 30
PROCESS_WAIT_TIMEOUT = 120


def trusted_download_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc.lower() not in {
        "github.com",
        "www.github.com",
    }:
        raise RuntimeError("The update URL is not a trusted GitHub URL")
    return url


def show_message(text: str, *, error: bool = False) -> None:
    try:
        ctypes.windll.user32.MessageBoxW(
            None,
            text,
            APP_TITLE,
            0x10 if error else 0x40,
        )
    except Exception:
        pass


def request_download(url: str, destination: Path) -> None:
    request = urllib.request.Request(
        trusted_download_url(url),
        headers={
            "Accept": "application/octet-stream",
            "User-Agent": "YouTubeDownloaderUpdater",
        },
    )
    with urllib.request.urlopen(request, timeout=DOWNLOAD_TIMEOUT) as response:
        with destination.open("wb") as output:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def checksum_from_manifest(manifest: Path) -> str:
    for line in manifest.read_text(encoding="utf-8").splitlines():
        fields = line.strip().split()
        if len(fields) < 2:
            continue
        filename = fields[-1].lstrip("*")
        if Path(filename).name == PACKAGE_NAME:
            checksum = fields[0].lower()
            if len(checksum) == 64 and all(
                character in "0123456789abcdef" for character in checksum
            ):
                return checksum
    raise RuntimeError(f"{PACKAGE_NAME} is missing from SHA256SUMS.txt")


def safe_extract(archive: Path, destination: Path) -> None:
    root = destination.resolve()
    with zipfile.ZipFile(archive) as package:
        for member in package.infolist():
            target = (destination / member.filename).resolve()
            try:
                common = os.path.commonpath((str(root), str(target)))
            except ValueError as error:
                raise RuntimeError("Update archive contains an invalid path") from error
            if common != str(root):
                raise RuntimeError("Update archive contains a path traversal entry")
        package.extractall(destination)


def package_root(extracted: Path) -> Path:
    if (extracted / "YouTubeDownloader.exe").is_file():
        return extracted
    directories = [
        child
        for child in extracted.iterdir()
        if child.is_dir() and (child / "YouTubeDownloader.exe").is_file()
    ]
    if len(directories) == 1:
        return directories[0]
    raise RuntimeError("Update archive does not contain YouTubeDownloader.exe")


def wait_for_process(pid: int) -> bool:
    if pid <= 0:
        return True

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    process = kernel32.OpenProcess(0x00100000, False, pid)
    if not process:
        return True
    try:
        result = kernel32.WaitForSingleObject(
            process,
            PROCESS_WAIT_TIMEOUT * 1000,
        )
        return result == 0
    finally:
        kernel32.CloseHandle(process)


def replace_release_files(source: Path, application: Path) -> None:
    if not application.is_dir():
        raise RuntimeError("The application folder no longer exists")

    for item in source.iterdir():
        if item.name in USER_FILES:
            continue
        target = application / item.name
        temporary_target = application / f".{item.name}.update-{os.getpid()}"

        if temporary_target.exists():
            if temporary_target.is_dir():
                shutil.rmtree(temporary_target)
            else:
                temporary_target.unlink()

        if item.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(item, target)
            continue

        shutil.copy2(item, temporary_target)
        if target.is_dir():
            shutil.rmtree(target)
        os.replace(temporary_target, target)


def relaunch(application_exe: Path, application_dir: Path) -> None:
    creationflags = (
        getattr(subprocess, "DETACHED_PROCESS", 0)
        | getattr(subprocess, "CREATE_NO_WINDOW", 0)
    )
    subprocess.Popen(
        [str(application_exe)],
        cwd=str(application_dir),
        creationflags=creationflags,
        close_fds=True,
    )


def apply_update(arguments: argparse.Namespace) -> int:
    application_dir = Path(arguments.app_dir).resolve()
    application_exe = Path(arguments.app_exe).resolve()
    if application_exe.parent != application_dir:
        raise RuntimeError("The application executable is outside its application folder")

    work_dir = Path(tempfile.mkdtemp(prefix="yt-downloader-update-"))
    archive = work_dir / PACKAGE_NAME
    manifest = work_dir / "SHA256SUMS.txt"
    extracted = work_dir / "extracted"
    try:
        request_download(arguments.download_url, archive)
        request_download(arguments.checksum_url, manifest)

        actual_checksum = sha256_file(archive)
        manifest_checksum = checksum_from_manifest(manifest)
        if actual_checksum != manifest_checksum:
            raise RuntimeError("The downloaded update failed the SHA-256 check")
        if arguments.expected_sha256 and (
            actual_checksum != arguments.expected_sha256.lower()
        ):
            raise RuntimeError("The downloaded update does not match GitHub metadata")

        extracted.mkdir()
        safe_extract(archive, extracted)
        source = package_root(extracted)
        if not (source / "_internal").is_dir():
            raise RuntimeError("Update archive does not contain the _internal folder")

        if not wait_for_process(arguments.pid):
            raise RuntimeError("Timed out while waiting for the application to close")

        replace_release_files(source, application_dir)
        if not application_exe.is_file():
            raise RuntimeError("The updated application executable was not installed")
        relaunch(application_exe, application_dir)
        return 0
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


def handoff(arguments: argparse.Namespace) -> int:
    if not getattr(sys, "frozen", False):
        show_message(
            "The automatic updater is available in the packaged Windows application.",
            error=True,
        )
        return 1

    source = Path(sys.executable).resolve()
    temporary_dir = Path(tempfile.mkdtemp(prefix="yt-downloader-updater-"))
    temporary_updater = temporary_dir / source.name
    try:
        shutil.copy2(source, temporary_updater)
        command = [
            str(temporary_updater),
            "--apply",
            "--app-dir",
            arguments.app_dir,
            "--app-exe",
            arguments.app_exe,
            "--pid",
            str(arguments.pid),
            "--download-url",
            arguments.download_url,
            "--checksum-url",
            arguments.checksum_url,
            "--expected-version",
            arguments.expected_version,
        ]
        if arguments.expected_sha256:
            command.extend(["--expected-sha256", arguments.expected_sha256])

        creationflags = (
            getattr(subprocess, "DETACHED_PROCESS", 0)
            | getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
        subprocess.Popen(
            command,
            cwd=str(temporary_dir),
            creationflags=creationflags,
            close_fds=True,
        )
        return 0
    except OSError:
        shutil.rmtree(temporary_dir, ignore_errors=True)
        raise


def argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="YouTube Downloader updater")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--app-dir", required=True)
    parser.add_argument("--app-exe", required=True)
    parser.add_argument("--pid", type=int, required=True)
    parser.add_argument("--download-url", required=True)
    parser.add_argument("--checksum-url", required=True)
    parser.add_argument("--expected-version", required=True)
    parser.add_argument("--expected-sha256", default="")
    return parser


def main() -> int:
    arguments = argument_parser().parse_args()
    try:
        if arguments.apply:
            return apply_update(arguments)
        return handoff(arguments)
    except Exception as error:
        show_message(f"Automatic update failed:\n\n{error}", error=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
