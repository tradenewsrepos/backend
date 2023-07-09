from django.test import TestCase, RequestFactory, SimpleTestCase
from django.urls import reverse

from rest_framework import status

from ..models import (

    TradeEvent,

)
from newsfeedner.views.views_main import (
    EventList,

)


# class MainPageTestCases(TestCase):
#     def setUp(self) -> None:
#         self.main_page_url = reverse('main_page')
#         self.feed = Feed.objects.create(
#             id=5,
#             name='test_name',  # Название источника новости
#             url='test_url',
#             last_fetched_at=(datetime.datetime.today() - datetime.timedelta(hours=2)),
#         )
#         self.trade_article = TradeArticle.objects.create(
#             feed_id=5,
#             title='test_title',  # Заголовок новости
#             published_parsed=datetime.datetime.strptime('2021-06-16 10:21:28', '%Y-%m-%d %H:%M:%S'),
#             url='test_url',
#             text='test_text',
#         )
#
#     def test_get_request(self):
#         """
#         Check response status code in queryset
#         """
#         response = self.client.get(self.main_page_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertTemplateUsed(response, 'newsfeedner/base.html')
#
#
#     def test_mainpage_context(self):
#         request = RequestFactory().get(self.main_page_url)
#         view = MainPage()
#         view.setup(request)
#         view.object_list = view.get_queryset()
#         context = view.get_context_data()
#         queryset_value = context['page_obj'][0]
#         test_queryset = TradeArticle.objects.all()
#         self.assertIsInstance(context, dict)
#         self.assertEqual(len(context['page_obj']), 1)
#         self.assertEqual(str(queryset_value), 'test_name: test_title')
#         self.assertQuerysetEqual(context['object_list'], test_queryset)


# class EntityDetailTestCases(TestCase):
#     def setUp(self) -> None:
#         self.kwargs_1 = {'entity': 'test_entity_1'}
#         self.entity_detail_url_1 = reverse('entity_detail', kwargs=self.kwargs_1)
#
#         self.kwargs_2 = {'entity': 'test_entity_2'}
#         self.entity_detail_url_2 = reverse('entity_detail', kwargs=self.kwargs_2)
#
#         Entity.objects.create(
#             name='сущность_1',
#             name_translit='test_entity_1',
#         )
#         Entity.objects.create(
#             name='сущность_2',
#             name_translit='test_entity_2',
#         )
#
#     def test_get_request(self):
#         """
#         Check response status code in queryset
#         """
#
#         response = self.client.get(self.entity_detail_url_1)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertTemplateUsed(response, 'newsfeedner/entity_detail.html')
#
#     def test_entity_detail_context(self):
#         request_1 = RequestFactory().get(self.entity_detail_url_1)
#         view = EntityDetail()
#         view.setup(request_1)
#         view.kwargs = self.kwargs_1
#         view.object_list = view.get_queryset()
#         context = view.get_context_data()
#         self.assertIsInstance(context, dict)
#         self.assertEqual(context['entity_name'], 'сущность_1')
#
#         request_2 = RequestFactory().get(self.entity_detail_url_2)
#         view.setup(request_2)
#         view.kwargs = self.kwargs_2
#         view.object_list = view.get_queryset()
#         context = view.get_context_data()
#         self.assertIsInstance(context, dict)
#         self.assertEqual(context['entity_name'], 'сущность_2')
#
#
# class EntClassTestCases(TestCase):
#     def setUp(self) -> None:
#         self.kwargs_1 = {'ent_class': 'PER'}
#         self.kwargs_2 = {'ent_class': 'ORG'}
#         self.kwargs_3 = {'ent_class': 'LOC'}
#
#         self.ent_class_url_1 = reverse('ent_class', kwargs=self.kwargs_1)
#         self.ent_class_url_2 = reverse('ent_class', kwargs=self.kwargs_2)
#         self.ent_class_url_3 = reverse('ent_class', kwargs=self.kwargs_3)
#
#         Feed.objects.create(
#             last_fetched_at=(datetime.datetime.today() - datetime.timedelta(hours=2))
#         )
#
#         Entity.objects.create(
#             name='сущность_1',
#             name_translit='test_entity_1',
#             entity_class='PER',
#         )
#         Entity.objects.create(
#             name='сущность_2',
#             name_translit='test_entity_2',
#             entity_class='ORG',
#         )
#         Entity.objects.create(
#             name='сущность_3',
#             name_translit='test_entity_3',
#             entity_class='LOC',
#         )
#
#     def test_get_request(self):
#         """
#         Check response status code in queryset
#         """
#
#         response = self.client.get(self.ent_class_url_1)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertTemplateUsed(response, 'newsfeedner/ent_class.html')
#         response = self.client.get(self.ent_class_url_2)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         response = self.client.get(self.ent_class_url_3)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#     def test_entity_class_context(self):
#         request_1 = RequestFactory().get(self.ent_class_url_1)
#         view = EntityClassList()
#         view.setup(request_1)
#         view.kwargs = self.kwargs_1
#         view.object_list = view.get_queryset()
#         context = view.get_context_data()
#         self.assertIsInstance(context, dict)
#         self.assertEqual(context['ent_class_name'], 'персоны')
#         self.assertEqual(context['ent_class'], 'PER')
#
#         request_2 = RequestFactory().get(self.ent_class_url_2)
#         view = EntityClassList()
#         view.setup(request_2)
#         view.kwargs = self.kwargs_2
#         view.object_list = view.get_queryset()
#         context = view.get_context_data()
#         self.assertIsInstance(context, dict)
#         self.assertEqual(context['ent_class_name'], 'организации')
#         self.assertEqual(context['ent_class'], 'ORG')
#
#         request_3 = RequestFactory().get(self.ent_class_url_3)
#         view = EntityClassList()
#         view.setup(request_3)
#         view.kwargs = self.kwargs_3
#         view.object_list = view.get_queryset()
#         context = view.get_context_data()
#         self.assertIsInstance(context, dict)
#         self.assertEqual(context['ent_class_name'], 'локации')
#         self.assertEqual(context['ent_class'], 'LOC')
#
#
# class WordCloudsTestcases(TestCase):
#     def setUp(self) -> None:
#         self.wordcloud_url = reverse('wordclouds')
#
#     def test_get_request(self):
#         """
#         Check response status code in queryset
#         """
#
#         response = self.client.get(self.wordcloud_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertTemplateUsed(response, 'newsfeedner/wordclouds.html')
#
#     def test_wordclouds_context(self):
#         pass
#
#
# class AboutTestCases(TestCase):
#     def setUp(self) -> None:
#         self.about_url = reverse('about')
#
#     def test_get_request(self):
#         """
#         Check response status code in queryset
#         """
#
#         response = self.client.get(self.about_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertTemplateUsed(response, 'newsfeedner/about.html')
#
#     def test_about_context(self):
#         pass


class EventlistTestCases(TestCase):
    def setUp(self) -> None:
        self.events_url = reverse('events')

        self.trade_event_1 = TradeEvent.objects.create(
            id=1,
            classes=['Торговля'],
            itc_codes='test_itc_code_1',
            locations='test country 1',
            product='test product 1',
            title='Турция поставит ударные беспилотники Bayraktar еще в одну страну.',
            url='test_url_1',
            dates=['2021-11-19 07:29:00+00'],
            manual=0,
        )
        self.trade_event_2 = TradeEvent.objects.create(
            id=2,
            classes=['Инвестиции'],
            itc_codes='test_itc_code_2',
            locations='test country 2',
            product='test product 2',
            title='Новость про инвестиции',
            url='test_url_2',
            dates=['2021-10-19 07:29:00+00'],
            manual=0,
        )

    def test_get_request(self):
        """
        Check response status code in queryset and used template
        """
        response = self.client.get(self.events_url, secure=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, "newsfeedner/events.html")

    def test_events_str(self):
        self.assertEqual(str(self.trade_event_1),
                         "['Торговля']: Турция поставит ударные беспилотники Bayraktar еще в одну страну.")
        self.assertEqual(str(self.trade_event_2),
                         "['Инвестиции']: Новость про инвестиции")

    def test_events_context(self):
        request = RequestFactory().get(self.events_url)
        view = EventList()
        view.setup(request)

        view.object_list = view.get_queryset()
        context = view.get_context_data()

        self.assertIsInstance(context, dict)
        self.assertIn('countries', context)
        self.assertIn('country_products', context)

    def test_events_queryset(self):
        queryset = TradeEvent.objects.all()
        itc_codes = [e.itc_codes for e in queryset]
        classes = [e.classes for e in queryset]
        urls = [e.url for e in queryset]
        titles = [e.title for e in queryset]
        self.assertIn('test_itc_code_1', itc_codes)
        self.assertIn(['Торговля'], classes)
        self.assertIn('test_url_1', urls)
        self.assertIn('Турция поставит ударные беспилотники Bayraktar еще в одну страну.', titles)


class EventlistTestCasesNoDB(SimpleTestCase):
    def setUp(self) -> None:
        self.event_list = EventList()
        self.test_locations_1 = ['Азия', 'Африка', 'Белоруссия', 'Ближний Восток', 'Дели', 'Индия', 'Китай', 'ОАЭ',
                                 'Объединённые Арабские Эмираты', 'Турция']
        self.expected_result_1 = ['Азия', 'Африка', 'Дели', 'ЕАЭС', 'Объединённые Арабские Эмираты']

        self.test_locations_2 = ['Египет', 'Марокко', 'США', 'Зимбабве']
        self.expected_result_2 = ['Египет', 'Зимбабве', 'Марокко', 'США']

        self.test_locations_3 = ['Египет', 'Марокко', 'США', 'Зимбабве', 'Турция']
        self.expected_result_3 = ['Ближний Восток', 'Зимбабве', 'Северная Америка', 'Северная Африка']

    def test_group_countries_1(self):
        result = self.event_list.group_countries(self.test_locations_1)
        self.assertEqual(result, self.expected_result_1)

    def test_group_countries_2(self):
        result = self.event_list.group_countries(self.test_locations_2)
        self.assertEqual(result, self.expected_result_2)

    def test_group_countries_3(self):
        result = self.event_list.group_countries(self.test_locations_3)
        self.assertEqual(result, self.expected_result_3)
