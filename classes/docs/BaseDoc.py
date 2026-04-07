from tkinter import END, ttk, messagebox, filedialog, Frame
import tkinter as tk
import threading
import subprocess
import shutil
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches
from os import path, makedirs
from tkcalendar import Calendar
from datetime import datetime

class BaseDoc(ttk.Frame):
    """Parent class containing shared logic for all document tabs."""
    def __init__(self, parent, labels, base_dir, data_mgr, template_dir, template_names):
        super().__init__(parent)
        self.labels = labels
        self.data_mgr = data_mgr
        self.signature_path = base_dir + "/templates/"
        self.template_dir = base_dir + "/templates/" + template_dir + "/"
        self.template_names = template_names if isinstance(template_names, list) else [template_names]

        # Shared UI Elements
        self.container = ttk.Frame(self, padding="20")
        self.container.pack(fill="both", expand=True)

        self.input_fields = []

        self.progress = ttk.Progressbar(self.container, orient="horizontal", length=200, mode="determinate")
        self.status_label = ttk.Label(self.container, text="")

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

        text_widget = tk.Text(field_frame, height=height, width=width, wrap="word")
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
        checkbox_var = tk.BooleanVar(value=show_by_default)
        
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
        var = tk.BooleanVar()
        
        # Create checkbox
        checkbox = ttk.Checkbutton(self.container, text=checkbox_text, variable=var)
        checkbox.pack(anchor="w", padx=10, pady=5)
        
        # Create listbox with height based on number of options (max 10)
        height = min(len(options), 10)
        listbox = tk.Listbox(self.container, selectmode=tk.MULTIPLE, height=height, exportselection=0)
        for option in options:
            listbox.insert(tk.END, option)
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
            context = self.get_context() # Defined in subclasses

            for template in self.template_names:
                doc = DocxTemplate(self.template_dir + template)

                if self.sig_path:
                    context['signature'] = InlineImage(doc, self.sig_path, width=Inches(1.5))

                doc.render(context)
                out_docx = f"{context['wt_date']}_{context['person_id']}_{template}"
                doc.save(out_docx)

                # PDF Conversion
                subprocess.run(['lowriter', '--headless', '--convert-to', 'pdf', out_docx])

                # Move files to output folder
                otput_folders = self.data_mgr.get_output_folders()
                move_path = f"{otput_folders['common']}{otput_folders['work_travels']}{context['wt_date']}"
                if not path.exists(move_path):
                    makedirs(move_path, exist_ok=True)
                shutil.move(out_docx, path.join(move_path, path.basename(out_docx)))
                pdf_path = out_docx.replace(".docx", ".pdf")
                shutil.move(pdf_path, path.join(move_path, path.basename(pdf_path)))
                pdf_path = path.join(move_path, path.basename(pdf_path))

                # Auto-open PDF
                subprocess.run(['xdg-open', pdf_path])

            messagebox.showinfo(self.labels["messages"]["success_title"], "Done!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.gen_btn.config(state="normal")
            self.progress.pack_forget()
