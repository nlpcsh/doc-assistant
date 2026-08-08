from enums.Enums import CCStatus


class CivilContractExporter:
    @staticmethod
    def build_civil_contract_payload(contract_title, project_id, person_id, context, status=None):
        return {
            "project_id": project_id,
            "cc_task": context.get("cc_task", ""),
            "cc_number": "",
            "person_id": person_id,
            "cc_task_start_date": context.get("cc_task_start_date", ""),
            "cc_task_end_date": context.get("cc_task_end_date", ""),
            "doc_date_and_ids_identifier": contract_title,
            "status": status or CCStatus.GENERATED.name,
        }
