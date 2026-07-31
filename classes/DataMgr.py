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

    def save_new_bussiness_trip(self, new_bussiness_trip):
        if 'business_trips' not in self.data:
            self.data['business_trips'] = {}
        self.data['business_trips'].update(new_bussiness_trip)

        with open('data/data.json', 'w', encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)