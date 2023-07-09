import uuid

from datetime import datetime, timedelta
from time import timezone

import jwt
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone as django_timezone

from .managers import CustomUserManager

URL_MAX_LENGTH = 2048  # https://stackoverflow.com/a/417184


class UserRoles(models.Model):
    # adding roles for users
    role = models.CharField(max_length=30, blank=False, null=False)

    def __str__(self):
        return self.role


class CustomUser(AbstractUser):
    # role choicefield will be automtically populated by values from DB table userroles
    role = models.ForeignKey(UserRoles,
                             null=True,
                             blank=True,
                             on_delete=models.CASCADE)
    objects = CustomUserManager()

    def __str__(self):
        return self.username

    def get_username(self):
        return self.username

    @property
    def token(self):
        """
        Позволяет нам получить токен пользователя, вызвав `user.token` вместо
        `user.generate_jwt_token().

        Декоратор `@property` выше делает это возможным.
        `token` называется «динамическим свойством ».
        """
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        """
        Создает веб-токен JSON, в котором хранится идентификатор
        этого пользователя и срок его действия
        составляет 60 дней в будущем.
        """
        dt = datetime.now() + timedelta(days=60)

        token = jwt.encode(
            {
                "id": self.pk,
                "exp": int(dt.strftime("%s"))
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )

        return token


class ExcludedIDs(models.Model):
    excluded_id = models.IntegerField(null=False, primary_key=True)


class ApprovedIDs(models.Model):
    approved_id = models.IntegerField(null=False, primary_key=True)


class CheckedIDs(models.Model):
    checked_id = models.IntegerField(null=False, primary_key=True)


class DuplicatedIDs(models.Model):
    duplicated_id = models.IntegerField(null=False, primary_key=True)


class TradeEventAbstract(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    classes = ArrayField(models.TextField())
    itc_codes = models.TextField(blank=True, null=False)
    locations = models.TextField(blank=True, null=False)
    product = models.TextField(blank=True, null=False)
    title = models.TextField(blank=True, null=False)
    url = models.TextField(blank=True, null=False)
    dates = models.TextField()
    article_ids = ArrayField(models.TextField())

    class Meta:
        abstract = True


class TradeEvent(TradeEventAbstract):
    status = models.TextField(null=False, default="not_seen")

    class Meta:
        managed = False
        db_table = "trade_news_events"
        ordering = ("-dates", )

    def __str__(self):
        return "{}: {}".format(self.classes, self.title)


class TradeEventForApproval(TradeEventAbstract):
    status = models.TextField(null=False, default="checked")
    user_checked = models.TextField(blank=True, null=False)
    date_checked = models.DateTimeField()

    class Meta:
        managed = True
        db_table = "trade_news_for_approval"
        ordering = ("-dates", )
        constraints = [
            models.UniqueConstraint(
                fields=("classes", "itc_codes", "locations", "title"),
                name="unique_approval_news",
            )
        ]


class TradeEventRelevant(TradeEventAbstract):
    user_checked = models.TextField(blank=True, null=False)
    user_approved = models.TextField(blank=True, null=False)
    date_checked = models.DateTimeField()
    date_approved = models.DateTimeField()
    to_delete = models.IntegerField(default=0)

    class Meta:
        managed = True
        db_table = "trade_news_relevant"
        ordering = ("-dates", )
        constraints = [
            models.UniqueConstraint(
                fields=("classes", "itc_codes", "locations", "title"),
                name="unique_relevant_news",
            )
        ]

    def __str__(self):
        return "{}: {}".format(self.classes, self.title, self.article_ids)


class TradeEditStatus(models.Model):
    id = models.UUIDField(null=False, primary_key=True)
    user = models.TextField(null=False)

    class Meta:
        managed = True
        db_table = "trade_news_edit_status"


class TradeNewsEmbeddings(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    embedding = models.BinaryField(null=False)
    article_id = models.TextField(null=True)
    model = models.TextField(null=False)
    # date_added = models.DateTimeField(default=datetime.today())
    date_added = models.DateTimeField(default=django_timezone.now)

    class Meta:
        managed = False
        db_table = "trade_news_embeddings"


class TradeNewsDuplicated(models.Model):
    pair_id = models.AutoField(primary_key=True)
    id_1 = models.UUIDField(editable=False, default=uuid.uuid4)
    title_1 = models.TextField(null=False)
    article_ids_1 = models.TextField(null=False)
    id_2 = models.UUIDField(editable=False, default=uuid.uuid4)
    title_2 = models.TextField(null=False)
    # date_added = models.DateTimeField(default=datetime.today())
    date_added = models.DateTimeField(default=django_timezone.now)

    class Meta:
        managed = True
        db_table = "trade_news_duplicates"
        constraints = [
            models.UniqueConstraint(
                fields=("id_1", "id_2"),
                name="unique_duplicated_pairs",
            )
        ]
