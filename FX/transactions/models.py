from django.db import models
import uuid
from django.core.exceptions import ValidationError
from .constants import SUPPORTED_CURRENCIES
from django.contrib.auth.models import User  # Django's built-in User model
from django.db import models

def validate_positive(value):
    if value <= 0:
        raise ValidationError('Amount must be positive.')

def validate_currency(value):
    if value not in SUPPORTED_CURRENCIES:
        raise ValidationError(f"{value} is not a valid currency. Supported currencies: {', '.join(SUPPORTED_CURRENCIES)}")

class FXTransaction(models.Model):
    identifier = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    customer_id = models.CharField(max_length=100)
    input_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[validate_positive])
    input_currency = models.CharField(max_length=10, validators=[validate_currency])
    output_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[validate_positive])
    output_currency = models.CharField(max_length=10, validators=[validate_currency])
    date_of_transaction = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.identifier} - {self.customer_id}"
    

class CurrencyPair(models.Model):
    input_currency = models.CharField(max_length=3)  # e.g., USD
    output_currency = models.CharField(max_length=3)  # e.g., KES

    def __str__(self):
        return f"{self.input_currency} to {self.output_currency}"

class UserCurrencyPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="currency_preferences")
    preferred_pairs = models.ManyToManyField(CurrencyPair)  # Multiple currency pairs
    decimal_places = models.PositiveIntegerField(default=2)  # One global preference for all pairs

    def __str__(self):
        return f"{self.user.username}'s preferences"

