from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager, PermissionsMixin
from django.db.models.signals import post_save
from django.utils import timezone
from datetime import date, timedelta
####(((CUSTOM-USER)))####
####((FRIENDS))####
class CustomUserManager(BaseUserManager):
    def create_user(self, username,email, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(username=username, **extra_fields)


        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username,email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username,email, password, **extra_fields)
    

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(unique=True, max_length=30)
    email = models.EmailField(unique=False)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    current_session_key = models.CharField(max_length=40, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    friends = models.ManyToManyField('self', symmetrical=True, blank=True)
    points = models.IntegerField(default=100)
    # New subscription-related fields
    subscription_status = models.CharField(
        max_length=20,
        default="Free",  # Default plan
        choices=[
            ("Free", "Free"),
            ("Star", "Star"),
        ],
    )
    subscription_expiry = models.DateField(null=True, blank=True)  # Expiry date for subscriptions
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    def __str__(self):
        return self.username
    
    def has_perm(self, perm, obj=None):
        return super().has_perm(perm, obj)

    def has_module_perms(self, app_label):
        return super().has_module_perms(app_label)

    # Utility method to update subscription details
    def update_subscription(self, plan_type):
        """
        Update the subscription status and expiry date based on the selected plan.
        """
        today = date.today()
        if plan_type == "Monthly":
            self.subscription_status = "Star"
            self.subscription_expiry = today + timedelta(days=30)
        elif plan_type == "Quarterly":
            self.subscription_status = "Star"
            self.subscription_expiry = today + timedelta(days=90)
        elif plan_type == "Yearly":
            self.subscription_status = "Star"
            self.subscription_expiry = today + timedelta(days=365)
        else:
            self.subscription_status = "Free"
            self.subscription_expiry = None
        self.save()

    # Utility method to check if the subscription is active
    def is_subscription_active(self):
        """
        Check if the subscription is still valid.
        """
        if self.subscription_expiry:
            return date.today() <= self.subscription_expiry
        return False
    
    def get_points_history(self):
        points=self.request.points()
        return [points]
    

class EmailVerification(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='email_verification')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_expired(self):
        # OTP is valid for 10 minutes
        return (timezone.now() - self.created_at).seconds > 600

    def __str__(self):
        return f"{self.user.email} - OTP: {self.otp}"
class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    friends = models.ManyToManyField('self', blank=True, symmetrical=True)

    def __str__(self):
        return self.user.username


class FriendRequest(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Accepted", "Accepted"),
        ("Rejected", "Rejected"),
    ]
    
    from_user = models.ForeignKey(CustomUser, related_name="sent_requests", on_delete=models.CASCADE)
    to_user = models.ForeignKey(CustomUser, related_name="received_requests", on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")  # Added status field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.from_user} to {self.to_user} ({self.status})"
