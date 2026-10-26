import re

from django.db import models
from django.utils.translation import gettext_lazy as _


def normalize_id(value: str) -> str:
    """Quita espacios y pasa a mayusculas."""
    return re.sub(r"\s+", "", value or "").upper()


class Country(models.Model):
    """Pais de la activacion, define el idioma de las pantallas."""

    class Language(models.TextChoices):
        SPANISH = "es", _("Spanish")
        ENGLISH = "en", _("English")

    code = models.SlugField(
        _("code"), max_length=5, unique=True,
        help_text=_("Short code used in the URL, e.g. pa, co, us."),
    )
    name = models.CharField(_("name"), max_length=100)
    language = models.CharField(
        _("language"), max_length=2, choices=Language.choices, default=Language.SPANISH,
    )
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("country")
        verbose_name_plural = _("countries")

    def __str__(self):
        return self.name


class Bank(models.Model):
    """Banco emisor, cada uno pertenece a un pais."""

    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name="banks", verbose_name=_("country"),
    )
    name = models.CharField(_("name"), max_length=100)
    position = models.PositiveSmallIntegerField(_("position"), default=0)
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        ordering = ["country", "position", "name"]
        verbose_name = _("bank")
        verbose_name_plural = _("banks")
        constraints = [
            models.UniqueConstraint(fields=["country", "name"], name="unique_bank_per_country"),
        ]

    def __str__(self):
        return f"{self.name} ({self.country.code.upper()})"


class Registration(models.Model):
    """Un ID con su banco. Cada ID participa una sola vez por pais."""

    country = models.ForeignKey(
        Country, on_delete=models.PROTECT, related_name="registrations", verbose_name=_("country"),
    )
    bank = models.ForeignKey(
        Bank, on_delete=models.PROTECT, related_name="registrations", verbose_name=_("bank"),
    )
    id_number = models.CharField(_("ID number"), max_length=50)
    email = models.EmailField(_("email"), blank=True, help_text=_("Optional. Not unique: several IDs can share an email."))
    created_at = models.DateTimeField(_("registered at"), auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("registration")
        verbose_name_plural = _("registrations")
        constraints = [
            models.UniqueConstraint(fields=["country", "id_number"], name="unique_id_per_country"),
        ]

    def __str__(self):
        return f"{self.id_number} · {self.bank.name}"

    def save(self, *args, **kwargs):
        self.id_number = normalize_id(self.id_number)
        super().save(*args, **kwargs)
