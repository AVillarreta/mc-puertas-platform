from django.core.management.base import BaseCommand

from registration.models import Bank, Country

DEMO = [
    {
        "code": "pa", "name": "Panamá", "language": "es",
        "banks": ["Banco A", "Banco B", "Banco C", "Banco D", "Otro banco"],
    },
    {
        "code": "co", "name": "Colombia", "language": "es",
        "banks": ["Banco A", "Banco B", "Otro banco"],
    },
    {
        "code": "us", "name": "United States", "language": "en",
        "banks": ["Bank A", "Bank B", "Bank C", "Other bank"],
    },
]


class Command(BaseCommand):
    help = "Crea paises y bancos de ejemplo (se puede correr varias veces)."

    def handle(self, *args, **options):
        for data in DEMO:
            banks = data.pop("banks")
            country, _ = Country.objects.update_or_create(code=data["code"], defaults=data)
            for position, name in enumerate(banks):
                Bank.objects.update_or_create(country=country, name=name, defaults={"position": position})
            data["banks"] = banks
        self.stdout.write(self.style.SUCCESS("Demo data ready."))
