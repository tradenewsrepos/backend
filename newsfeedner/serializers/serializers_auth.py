from django.contrib.auth import authenticate
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """
    Authenticates an existing user.
    Email and password are required.
    Returns a JSON web token.
    """

    username = serializers.CharField(write_only=True)
    password = serializers.CharField(max_length=128, write_only=True)

    # Ignore these fields if they are included in the request.
    token = serializers.CharField(max_length=255, read_only=True)
    role = serializers.CharField(max_length=30, read_only=True)

    def validate(self, data):
        """
        Validates user data.
        """
        username = data.get("username", None)
        password = data.get("password", None)

        if username is None:
            raise serializers.ValidationError("An username is required to log in.")

        if password is None:
            raise serializers.ValidationError("A password is required to log in.")

        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError(
                "A user with this username and password was not found."
            )

        if not user.is_active:
            raise serializers.ValidationError("This user has been deactivated.")

        if not user.role:
            raise serializers.ValidationError("User role is not found.")

        return {
            "token": user.token,
            "role": user.role,
        }
