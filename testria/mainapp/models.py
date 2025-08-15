from django.contrib.auth import get_user_model
from django.db import models


class Folder(models.Model):
    name=models.CharField(max_length=100)
    description=models.TextField(null=True, blank=True)
    time_create=models.DateTimeField(auto_now_add=True)
    time_update=models.DateTimeField(auto_now=True)

    author=models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, related_name='folders')


    class Meta:
        ordering=['-time_update']
        unique_together=['name', 'author']

    def __str__(self):
        return self.name

class Set(models.Model):
    SET_TYPE_CHOICES=[
        ('card_set', 'Card set'),
        ('test', 'Test'),
    ]

    name = models.CharField(max_length=100)
    type=models.CharField(max_length=8, choices=SET_TYPE_CHOICES)
    description = models.TextField(null=True, blank=True)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)

    author=models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)
    folder=models.ForeignKey('Folder', on_delete=models.CASCADE, null=True, related_name='sets')

class Block(models.Model):
    text=models.TextField(null=True, blank=True)
    image=models.ImageField(upload_to='set_photos/%Y/%m/%d', blank=True, null=True)



class Question(models.Model):
    content=models.ForeignKey('Block', on_delete=models.CASCADE)
    set=models.ForeignKey('Set', on_delete=models.CASCADE, related_name='questions')

class Answer(models.Model):
    question=models.ForeignKey('Question', on_delete=models.CASCADE, related_name='answers')
    content=models.ForeignKey('Block', on_delete=models.CASCADE)
    is_correct=models.BooleanField()

class TestSession(models.Model):
    user=models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    test_set=models.ForeignKey(Set, on_delete=models.CASCADE)
    is_completed=models.BooleanField(default=False)
    next_question_num=models.IntegerField(default=0)

class UserTestAnswer(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    test_set = models.ForeignKey(Set, on_delete=models.CASCADE)
    selected_answer=models.ForeignKey(Answer, on_delete=models.CASCADE)


