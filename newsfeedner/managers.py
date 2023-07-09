from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Django требует, чтобы кастомные пользователи определяли свой собственный
    класс Manager. Унаследовавшись от BaseUserManager, мы получаем много того
    же самого кода, который Django использовал для создания User (для демонстрации).
    """

    def create_user(self, username, email, password=None, role=None):
        """Создает и возвращает пользователя с имэйлом, паролем, именем и ролью.."""
        if username is None:
            raise TypeError(_("Users must have a username."))

        if email is None:
            raise TypeError(_("Users must have an email address."))

        user = self.model(role, username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        """Создает и возввращет пользователя с привилегиями суперадмина."""
        if password is None:
            raise TypeError(_("Superusers must have a password."))

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user
