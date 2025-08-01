from django.contrib import admin
from .models import Widget, Service, Thread, Post, Attachment, Folder, Note, WidgetGroup
from django.contrib.admin import AdminSite
from django import forms

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'bg-gray-800 text-white p-2 rounded w-full',
                'rows': 5,
                'placeholder': 'Write your reply here…'
            }),
        }

@admin.register(Widget)
class WidgetAdmin(admin.ModelAdmin):
    list_display = ('title', 'link', 'order', 'open_in_new_tab')
    list_editable = ('order', 'open_in_new_tab')
    ordering = ('order',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    
class MyAdminSite(AdminSite):
    site_header = 'Homelab Dashboard Admin'
    site_title = 'Homelab Admin'
    index_title = 'Manage Homelab'

admin_site = MyAdminSite(name='myadmin')

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at')
    search_fields = ('title',)

class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('thread', 'author', 'created_at')
    inlines = [AttachmentInline]

class NoteInline(admin.TabularInline):
    model = Note; extra = 0

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('name','parent','order'); inlines=[NoteInline]

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title','folder','created_by','created_at')
    list_filter = ('folder',); search_fields=('title','content')

admin.site.register(WidgetGroup)