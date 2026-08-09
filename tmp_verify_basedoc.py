import os
import sys
import types
import tkinter as tk

if 'docxtpl' not in sys.modules:
    docxtpl_stub = types.ModuleType('docxtpl')
    class DocxTemplate:
        def __init__(self, path):
            self.path = path
        def render(self, context):
            pass
        def save(self, path):
            with open(path, 'wb') as f:
                f.write(b'PK')
    docxtpl_stub.DocxTemplate = DocxTemplate
    sys.modules['docxtpl'] = docxtpl_stub

if 'tkcalendar' not in sys.modules:
    tkcalendar_stub = types.ModuleType('tkcalendar')
    class Calendar:
        def __init__(self, master, **kwargs):
            pass
        def pack(self, **kwargs):
            pass
        def get_date(self):
            return '01/01/2026'
    tkcalendar_stub.Calendar = Calendar
    sys.modules['tkcalendar'] = tkcalendar_stub

if 'tkinterdnd2' not in sys.modules:
    tkinterdnd2_stub = types.ModuleType('tkinterdnd2')
    tkinterdnd2_stub.DND_FILES = 'DND_FILES'
    sys.modules['tkinterdnd2'] = tkinterdnd2_stub

from classes.docs.BaseDoc import BaseDoc
from classes.DataMgr import DataMgr

root = tk.Tk()
root.withdraw()

class DummyDoc(BaseDoc):
    def __init__(self, parent, data_mgr):
        super().__init__(parent, data_mgr, 'business_trip', ['business_trip_order.docx'])

    def get_context(self):
        return {'doc_date_and_ids_identifier': 'testid', 'sub_folder': '', 'bt_date': '20260101'}

    def final_action(self):
        pass

try:
    d = DummyDoc(root, DataMgr(os.getcwd()))
    d._find_office_converter = lambda: None
    d._try_docx2pdf = lambda out_docx: False
    d.process_doc()
    print('ok')
finally:
    root.destroy()
