from tkinter import ttk, messagebox, filedialog
import threading
import subprocess
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches

class BaseDocTab(ttk.Frame):
    """Parent class containing shared logic for all document tabs."""
    def __init__(self, parent, labels, base_dir, template_name):
        super().__init__(parent)
        self.labels = labels
        self.sig_path = ""
        self.template_dir = base_dir + "/templates/"
        self.template_name = template_name

        # Shared UI Elements
        self.container = ttk.Frame(self, padding="20")
        self.container.pack(fill="both", expand=True)

        self.progress = ttk.Progressbar(self.container, orient="horizontal", length=200, mode="determinate")
        self.status_label = ttk.Label(self.container, text="")

    def add_field(self, label_key):
        ttk.Label(self.container, text=self.labels["fields"][label_key]).pack(anchor="w")
        entry = ttk.Entry(self.container, width=40)
        entry.pack(pady=5)
        return entry

    def add_common_buttons(self, gen_label_key):
        ttk.Button(self.container, text=self.labels["buttons"]["select_sig"], 
                   command=self.get_signature).pack(pady=10)

        self.gen_btn = ttk.Button(self.container, text=self.labels["buttons"][gen_label_key], 
                                  command=self.start_generation)
        self.gen_btn.pack(pady=20)

    def get_signature(self):
        self.sig_path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])

    def start_generation(self):
        self.gen_btn.config(state="disabled")
        self.progress.pack(pady=5)
        self.status_label.pack()
        threading.Thread(target=self.process_doc).start()

    def add_dropdown(self, label_key, options):
        ttk.Label(self.container, text=self.labels["fields"][label_key]).pack(anchor="w")
        # readonly state prevents users from typing custom text if you don't want them to
        combo = ttk.Combobox(self.container, values=options, state="readonly", width=37)
        combo.pack(pady=5)
        if options:
            combo.current(0) # Set default to the first name
        return combo

    def process_doc(self):
        try:
            doc = DocxTemplate(self.template_dir + self.template_name)
            context = self.get_context() # Defined in subclasses

            if self.sig_path:
                context['signature'] = InlineImage(doc, self.sig_path, width=Inches(1.5))

            doc.render(context)
            out_docx = f"Generated_{self.template_name}"
            doc.save(out_docx)

            # PDF Conversion
            subprocess.run(['lowriter', '--headless', '--convert-to', 'pdf', out_docx])

            # Auto-open PDF
            pdf_path = out_docx.replace(".docx", ".pdf")
            subprocess.run(['xdg-open', pdf_path])

            messagebox.showinfo(self.labels["messages"]["success_title"], "Done!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.gen_btn.config(state="normal")
            self.progress.pack_forget()