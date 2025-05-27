from django.db import models
from django.contrib import auth
import uuid

GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
)

class UserCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class User(models.Model):
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='O')
    notes = models.TextField(blank=True, null=True)
    category = models.ForeignKey(UserCategory, on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} {self.surname}"
    
class Card(models.Model):
    id = models.AutoField(primary_key=True)
    card_number = models.UUIDField(
         default = uuid.uuid4,
         editable = False)
    printed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    
STATUS_CHOICES = (
    ('active', 'Active'),
    ('suspended', 'Suspended'),
    ('lost', 'Lost'),
    ('stolen', 'Stolen'),
)
    
class UserCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card = models.OneToOneField(Card, on_delete=models.CASCADE)

    status = models.CharField(max_length=20, default='active', choices=STATUS_CHOICES)
    notes = models.TextField(blank=True, null=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(auth.models.User, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.user.name} {self.user.surname} - {self.card.card_number} "

class TransactionCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    card_id = models.ForeignKey(Card, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) # da togliere

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(TransactionCategory, on_delete=models.CASCADE, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(auth.models.User, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.card_id.card_number} - {self.amount} - {self.category.name if self.category else 'No Category'}"