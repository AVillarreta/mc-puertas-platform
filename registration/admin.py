import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import action

from .models import Bank, Country, Registration


class BankInline(TabularInline):
    model = Bank
    extra = 1
    fields = ("name", "position", "is_active")


@admin.register(Country)
class CountryAdmin(ModelAdmin):
    list_display = ("name", "code", "language", "is_active")
    list_filter = ("language", "is_active")
    search_fields = ("name", "code")
    inlines = [BankInline]


@admin.register(Bank)
class BankAdmin(ModelAdmin):
    list_display = ("name", "country", "position", "is_active")
    list_filter = ("country", "is_active")
    search_fields = ("name",)
    list_editable = ("position", "is_active")


@admin.register(Registration)
class RegistrationAdmin(ModelAdmin):
    list_display = ("id_number", "email", "bank", "country", "created_at")
    list_filter = ("country", "bank", "created_at")
    search_fields = ("id_number", "email")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at",)
    actions = ["export_csv"]

    @action(description=_("Export selected to CSV"))
    def export_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="registrations.csv"'
        writer = csv.writer(response)
        writer.writerow(["country", "bank", "id_number", "email", "registered_at"])
        for r in queryset.select_related("country", "bank"):
            writer.writerow([r.country.code, r.bank.name, r.id_number, r.email, r.created_at.isoformat()])
        return response
