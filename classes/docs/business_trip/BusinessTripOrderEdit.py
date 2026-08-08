from enums.Enums import BTStatus

from classes.docs.business_trip.BusinessTripOrder import BusinessTripOrder

class BusinessTripOrderEdit(BusinessTripOrder):
    """Edit and regenerate an existing business-trip order."""

    def __init__(self, parent, data_mgr):
        self.business_trip_ids = []
        self.selected_business_trip_id = None
        super().__init__(parent, data_mgr)
        if self.business_trip_ids:
            self.business_trips_dropdown.current(0)
            self.on_business_trip_selected(None)
        else:
            self.gen_btn.configure(state="disabled")

    def setup_additional_ui_components(self):
        statuses = [status for status in BTStatus if status != BTStatus.REPORTED]
        business_trips = self.data_mgr.get_all_bussiness_trips_by_status(statuses)
        self.business_trip_ids = list(business_trips)
        self.business_trips = business_trips
        self.business_trips_dropdown = self.ui_mgr.add_dropdown(
            self, "business_trips", self.business_trip_ids
        )
        self.business_trips_dropdown.bind(
            "<<ComboboxSelected>>", self.on_business_trip_selected
        )

    def on_business_trip_selected(self, event):
        business_trip_id = self.business_trips_dropdown.get()
        business_trip = self.business_trips.get(business_trip_id)
        if not business_trip:
            return

        self.selected_business_trip_id = business_trip_id
        project_id = business_trip.get("project_id", "")
        if project_id in self.projects_list:
            self.all_projects.set(project_id)
            self.on_project_selected(None)

        self._select_persons(business_trip.get("person_ids", []))
        self._set_entry(self.date_from, business_trip.get("start_date", ""))
        self._set_entry(self.date_to, business_trip.get("end_date", ""))
        self._set_checkbox_field("bt_euro_per_day", business_trip.get("bt_euro_per_day", ""))
        self._set_checkbox_field("bt_nights_max_value", business_trip.get("bt_nights_max_value", ""))
        self._set_checkbox_field("bt_other_expences", business_trip.get("bt_other_expences", ""))
        self._set_entry_by_key("bt_destination", business_trip.get("bt_destination", ""))
        self._set_text_by_key("bt_purpose", business_trip.get("bt_heading", ""))
        self._set_entry_by_key("bt_euro_per_day", business_trip.get("bt_euro_per_day", ""))
        self._set_entry_by_key("bt_nights_max_value", business_trip.get("bt_nights_max_value", ""))
        self._set_entry_by_key("bt_other_expences", business_trip.get("bt_other_expences", ""))
        self._select_travel_options(business_trip.get("bt_travel_with", ""))

    def get_context(self):
        """Build the order context with a separate identifier for edited files."""
        context = super().get_context()
        identifier = context.get("doc_date_and_ids_identifier", "")
        if identifier and not identifier.endswith("_Edited"):
            context["doc_date_and_ids_identifier"] = identifier + "_Edited"
        return context

    def _select_persons(self, person_ids):
        self.persons_dropdown.selection_clear(0, "end")
        person_ids = set(person_ids or [])
        for index in range(self.persons_dropdown.size()):
            person_id = self.persons_dropdown.get(index).split(")", 1)[0].lstrip("(")
            if person_id in person_ids:
                self.persons_dropdown.selection_set(index)

    def _select_travel_options(self, travel_with):
        options = {option.strip() for option in (travel_with or "").split(",") if option.strip()}
        self.travel_multiselect.selection_clear(0, "end")
        for index, option in enumerate(self.labels["multiselect"]["travel_with"]):
            if option in options:
                self.travel_multiselect.selection_set(index)
        self.bt_travel_with_var.set(bool(options))
        self.on_travel_options_changed(None)

    def _set_entry(self, widget, value):
        widget.delete(0, "end")
        widget.insert(0, value or "")

    def _set_entry_by_key(self, key, value):
        for field_key, _, widget in self.input_fields:
            if field_key == key:
                self._set_entry(widget, value)
                return

    def _set_text_by_key(self, key, value):
        for field_key, _, widget in self.input_fields:
            if field_key == key:
                widget.delete("1.0", "end")
                widget.insert("1.0", value or "")
                return

    def _set_checkbox_field(self, key, value):
        variable = getattr(self, f"{key}_var", None)
        if variable is not None:
            variable.set(bool(value))

    def final_action(self):
        if not self.selected_business_trip_id:
            return

        current_trip = self.data_mgr.data["business_trips"].get(self.selected_business_trip_id, {})
        context = self.bt_context
        current_trip.update({
            "project_id": self.all_projects.get(),
            "bt_heading": context.get("bt_purpose", ""),
            "person_ids": self.selected_person_ids,
            "start_date": context.get("bt_from", ""),
            "end_date": context.get("bt_to", ""),
            "doc_date_and_ids_identifier": context.get("doc_date_and_ids_identifier", ""),
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
        })
        self.data_mgr.data["business_trips"][self.selected_business_trip_id] = current_trip
        self.data_mgr.save_data()