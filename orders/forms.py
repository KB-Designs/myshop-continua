from django import forms
from .models import Order, COUNTY_CHOICES, PICKUP_STATION_CHOICES

class OrderCreateForm(forms.ModelForm):
    county = forms.ChoiceField(choices=COUNTY_CHOICES, required=True)
    pickup_station = forms.ChoiceField(choices=[], required=True)

    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'phone', 'email',
            'county', 'pickup_station', 'payment_method'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically set pickup_station choices based on selected county (if POSTed)
        if 'county' in self.data:
            selected_county = self.data.get('county')
        elif self.instance and self.instance.county:
            selected_county = self.instance.county
        else:
            selected_county = 'Nairobi'  # Default fallback

        # Grouped choices for pickup_station
        grouped_choices = [
            (county, [(station, station) for station in stations])
            for county, stations in PICKUP_STATION_CHOICES.items()
        ]
        self.fields['pickup_station'].choices = grouped_choices

        # Optionally pre-select based on selected county
        if selected_county in PICKUP_STATION_CHOICES:
            self.fields['pickup_station'].initial = PICKUP_STATION_CHOICES[selected_county][0]
