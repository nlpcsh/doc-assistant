from tkinter import ttk, messagebox, filedialog
from tkinter import Frame
import tkinter as tk
import threading
import subprocess
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches
from os import path
from tkcalendar import Calendar
from datetime import datetime

class BaseDocTab(ttk.Frame):
    """Parent class containing shared logic for all document tabs."""
    def __init__(self, parent, labels, base_dir, data_mgr, template_dir, template_name):
        super().__init__(parent)
        self.labels = labels
        self.data_mgr = data_mgr
        self.signature_path = base_dir + "/templates/"
        self.template_dir = base_dir + "/templates/" + template_dir + "/"
        self.template_name = template_name

        # Shared UI Elements
        self.container = ttk.Frame(self, padding="20")
        self.container.pack(fill="both", expand=True)

        self.input_fields = []

        self.progress = ttk.Progressbar(self.container, orient="horizontal", length=200, mode="determinate")
        self.status_label = ttk.Label(self.container, text="")

    def add_field(self, label_key):
        ttk.Label(self.container, text=self.labels["fields"][label_key]).pack(anchor="w")
        entry = ttk.Entry(self.container, width=40)
        entry.pack(pady=5)
        self.input_fields.append((label_key, entry))
        return entry

    def add_checkbox_field(self, label_key, checkbox_text, default_value="", show_by_default=False):
        """Add a checkbox that controls the visibility of a field with a predefined value."""
        # Create a frame to hold the checkbox and the field
        field_frame = Frame(self.container)
        
        # Create checkbox variable (default unchecked)
        checkbox_var = tk.BooleanVar(value=show_by_default)
        
        # Create checkbox
        checkbox = ttk.Checkbutton(field_frame, text=checkbox_text, variable=checkbox_var)
        checkbox.pack(side="left", padx=(0, 10))
        
        # Create the field
        entry = ttk.Entry(field_frame, width=20)
        entry.insert(0, default_value)
        
        # Function to toggle field visibility
        def toggle_visibility():
            if checkbox_var.get():
                entry.pack(side="left", padx=(5, 0))
            else:
                entry.pack_forget()
        
        # Bind checkbox to toggle function
        checkbox_var.trace_add("write", lambda *args: toggle_visibility())
        
        # Pack the frame and initially show/hide based on default
        field_frame.pack(fill="x", padx=10, pady=5)
        if show_by_default:
            entry.pack(side="left", padx=(5, 0))
        else:
            entry.pack_forget()
        
        # Add to input fields for context generation
        self.input_fields.append((label_key, entry))
        return entry

    def add_date_field(self, label_key, preselect_today=False, min_date_from=None):
        ttk.Label(self.container, text=self.labels["fields"][label_key]).pack(anchor="w")
        
        # Create a frame to hold the date entry and button
        date_frame = Frame(self.container)
        date_frame.pack(pady=5, padx=5, fill="x")
        
        # Create entry field for the date
        date_entry = ttk.Entry(date_frame, width=30)
        date_entry.pack(side="left", padx=5)
        
        # Preselect today's date if requested
        if preselect_today:
            today = datetime.today()
            date_entry.insert(0, today.strftime('%d/%m/%Y'))
        
        # Create button to open calendar
        def open_calendar():
            # Create toplevel window for calendar
            cal_window = tk.Toplevel(self.winfo_toplevel())
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
                date_entry.delete(0, tk.END)
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
        #self.input_fields.append(combo)
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