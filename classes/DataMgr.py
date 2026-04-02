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