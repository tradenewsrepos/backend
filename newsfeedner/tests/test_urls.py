from django.urls import resolve, reverse

from django.test import SimpleTestCase
from newsfeedner.views.views_main import EventList


class TestUrls(SimpleTestCase):
    def test_views_resolve(self):

        url_events = reverse("events")

        self.assertEquals(resolve(url_events).func.view_class, EventList)
