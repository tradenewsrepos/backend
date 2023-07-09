import pickle
from datetime import datetime

import numpy as np
from rest_framework import serializers

from newsfeedner.models import (
    TradeEvent,
    TradeEventRelevant,
    TradeEventForApproval,
    TradeNewsEmbeddings,
)
from newsfeedner.utils.trade_utils import (
    relations,
    smtk_product_all,
    countries_and_regions,
)


class EventSerializerWrite(serializers.ModelSerializer):
    id = serializers.UUIDField()
    classes = serializers.CharField()
    itc_codes = serializers.CharField()
    locations = serializers.CharField()
    product = serializers.CharField()
    title = serializers.CharField()
    url = serializers.CharField()
    dates = serializers.CharField()
    article_ids = serializers.CharField()

    class Meta:
        model = TradeEvent
        fields = "__all__"

class ItemsClasseSerializer(serializers.Serializer):
    relaton:  serializers.CharField()


class EventSerializerRead(serializers.ModelSerializer):
    classes = serializers.ListField()
    itc_codes = serializers.CharField()
    locations = serializers.CharField()
    product = serializers.CharField()
    title = serializers.CharField()
    url = serializers.CharField()
    dates = serializers.CharField()
    article_ids = serializers.ListField(child=serializers.CharField())

    def get_fields(self):
        """make all fields Read Only without specifying them explicitely
        https://stackoverflow.com/questions/57475808
        Returns:
            [type]: [description]
        """
        fields = super().get_fields()
        for field in fields.values():
            field.read_only = True
        return fields

    class Meta:
        model = TradeEvent
        fields = "__all__"


class EventSerializerWrite(serializers.ModelSerializer):
    id = serializers.UUIDField()
    classes = serializers.CharField()
    itc_codes = serializers.CharField()
    locations = serializers.CharField()
    product = serializers.CharField()
    title = serializers.CharField()
    url = serializers.CharField()
    dates = serializers.CharField()
    article_ids = serializers.CharField()

    class Meta:
        model = TradeEvent
        fields = "__all__"


class EventApprovalSerializerRead(serializers.ModelSerializer):
    id = serializers.UUIDField()
    classes = serializers.ListField()
    itc_codes = serializers.CharField()
    locations = serializers.CharField()
    title = serializers.CharField()
    url = serializers.CharField()
    dates = serializers.CharField()
    product = serializers.CharField()
    article_ids = serializers.ListField(child=serializers.CharField())
    user_checked = serializers.CharField()
    date_checked = serializers.DateTimeField()

    def get_fields(self):
        """make all fields Read Only without specifying them explicitely
        https://stackoverflow.com/questions/57475808
        Returns:
            [type]: [description]
        """
        fields = super().get_fields()
        for field in fields.values():
            field.read_only = True
        return fields

    class Meta:
        model = TradeEventForApproval
        fields = "__all__"


class EventApprovalSerializerWrite(serializers.ModelSerializer):
    id = serializers.UUIDField()
    classes = serializers.CharField()
    itc_codes = serializers.CharField()
    locations = serializers.CharField()
    title = serializers.CharField()
    url = serializers.CharField()
    dates = serializers.CharField()
    article_ids = serializers.CharField()
    product = serializers.CharField()
    user_checked = serializers.CharField()
    date_checked = serializers.DateTimeField()

    def check_classes(self, classes):
        print("validate_classes", classes)
        print("validate_classes", type(classes))

        classes = classes.split("; ")
        for cl in classes:
            if cl not in relations:
                raise serializers.ValidationError({
                    "classes":
                    f"'{cl}' class is wrong. Values should be {relations}"
                })

    def check_itc_codes(self, itc_codes):
        itc_codes = itc_codes.split(";; ")
        for code in itc_codes:
            if code not in smtk_product_all:
                raise serializers.ValidationError({
                    "itc_codes":
                    f"'{code}' code is wrong. Check if it is written correctly"
                })

    def check_article_ids(self, article_ids):
        article_ids = article_ids.split(",")
        for article_id in article_ids:
            if not article_id.isdigit():
                raise serializers.ValidationError({
                    "article_ids":
                    f"'{article_id}' is wrong. Article ids should be integer numbers"
                })

    def check_dates(self, dates):
        dates = dates.split(",")
        for d in dates:
            try:
                d = datetime.strptime(d, "%Y-%m-%d")
            except ValueError:
                raise serializers.ValidationError({
                    "dates":
                    f"'{d}' date format is wrong. Date should be in format YYYY-MM-DD"
                })

    def check_locations(self, locations: str):
        print(locations)
        locations = locations.split(", ")
        for loc in locations:
            if "Страны" in loc and "Персид" not in loc:
                loc = loc.replace("Разные ", "")
            if loc not in countries_and_regions:
                raise serializers.ValidationError({
                    "locations":
                    f" Location name '{loc}' is wrong. Check if it exists"
                })

    def validate(self, data):
        """
        Validates user data.
        """
        classes = data.get("classes", None)
        itc_codes = data.get("itc_codes", None)
        locations = data.get("locations", None)
        title = data.get("title", None)
        url = data.get("url", None)
        dates = data.get("dates", None)
        article_ids = data.get("article_ids", None)
        product = data.get("product", None)
        user_checked = data.get("user_checked", None)
        date_checked = data.get("date_checked", None)

        self.check_classes(classes)
        self.check_itc_codes(itc_codes)
        self.check_locations(locations)
        self.check_dates(dates)
        self.check_article_ids(article_ids)

        data_output = {
            "id": data["id"],
            "classes": classes.split("; "),
            "itc_codes": itc_codes,
            "locations": locations,
            "title": title,
            "url": url,
            "dates": dates,
            "article_ids": article_ids.split(","),
            "product": product,
            "user_checked": user_checked,
            "date_checked": date_checked,
        }
        return data_output

    class Meta:
        model = TradeEventForApproval
        exclude = ("status", )


class EventApprovalSerializerWriteStatus(serializers.ModelSerializer):
    status = serializers.CharField()

    class Meta:
        model = TradeEventForApproval
        fields = ("status", )


class EventRelevantSerializerWrite(serializers.ModelSerializer):
    id = serializers.UUIDField()
    classes = serializers.CharField()
    itc_codes = serializers.CharField()
    locations = serializers.CharField()
    title = serializers.CharField()
    url = serializers.CharField()
    dates = serializers.CharField()
    article_ids = serializers.CharField()
    product = serializers.CharField()
    user_checked = serializers.CharField()
    date_checked = serializers.DateTimeField()
    user_approved = serializers.CharField()
    date_approved = serializers.DateTimeField()

    def check_classes(self, classes):
        classes = classes.split("; ")
        for cl in classes:
            if cl not in relations:
                raise serializers.ValidationError({
                    "classes":
                    f"'{cl}' class is wrong. Values should be {relations}"
                })

    def check_itc_codes(self, itc_codes):
        itc_codes = itc_codes.split(";; ")
        for code in itc_codes:
            if code not in smtk_product_all:
                raise serializers.ValidationError({
                    "itc_codes":
                    f"'{code}' code is wrong. Check if it is written correctly"
                })

    def check_article_ids(self, article_ids):
        article_ids = article_ids.split(",")
        for article_id in article_ids:
            if not article_id.isdigit():
                raise serializers.ValidationError({
                    "article_ids":
                    f"'{article_id}' is wrong. Article ids should be integer numbers"
                })

    def check_dates(self, dates):
        dates = dates.split(",")
        for d in dates:
            try:
                d = datetime.strptime(d, "%Y-%m-%d")
            except ValueError:
                raise serializers.ValidationError({
                    "dates":
                    f"'{d}' date format is wrong. Date should be in format YYYY-MM-DD"
                })

    def check_locations(self, locations: str):
        locations = locations.split(", ")
        for loc in locations:
            if "Страны" in loc and "Персид" not in loc:
                loc = loc.replace("Разные ", "")
            if loc not in countries_and_regions:
                raise serializers.ValidationError({
                    "locations":
                    f" Location name '{loc}' is wrong. Check if it exists"
                })

    def validate(self, data):
        """
        Validates user data.
        """
        classes = data.get("classes", None)
        itc_codes = data.get("itc_codes", None)
        locations = data.get("locations", None)
        title = data.get("title", None)
        url = data.get("url", None)
        dates = data.get("dates", None)
        article_ids = data.get("article_ids", None)
        product = data.get("product", None)
        user_checked = data.get("user_checked", None)
        date_checked = data.get("date_checked", None)
        user_approved = data.get("user_approved", None)
        date_approved = data.get("date_approved", None)

        self.check_classes(classes)
        self.check_itc_codes(itc_codes)
        self.check_locations(locations)
        self.check_dates(dates)
        # Добавлено 17.02.2023
        if article_ids == '' or article_ids == '0':
            pass
        else:
            self.check_article_ids(article_ids)

        data_output = {
            "id": data["id"],
            "classes": classes.split("; "),
            "itc_codes": itc_codes,
            "locations": locations,
            "title": title,
            "url": url,
            "dates": dates,
            "article_ids": article_ids.split(","),
            "product": product,
            "user_checked": user_checked,
            "date_checked": date_checked,
            "user_approved": user_approved,
            "date_approved": date_approved,
        }
        return data_output

    class Meta:
        model = TradeEventRelevant
        exclude = ("to_delete", )


class EventRelevantSerializerRead(serializers.ModelSerializer):
    id = serializers.UUIDField()
    classes = serializers.ListField()
    itc_codes = serializers.CharField()
    locations = serializers.CharField()
    title = serializers.CharField()
    url = serializers.CharField()
    dates = serializers.CharField()
    article_ids = serializers.ListField(child=serializers.CharField())
    product = serializers.CharField()
    user_checked = serializers.CharField()
    date_checked = serializers.DateTimeField()
    user_approved = serializers.CharField()
    date_approved = serializers.DateTimeField()

    def get_fields(self):
        """make all fields Read Only without specifying them explicitely
        https://stackoverflow.com/questions/57475808
        Returns:
            [type]: [description]
        """
        fields = super().get_fields()
        for field in fields.values():
            field.read_only = True
        return fields

    class Meta:
        model = TradeEventRelevant
        exclude = ("to_delete", )


class BinaryVectorSerializer:

    def __init__(self, vector: np.array):
        self.vector = vector


class BinaryVectorField(serializers.Field):
    """
    Byte representation of vector are serialized into numpy array
    """

    def to_internal_value(self, value: list) -> bytes:
        value = np.array(value).astype(np.float16)
        value = pickle.dumps(value)

        return BinaryVectorSerializer(value)

    def to_representation(self, data: bytes) -> list:
        vector = pickle.loads(data)
        return vector


class EmbeddingSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    embedding = BinaryVectorField()
    article_id = serializers.CharField()
    model = serializers.CharField()
    date_added = serializers.DateTimeField()

    def to_internal_value(self, data):
        """
        Метод переписан для того, чтобы возвращать в Response читабельный формат,
        а не байты, которые записываются в базу
        """
        value = data.get("embedding")
        value = np.array(value).astype(np.float16)
        value = pickle.dumps(value)
        data["embedding"] = value
        return data

    def validate(self, data):
        """
        Validates user data.
        """
        uuid = data.get("id", None)

        if not uuid:
            raise serializers.ValidationError(
                {"id": "An duplicated_id is required"})
        return data

    def create(self, validated_data):
        obj, created = TradeNewsEmbeddings.objects.update_or_create(
            id=validated_data["id"],
            defaults={
                "embedding": validated_data["embedding"],
                "article_id": validated_data["article_id"],
                "model": validated_data["model"],
                "date_added": validated_data["date_added"],
            },
        )
        return obj
