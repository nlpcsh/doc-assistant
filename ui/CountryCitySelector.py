from Helpers import Helpers
from tkinter import ttk, StringVar, END


class CountryCitySelector:
    def __init__(self, root, field_labels={}):
        self.root = root
        # self.root.title("Countries and Cities")
        # self.root.geometry("900x350")
        self.field_labels = field_labels.get("fields", {})

        self.countries = Helpers.get_countries(root=self.root)

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

        # -----------------------------
        # Text fields area
        # -----------------------------
        self.text_frame = ttk.Frame(root)
        self.text_frame.pack(
            fill="x",
            padx=10,
            pady=10
        )

        self.text_fields = []

        # Text fields MUST be created before
        # initializing the first pair.
        self.create_text_fields()

        # First pair:
        # default country + first city
        self.add_dropdown_pair(first=True)

        # Second pair:
        # completely empty
        self.add_dropdown_pair(first=False)

    def get_default_country(self):
        for country, data in self.countries.items():
            if data.get("default") is True:
                return country

        return next(iter(self.countries), "")

    # =========================================================
    # Text fields
    # =========================================================

    def create_text_fields(self):
        labels = [
            "Selected cities:",
            "Accommodation:",
            "Daily:"
        ]

        for label_text in labels:
            row = ttk.Frame(self.text_frame)
            row.pack(
                fill="x",
                pady=3
            )

            label = ttk.Label(
                row,
                text=label_text,
                width=18
            )
            label.pack(side="left")

            entry = ttk.Entry(row)
            entry.pack(
                side="left",
                fill="x",
                expand=True
            )

            self.text_fields.append(entry)

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
            label_text = self.field_labels["bt_depart_from"]
        else:
            label_text = self.field_labels["bt_arrive_to"]

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
            lambda event, p=pair:
                self.country_selected(p)
        )

        # City selection
        city_combo.bind(
            "<<ComboboxSelected>>",
            lambda event, p=pair:
                self.city_selected(p)
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

                    # Update text fields, but DON'T create
                    # another pair because the second pair
                    # already exists.
                    self.process_city_selection(
                        default_country,
                        cities[0]
                    )

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

        # Selecting a new country clears
        # the previous city.
        pair["city_var"].set("")

    # =========================================================
    # City selection
    # =========================================================
    def city_selected(self, pair):
        country = pair["country_var"].get()
        city = pair["city_var"].get()

        if not country or not city:
            return

        # ALWAYS add/update the selected city first.
        self.process_city_selection(
            country,
            city
        )

        # # Only add a new empty pair if this pair
        # # is currently the last pair.
        # pair_index = self.dropdown_pairs.index(pair)

        # if pair_index == len(self.dropdown_pairs) - 1:
        #     self.add_dropdown_pair()


    def process_city_selection(self, country, city):
        data = self.countries.get(
            country,
            {}
        )

        accommodation = data.get(
            "accommodation",
            ""
        )

        daily = data.get(
            "daily",
            ""
        )

        # ----------------------------------
        # Add city to Selected cities field
        # ----------------------------------

        current_cities = self.text_fields[0].get().strip()

        if current_cities:
            existing_cities = [
                value.strip()
                for value in current_cities.split(",")
            ]

            if city not in existing_cities:
                existing_cities.append(city)

            current_cities = ", ".join(existing_cities)
        else:
            current_cities = city

        self.set_entry(
            self.text_fields[0],
            current_cities
        )

        # ----------------------------------
        # Update accommodation
        # ----------------------------------

        self.set_entry(
            self.text_fields[1],
            str(accommodation)
        )

        # ----------------------------------
        # Update daily
        # ----------------------------------

        self.set_entry(
            self.text_fields[2],
            str(daily)
        )

    # =========================================================
    # Utility
    # =========================================================

    @staticmethod
    def set_entry(entry, value):
        entry.delete(
            0,
            END
        )

        entry.insert(
            0,
            value
        )


# =============================================================
# Application
# =============================================================

# if __name__ == "__main__":
#     root = tk.Tk()

#     app = CountryCityApp(root)

#     root.mainloop()