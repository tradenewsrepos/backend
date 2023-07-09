from rest_framework import serializers
from datetime import datetime
from newsfeedner.models import (
    TradeNewsDuplicated,
)


class DuplicatedSerializer(serializers.Serializer):
    id_1 = serializers.UUIDField()
    title_1 = serializers.CharField()
    article_ids_1 = serializers.CharField()
    id_2 = serializers.UUIDField()
    title_2 = serializers.CharField()
    date_added = serializers.DateTimeField()

    def validate(self, data):
        """
        Validates user data.
        """
        id_1 = data.get("id_1")
        id_2 = data.get("id_2")
        title_1 = data.get("title_1")
        title_2 = data.get("title_2")
        date = data.get("date_added")

        if not id_1 or not id_2:
            raise serializers.ValidationError({"id": "Id is required"})
        if id_1 == id_2:
            raise serializers.ValidationError("uuid_1 and uuid_2 should be different")
        if not title_1 or not title_2:
            raise serializers.ValidationError("title_1 and title_2 are different")
        try:
            date = datetime.strftime(date, "%Y-%m-%d")
        except ValueError:
            raise serializers.ValidationError(
                {
                    "dates": f"'{date}' date format is wrong. Date should be in format YYYY-MM-DD"
                }
            )
        return data

    def create(self, validated_data):
        return TradeNewsDuplicated.objects.create(**validated_data)

    class Meta:
        model = TradeNewsDuplicated
        fields = "__all__"


class TextSerializer(serializers.Serializer):
    text_id = serializers.CharField()
    text = serializers.CharField()
