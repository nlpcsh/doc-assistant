from dataclasses import dataclass

from PIL import Image, ImageTk
import fitz


@dataclass
class SignatureRect:
    x0: float
    y0: float
    x1: float
    y1: float


def build_signature_rect(page_width, page_height, click_x, click_y, signature_width, signature_height):
    """Create a PDF rectangle for a signature using the clicked point as the center."""
    x0 = click_x - (signature_width / 2)
    y0 = page_height - (click_y + (signature_height / 2))
    x1 = x0 + signature_width
    y1 = y0 + signature_height
    return SignatureRect(x0=x0, y0=y0, x1=x1, y1=y1)


def render_pdf_page_to_photoimage(pdf_path, max_width=900, max_height=1100):
    doc = fitz.open(pdf_path)
    page = doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    scale = min(max_width / pix.width, max_height / pix.height, 1.0)
    if scale < 1.0:
        image = image.resize((int(pix.width * scale), int(pix.height * scale)))
        pix_width = int(pix.width * scale)
        pix_height = int(pix.height * scale)
    else:
        pix_width = pix.width
        pix_height = pix.height
    photo = ImageTk.PhotoImage(image=image)
    doc.close()
    return photo, pix_width, pix_height, scale if scale < 1.0 else 1.0


def add_visible_signature_to_pdf(pdf_path, output_path, signature_image_path, signature_rect):
    doc = fitz.open(pdf_path)
    page = doc[0]
    rect = fitz.Rect(signature_rect.x0, signature_rect.y0, signature_rect.x1, signature_rect.y1)
    page.insert_image(rect, filename=signature_image_path)
    doc.save(output_path)
    doc.close()
