import tkinter as tk
from tkinter import END, ttk, messagebox, filedialog, Frame, Text, BooleanVar, Listbox, MULTIPLE, Toplevel, simpledialog
import threading
import subprocess
import shutil
from os import path, makedirs, unlink
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches

from tkcalendar import Calendar
from datetime import datetime

from classes.CertificateManager import CertificateManager
from classes.signing_utils import add_visible_signature_to_pdf, build_signature_rect, render_pdf_page_to_photoimage

from pdfrw import PdfReader, PdfWriter, PageMerge
from reportlab.pdfgen import canvas

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

        # Shared UI Elements
        self.container = ttk.Frame(self, padding="20")
        self.container.pack(fill="both", expand=True)

        self.input_fields = []

        self.progress = ttk.Progressbar(self.container, orient="horizontal", length=200, mode="determinate")
        self.status_label = ttk.Label(self.container, text="")
        self.preview_window = None
        self.preview_canvas = None
        self.preview_photo = None
        self.preview_pdf_path = None
        self.preview_page_width = None
        self.preview_page_height = None
        self.preview_scale = 1.0
        self.preview_rect = None
        self.selected_signature_rect = None

    def add_field(self, label_key, show_by_default=True, initial_value="", width=30):
        # Create a frame to hold the label and entry
        field_frame = Frame(self.container)
        
        # Create label and entry
        label = ttk.Label(field_frame, text=self.labels["fields"][label_key])
        label.pack(side="left", padx=(0, 10))
        entry = ttk.Entry(field_frame, width=width)
        # Configure entry for Unicode/Cyrillic support
        entry.configure(font=('Arial', 10))  # Ensure font supports Cyrillic
        entry.pack(side="left")
        
        # Set initial value if provided
        if initial_value:
            entry.insert(0, initial_value)
        
        # Pack the frame initially based on show_by_default
        if show_by_default:
            field_frame.pack(fill="x", padx=10, pady=5)
        else:
            field_frame.pack_forget()
        
        # Add to input fields with frame for visibility control
        self.input_fields.append((label_key, field_frame, entry))
        return entry

    def add_text_field(self, label_key, height=4, width=40):
        # Create a frame to hold the label and text widget
        field_frame = Frame(self.container)

        label = ttk.Label(field_frame, text=self.labels["fields"][label_key])
        label.pack(anchor="w")

        text_widget = Text(field_frame, height=height, width=width, wrap="word")
        text_widget.configure(font=("Arial", 10))
        text_widget.pack(fill="x")

        field_frame.pack(fill="x", padx=10, pady=5)

        self.input_fields.append((label_key, field_frame, text_widget))
        return text_widget

    def add_checkbox_field(self, label_key, checkbox_text, default_value="", show_by_default=False, width=20):
        """Add a checkbox that controls the visibility of a field with a predefined value."""
        # Create a frame to hold the checkbox and the field
        field_frame = Frame(self.container)
        
        # Create checkbox variable (default unchecked)
        checkbox_var = BooleanVar(value=show_by_default)
        
        # Create checkbox
        checkbox = ttk.Checkbutton(field_frame, text=checkbox_text, variable=checkbox_var)
        checkbox.pack(side="left", padx=(0, 10))
        
        # Create the field
        entry = ttk.Entry(field_frame, width=width)
        # Configure entry for Unicode/Cyrillic support
        entry.configure(font=('Arial', 10))  # Ensure font supports Cyrillic
        
        # Function to toggle field visibility
        def toggle_visibility():
            if checkbox_var.get():
                entry.pack(side="left", padx=(5, 0))
                entry.delete(0, END)
                entry.insert(0, default_value)
            else:
                entry.pack_forget()
                entry.insert(0, "")  # Clear the field when hiding
        
        # Bind checkbox to toggle function
        checkbox_var.trace_add("write", lambda *args: toggle_visibility())
        
        # Pack the frame and initially show/hide based on default
        field_frame.pack(fill="x", padx=10, pady=5)
        if show_by_default:
            entry.pack(side="left", padx=(5, 0))
        else:
            entry.pack_forget()
        
        # Add to input fields with frame for visibility control
        self.input_fields.append((label_key, field_frame, entry))
        return entry

    def add_checkbox_multi(self, checkbox_text, options):
        """Add a checkbox that controls the visibility of a multiselect listbox."""
        # Create checkbox variable
        var = BooleanVar()
        
        # Create checkbox
        checkbox = ttk.Checkbutton(self.container, text=checkbox_text, variable=var)
        checkbox.pack(anchor="w", padx=10, pady=5)
        
        # Create listbox with height based on number of options (max 10)
        height = min(len(options), 10)
        listbox = Listbox(self.container, selectmode=MULTIPLE, height=height, exportselection=0)
        for option in options:
            listbox.insert(END, option)
        listbox.pack_forget()
        
        # Function to toggle listbox visibility
        def toggle():
            if var.get():
                listbox.pack(after=checkbox, padx=10, pady=5)
            else:
                listbox.pack_forget()
        
        # Bind checkbox to toggle function
        var.trace_add("write", lambda *args: toggle())
        
        return var, listbox

    def add_date_field(self, label_key, preselect_today=False, min_date_from=None, width=30):
        ttk.Label(self.container, text=self.labels["fields"][label_key]).pack(anchor="w")
        
        # Create a frame to hold the date entry and button
        date_frame = Frame(self.container)
        date_frame.pack(pady=5, padx=5, fill="x")
        
        # Create entry field for the date
        date_entry = ttk.Entry(date_frame, width=width)
        date_entry.pack(side="left", padx=5)
        
        # Preselect today's date if requested
        if preselect_today:
            today = datetime.today()
            date_entry.insert(0, today.strftime('%d/%m/%Y'))
        
        # Create button to open calendar
        def open_calendar():
            # Create toplevel window for calendar
            cal_window = Toplevel(self.winfo_toplevel())
            cal_window.title(self.labels["fields"][label_key])
            
            # Set minimum date if linked to another date field
            mindate = None
            if min_date_from:
                try:
                    min_date_str = min_date_from.get()
                    if min_date_str:
                        mindate = datetime.strptime(min_date_str, '%d/%m/%Y').date()
                except (ValueError, AttributeError):
                    pass
            
            def select_date():
                selected_date = calendar.get_date()
                date_entry.delete(0, END)
                date_entry.insert(0, selected_date)
                cal_window.destroy()
            
            # Create calendar widget
            today = datetime.today()
            calendar = Calendar(cal_window, selectmode='day', year=today.year, month=today.month, day=today.day,
                              background='darkblue', foreground='white', date_pattern='dd/mm/yyyy', mindate=mindate)
            calendar.pack(pady=10, padx=10)
            
            # Create button to confirm selection
            ttk.Button(cal_window, text="Select", command=select_date).pack(pady=5)
            
            # Make window modal and on top
            cal_window.transient(self.winfo_toplevel())
            cal_window.grab_set()
        
        # Add button to open calendar
        ttk.Button(date_frame, text="📅", command=open_calendar, width=3).pack(side="left", padx=2)
        
        #self.input_fields.append(date_entry)
        return date_entry

    def add_common_buttons(self, gen_label_key):
        if path.exists(self.signature_path + "sig.png"):
            self.sig_path = self.signature_path + "sig.png"
        else:
            ttk.Button(self.container, text=self.labels["buttons"]["select_sig"], 
                command=self.get_signature).pack(pady=10)

        self.gen_btn = ttk.Button(self.container, text=self.labels["buttons"][gen_label_key], 
                                  command=self.start_generation)
        self.gen_btn.pack(pady=20)

    def _find_office_converter(self):
        for cmd in ('lowriter', 'soffice', 'libreoffice'):
            path = shutil.which(cmd)
            if path:
                return path
        return None

    def get_signature(self):
        self.sig_path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])

    def get_signature_settings(self, template_name):
        return self.data_mgr.get_signature_settings(self.template_group, template_name)

    def get_signature_coordinates(self, template_name):
        """Return the PDF coordinates where the signature should be placed.

        Coordinates are in PDF points from the bottom-left corner.
        If template-specific settings exist in data.json, use them.
        """
        settings = self.get_signature_settings(template_name)
        if settings is None or 'coords' not in settings:
            messagebox.showerror("Error", f"Невалидни координати на подписа за {template_name}!")
            return (0, 0)
        return settings.get('coords')

    def get_signature_size(self, template_name):
        """Return the width and height for the signature in PDF points."""
        settings = self.get_signature_settings(template_name)
        if settings is None or 'size' not in settings:
            messagebox.showerror("Error", f"Невалиден размер на подписа за {template_name}!")
            return (0, 0)
        return settings.get('size')

    def stamp_signature_pdf(self, pdf_path, template_name):
        if not getattr(self, 'sig_path', None) or not path.exists(self.sig_path):
            return

        # Read the generated PDF to determine page size
        pdf = PdfReader(pdf_path)
        if not pdf.pages:
            return

        page = pdf.pages[0]
        media_box = page.MediaBox
        page_width = float(media_box[2]) - float(media_box[0])
        page_height = float(media_box[3]) - float(media_box[1])

        # Create a temporary overlay PDF with the signature image at the desired position
        overlay_path = f"{pdf_path}.sig-overlay.pdf"
        x, y = self.get_signature_coordinates(template_name)
        sig_width, sig_height = self.get_signature_size(template_name)

        c = canvas.Canvas(overlay_path, pagesize=(page_width, page_height))
        c.drawImage(self.sig_path, x, y, width=sig_width, height=sig_height, mask='auto')
        c.save()

        overlay = PdfReader(overlay_path)
        overlay_page = overlay.pages[0]

        # Stamp the overlay onto the first page of the generated PDF
        PageMerge(page).add(overlay_page).render()
        PdfWriter(pdf_path, trailer=pdf).write()

        if path.exists(overlay_path):
            unlink(overlay_path)

    def start_generation(self):
        self.gen_btn.config(state="disabled")
        self.progress.pack(pady=5)
        self.status_label.pack()
        threading.Thread(target=self.process_doc, daemon=True).start()

    def add_dropdown(self, label_key, options):
        ttk.Label(self.container, text=self.labels["fields"][label_key]).pack(anchor="w")
        # readonly state prevents users from typing custom text if you don't want them to
        combo = ttk.Combobox(self.container, values=options, state="readonly", width=37)
        combo.pack(pady=5)
        if options:
            combo.current(0) # Set default to the first name
        #self.input_fields.append(combo)
        return combo

    def process_doc(self):
        try:
            context = self.get_context()  # Defined in subclasses
            generated_pdfs = []

            for template in self.template_names:
                doc = DocxTemplate(self.template_dir + template)

                if self.sig_path:
                    context['signature'] = InlineImage(doc, self.sig_path, width=Inches(1.5))

                doc.render(context)
                out_docx = f"{context['wt_date']}_{context['person_id']}_{template}"
                doc.save(out_docx)

                office_converter = self._find_office_converter()
                if not office_converter:
                    raise FileNotFoundError(
                        "LibreOffice converter not found. Install LibreOffice and ensure 'lowriter', 'soffice', or 'libreoffice' is available in PATH."
                    )
                subprocess.run([office_converter, '--headless', '--convert-to', 'pdf', out_docx], check=True)

                # Stamp signature onto the generated PDF if available
                pdf_path = out_docx.replace(".docx", ".pdf")
                self.stamp_signature_pdf(pdf_path, template)

                # Move files to output folder
                output_folders = self.data_mgr.get_output_folders()
                move_path = f"{output_folders['common']}{output_folders['work_travels']}{context['wt_date']}"
                if not path.exists(move_path):
                    makedirs(move_path, exist_ok=True)
                # Only move PDF file
                pdf_path = out_docx.replace(".docx", ".pdf")
                shutil.move(pdf_path, path.join(move_path, path.basename(pdf_path)))
                generated_pdfs.append(path.join(move_path, path.basename(pdf_path)))

            if generated_pdfs:
                self.after(0, lambda: self.show_signature_preview(generated_pdfs[-1]))
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
            self.after(0, self.reset_generation_ui)

    def reset_generation_ui(self):
        self.gen_btn.config(state="normal")
        self.progress.pack_forget()
        self.status_label.config(text="")

    def show_signature_preview(self, pdf_path):
        self.preview_pdf_path = pdf_path
        self.selected_signature_rect = None

        if self.preview_window and self.preview_window.winfo_exists():
            self.preview_window.destroy()

        self.preview_window = tk.Toplevel(self.winfo_toplevel())
        self.preview_window.title("Place signature")
        self.preview_window.geometry("1000x900")

        toolbar = ttk.Frame(self.preview_window)
        toolbar.pack(fill="x", padx=8, pady=6)
        ttk.Label(toolbar, text="Click inside the document to place the visible signature. Then sign the PDF.").pack(side="left")
        ttk.Button(toolbar, text="Sign PDF", command=self.sign_current_document).pack(side="right")

        self.preview_canvas = tk.Canvas(self.preview_window, bg="white")
        self.preview_canvas.pack(fill="both", expand=True, padx=8, pady=8)
        self.preview_canvas.bind("<Button-1>", self.on_signature_click)

        self.load_preview_pdf(pdf_path)

    def load_preview_pdf(self, pdf_path):
        self.preview_photo, self.preview_page_width, self.preview_page_height, self.preview_scale = render_pdf_page_to_photoimage(
            pdf_path,
            max_width=900,
            max_height=1100,
        )
        self.preview_canvas.config(width=self.preview_photo.width(), height=self.preview_photo.height())
        self.preview_canvas.delete("all")
        self.preview_canvas.create_image(0, 0, anchor="nw", image=self.preview_photo)

    def on_signature_click(self, event):
        if not self.preview_page_width or not self.preview_page_height:
            return

        pdf_click_x = event.x / self.preview_scale
        pdf_click_y = event.y / self.preview_scale
        width = 140
        height = 60
        self.selected_signature_rect = build_signature_rect(
            page_width=self.preview_page_width,
            page_height=self.preview_page_height,
            click_x=pdf_click_x,
            click_y=pdf_click_y,
            signature_width=width,
            signature_height=height,
        )

        self.preview_canvas.delete("preview_marker")
        self.preview_canvas.create_rectangle(
            event.x - 30,
            event.y - 20,
            event.x + 30,
            event.y + 20,
            outline="red",
            width=2,
            tags="preview_marker",
        )
        self.preview_canvas.create_text(event.x, event.y, text="Signature", fill="red", tags="preview_marker")

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
