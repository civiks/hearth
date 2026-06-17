from pathlib import Path

MEDIA_ROOT = Path(__file__).resolve().parents[1] / "media"
AVATAR_DIR = MEDIA_ROOT / "avatars"


def ensure_media_dirs() -> None:
    AVATAR_DIR.mkdir(parents=True, exist_ok=True)
