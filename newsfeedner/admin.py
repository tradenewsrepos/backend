from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from newsfeedner.models import CustomUser
from newsfeedner.models import TradeEventRelevant
from .forms import UserCreationForm, UserChangeForm


class CustomUserAdmin(UserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ("username", "is_superuser")
    list_filter = ("is_superuser",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "username",
                    "password",
                )
            },
        ),
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                )
            },
        ),
        ("Permissions", {"fields": ("is_superuser",)}),
        ("User role", {"fields": ("role",)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
            },
        ),
    )
    search_fields = ("username",)
    ordering = ("username",)
    filter_horizontal = ()


@admin.register(TradeEventRelevant)
class TradeEventRelevantAdmin(admin.ModelAdmin):
    pass


admin.site.register(CustomUser, CustomUserAdmin)
