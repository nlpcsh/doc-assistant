from tkinter import ttk
import platform
import threading
import subprocess
import shutil
from os import path, makedirs, unlink
from docxtpl import DocxTemplate

from ui.UIMgr import UIMgr

class BaseDoc(ttk.Frame):
    """Parent class containing shared logic for all document tabs."""
    def __init__(self, parent, data_mgr, template_dir, template_names, output_folder='business_trip'):
        super().__init__(parent)
        self.data_mgr = data_mgr
        self.labels = self.data_mgr.get_labels()
        base_dir = self.data_mgr.base_dir
        self.signature_path = path.join(base_dir, "templates")
        self.template_dir = path.join(base_dir, "templates", template_dir)
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
            pythoncom = None
            try:
                import pythoncom
            except ImportError:
                pass

            if pythoncom is not None:
                pythoncom.CoInitialize()
            try:
                convert(out_docx, pdf_path)
            finally:
                if pythoncom is not None:
                    pythoncom.CoUninitialize()

            return path.exists(pdf_path)
        except Exception as e:
            error_message = str(e)
            self.after(0, lambda error_message=error_message: self.ui_mgr.show_error("Error", error_message))
            return False

    def get_signature(self):
        self.sig_path = self.ui_mgr.ask_open_filename(filetypes=[("Images", "*.png *.jpg *.jpeg")])

    def start_generation(self):
        self.ui_mgr.start_generation(self)
        threading.Thread(target=self.process_doc, daemon=True).start()

    def _build_template_output_path(self, context, template):
        output_dir = self._build_output_path(context)
        if not path.exists(output_dir):
            makedirs(output_dir, exist_ok=True)
        return path.join(output_dir, f"{context['doc_date_and_ids_identifier']}_{template}")

    def _render_template(self, template, context):
        doc = DocxTemplate(path.join(self.template_dir, template))

        try:
            doc.render(context)
        except Exception as render_exc:
            # Surface template rendering errors with template name and traceback
            import traceback
            tb = traceback.format_exc()
            raise RuntimeError(f"Template render error in {template}: {render_exc}\n{tb}") from render_exc

        out_docx = self._build_template_output_path(context, template)
        doc.save(out_docx)
        return out_docx

    def _convert_docx_to_pdf(self, out_docx):
        office_converter = self._find_office_converter()
        if office_converter:
            try:
                subprocess.run([office_converter, '--headless', '--convert-to', 'pdf', out_docx], check=True)
                return True
            except Exception as e:
                error_message = str(e)
                self.after(0, lambda error_message=error_message: self.ui_mgr.show_error("Error", error_message))

        return self._try_docx2pdf(out_docx)

    def _build_output_path(self, context):
        output_folders = self.data_mgr.get_output_folders()
        return path.join(output_folders['common'], output_folders[self.output_folder], context['doc_date_and_ids_identifier'], context['sub_folder'])

    def _get_unique_destination(self, destination):
        if not path.exists(destination):
            return destination

        base, ext = path.splitext(destination)
        index = 1
        while True:
            candidate = f"{base}_{index}{ext}"
            if not path.exists(candidate):
                return candidate
            index += 1

    def _move_pdf_to_output(self, out_docx, context):
        move_path = self._build_output_path(context)
        if not path.exists(move_path):
            makedirs(move_path, exist_ok=True)

        pdf_path = out_docx.replace(".docx", ".pdf")
        destination = path.join(move_path, path.basename(pdf_path))
        new_path = self._get_unique_destination(destination)
        shutil.move(pdf_path, new_path)
        return new_path

    def _move_docx_to_output(self, out_docx, context):
        move_path = self._build_output_path(context)
        if not path.exists(move_path):
            makedirs(move_path, exist_ok=True)

        destination = path.join(move_path, path.basename(out_docx))
        new_path = self._get_unique_destination(destination)
        shutil.move(out_docx, new_path)
        return new_path

    def process_doc(self):
        try:
            context = self.get_context()  # Defined in subclasses
            generated_pdfs = []
            moved_docx = []
            converted_docx = []

            for template in self.template_names:
                out_docx = self._render_template(template, context)
                converted_docx.append(out_docx)
                if self._convert_docx_to_pdf(out_docx):
                    generated_pdfs.append(out_docx.replace(".docx", ".pdf"))
                else:
                    moved_docx.append(out_docx)

            if generated_pdfs:
                self.after(0, lambda: self.ui_mgr.show_signature_preview(self, generated_pdfs))
                for out_docx in converted_docx:
                    pdf_path = out_docx.replace(".docx", ".pdf")
                    if path.exists(out_docx) and path.exists(pdf_path):
                        unlink(out_docx)
                    else:
                        raise FileNotFoundError(f"Path {out_docx} and {pdf_path} does not exists!")

            if moved_docx:
                message = (
                    "Generated DOCX output, but no PDF converter was available. "
                    "Install LibreOffice or docx2pdf to enable PDF conversion."
                    if not generated_pdfs
                    else "Some templates were saved as DOCX because PDF conversion was unavailable. "
                    "Install LibreOffice or docx2pdf for full PDF generation."
                )
                self.after(0, lambda message=message: self.ui_mgr.show_info("Info", message))

            self.final_action()  # Defined in subclasses
        except Exception as e:
            error_message = str(e)
            self.after(0, lambda error_message=error_message: self.ui_mgr.show_error("Error", error_message))
        finally:
            self.after(0, lambda: self.ui_mgr.reset_generation_ui(self))
