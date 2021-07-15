from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import date
from django.utils import timezone
from django.urls import reverse

# Profile table containing information user table does not have such as image, student number, and grade level
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    student_no = models.CharField("Student Number", max_length=6, blank=True)
    choices = (
        ('9th', '9th grade'),
        ('10th', '10th grade'),
        ('11th', '11th grade'),
        ('12th', '12th grade')
    )
    grade = models.CharField("Grade", choices=choices, max_length=4, blank=True)

    # Display user's username in Profile Admin
    def __str__(self):
        return f'{self.user.username} Profile'

    # Profile save
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Resize/Scale image to fit
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

# Post table has basic User information, hours, description, and service date shown on front end.
# There is also a field named date_posted, but not shown on the front end
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hours = models.IntegerField("Hours", validators=[MaxValueValidator(999), MinValueValidator(1)])
    desc = models.CharField("Description", max_length=200)
    service_date = models.DateField("Service Date", default=date.today)
    date_posted = models.DateTimeField(default=timezone.now)


    # Redirect to MyHours page after new post
    def get_absolute_url(self):
        return reverse('post-my')

# Category table keeping track of all CSA categories such as Community, Service, Achievement and their
# corresponding hour total.
class Category(models.Model):
    category_total_hours = models.IntegerField(validators=[MaxValueValidator(999), MinValueValidator(1)])
    category_text = models.CharField(max_length=20)

    # When maintaining categories in admin,
    # categories list shows category text, not the object ids
    def __str__(self):
        return self.category_text