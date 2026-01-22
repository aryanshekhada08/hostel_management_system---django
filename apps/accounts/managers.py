from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):

    def create_user(self, email, full_name, role, password=None):
        if not email:
            raise ValueError("Email is required")

        if not role:
            raise ValueError("Role is required")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            full_name=full_name,
            role=role,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password):
        user = self.create_user(
            email=email,
            full_name=full_name,
            role='ADMIN',
            password=password
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
