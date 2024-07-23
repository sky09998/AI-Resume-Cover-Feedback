from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Order(models.Model):
    name = models.CharField( max_length=100)
    card_number = models.CharField(max_length=16)
    expiry_month = models.CharField( max_length=2)
    expiry_year = models.CharField( max_length=4)
    
    def __str__(self):
                return self.name
    
class Document(models.Model):
    uploaded_file = models.FileField(upload_to='documents/')
    feedback = models.TextField(blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.uploaded_file.name} uploaded on {self.upload_date}"

class APIRequestLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    request_type = models.CharField(max_length=100)  # Could be 'resume' or 'cover letter' etc.

    def __str__(self):
        return f"{self.user.username} made a {self.request_type} request at {self.timestamp}"
    
class UserActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    details = models.TextField()

    def __str__(self):
        return f"{self.user.username} {self.activity_type} on {self.timestamp}"

    class Meta:
        verbose_name = 'User Activity Log'
        verbose_name_plural = 'User Activity Logs'

class UserM(models.Model):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=70, default="")
    phone = models.CharField(max_length=70, default="")

    def __str__(self):
        return self.first_name

class UserMAdmin(models.Model):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=70, default="")
    phone = models.CharField(max_length=70, default="")

    def __str__(self):
        return self.first_name

class Contact(models.Model):
    c_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=70, default="")
    msg = models.CharField(max_length=100)

    def __str__(self):
        return self.name