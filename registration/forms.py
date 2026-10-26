import re

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Bank, normalize_id

ID_PATTERN = re.compile(r"[A-Z0-9-]+")


class RegistrationForm(forms.Form):
    id_number = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(
        required=False,
        error_messages={"invalid": _("Enter a valid email address.")},
    )
    bank = forms.ModelChoiceField(
        queryset=Bank.objects.none(),
        empty_label=None,
        error_messages={
            "required": _("Select the card issuing bank."),
            "invalid_choice": _("Select the card issuing bank."),
        },
    )

    def __init__(self, *args, country, **kwargs):
        super().__init__(*args, **kwargs)
        self.country = country
        self.fields["bank"].queryset = country.banks.filter(is_active=True)
        self.fields["id_number"].error_messages["required"] = _("Enter the ID number.")

    def clean_id_number(self):
        return normalize_id(self.cleaned_data["id_number"])

    def clean(self):
        cleaned = super().clean()
        id_number = cleaned.get("id_number")
        if id_number and not ID_PATTERN.fullmatch(id_number):
            self.add_error("id_number", _("The ID may only contain letters, numbers and dashes."))
        return cleaned
