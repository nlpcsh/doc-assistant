import os

from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from classes.digisign.CertificateManager import CertificateManager
from classes.digisign.DataClasses import SignaturePlacement
from typing import Optional

from reportlab.lib.units import inch

class SignatureOverlay:
    @staticmethod
    def create(
        placement: SignaturePlacement,
        signer_name: str,
        signature_type: str,
        output_path: str,
        page_width: float,
        page_height: float,
        signature_image_path: Optional[str] = None,
        visual_only: bool = False,
    ) -> None:
        c = canvas.Canvas(output_path, pagesize=(page_width, page_height))

        if visual_only:
            SignatureOverlay._draw_centered_image(c, placement, signature_image_path)
            c.save()
            return

        SignatureOverlay._draw_border(c, placement)

        text_lines = SignatureOverlay._build_text_lines(signer_name, signature_type)
        text_start_y, line_height = SignatureOverlay._calculate_text_layout(placement, text_lines)

        text_x = placement.x + 0.1 * inch
        text_x = SignatureOverlay._draw_image_and_adjust_text_x(
            c, placement, signature_image_path, text_x
        )

        SignatureOverlay._draw_text_lines(c, text_lines, text_x, text_start_y, line_height)
        c.save()

    @staticmethod
    def _draw_border(c, placement: SignaturePlacement) -> None:
        c.setStrokeColorRGB(0.867, 0.894, 1.0)
        c.setFillColorRGB(0, 0, 0)
        c.setLineWidth(1)
        c.rect(placement.x, placement.y, placement.width, placement.height)

    @staticmethod
    def _build_text_lines(signer_name: str, signature_type: str):
        size = 6
        return [
            ("Digitally signed by:", "Helvetica", size),
            (signer_name, "Helvetica-Bold", size),
            (f"Reason: {signature_type}", "Helvetica", size),
            (f"Date: {CertificateManager.get_current_time_iso()}", "Helvetica", size),
        ]

    @staticmethod
    def _calculate_text_layout(placement: SignaturePlacement, text_lines):
        line_spacing = 2
        total_height = sum(size + line_spacing for _, _, size in text_lines) - line_spacing
        line_height = text_lines[0][2] + line_spacing

        box_center_y = placement.y + placement.height / 2
        start_y = box_center_y + total_height / 2 - line_height / 2 - line_spacing / 2

        return start_y, line_height

    @staticmethod
    def _draw_centered_image(c, placement: SignaturePlacement, path: Optional[str]) -> None:
        if not path or not os.path.isfile(path):
            return

        try:
            reader = ImageReader(path)
            img_w, img_h = reader.getSize()
            if img_w <= 0 or img_h <= 0:
                return

            scale = min(placement.width / img_w, placement.height / img_h, 1.0)
            w, h = img_w * scale, img_h * scale

            x = placement.x + (placement.width - w) / 2
            y = placement.y + (placement.height - h) / 2

            c.drawImage(reader, x, y, width=w, height=h, mask="auto")
        except Exception:
            pass

    @staticmethod
    def _draw_image_and_adjust_text_x(c, placement: SignaturePlacement, path: Optional[str], default_text_x: float) -> float:
        if not path or not os.path.isfile(path):
            return default_text_x

        try:
            reader = ImageReader(path)
            img_w, img_h = reader.getSize()
            if img_w <= 0 or img_h <= 0:
                return default_text_x

            margin = 0.08 * inch
            area_w = placement.width * 0.35
            area_h = placement.height - (margin * 2)

            scale = min(area_w / img_w, area_h / img_h, 1.0)
            w, h = img_w * scale, img_h * scale

            x = placement.x + margin
            y = placement.y + placement.height - h - margin

            c.drawImage(reader, x, y, width=w, height=h, mask="auto")
            return x + w + 0.1 * inch

        except Exception:
            return default_text_x

    @staticmethod
    def _draw_text_lines(c, text_lines, x: float, start_y: float, line_height: float):
        y = start_y
        for text, font, size in text_lines:
            c.setFont(font, size)
            c.drawString(x, y, text)
            y -= line_height