from classes.docs.BaseDoc import BaseDoc
from classes.docs.business_trip.BusinessTripExporter import BusinessTripExporter
from datetime import datetime

DATE_FORMAT = "%d/%m/%Y"

class BusinessTripOrder(BaseDoc):
    def __init__(self, parent, data_mgr):
        super().__init__(parent, data_mgr, "business_trip", ["business_trip_order.docx", "business_trip_report.docx"])
        self.setup_ui_components()
        self.preselect_latest_project()

    def setup_ui_components(self):
        self.ui_mgr.add_tab_title(self, "bt_order")
        self.setup_additional_ui_components()
        self.bt_context = {}
        self.projects_list = self.data_mgr.get_all_projects()
        self.all_projects = self.ui_mgr.add_dropdown(self, "projects", self.projects_list)
        self.all_projects.bind("<<ComboboxSelected>>", self.on_project_selected)
        self.persons_multiselect = self.ui_mgr.add_multiselect(self, "select_person", [])
        self.bt_purpose_field = self.ui_mgr.add_text_field(self, "bt_purpose", height=5, width=50)
        self.bt_destination_field = self.ui_mgr.add_field(self, "bt_destination")
        self.date_from = self.ui_mgr.add_date_field(self, "bt_from", preselect_today=True, width=11)
        self.date_to = self.ui_mgr.add_date_field(self, "bt_to", min_date_from=self.date_from, width=11)
        self.ui_mgr.add_checkbox_field(self, "bt_euro_per_day", self.labels["fields"]["bt_euro_per_day"], default_value=str(self.data_mgr.data['common'].get("euro_per_day", "")), width=5)
        self.ui_mgr.add_checkbox_field(self, "bt_nights_max_value", self.labels["fields"]["bt_night_money"], width=5)
        travel_row = self.ui_mgr.add_frame(self, show_by_default=False)
        travel_row.pack(fill='x', padx=0, pady=0)

        travel_left = self.ui_mgr.add_frame(self, show_by_default=False, container=travel_row)
        travel_left.pack(side='left', anchor='n')
        travel_right = self.ui_mgr.add_frame(self, show_by_default=False, container=travel_row)
        travel_right.pack(side='left', fill='y', pady=(20, 0), padx=(10, 0))

        self.bt_travel_with_var, self.travel_multiselect = self.ui_mgr.add_checkbox_multi(
            self,
            self.labels["fields"]["bt_travel_money"],
            self.labels["multiselect"]["travel_with"],
            parent=travel_left,
        )

        self.persons_cars_frame = self.ui_mgr.add_frame(self, show_by_default=False, container=travel_right)
        self.ui_mgr.add_label(self, self.labels["fields"]["select_car"], container=self.persons_cars_frame, anchor='w')
        self.persons_cars = self.ui_mgr.add_listbox(
            self,
            selectmode="multiple",
            height=10,
            exportselection=0,
            container=self.persons_cars_frame,
            pack_kwargs={"fill": "both", "expand": True},
        )
        self.persons_cars_frame.pack_forget()

        # internal mapping of displayed car entries -> (person_id, car_dict)
        self.persons_cars_items = []
        # bind travel and persons selection events to keep cars list in sync
        try:
            self.travel_multiselect.bind('<<ListboxSelect>>', self.on_travel_options_changed)
        except Exception:
            pass
        try:
            self.persons_multiselect.bind('<<ListboxSelect>>', self.on_persons_selection_changed)
        except Exception:
            pass
        self.ui_mgr.add_checkbox_field(self, "bt_other_expences", self.labels["fields"]["bt_other_expences"], default_value=self.data_mgr.data['common'].get("other_expences", ""), width=30)
        self.ui_mgr.add_common_buttons(self, "gen_business_trip")

    def setup_additional_ui_components(self):
        """Hook for subclasses that need controls before the order fields."""

    def preselect_latest_project(self):
        if self.projects_list:
            latest_project_id = self.get_latest_project_id()
            self.all_projects.set(latest_project_id)
            self.on_project_selected(None)

    def get_latest_project_id(self):
        return max(
            self.projects_list,
            key=lambda pid: datetime.strptime(
                self.data_mgr.get_project_by_id(pid).get('end_date', '2001-01-01'),
                '%Y-%m-%d'
            )
        )

    def on_project_selected(self, event):
        selected_project = self.all_projects.get()
        project = self.data_mgr.get_project_by_id(selected_project)
        if project:
            team = project.get('team', [])
            self.persons_multiselect.delete(0, 'end')
            for coworker_id in team:
                coworker = self.data_mgr.get_coworker_by_id(coworker_id)
                self.persons_multiselect.insert('end', f"({coworker_id}) {coworker.get('names', 'Unknown')}")
            self.persons_multiselect.config(height=min(max(len(team), 1), 10))

    def on_travel_options_changed(self, event):
        # Show or hide the persons_cars multi-select when "кола" travel option is toggled
        try:
            selected_indices = self.travel_multiselect.curselection()
            selected_options = [self.labels["multiselect"]["travel_with"][i] for i in selected_indices]
        except Exception:
            selected_options = []
        if "кола" in selected_options:
            self.update_persons_cars()
            try:
                self.persons_cars_frame.pack(side='left', fill='both', expand=True)
            except Exception:
                pass
        else:
            try:
                self.persons_cars_frame.pack_forget()
            except Exception:
                pass

    def on_persons_selection_changed(self, event):
        # Refresh persons_cars when selected persons change
        try:
            selected_indices = self.travel_multiselect.curselection()
            selected_options = [self.labels["multiselect"]["travel_with"][i] for i in selected_indices]
        except Exception:
            selected_options = []
        if "кола" in selected_options:
            self.update_persons_cars()

    def update_persons_cars(self):
        # Populate persons_cars with cars for selected persons (or whole team if none selected)
        person_ids = self.get_selected_person_ids()
        if not person_ids:
            proj = self.data_mgr.get_project_by_id(self.all_projects.get())
            person_ids = proj.get('team', []) if proj else []
        self.persons_cars.delete(0, 'end')
        self.persons_cars_items = []
        for pid in person_ids:
            cw = self.data_mgr.get_coworker_by_id(pid)
            if not cw:
                continue
            car = cw.get('car')
            if not car:
                continue
            label = f"{pid} - {car.get('brand','')} {car.get('model','')} {car.get('year','')} ({car.get('plate','')})"
            self.persons_cars.insert('end', label)
            self.persons_cars_items.append((pid, car))
        # ensure no car is pre-selected
        try:
            self.persons_cars.selection_clear(0, 'end')
        except Exception:
            pass
        # adjust visible rows so all cars are visible (limit to 10)
        try:
            self.persons_cars.config(height=min(max(len(self.persons_cars_items), 1), 10))
        except Exception:
            pass

    def get_selected_person_ids(self):
        selected_persons_ids = []
        for i in self.persons_multiselect.curselection():
            item = self.persons_multiselect.get(i)
            # Extract person ID from the formatted string
            person_id = item.split(')')[0].strip('(')
            selected_persons_ids.append(person_id)
        return selected_persons_ids

    def get_all_selected_co_workers(self):
        return [self.data_mgr.get_coworker_by_id(person_id) for person_id in self.selected_person_ids if self.data_mgr.get_coworker_by_id(person_id)]

    def get_all_persons_names_for_bt(self):
        result = ""
        nb = 1
        selected_persons_count = len(self.selected_persons)
        for co_worker in self.selected_persons:
            result += f"{nb}.\t{co_worker['titles']} {co_worker['full_name']}, {co_worker['department']}, {co_worker['work_place']}"
            if selected_persons_count > nb:
                result += '\n'
            nb += 1
        return result

    def add_project_and_person_data(self):
        project = self.data_mgr.get_project_by_id(self.all_projects.get())
        project_leader = self.data_mgr.get_coworker_by_id(project["project_lead"])
        self.selected_person_ids = self.get_selected_person_ids()
        self.selected_persons = self.get_all_selected_co_workers()
        bt_contract_info = project["description"]
        self.bt_context.update({
            "leader_titles": project_leader["titles"],
            "leader_names": project_leader["names"],
            "leader_full_name": project_leader["full_name"],
            "leader_work_place": project_leader["department"] + ", " + project_leader["work_place"],
            "bt_all_persons": self.get_all_persons_names_for_bt(),
            "bt_contract_info": bt_contract_info,
            "person_id": "_".join(self.selected_person_ids) if self.selected_person_ids else ""
        })
        return bt_contract_info

    def _get_widget_value(self, widget):
        if widget is None:
            return ""
        try:
            return widget.get("1.0", "end-1c").strip()
        except Exception:
            try:
                if hasattr(widget, "curselection"):
                    return "selected" if widget.curselection() else ""
                return widget.get().strip()
            except Exception:
                return ""

    def _apply_required_field_border(self, widget, is_valid):
        if widget is None:
            return
        try:
            widget.config(
                highlightthickness=2 if not is_valid else 1,
                highlightbackground="#d62728" if not is_valid else "#b0b0b0",
                highlightcolor="#d62728" if not is_valid else "#b0b0b0",
                relief="solid" if not is_valid else "flat",
                borderwidth=2 if not is_valid else 1,
            )
        except Exception:
            pass

    def _apply_required_fields_state(self, missing_fields):
        for field_name, attr_name in (
            ("bt_purpose", "bt_purpose_field"),
            ("bt_destination", "bt_destination_field"),
            ("persons_multiselect", "persons_multiselect"),
            ("bt_from", "date_from"),
            ("bt_to", "date_to"),
        ):
            widget = getattr(self, attr_name, None)
            self._apply_required_field_border(widget, field_name not in missing_fields)

    def get_missing_required_fields(self):
        missing_fields = []

        if not self._get_widget_value(getattr(self, "bt_purpose_field", None)):
            missing_fields.append("bt_purpose")

        if not self._get_widget_value(getattr(self, "bt_destination_field", None)):
            missing_fields.append("bt_destination")

        if not self._get_widget_value(getattr(self, "persons_multiselect", None)):
            missing_fields.append("persons_multiselect")

        for field_name, attr_name in (("bt_from", "date_from"), ("bt_to", "date_to")):
            widget = getattr(self, attr_name, None)
            value = self._get_widget_value(widget)
            if not value:
                missing_fields.append(field_name)
                continue

            try:
                datetime.strptime(value, DATE_FORMAT)
            except ValueError:
                missing_fields.append(field_name)

        return missing_fields

    def validate_required_fields(self):
        missing_fields = self.get_missing_required_fields()
        self._apply_required_fields_state(missing_fields)
        if missing_fields:
            labels = []
            for field_name in missing_fields:
                field_label = self.labels.get("fields", {}).get(field_name, field_name)
                labels.append(field_label)
            raise ValueError("Please fill in the required fields: " + ", ".join(labels))

    def calculate_date_context(self):
        bt_from_str = self.date_from.get()
        bt_to_str = self.date_to.get()
        if bt_from_str and bt_to_str:
            try:
                bt_from = datetime.strptime(bt_from_str, DATE_FORMAT)
                bt_to = datetime.strptime(bt_to_str, DATE_FORMAT)
                total_days = (bt_to - bt_from).days + 1
                self.bt_context.update({
                    "bt_from": bt_from_str,
                    "bt_to": bt_to_str,
                    "bt_total_days": str(total_days),
                    "bt_nights_count": str(max(0, total_days - 1)),
                    "bt_date": bt_from.strftime('%Y%m%d'),
                })
            except ValueError:
                self.bt_context.update({
                    "bt_total_days": "Invalid dates",
                    "bt_nights_count": "",
                    "bt_date": "date_error"
                })
        else:
            self.bt_context.update({
                "bt_total_days": "",
                "bt_nights_count": "",
                "bt_date": "no_date"
            })

    def process_field_values(self):
        for field_key, _, widget in self.input_fields:
            try:
                value = widget.get("1.0", "end-1c").strip()
            except TypeError:
                value = widget.get().strip()
            self.bt_context[field_key] = value

    def process_money_sources(self):
        bt_contract_info = self.bt_context.get("bt_contract_info", "")

        if self.bt_context.get("bt_euro_per_day"):
            self.bt_context["bt_day_money_from"] = self.labels["messages"]["account_on"] + bt_contract_info
        else:
            self.bt_context["bt_day_money_from"] = self.labels["messages"]["account_on"] + self.labels["messages"]["third_party"]

        if self.bt_context.get("bt_nights_max_value"):
            self.bt_context["bt_nights_money_from"] = self.labels["messages"]["account_on"] + bt_contract_info
        else:
            self.bt_context["bt_nights_money_from"] = self.labels["messages"]["account_on"] + self.labels["messages"]["third_party"]

    def get_selected_travel_options(self):
        if not self.bt_travel_with_var.get():
            return []

        selected_indices = self.travel_multiselect.curselection()
        return [self.labels["multiselect"]["travel_with"][i] for i in selected_indices]

    def get_selected_car_details(self):
        if not hasattr(self, 'persons_cars') or not getattr(self, 'persons_cars_items', None):
            return ""

        car_texts = []
        for index in self.persons_cars.curselection():
            try:
                _, personal_car = self.persons_cars_items[index]
            except Exception:
                continue
            if personal_car:
                car_texts.append(
                    f"Лично МПС {personal_car.get('brand','')} {personal_car.get('model','')} "
                    f"{personal_car.get('year','')}г. с рег. номер {personal_car.get('plate','')}, "
                    f"разход {personal_car.get('liters_per_100km','')} л/100км, "
                    f"{personal_car.get('fuel_type','')}."
                )
        return " ".join(car_texts)

    def process_travel_options(self):
        bt_contract_info = self.bt_context.get("bt_contract_info", "")
        selected_options = self.get_selected_travel_options()
        if self.bt_travel_with_var.get():
            self.bt_context["bt_travel_money_from"] = self.labels["messages"]["account_on"] + bt_contract_info
            self.bt_context["bt_travel_with"] = ", ".join(selected_options)
        else:
            self.bt_context["bt_travel_money_from"] = self.labels["messages"]["account_on"] + self.labels["messages"]["third_party"]
            self.bt_context["bt_travel_with"] = ""

        if "кола" in selected_options:
            car_details = self.get_selected_car_details()
            if car_details:
                self.bt_context["bt_travel_money_from"] += " " + car_details

    def _get_date_value(self, widget, date_format="%d.%m.%Y"):
        value = widget.get()
        if value:
            try:
                return datetime.strptime(value, DATE_FORMAT).strftime(date_format)
            except ValueError:
                pass
        return ""

    def get_context(self):
        self.validate_required_fields()
        self.bt_context = {}
        self.add_project_and_person_data()
        self.calculate_date_context()
        self.process_field_values()
        self.process_money_sources()
        self.process_travel_options()
        self.bt_context["sub_folder"] = ""
        bt_start_date = self._get_date_value(self.date_from, date_format='%Y_%m_%d')
        self.bt_context["doc_date_and_ids_identifier"] = bt_start_date + "_" + self.all_projects.get() + "_" + "_".join(self.selected_person_ids)
        return self.bt_context

    def final_action(self):
        project_id = self.all_projects.get()
        bt_title = self.bt_context.get("doc_date_and_ids_identifier", "")
        new_bussiness_trip = {
            bt_title: BusinessTripExporter.build_business_trip_payload(
                bt_title=bt_title,
                project_id=project_id,
                context=self.bt_context,
                selected_person_ids=self.selected_person_ids,
            )
        }
        self.data_mgr.save_new_bussiness_trip(new_bussiness_trip)
