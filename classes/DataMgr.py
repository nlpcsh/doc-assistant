import json
from os import path

class DataMgr:
    """Manages data from data.json file."""
    def __init__(self, base_dir):
        self.base_dir = base_dir

        data_file = path.join(self.base_dir, "data/data.json")
        with open(data_file, 'r', encoding="utf-8") as f:
            self.data = json.load(f)

        labels_path = path.join(self.base_dir, "settings/labels.json")
        self.labels = {}
        with open(labels_path, "r", encoding="utf-8") as f:
            self.labels = json.load(f)

    def get_labels(self):
        return self.labels
    
    def get_project_by_id(self, project_id):
        for p_id in self.data['projects']:
            if p_id == project_id:
                return self.data['projects'][p_id]
        return None
    
    def get_coworker_by_id(self, coworker_id):
        for c_id in self.data['co_workers']:
            if c_id == coworker_id:
                return self.data['co_workers'][c_id]
        return None
    
    def get_all_projects(self):
        return list(self.data['projects'].keys())
    
    def get_output_folders(self):
        return self.data['output_folders']

    def get_signature_settings(self, group, template_name):
        signatures = self.data.get('signatures', {})
        group_signatures = signatures.get(group, {})
        if not group_signatures:
            return None

        name_no_ext = path.splitext(template_name.lower())[0]
        for key, value in group_signatures.items():
            if key == name_no_ext or key in name_no_ext or name_no_ext in key:
                return value
        return None

    def save_business_trip(self, bt_date, person_id, project_id):
        if 'business_trip' not in self.data:
            self.data['business_trip'] = {}
        if bt_date not in self.data['business_trip']:
            self.data['business_trip'][bt_date] = {"persons": [], "project": None}

        self.data['business_trip'][bt_date]["persons"].append(person_id)
        self.data['business_trip'][bt_date]["project"] = project_id

        with open('data/data.json', 'w', encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)