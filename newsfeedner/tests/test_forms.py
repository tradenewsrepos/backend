from django.test import TestCase
from ..forms import ContactForm


class TestEventsForm(TestCase):
    """
    Test if form /events.html contains relevant fields
    """

    def setUp(self) -> None:
        self.request_data = {
            "country": ["Алжир"],
            "product": ["05 - Овощи и фрукты"],
            "relation": ["Инвестиции"],
        }

    def test_empty_form(self):
        form = ContactForm()
        self.assertIn("country", form.fields)
        self.assertIn("product", form.fields)
        self.assertIn("relation", form.fields)

    def test_form_contains(self):
        response = self.client.get("/events/")
        self.assertContains(response, "country")
        self.assertContains(response, "product")
        self.assertContains(response, "relation")
