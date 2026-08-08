from Helpers import Helpers
from enums.Enums import BTStatus


class BusinessTripExporter:
    @staticmethod
    def build_business_trip_payload(
        bt_title,
        project_id,
        context,
        selected_person_ids,
        based_on=None,
        reported_ids=None,
        status=None,
    ):
        payload = Helpers.build_common_export_payload(
            document_id=bt_title,
            project_id=project_id,
            status=status or BTStatus.GENERATED.name,
            extra_fields={
                "bt_heading": context.get("bt_purpose", ""),
                "bt_order_number": "",
                "person_ids": list(selected_person_ids or []),
                "start_date": context.get("bt_from", ""),
                "end_date": context.get("bt_to", ""),
                "bt_travel_with": context.get("bt_travel_with", ""),
                "bt_day_money_from": context.get("bt_day_money_from", ""),
                "bt_nights_money_from": context.get("bt_nights_money_from", ""),
                "bt_travel_money_from": context.get("bt_travel_money_from", ""),
                "bt_destination": context.get("bt_destination", ""),
                "bt_euro_per_day": context.get("bt_euro_per_day", ""),
                "bt_nights_max_value": context.get("bt_nights_max_value", ""),
                "bt_other_expences": context.get("bt_other_expences", ""),
                "bt_contract_info": context.get("bt_contract_info", ""),
                "leader_titles": context.get("leader_titles", ""),
                "leader_names": context.get("leader_names", ""),
                "leader_full_name": context.get("leader_full_name", ""),
                "leader_work_place": context.get("leader_work_place", ""),
                "bt_all_persons": context.get("bt_all_persons", ""),
                "reported_ids": list(reported_ids or []),
            },
        )
        if based_on is not None:
            payload["based_on"] = based_on
        return payload
