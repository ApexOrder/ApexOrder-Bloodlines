from __future__ import annotations

import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD_DIR = ROOT / "ApexOrder_Bloodlines"
VERSION_FILE = MOD_DIR / "version.txt"
MANIFEST_FILE = ROOT / "manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_xml() -> None:
    xml_files = sorted(MOD_DIR.rglob("*.xml"))
    if not xml_files:
        raise RuntimeError("No XML files found in the mod directory.")

    for xml_file in xml_files:
        try:
            ET.parse(xml_file)
        except ET.ParseError as exc:
            raise RuntimeError(f"Malformed XML: {xml_file.relative_to(ROOT)}: {exc}") from exc


def main() -> int:
    if not MOD_DIR.is_dir():
        print(f"Missing mod directory: {MOD_DIR}", file=sys.stderr)
        return 1

    if not VERSION_FILE.is_file():
        print(f"Missing version file: {VERSION_FILE}", file=sys.stderr)
        return 1

    try:
        validate_xml()
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 1

    version = VERSION_FILE.read_text(encoding="utf-8").strip()
    files: dict[str, str] = {}

    for path in sorted(MOD_DIR.rglob("*")):
        if path.is_file():
            relative = path.relative_to(MOD_DIR).as_posix()
            files[relative] = sha256(path)

    manifest = {
        "mod": "ApexOrder Bloodlines",
        "folder": "ApexOrder_Bloodlines",
        "version": version,
        "files": files,
    }

    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Validated {len(files)} files and wrote {MANIFEST_FILE.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
