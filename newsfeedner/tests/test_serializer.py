from django.test import TestCase

from ..models import TradeEvent

#
#
#
# class EventSerializerTestCase(TestCase):
#     def setUp(self) -> None:
#         self.trade_event_1 = TradeEvent.objects.create(
#             id=1,
#             classes=["Торговля"],
#             itc_codes="test_itc_code_1",
#             locations="test country 1",
#             product="test product 1",
#             title="Турция поставит ударные беспилотники Bayraktar еще в одну страну.",
#             url="test_url_1",
#             dates=["2021-11-19 07:29:00+00"],
#             manual=0,
#             article_ids=[0, 1],
#         )
#         self.trade_event_2 = TradeEvent.objects.create(
#             id=2,
#             classes=["Инвестиции"],
#             itc_codes="test_itc_code_2",
#             locations="test country 2",
#             product="test product 2",
#             title="Новость про инвестиции",
#             url="test_url_2",
#             dates=["2021-10-19 07:29:00+00"],
#             manual=0,
#             article_ids=[2],
#         )
#
#     def test_ok(self):
#         data = EventSerializer(
#             [self.trade_event_1, self.trade_event_2], many=True
#         ).data
#         print(data)
#         expected_data = [
#             {
#                 "id": self.trade_event_1.id,
#                 "classes": "['Торговля']",
#                 "itc_codes": "test_itc_code_1",
#                 "locations": "test country 1",
#                 "product": "test product 1",
#                 "title": "Турция поставит ударные беспилотники Bayraktar еще в одну страну.",
#                 "url": "test_url_1",
#                 "dates": "['2021-11-19 07:29:00+00']",
#                 "manual": 0,
#                 "article_ids": [0, 1],
#             },
#             {
#                 "id": self.trade_event_2.id,
#                 "classes": "['Инвестиции']",
#                 "itc_codes": "test_itc_code_2",
#                 "locations": "test country 2",
#                 "product": "test product 2",
#                 "title": "Новость про инвестиции",
#                 "url": "test_url_2",
#                 "dates": "['2021-10-19 07:29:00+00']",
#                 "manual": 0,
#                 "article_ids": [2],
#             },
#         ]
#         self.assertEqual(expected_data, data)
