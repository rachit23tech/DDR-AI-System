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

    MAX_WIDTH = 800  # resize images larger than this

    for page_num in range(len(doc)):
        page = doc[page_num]

        # Extract text
        page_text = page.get_text()
        if page_text:
            text_blocks.append(page_text)

        # Extract images
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list, start=1):

            xref = img[0]
            base_image = doc.extract_image(xref)

            image_bytes = base_image["image"]
            image_ext = base_image.get("ext", "png")

            image_name = f"{os.path.splitext(os.path.basename(pdf_path))[0]}_p{page_num+1}_{img_index}.{image_ext}"
            image_path = os.path.join(upload_dir, image_name)

            # Convert bytes to PIL image
            image = Image.open(io.BytesIO(image_bytes))

            # Skip tiny images (logos/icons)
            if image.width < 100 or image.height < 100:
                continue

            # Resize if too large
            if image.width > MAX_WIDTH:
                ratio = MAX_WIDTH / image.width
                new_height = int(image.height * ratio)
                image = image.resize((MAX_WIDTH, new_height), Image.LANCZOS)

            # Save compressed image
            image.save(image_path, optimize=True, quality=75)

            images.append(image_path)

    return {
        "text": "\n".join(text_blocks),
        "images": images
    }