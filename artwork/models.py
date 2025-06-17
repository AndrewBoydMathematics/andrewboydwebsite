from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class SiteSettings(models.Model):
    show_models_page = models.BooleanField(default=True, help_text="Show the Models page in the navigation bar")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    @classmethod
    def get_settings(cls):
        settings, created = cls.objects.get_or_create(pk=1)
        return settings

    def __str__(self):
        return "Site Settings"

class Artwork(models.Model):
    STATUS_CHOICES = [
        ('FOR_SALE', 'For Sale'),
        ('SOLD', 'Sold'),
        ('NOT_AVAILABLE', 'Not Available'),
    ]

    MEDIUM_CHOICES = [
        ('GRAPHITE', 'Graphite'),
        ('OIL', 'Oil'),
    ]

    BACKING_CHOICES = [
        ('PAPER', 'Paper'),
        ('STRETCH_CANVAS', 'Stretch Canvas'),
        ('CANVAS_BOARD', 'Canvas Board'),
    ]

    CATEGORY_CHOICES = [
        ('PORTRAIT', 'Portrait'),
        ('FIGURE', 'Figure'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='artwork/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_AVAILABLE')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                              validators=[MinValueValidator(0)])
    medium = models.CharField(max_length=20, choices=MEDIUM_CHOICES)
    backing = models.CharField(max_length=20, choices=BACKING_CHOICES, default='PAPER')
    size = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class CommissionRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField()
    description = models.TextField()
    reference_images = models.ImageField(upload_to='commissions/references/', null=True, blank=True)
    size = models.CharField(max_length=100)
    medium = models.CharField(max_length=20, choices=Artwork.MEDIUM_CHOICES)
    category = models.CharField(max_length=20, choices=Artwork.CATEGORY_CHOICES)
    budget = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Commission Request from {self.name}"

class PayPalAccount(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True, help_text="A title to identify this PayPal account (e.g., 'Production', 'Sandbox')")
    email = models.EmailField(unique=True)
    client_id = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title', 'email']
        verbose_name = 'PayPal Account'
        verbose_name_plural = 'PayPal Accounts'

    def __str__(self):
        return f"{self.title or 'Untitled'} ({self.email})"

    @classmethod
    def get_active_account(cls):
        return cls.objects.filter(is_active=True).first()

class ModelApplication(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    modeling_type = models.CharField(max_length=20, choices=[
        ('voluntary', 'Voluntary'),
        ('paid', 'Paid')
    ])
    description = models.TextField()
    availability = models.TextField()
    additional_info = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ], default='pending')

    def __str__(self):
        return f"{self.name} - {self.modeling_type}"

class ModelImage(models.Model):
    application = models.ForeignKey(ModelApplication, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='model_applications/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.application.name}" 