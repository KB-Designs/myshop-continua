

from django import forms
from .models import Order, COUNTY_CHOICES, PAYMENT_METHOD_CHOICES

PICKUP_CHOICES = {
    'Nairobi': [('CBD', 'CBD'), ('Westlands', 'Westlands')],
    'Mombasa': [('Nyali', 'Nyali'), ('Likoni', 'Likoni')],
    'Kisumu': [('Milimani', 'Milimani'), ('Kondele', 'Kondele')],
}

class OrderCreateForm(forms.ModelForm):
    county = forms.ChoiceField(choices=COUNTY_CHOICES, label='County')
    pickup_station = forms.ChoiceField(choices=[], label='Pickup Station')
    payment_method = forms.ChoiceField(choices=PAYMENT_METHOD_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'phone',
            'email', 'county', 'pickup_station', 'payment_method'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Always start with empty pickup stations (populated via JS)
        self.fields['pickup_station'].choices = []

        # If form is being re-rendered with POSTed data, repopulate based on county
        if 'county' in self.data:
            selected_county = self.data.get('county')
            self.fields['pickup_station'].choices = PICKUP_CHOICES.get(selected_county, [])
