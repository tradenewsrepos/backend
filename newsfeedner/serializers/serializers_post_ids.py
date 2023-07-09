from rest_framework import serializers

from newsfeedner.models import (
    ExcludedIDs,
    ApprovedIDs,
    CheckedIDs,
    DuplicatedIDs,
    TradeEditStatus,
)


class AddToExceptionsSerializer(serializers.Serializer):
    excluded_id = serializers.CharField()

    def validate(self, data):
        """
        Validates user data.
        """
        excluded_id = data.get("excluded_id", None)
        if excluded_id is None:
            raise serializers.ValidationError(
                {"excluded_id": "An excluded_id is required"}
            )
        if not excluded_id.isdigit():
            raise serializers.ValidationError(
                {"excluded_id": "excluded_id must be an integer"}
            )
        return data

    def create(self, validated_data):
        obj, created = ExcludedIDs.objects.get_or_create(**validated_data)
        return obj


class ApprovedIDSerializer(serializers.Serializer):
    approved_id = serializers.CharField()

    def validate(self, data):
        """
        Validates user data.
        """
        approved_id = data.get("approved_id", None)
        if approved_id is None:
            raise serializers.ValidationError(
                {"approved_id": "An approved_id is required"}
            )
        if not approved_id.isdigit():
            raise serializers.ValidationError(
                {"approved_id": "approved_id must be an integer"}
            )
        return data

    def create(self, validated_data):
        obj, created = ApprovedIDs.objects.get_or_create(**validated_data)
        return obj


class CheckedIDSerializer(serializers.Serializer):
    checked_id = serializers.CharField()

    def validate(self, data):
        """
        Validates user data.
        """
        checked_id = data.get("checked_id", None)

        if checked_id is None:
            raise serializers.ValidationError(
                {"checked_id": "An checked_id is required"}
            )
        if not checked_id.isdigit():
            raise serializers.ValidationError(
                {"checked_id": "checked_id must be an integer"}
            )
        return data

    def create(self, validated_data):
        obj, created = CheckedIDs.objects.get_or_create(**validated_data)
        return obj


class DuplicatedIDSerializer(serializers.Serializer):
    duplicated_id = serializers.CharField()

    def validate(self, data):
        """
        Validates user data.
        """
        duplicated_id = data.get("duplicated_id", None)

        if duplicated_id is None:
            raise serializers.ValidationError(
                {"duplicated_id": "An duplicated_id is required"}
            )
        if not duplicated_id.isdigit():
            raise serializers.ValidationError(

                {"duplicated_id": "duplicated_id must be an integer"}
            )
        return data

    def create(self, validated_data):
        obj, created = DuplicatedIDs.objects.get_or_create(**validated_data)
        return obj


class EditStatusSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    user = serializers.CharField()

    def validate(self, data):
        """
        Validates user data.
        """
        id = data.get("id", None)
        user = data.get("user", None)

        if id is None:
            raise serializers.ValidationError({"id": "An id is required"})

        return {"id": id, "user": user}

    def create(self, validated_data):
        return TradeEditStatus.objects.create(**validated_data)


class EditStatusSerializerDelete(serializers.Serializer):
    id = serializers.UUIDField()

    def validate(self, data):
        """
        Validates user data.
        """
        id = data.get("id", None)

        if id is None:
            raise serializers.ValidationError({"id": "An id is required"})

        return {
            "id": id,
        }
