from functools import wraps

from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import translation

from .forms import RegistrationForm
from .models import Country, Registration

SESSION_KEY = "last_registration_id"


def country_view(view):
    """Busca el pais por la url y renderiza en su idioma."""

    @wraps(view)
    def wrapper(request, country_code, *args, **kwargs):
        country = get_object_or_404(Country, code=country_code.lower(), is_active=True)
        with translation.override(country.language):
            request.LANGUAGE_CODE = country.language
            return view(request, country, *args, **kwargs)

    return wrapper


def _context(country, **extra):
    return {
        "country": country,
        "lang": country.language,
        **extra,
    }


def index(request):
    """Pantalla inicial: el staff elige su pais."""
    countries = Country.objects.filter(is_active=True)
    return render(request, "registration/countries.html", {"countries": countries, "lang": "en"})


@country_view
def register(request, country):
    if request.method == "POST":
        form = RegistrationForm(request.POST, country=country)
        if form.is_valid():
            id_number = form.cleaned_data["id_number"]
            registration = Registration.objects.filter(country=country, id_number=id_number).first()
            created = False
            if registration is None:
                try:
                    with transaction.atomic():
                        registration = Registration.objects.create(
                            country=country, bank=form.cleaned_data["bank"], id_number=id_number,
                            email=form.cleaned_data["email"],
                        )
                        created = True
                except IntegrityError:  # otro dispositivo lo registro justo antes
                    registration = Registration.objects.get(country=country, id_number=id_number)
            request.session[SESSION_KEY] = registration.pk
            target = "registration:success" if created else "registration:duplicate"
            return redirect(target, country_code=country.code)
    else:
        form = RegistrationForm(country=country, initial={"id_number": request.GET.get("id", "")})

    selected_bank = form["bank"].value()
    return render(
        request, "registration/register.html",
        _context(country, form=form, banks=form.fields["bank"].queryset, selected_bank=str(selected_bank or "")),
    )


@country_view
def success(request, country):
    return render(request, "registration/success.html", _context(country))


@country_view
def duplicate(request, country):
    registration = Registration.objects.filter(
        pk=request.session.get(SESSION_KEY), country=country,
    ).first()
    if registration is None:
        return redirect("registration:register", country_code=country.code)
    return render(request, "registration/duplicate.html", _context(country, registration=registration))
