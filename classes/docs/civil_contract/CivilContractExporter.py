from Helpers import Helpers
from enums.Enums import CCStatus


class CivilContractExporter:
    @staticmethod
    def build_civil_contract_payload(contract_title, project_id, person_id, context, status=None):
        return Helpers.build_common_export_payload(
            document_id=contract_title,
            project_id=project_id,
            status=status or CCStatus.GENERATED.name,
            extra_fields={
                "cc_task": context.get("cc_task", ""),
                "cc_number": "",
                "person_id": person_id,
                "cc_task_start_date": context.get("cc_task_start_date", ""),
                "cc_task_end_date": context.get("cc_task_end_date", ""),
            },
        )
