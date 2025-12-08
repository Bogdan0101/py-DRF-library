from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.utils.translation import gettext as _


class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(
        write_only=True,
        min_length=5,
        style={"input_type": "password"},
        label=_("Password"),
    )
    password2 = serializers.CharField(
        write_only=True,
        min_length=5,
        style={"input_type": "password"},
        label=_("Repeat password"),
    )

    class Meta:
        model = get_user_model()
        fields = ("id",
                  "email",
                  "first_name",
                  "last_name",
                  "password1",
                  "password2",
                  "is_staff",
                  )
        read_only_fields = ("is_staff",)

    def validate(self, attrs):
        if attrs["password1"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password_error": "The two password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password1", None)
        validated_data.pop("password2")
        return get_user_model().objects.create_user(
            password=password,
            **validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password1", None)
        validated_data.pop("password2")
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
