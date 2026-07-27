import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import threading
import subprocess
import shutil
from os import path, makedirs, unlink
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches

from classes.digisign.CertificateManager import CertificateManager
from classes.digisign.signing_utils import add_visible_signature_to_pdf
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
        self.sig_path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])

    def start_generation(self):
        self.ui_mgr.start_generation(self)
        threading.Thread(target=self.process_doc, daemon=True).start()

    def process_doc(self):
        try:
            context = self.get_context()  # Defined in subclasses
            generated_pdfs = []

            for template in self.template_names:
                doc = DocxTemplate(self.template_dir + template)

                if self.sig_path:
                    context['signature'] = InlineImage(doc, self.sig_path, width=Inches(1.5))

                doc.render(context)
                out_docx = f"{context['bt_date']}_{context['person_id']}_{template}"
                doc.save(out_docx)

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
                shutil.move(pdf_path, path.join(move_path, path.basename(pdf_path)))
                generated_pdfs.append(path.join(move_path, path.basename(pdf_path)))

            if generated_pdfs:
                self.after(0, lambda: self.ui_mgr.show_signature_preview(self, generated_pdfs[-1]))
                # Delete the temporary DOCX file
                if path.exists(out_docx):
                    unlink(out_docx)

                # Auto-open PDF
                subprocess.run(['xdg-open', pdf_path])

            messagebox.showinfo(self.labels["messages"]["success_title"], "Done!")
        except Exception as e:
            error_message = str(e)
            self.after(0, lambda error_message=error_message: messagebox.showerror("Error", error_message))
        finally:
            self.after(0, lambda: self.ui_mgr.reset_generation_ui(self))

    def sign_current_document(self):
        if not self.preview_pdf_path:
            return
        if not self.selected_signature_rect:
            messagebox.showwarning("Signature placement", "Please click inside the preview to place the visible signature first.")
            return

        signature_image_path = self.sig_path
        if not signature_image_path:
            signature_image_path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
            if not signature_image_path:
                return
            self.sig_path = signature_image_path

        cert_path, password, signer_name = self.select_certificate_for_signing()
        if not cert_path:
            return

        if not path.exists(signature_image_path):
            messagebox.showerror("Signature image", "The selected signature image could not be found.")
            return

        temp_pdf_path = self.preview_pdf_path.replace(".pdf", "_with_signature.pdf")
        signed_pdf_path = self.preview_pdf_path.replace(".pdf", "_signed.pdf")

        try:
            add_visible_signature_to_pdf(self.preview_pdf_path, temp_pdf_path, signature_image_path, self.selected_signature_rect)
            success = CertificateManager.sign_pdf_with_certificate(
                temp_pdf_path,
                cert_path,
                signed_pdf_path,
                password=password,
                signer_name=signer_name,
            )
            if success:
                if self.preview_window and self.preview_window.winfo_exists():
                    self.preview_window.destroy()
                messagebox.showinfo("Signed PDF", f"The signed PDF was created successfully:\n{signed_pdf_path}")
                subprocess.run(['xdg-open', signed_pdf_path], check=False)
            else:
                messagebox.showerror("Signed PDF", "The chosen certificate could not sign the document.")
        except Exception as exc:
            messagebox.showerror("Signed PDF", str(exc))

    def select_certificate_for_signing(self):
        cert_path = filedialog.askopenfilename(
            title="Select certificate for signing",
            filetypes=[
                ("PKCS#12 files", "*.pfx;*.p12"),
                ("Certificate files", "*.pem;*.crt;*.cer"),
                ("All files", "*.*"),
            ],
        )
        if not cert_path:
            return None, None, None

        password = None
        if cert_path.lower().endswith(('.pfx', '.p12')):
            password = simpledialog.askstring(
                "Certificate Password",
                "Enter the password for the certificate file (leave blank if none):",
                show="*",
            )

        cert_info = CertificateManager.load_certificate_file(cert_path, password=password)
        if not cert_info:
            messagebox.showerror("Certificate", "The selected certificate could not be loaded.")
            return None, None, None

        return cert_path, password, cert_info.friendly_name or path.basename(cert_path)
