from Helpers import Helpers
from tkinter import ttk, StringVar


class CountryCitySelector:
    def __init__(self, root, field_labels=None, on_selection_change=None):
        self.root = root
        if field_labels is None:
            field_labels = {}
        self.field_labels = field_labels.get("fields", {}) if isinstance(field_labels, dict) else {}
        self.on_selection_change = on_selection_change

        self.countries = Helpers.get_countries(root=self.root)

        # Selection properties
        self.from_country = ""
        self.from_city = ""
        self.to_country = ""
        self.to_city = ""
        self.selected_cities = ""
        self.accommodation = ""
        self.daily = ""
        self.destination = ""

        # All dropdown pairs are stored here.
        self.dropdown_pairs = []

        # -----------------------------
        # Dropdowns area
        # -----------------------------
        self.dropdowns_frame = ttk.Frame(root)
        self.dropdowns_frame.pack(
            fill="x",
            padx=10,
            pady=10
        )

        # First pair: default country + first city
        self.add_dropdown_pair(first=True)

        # Second pair: completely empty
        self.add_dropdown_pair(first=False)

    def get_default_country(self):
        for country, data in self.countries.items():
            if data.get("default") is True:
                return country

        return next(iter(self.countries), "")

    @property
    def destination_obj(self):
        return {
            "from": [self.from_country, self.from_city],
            "to": [self.to_country, self.to_city]
        }

    def get_destination_obj(self):
        return self.destination_obj

    # =========================================================
    # Dropdown pairs
    # =========================================================

    def add_dropdown_pair(self, first=False):
        pair_frame = ttk.Frame(
            self.dropdowns_frame,
            relief="groove",
            borderwidth=1
        )

        pair_frame.pack(
            side="left",
            padx=5,
            pady=5,
            anchor="n"
        )

        # -----------------------------
        # Country dropdown
        # -----------------------------

        country_var = StringVar()

        if first is True:
            label_text = self.field_labels.get("bt_depart_from", "От:")
        else:
            label_text = self.field_labels.get("bt_arrive_to", "До:")

        label = ttk.Label(
            pair_frame,
            text=label_text,
            width=18
        )

        label.pack(
            padx=5,
            pady=(5, 3)
        )

        country_combo = ttk.Combobox(
            pair_frame,
            textvariable=country_var,
            values=list(self.countries.keys()),
            state="readonly",
            width=18
        )

        country_combo.pack(
            padx=5,
            pady=(5, 3)
        )

        # -----------------------------
        # City dropdown
        # -----------------------------

        city_var = StringVar()

        city_combo = ttk.Combobox(
            pair_frame,
            textvariable=city_var,
            state="readonly",
            width=18
        )

        city_combo.pack(
            padx=5,
            pady=(3, 5)
        )

        pair = {
            "first": first,
            "frame": pair_frame,
            "country_var": country_var,
            "country_combo": country_combo,
            "city_var": city_var,
            "city_combo": city_combo,
        }

        self.dropdown_pairs.append(pair)

        # Country selection
        country_combo.bind(
            "<<ComboboxSelected>>",
            lambda event, p=pair: self.country_selected(p)
        )

        # City selection
        city_combo.bind(
            "<<ComboboxSelected>>",
            lambda event, p=pair: self.city_selected(p)
        )

        # Initialize the first pair.
        if first:
            default_country = self.get_default_country()

            if default_country:
                country_var.set(default_country)
                self.populate_cities(
                    pair,
                    default_country
                )

                cities = self.countries[
                    default_country
                ].get("cities", [])

                if cities:
                    city_var.set(cities[0])
                    self.from_country = default_country
                    self.from_city = cities[0]

                self._update_properties()

    # =========================================================
    # Country selection
    # =========================================================

    def country_selected(self, pair):
        country = pair["country_var"].get()

        if not country:
            return

        self.populate_cities(
            pair,
            country
        )

        self._update_properties()

        if self.on_selection_change:
            self.on_selection_change(self)

    # =========================================================
    # Populate cities
    # =========================================================

    def populate_cities(self, pair, country):
        data = self.countries.get(
            country,
            {}
        )

        cities = data.get(
            "cities",
            []
        )

        pair["city_combo"]["values"] = cities

        # Selecting a new country clears the previous city.
        pair["city_var"].set("")

    # =========================================================
    # City selection
    # =========================================================

    def city_selected(self, pair):
        country = pair["country_var"].get()
        city = pair["city_var"].get()

        if not country or not city:
            return

        self._update_properties()

        if self.on_selection_change:
            self.on_selection_change(self)

    def _update_properties(self):
        if len(self.dropdown_pairs) > 0:
            self.from_country = self.dropdown_pairs[0]["country_var"].get()
            self.from_city = self.dropdown_pairs[0]["city_var"].get()

        if len(self.dropdown_pairs) > 1:
            self.to_country = self.dropdown_pairs[1]["country_var"].get()
            self.to_city = self.dropdown_pairs[1]["city_var"].get()

        # Rates are based on destination country if selected, otherwise departure country
        target_country = self.to_country if self.to_country else self.from_country
        data = self.countries.get(target_country, {})

        accommodation_val = data.get("accommodation", "")
        daily_val = data.get("daily", "")
        self.accommodation = str(accommodation_val) if accommodation_val != "" else ""
        self.daily = str(daily_val) if daily_val != "" else ""

        # Selected cities string
        if self.from_city and self.to_city:
            if self.from_city == self.to_city:
                self.selected_cities = self.from_city
            else:
                self.selected_cities = f"{self.from_city} - {self.to_city}"
        elif self.from_city:
            self.selected_cities = self.from_city
        elif self.to_city:
            self.selected_cities = self.to_city
        else:
            self.selected_cities = ""

        # Destination string: "from city" - "to city" - "from city"
        if self.from_city and self.to_city:
            self.destination = f"{self.from_city} - {self.to_city} - {self.from_city}"
        else:
            self.destination = ""

    def set_selection(self, from_country="", from_city="", to_country="", to_city=""):
        if len(self.dropdown_pairs) > 0:
            if from_country:
                self.dropdown_pairs[0]["country_var"].set(from_country)
                self.populate_cities(self.dropdown_pairs[0], from_country)
            if from_city:
                self.dropdown_pairs[0]["city_var"].set(from_city)

        if len(self.dropdown_pairs) > 1:
            if to_country:
                self.dropdown_pairs[1]["country_var"].set(to_country)
                self.populate_cities(self.dropdown_pairs[1], to_country)
            if to_city:
                self.dropdown_pairs[1]["city_var"].set(to_city)

        self._update_properties()

        if self.on_selection_change:
            self.on_selection_change(self)