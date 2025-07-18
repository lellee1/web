from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
class Widget(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='widgets/icons/', blank=True, null=True)
    link = models.URLField()
    order = models.PositiveIntegerField(default=0)
    open_in_new_tab = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title
    
class Service(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField()
    icon = models.ImageField(upload_to='services/icons/')
    is_active = models.BooleanField(default=True)
    
User = get_user_model()

class Thread(models.Model):
    title = models.CharField(max_length=200)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Post(models.Model):
    thread = models.ForeignKey(Thread, related_name='posts', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Attachment(models.Model):
    post = models.ForeignKey(Post, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='forum/attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
class Folder(models.Model):
    name       = models.CharField(max_length=100)
    parent     = models.ForeignKey('self', null=True, blank=True,
    related_name='children', on_delete=models.CASCADE)
    order      = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True, blank=True,
        help_text='User who created this folder (optional)'
    )
    class Meta:
        ordering = ['parent__id', 'order', 'name']
    def __str__(self):
        return self.name

class Note(models.Model):
    folder     = models.ForeignKey(Folder, related_name='notes', on_delete=models.CASCADE)
    title      = models.CharField(max_length=200)
    content    = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True, blank=True,
        help_text='User who created this note (optional)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['title']
    def __str__(self):
        return self.title