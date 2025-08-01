import os
from django.db import models
from django.contrib.auth import get_user_model
from django import forms
from django.core.exceptions import ValidationError

def validate_document_file(file):
    """Validate that uploaded file is a PDF or Word document"""
    valid_extensions = ['.pdf', '.doc', '.docx']
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError('Only PDF and Word documents (.pdf, .doc, .docx) are allowed.')

# Create your models here.
class WidgetGroup(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Widget(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='widgets/icons/', blank=True, null=True)
    link = models.URLField()
    order = models.PositiveIntegerField(default=0)
    open_in_new_tab = models.BooleanField(default=True)
    group = models.ForeignKey(WidgetGroup, on_delete=models.SET_NULL, null=True, blank=True)

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
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    author_name = models.CharField(max_length=100, blank=True, help_text="Name for anonymous users")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_author_display(self):
        if self.created_by:
            return self.created_by.username
        return self.author_name or "Anonymous"

class Post(models.Model):
    thread = models.ForeignKey(Thread, related_name='posts', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    author_name = models.CharField(max_length=100, blank=True, help_text="Name for anonymous users")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def get_author_display(self):
        if self.author:
            return self.author.username
        return self.author_name or "Anonymous"

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

class Document(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="Brief description of the document")
    file = models.FileField(upload_to='documents/', validators=[validate_document_file], help_text="Upload PDF or Word documents only")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_visible = models.BooleanField(default=True, help_text="Whether this document is visible on the About Us page")
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.title
    
    def get_file_extension(self):
        return self.file.name.split('.')[-1].lower() if self.file else ''
    
    def is_pdf(self):
        return self.get_file_extension() == 'pdf'
    
    def is_word(self):
        return self.get_file_extension() in ['doc', 'docx']

class WidgetForm(forms.ModelForm):
    class Meta:
        model = Widget
        fields = ['title', 'description', 'icon', 'link', 'order', 'open_in_new_tab', 'group']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'description', 'file', 'is_visible']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
            'file': forms.FileInput(attrs={'accept': '.pdf,.doc,.docx'}),
        }