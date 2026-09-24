from classes.docs.db_management.BaseManagementTab import BaseManagementTab


class CoWorkersManagementTab(BaseManagementTab):
    def __init__(self, parent, data_mgr):
        default_fields = {
            "full_name": "",
            "titles": "",
            "names": "",
            "position": "",
            "department": "",
            "work_place": "",
            "email": "",
            "egn": "",
            "address.main_line": "",
            "address.city": "",
            "address.zip": "",
            "address.municipality": "",
            "id.number": "",
            "id.issue_date": "",
            "id.issuer": "",
            "iban": "",
            "car.brand": "",
            "car.model": "",
            "car.year": "",
            "car.plate": "",
            "car.liters_per_100km": "",
            "car.fuel_type": "",
        }
        super().__init__(parent, data_mgr, "co_workers", "Co-workers", default_fields)
