import fitz
import os
from typing import Dict, List
from PIL import Image
import io


def extract_text_and_images(pdf_path: str, upload_dir: str) -> Dict[str, object]:
    """Extract text and images from a PDF file."""

    doc = fitz.open(pdf_path)
    text_blocks: List[str] = []
    images: List[str] = []

    MAX_WIDTH = 800
    MAX_IMAGES_PER_PAGE = 4   # performance limit

    for page_num in range(len(doc)):
        page = doc[page_num]

        # Extract text
        page_text = page.get_text()
        if page_text:
            text_blocks.append(page_text)

        # Extract images
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list[:MAX_IMAGES_PER_PAGE], start=1):

            try:
                xref = img[0]
                base_image = doc.extract_image(xref)

                image_bytes = base_image["image"]
                image_ext = base_image.get("ext", "png")

                image_name = f"{os.path.splitext(os.path.basename(pdf_path))[0]}_p{page_num+1}_{img_index}.jpg"
                image_path = os.path.join(upload_dir, image_name)

                # Convert bytes to PIL image
                image = Image.open(io.BytesIO(image_bytes))

                # Convert to RGB to avoid save errors
                if image.mode != "RGB":
                    image = image.convert("RGB")

                # Skip tiny images (icons/logos)
                if image.width < 150 or image.height < 150:
                    continue

                # Resize large images
                if image.width > MAX_WIDTH:
                    ratio = MAX_WIDTH / image.width
                    new_height = int(image.height * ratio)
                    image = image.resize((MAX_WIDTH, new_height), Image.LANCZOS)

                # Save compressed image
                image.save(image_path, "JPEG", optimize=True, quality=70)

                images.append(image_path)

            except Exception:
                # Skip corrupted or unsupported images
                continue

    return {
        "text": "\n".join(text_blocks),
        "images": images
    }