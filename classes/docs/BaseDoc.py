from tkinter import ttk
import threading
import subprocess
import shutil
from os import path, makedirs, unlink
from docxtpl import DocxTemplate  #, InlineImage

from classes.UIMgr import UIMgr

class BaseDoc(ttk.Frame):
    """Parent class containing shared logic for all document tabs."""
    def __init__(self, parent, data_mgr, template_dir, template_names):
        super().__init__(parent)
        self.data_mgr = data_mgr
        self.labels = self.data_mgr.get_labels()
        base_dir = self.data_mgr.base_dir
        self.signature_path = base_dir + "/templates/"
        self.template_dir = base_dir + "/templates/" + template_dir + "/"
        self.template_group = template_dir
        self.template_names = template_names if isinstance(template_names, list) else [template_names]
        self.ui_mgr = UIMgr(data_mgr)

        self.ui_mgr.initialize_document_container(self)

    def _find_office_converter(self):
        for cmd in ('lowriter', 'soffice', 'libreoffice'):
            path_value = shutil.which(cmd)
            if path_value:
                return path_value
        return None

    def get_signature(self):
        self.sig_path = self.ui_mgr.ask_open_filename(filetypes=[("Images", "*.png *.jpg *.jpeg")])

    def start_generation(self):
        self.ui_mgr.start_generation(self)
        threading.Thread(target=self.process_doc, daemon=True).start()

    def process_doc(self):
        try:
            context = self.get_context()  # Defined in subclasses
            generated_pdfs = []
            generated_docx = []

            for template in self.template_names:
                doc = DocxTemplate(self.template_dir + template)

                doc.render(context)
                out_docx = f"{context['bt_date']}_{context['person_id']}_{template}"
                doc.save(out_docx)
                generated_docx.append(out_docx)

                office_converter = self._find_office_converter()
                if not office_converter:
                    raise FileNotFoundError(
                        "LibreOffice converter not found. Install LibreOffice and ensure 'lowriter', 'soffice', or 'libreoffice' is available in PATH."
                    )
                subprocess.run([office_converter, '--headless', '--convert-to', 'pdf', out_docx], check=True)

                # Move files to output folder
                output_folders = self.data_mgr.get_output_folders()
                move_path = f"{output_folders['common']}{output_folders['business_trip']}{context['bt_date']}"
                if not path.exists(move_path):
                    makedirs(move_path, exist_ok=True)
                # Only move PDF file
                pdf_path = out_docx.replace(".docx", ".pdf")
                new_path = path.join(move_path, path.basename(pdf_path))
                shutil.move(pdf_path, new_path)
                generated_pdfs.append(new_path)

            if generated_pdfs:
                self.after(0, lambda: self.ui_mgr.show_signature_preview(self, generated_pdfs))
                # Delete the temporary DOCX file
                for out_docx in generated_docx:
                    if path.exists(out_docx):
                        unlink(out_docx)

                # Auto-open PDF
                #subprocess.run(['xdg-open', new_path])

            #self.ui_mgr.show_info(self.labels["messages"]["success_title"], "Done!")
            self.final_action() # Defined in subclasses
        except Exception as e:
            error_message = str(e)
            self.after(0, lambda error_message=error_message: self.ui_mgr.show_error("Error", error_message))
        finally:
            self.after(0, lambda: self.ui_mgr.reset_generation_ui(self))
