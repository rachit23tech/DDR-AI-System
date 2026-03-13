import fitz
import os
from typing import Dict, List

def extract_text_and_images(pdf_path: str, upload_dir: str) -> Dict[str, object]:
    """Extract text and images from a PDF file.

    Returns a dictionary with keys:
        text: concatenated text observations
        images: list of image file paths saved under upload_dir
    """
    doc = fitz.open(pdf_path)
    text_blocks: List[str] = []
    images: List[str] = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        # extract text
        page_text = page.get_text()
        if page_text:
            text_blocks.append(page_text)

        # extract images
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list, start=1):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image.get("ext", "png")
            image_name = f"{os.path.splitext(os.path.basename(pdf_path))[0]}_p{page_num+1}_{img_index}.{image_ext}"
            image_path = os.path.join(upload_dir, image_name)
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)
            images.append(image_path)
    return {"text": "\n".join(text_blocks), "images": images}
