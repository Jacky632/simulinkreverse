"""File discovery and loading for generated C code folders."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class SourceFile:
    path: Path
    relative_path: str
    text: str


class CCodeLoader:
    """Load relevant generated C and header files from a folder tree."""

    SOURCE_SUFFIXES = {".c", ".h"}
    IGNORED_DIRS = {
        ".git",
        "__pycache__",
        "slprj",
        "html",
        "tmwinternal",
        "build",
        "derived",
    }
    IGNORED_SUFFIXES = {
        ".o",
        ".obj",
        ".a",
        ".lib",
        ".dll",
        ".so",
        ".dylib",
        ".exe",
        ".mat",
        ".mk",
        ".tmw",
        ".dmr",
        ".xml",
        ".html",
        ".js",
        ".css",
        ".png",
        ".gif",
        ".svg",
        ".woff",
        ".cur",
        ".ds_store",
        ".tmp",
        ".bak",
    }

    def __init__(self, root: Path) -> None:
        self.root = root

    def load(self) -> list[SourceFile]:
        if not self.root.exists():
            raise FileNotFoundError(f"input folder does not exist: {self.root}")
        if not self.root.is_dir():
            raise NotADirectoryError(f"input path is not a folder: {self.root}")

        files: list[SourceFile] = []
        for path in sorted(self.root.rglob("*")):
            if not path.is_file():
                continue
            if self._is_ignored(path):
                LOGGER.debug("Ignoring non-source file: %s", path)
                continue
            if path.suffix.lower() not in self.SOURCE_SUFFIXES:
                LOGGER.debug("Ignoring file with unsupported suffix: %s", path)
                continue
            try:
                raw = path.read_bytes()
            except OSError as exc:
                LOGGER.warning("Could not read %s: %s", path, exc)
                continue
            if self._looks_binary(raw):
                LOGGER.warning("Ignoring binary-looking source candidate: %s", path)
                continue
            text = raw.decode("utf-8", errors="replace")
            relative = path.relative_to(self.root).as_posix()
            files.append(SourceFile(path=path, relative_path=relative, text=text))
            LOGGER.info("Loaded %s", relative)

        if not files:
            raise FileNotFoundError(f"no .c or .h files found under {self.root}")
        return files

    def _is_ignored(self, path: Path) -> bool:
        relative_parts = path.relative_to(self.root).parts
        if any(part in self.IGNORED_DIRS for part in relative_parts[:-1]):
            return True
        suffix = path.suffix.lower()
        name = path.name.lower()
        return suffix in self.IGNORED_SUFFIXES or name.endswith("~")

    @staticmethod
    def _looks_binary(raw: bytes) -> bool:
        if b"\x00" in raw[:4096]:
            return True
        return False
