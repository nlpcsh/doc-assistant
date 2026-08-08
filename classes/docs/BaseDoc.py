from tkinter import ttk
import platform
import threading
import subprocess
import shutil
from os import path, makedirs, unlink
from docxtpl import DocxTemplate  #, InlineImage

from ui.UIMgr import UIMgr

class BaseDoc(ttk.Frame):
    """Parent class containing shared logic for all document tabs."""
    def __init__(self, parent, data_mgr, template_dir, template_names, output_folder='business_trip'):
        super().__init__(parent)
        self.data_mgr = data_mgr
        self.labels = self.data_mgr.get_labels()
        base_dir = self.data_mgr.base_dir
        self.signature_path = base_dir + "/templates/"
        self.template_dir = base_dir + "/templates/" + template_dir + "/"
        self.template_group = template_dir
        self.template_names = template_names if isinstance(template_names, list) else [template_names]
        self.output_folder = output_folder

        self.ui_mgr = UIMgr(data_mgr)

        self.ui_mgr.initialize_document_container(self)

    def _find_office_converter(self):
        for cmd in ('lowriter', 'soffice', 'libreoffice'):
            path_value = shutil.which(cmd)
            if path_value:
                return path_value
        return None

    def _try_docx2pdf(self, out_docx):
        try:
            from docx2pdf import convert
        except ImportError:
            return False

        if platform.system() not in ('Windows', 'Darwin'):
            return False

        pdf_path = out_docx.replace('.docx', '.pdf')
        try:
            convert(out_docx, pdf_path)
            return path.exists(pdf_path)
        except Exception:
            return False

    def get_signature(self):
        self.sig_path = self.ui_mgr.ask_open_filename(filetypes=[("Images", "*.png *.jpg *.jpeg")])

    def start_generation(self):
        self.ui_mgr.start_generation(self)
        threading.Thread(target=self.process_doc, daemon=True).start()

    def _render_template(self, template, context):
        doc = DocxTemplate(self.template_dir + template)

        try:
            doc.render(context)
        except Exception as render_exc:
            # Surface template rendering errors with template name and traceback
            import traceback
            tb = traceback.format_exc()
            raise RuntimeError(f"Template render error in {template}: {render_exc}\n{tb}") from render_exc

        out_docx = f"{context['doc_date_and_ids_identifier']}_{template}"
        doc.save(out_docx)
        return out_docx

    def _convert_docx_to_pdf(self, out_docx):
        office_converter = self._find_office_converter()
        if office_converter:
            subprocess.run([office_converter, '--headless', '--convert-to', 'pdf', out_docx], check=True)
            return

        if self._try_docx2pdf(out_docx):
            print(f"Converted {out_docx} to PDF using docx2pdf.")
            return

        raise RuntimeError("No suitable method found to convert DOCX to PDF. Please install LibreOffice or docx2pdf.")

    def _build_output_path(self, context):
        output_folders = self.data_mgr.get_output_folders()
        return f"{output_folders['common']}{output_folders[self.output_folder]}{context['doc_date_and_ids_identifier']}{context['sub_folder']}"

    def _move_pdf_to_output(self, out_docx, context):
        move_path = self._build_output_path(context)
        if not path.exists(move_path):
            makedirs(move_path, exist_ok=True)

        pdf_path = out_docx.replace(".docx", ".pdf")
        new_path = path.join(move_path, path.basename(pdf_path))
        shutil.move(pdf_path, new_path)
        return new_path

    def process_doc(self):
        try:
            context = self.get_context()  # Defined in subclasses
            generated_pdfs = []
            generated_docx = []

            for template in self.template_names:
                out_docx = self._render_template(template, context)
                generated_docx.append(out_docx)
                self._convert_docx_to_pdf(out_docx)
                generated_pdfs.append(self._move_pdf_to_output(out_docx, context))

            if generated_pdfs:
                self.after(0, lambda: self.ui_mgr.show_signature_preview(self, generated_pdfs))
                for out_docx in generated_docx:
                    if path.exists(out_docx):
                        unlink(out_docx)

            self.final_action()  # Defined in subclasses
        except Exception as e:
            error_message = str(e)
            self.after(0, lambda error_message=error_message: self.ui_mgr.show_error("Error", error_message))
        finally:
            self.after(0, lambda: self.ui_mgr.reset_generation_ui(self))
