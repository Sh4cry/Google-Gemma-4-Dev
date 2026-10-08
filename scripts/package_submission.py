"""
Package submission archive for The Gemma 4 Developer Agent Competition.

Creates a clean `submission.zip` containing:
- agent.yaml (at root)
- prompts/
- configs/
- sub_agents/ (if present)
- adapters/ (if present)
Excludes scripts, tests, caches, and git directories.
"""

import hashlib
import os
import sys
import zipfile
from pathlib import Path

# Directories and files to include in the submission zip
INCLUDED_FILES = ["agent.yaml"]
INCLUDED_DIRS = ["prompts", "configs", "sub_agents", "adapters", "skills"]
OUTPUT_ZIP = "submission.zip"


def calculate_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def main():
    base_dir = Path(__file__).resolve().parent.parent
    output_path = base_dir / OUTPUT_ZIP

    print(f"[*] Packaging submission from: {base_dir}")
    print(f"[*] Target archive: {output_path}")

    # Ensure agent.yaml exists
    if not (base_dir / "agent.yaml").exists():
        print("[X] Error: agent.yaml not found at root directory!")
        sys.exit(1)

    file_count = 0
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add root files
        for fname in INCLUDED_FILES:
            fpath = base_dir / fname
            if fpath.exists():
                print(f"  + Adding root file: {fname}")
                zf.write(fpath, arcname=fname)
                file_count += 1

        # Add subdirectories
        for dname in INCLUDED_DIRS:
            dpath = base_dir / dname
            if dpath.exists() and dpath.is_dir():
                for root, _, files in os.walk(dpath):
                    for file in files:
                        if file.endswith((".pyc", ".DS_Store")) or file.startswith("."):
                            continue
                        full_path = Path(root) / file
                        arcname = full_path.relative_to(base_dir).as_posix()
                        print(f"  + Adding {arcname}")
                        zf.write(full_path, arcname=arcname)
                        file_count += 1

    zip_size_mb = output_path.stat().st_size / (1024 * 1024)
    sha = calculate_sha256(output_path)

    print("\n[OK] Package created successfully!")
    print(f"  - Total files packaged: {file_count}")
    print(f"  - Archive size: {zip_size_mb:.2f} MB")
    print(f"  - SHA256: {sha}")
    print(f"  - Output file: {output_path.resolve()}")


if __name__ == "__main__":
    main()
