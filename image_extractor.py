# for now, extraction is handled in pdf_parser. This module can hold helper functions

from typing import List


def save_image_from_bytes(image_bytes: bytes, dest_path: str) -> str:
    with open(dest_path, "wb") as f:
        f.write(image_bytes)
    return dest_path


# placeholder in case we want advanced processing
