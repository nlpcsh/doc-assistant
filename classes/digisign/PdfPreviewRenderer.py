from PIL import Image
from typing import Tuple


class PdfPreviewRenderer:
    def __init__(self, canvas, width: int, height: int):
        self.canvas = canvas
        self.canvas_width = width
        self.canvas_height = height

    def render_page_preview(self, fitz_doc, page_index: int):
        if not fitz_doc:
            return None
        try:
            page = fitz_doc.load_page(page_index)
            pix = page.get_pixmap(alpha=False)
            return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        except Exception:
            return None

    def pdf_to_canvas_coords(self, x: float, y: float, page_size: Tuple[float, float]) -> Tuple[float, float]:
        page_w, page_h = page_size
        scale = min(self.canvas_width / page_w, self.canvas_height / page_h)
        disp_w = int(page_w * scale)
        disp_h = int(page_h * scale)
        x_offset = (self.canvas_width - disp_w) / 2
        y_offset = (self.canvas_height - disp_h) / 2

        canvas_x = x * scale + x_offset
        canvas_y = self.canvas_height - (y * scale) - y_offset
        return canvas_x, canvas_y

    def canvas_to_pdf_coords(self, x: float, y: float, page_size: Tuple[float, float]) -> Tuple[float, float]:
        page_w, page_h = page_size
        scale = min(self.canvas_width / page_w, self.canvas_height / page_h)
        disp_w = int(page_w * scale)
        disp_h = int(page_h * scale)
        x_offset = (self.canvas_width - disp_w) / 2
        y_offset = (self.canvas_height - disp_h) / 2

        pdf_x = (x - x_offset) / scale
        pdf_y = (self.canvas_height - y - y_offset) / scale
        return pdf_x, pdf_y
