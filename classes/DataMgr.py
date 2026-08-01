import json
from os import path
from datetime import datetime
from enums.Enums import BTStatus

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

        self.save_data()

    def get_all_bussiness_trips_by_status(self, status):
        status_value = getattr(status, 'value', status)
        expected_statuses = {
            status,
            status_value,
            str(status_value),
            getattr(status, 'name', status),
        }
        return {
            k: v for k, v in self.data.get('business_trips', {}).items()
            if v.get('status') in expected_statuses
        }

    def save_data(self):
        with open(path.join(self.base_dir, 'data/data.json'), 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4)

    def update_business_trip_statuses(self):
        if 'business_trips' not in self.data:
            self.data['business_trips'] = {}
        all_bt = self.data['business_trips']
        bt_to_update = {}
        for key, value in all_bt.items():
            if value.get('status') in [BTStatus.GENERATED.name, BTStatus.ONGOING.name]:
                value['status'] = BTStatus.GENERATED.name  # Default status if not present
                bt_to_update[key] = value
        for bt_id, bt in bt_to_update.items():
            # Here you would implement the logic to check the current date against the business trip's date
            current_date = datetime.now().date()
            bt_start_date = datetime.strptime(bt.get('start_date'), '%d/%m/%Y').date()  # Assuming 'date' is in 'YYYYMMDD' format
            bt_end_date = datetime.strptime(bt.get('end_date'), '%d/%m/%Y').date()  # Assuming 'date' is in 'YYYYMMDD' format
            if current_date > bt_start_date and current_date <= bt_end_date:
                # If the current date is past the business trip's date, update the status to 3
                bt['status'] = BTStatus.ONGOING.name  # Update status to IN_PROGRESS
            elif current_date > bt_end_date:
                # If the current date is past the business trip's end date, update the status to 3
                bt['status'] = BTStatus.READY_TO_REPORT.name  # Update status to READY_TO_REPORT

        self.save_data()
    # end def