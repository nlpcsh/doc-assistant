import json

class DataMgr:
    """Manages data from data.json file."""
    def __init__(self, data_file):
        with open(data_file, 'r', encoding="utf-8") as f:
            self.data = json.load(f)
    
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

    def save_work_travel(self, wt_date, person_id, project_id):
        if 'work_travel' not in self.data:
            self.data['work_travel'] = {}
        if wt_date not in self.data['work_travel']:
            self.data['work_travel'][wt_date] = {"persons": [], "project": None}

        self.data['work_travel'][wt_date]["persons"].append(person_id)
        self.data['work_travel'][wt_date]["project"] = project_id

        with open('data/data.json', 'w', encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)