#!/usr/bin/env python3
"""
Export CITS3200 meeting minutes from Google Drive to Teams as PDFs.

Flow:
- Prompt for Week number (2-11)
- Find .md files in gdrive:CITS3200/Week<week>
- Download to temp dir
- Convert each to PDF using pandoc
- Upload PDFs to teams:General/Group_31/Week<week>
"""

from __future__ import annotations

import os
import sys
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import logging
from rich.logging import RichHandler


# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)
logger = logging.getLogger("minutes_export")


# ---------- Configuration ----------
@dataclass
class ExportConfig:
    gdrive_remote: str = "gdrive"
    gdrive_base: str = "CITS3200"
    teams_remote: str = "teams"
    teams_base: str = "General/Group_31"
    pandoc_path: str = "pandoc"  # Expect pandoc on PATH


def run_cmd(cmd: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def ensure_tool_exists(tool: str, hint: str) -> bool:
    result = run_cmd(["bash", "-lc", f"command -v {tool} >/dev/null 2>&1; echo $?" ])
    if result.returncode != 0 or result.stdout.strip() not in {"0", ""}:
        logger.error(f"❌ Required tool not found: {tool}. {hint}")
        return False
    return True


def prompt_week() -> Optional[int]:
    while True:
        try:
            val = input("Enter week number (2-11): ").strip()
        except EOFError:
            return None
        if not val:
            return None
        try:
            week = int(val)
            if 2 <= week <= 11:
                return week
            logger.error("❌ Week number must be between 2 and 11")
        except ValueError:
            logger.error("❌ Please enter a valid integer")


def list_md_files_on_gdrive(cfg: ExportConfig, week: int) -> List[str]:
    remote_path = f"{cfg.gdrive_remote}:{cfg.gdrive_base}/Week{week}"
    ls = run_cmd(["rclone", "lsf", remote_path, "--files-only", "--include", "*.md"])
    if ls.returncode != 0:
        logger.error(f"❌ Failed to list markdown files on {remote_path}: {ls.stderr}")
        return []
    files = [line.strip() for line in ls.stdout.splitlines() if line.strip()]
    return files


def download_files(cfg: ExportConfig, week: int, filenames: List[str], dest_dir: Path) -> List[Path]:
    remote_path = f"{cfg.gdrive_remote}:{cfg.gdrive_base}/Week{week}"
    downloaded: List[Path] = []
    for name in filenames:
        src = f"{remote_path}/{name}"
        dst = dest_dir / name
        cp = run_cmd(["rclone", "copyto", src, str(dst)])
        if cp.returncode != 0:
            logger.error(f"❌ Failed to download {src}: {cp.stderr}")
            continue
        logger.info(f"📥 Downloaded: {name}")
        downloaded.append(dst)
    return downloaded


def _have(cmd: str) -> bool:
    chk = run_cmd(["bash", "-lc", f"command -v {cmd} >/dev/null 2>&1; echo $?" ])
    return chk.returncode == 0 and chk.stdout.strip() == "0"


def _sanitize_markdown(src: Path) -> Path:
    """Make a sanitized copy to avoid common LaTeX unicode issues (μ, en-dash, curly quotes)."""
    text = src.read_text(encoding="utf-8", errors="ignore")
    replacements = {
        "μ": "$\\mu$",  # Greek mu
        "µ": "$\\mu$",  # Micro sign
        "–": "-",         # en dash
        "—": "-",         # em dash
        "“": '"',
        "”": '"',
        "’": "'",
        "·": "-",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    out = src.with_suffix(".sanitized.md")
    out.write_text(text, encoding="utf-8")
    return out


def convert_md_to_pdf(pandoc: str, md_file: Path, out_pdf: Path) -> bool:
    # Prefer HTML-to-PDF if available, else a Unicode-capable LaTeX engine
    if _have("wkhtmltopdf"):
        cmd = [pandoc, str(md_file), "-o", str(out_pdf), "--from", "gfm", "--pdf-engine=wkhtmltopdf"]
        engine_label = "wkhtmltopdf"
    elif _have("xelatex"):
        cmd = [pandoc, str(md_file), "-o", str(out_pdf), "--from", "gfm", "--pdf-engine=xelatex"]
        engine_label = "xelatex"
    elif _have("lualatex"):
        cmd = [pandoc, str(md_file), "-o", str(out_pdf), "--from", "gfm", "--pdf-engine=lualatex"]
        engine_label = "lualatex"
    else:
        # Last resort: try default engine with sanitized markdown
        san = _sanitize_markdown(md_file)
        cmd = [pandoc, str(san), "-o", str(out_pdf), "--from", "gfm"]
        engine_label = "default-with-sanitization"

    proc = run_cmd(cmd)
    if proc.returncode != 0:
        # One more attempt with sanitization if we haven't tried already
        if "sanitized" not in " ".join(cmd):
            san = _sanitize_markdown(md_file)
            retry = cmd.copy()
            retry[1] = str(san)
            proc2 = run_cmd(retry)
            if proc2.returncode == 0:
                logger.info(f"📝 Converted to PDF: {out_pdf.name} (engine={engine_label}, sanitized)")
                return True
        logger.error(f"❌ Pandoc failed for {md_file.name} (engine={engine_label}): {proc.stderr}")
        return False

    logger.info(f"📝 Converted to PDF: {out_pdf.name} (engine={engine_label})")
    return True


def upload_pdfs_to_teams(cfg: ExportConfig, week: int, pdf_files: List[Path]) -> bool:
    remote_week = f"{cfg.teams_remote}:{cfg.teams_base}/Week {week}"
    # Ensure remote folder exists
    mk = run_cmd(["rclone", "mkdir", remote_week])
    if mk.returncode != 0:
        logger.error(f"❌ Failed to create Teams folder {remote_week}: {mk.stderr}")
        return False
    ok = True
    for pdf in pdf_files:
        up = run_cmd(["rclone", "copy", str(pdf), remote_week])
        if up.returncode != 0:
            logger.error(f"❌ Upload failed for {pdf.name}: {up.stderr}")
            ok = False
        else:
            logger.info(f"📤 Uploaded: {pdf.name}")
    return ok


def main() -> int:
    cfg = ExportConfig()

    # Tool checks
    if not ensure_tool_exists("rclone", "Install from https://rclone.org/downloads/ and configure remotes 'gdrive' and 'teams'."):
        return 1
    if not ensure_tool_exists(cfg.pandoc_path, "Install pandoc, e.g. 'brew install pandoc'."):
        return 1

    # Prompt for week
    week = prompt_week()
    if week is None:
        logger.error("❌ No week provided. Exiting.")
        return 1
    logger.info(f"✅ Week {week} selected")

    # List markdown files on Google Drive
    files = list_md_files_on_gdrive(cfg, week)
    if not files:
        logger.warning(f"⚠️  No .md files found in {cfg.gdrive_remote}:{cfg.gdrive_base}/Week{week}")
        return 0

    with tempfile.TemporaryDirectory(prefix=f"minutes_week{week}_") as tmpdir:
        tmp_path = Path(tmpdir)
        logger.info(f"📂 Working directory: {tmp_path}")

        # Download
        md_paths = download_files(cfg, week, files, tmp_path)
        if not md_paths:
            logger.error("❌ Failed to download markdown files.")
            return 1

        # Convert
        pdf_paths: List[Path] = []
        for md in md_paths:
            pdf = md.with_suffix(".pdf")
            if convert_md_to_pdf(cfg.pandoc_path, md, pdf):
                pdf_paths.append(pdf)

        if not pdf_paths:
            logger.error("❌ No PDFs were created.")
            return 1

        # Upload
        if not upload_pdfs_to_teams(cfg, week, pdf_paths):
            return 1

    logger.info("✅ Minutes export completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())


