from django.test import TestCase
from django.urls import reverse

from .models import Bank, Country, Registration


class RegistrationFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pa = Country.objects.create(code="pa", name="Panamá", language="es")
        cls.us = Country.objects.create(code="us", name="United States", language="en")
        cls.pa_bank = Bank.objects.create(country=cls.pa, name="Banco A")
        cls.us_bank = Bank.objects.create(country=cls.us, name="Bank A")

    def url(self, name, code="pa"):
        return reverse(f"registration:{name}", kwargs={"country_code": code})

    def test_root_lists_countries(self):
        r = self.client.get("/")
        self.assertContains(r, "Panamá")
        self.assertContains(r, self.url("register", "us"))

    def test_language_depends_on_country(self):
        self.assertContains(self.client.get(self.url("register", "pa")), "Confirmar registro")
        self.assertContains(self.client.get(self.url("register", "us")), "Confirm registration")

    def test_inactive_or_unknown_country_404(self):
        self.assertEqual(self.client.get(self.url("register", "zz")).status_code, 404)

    def test_successful_registration(self):
        r = self.client.post(self.url("register"), {"id_number": "8-123-456", "bank": self.pa_bank.pk})
        self.assertRedirects(r, self.url("success"), fetch_redirect_response=False)
        self.assertTrue(Registration.objects.filter(country=self.pa, id_number="8-123-456").exists())

    def test_invalid_id_characters_rejected(self):
        r = self.client.post(self.url("register"), {"id_number": "ab#c", "bank": self.pa_bank.pk})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Registration.objects.count(), 0)

    def test_bank_from_other_country_rejected(self):
        r = self.client.post(self.url("register"), {"id_number": "8-123-456", "bank": self.us_bank.pk})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Registration.objects.count(), 0)

    def test_duplicate_id_shows_duplicate_page(self):
        data = {"id_number": "8-123-456", "bank": self.pa_bank.pk}
        self.client.post(self.url("register"), data)
        r = self.client.post(self.url("register"), data)
        self.assertRedirects(r, self.url("duplicate"), fetch_redirect_response=False)
        page = self.client.get(self.url("duplicate"))
        self.assertContains(page, "¡Este ID ya fue registrado!")
        self.assertContains(page, "8-123-456")
        self.assertEqual(Registration.objects.count(), 1)

    def test_same_id_allowed_in_different_countries(self):
        Registration.objects.create(country=self.pa, bank=self.pa_bank, id_number="A12345")
        r = self.client.post(self.url("register", "us"), {"id_number": "A12345", "bank": self.us_bank.pk})
        self.assertRedirects(r, self.url("success", "us"), fetch_redirect_response=False)

    def test_email_is_optional_and_not_unique(self):
        base = {"bank": self.pa_bank.pk, "email": "same@example.com"}
        self.client.post(self.url("register"), {**base, "id_number": "8-111-111"})
        self.client.post(self.url("register"), {**base, "id_number": "8-222-222"})
        self.client.post(self.url("register"), {"bank": self.pa_bank.pk, "id_number": "8-333-333"})
        self.assertEqual(Registration.objects.count(), 3)
        self.assertEqual(Registration.objects.filter(email="same@example.com").count(), 2)

    def test_invalid_email_rejected(self):
        r = self.client.post(self.url("register"), {"id_number": "8-1-1", "bank": self.pa_bank.pk, "email": "nope"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Registration.objects.count(), 0)

    def test_no_change_country_link_on_register(self):
        self.assertNotContains(self.client.get(self.url("register")), "Cambiar de país")
