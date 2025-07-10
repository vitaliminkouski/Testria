from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    photo=models.ImageField(upload_to='users/%Y/%m/%d', blank=True, null=True)
    bio=models.TextField(max_length=500, blank=True, null=True)
    is_verified=models.BooleanField(default=False)
    following=models.ManyToManyField('self', symmetrical=False, blank=True, related_name='followers')

    def is_following(self, other_user):
        return self.following.filter(pk=other_user.pk).exists()

    def __str__(self):
        return self.username
