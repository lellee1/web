from django.contrib import admin
from .models import Widget, Service, Thread, Post, Attachment, Folder, Note, WidgetGroup, Document
from django.contrib.admin import AdminSite
from django import forms
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.sessions.models import Session
from django.contrib.contenttypes.models import ContentType

class CustomAdminSite(AdminSite):
    site_header = 'Homelab Administration'
    site_title = 'Homelab Admin'
    index_title = 'Welcome to Homelab Administration'
    
    def has_permission(self, request):
        """
        Check if user has permission to access admin.
        User must be authenticated AND be staff/superuser.
        """
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False
        
        # Check if user is staff or superuser
        if not (request.user.is_staff or request.user.is_superuser):
            return False
            
        return True
    
    def admin_view(self, view, cacheable=False):
        """
        Override admin view to add custom permission checking
        """
        def inner(request, *args, **kwargs):
            if not self.has_permission(request):
                if request.user.is_authenticated:
                    # User is logged in but doesn't have admin access
                    return HttpResponseForbidden(
                        '''
                        <!DOCTYPE html>
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>Access Denied - Homelab</title>
                            <style>
                                body {
                                    margin: 0;
                                    padding: 0;
                                    min-height: 100vh;
                                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                }
                                .container {
                                    text-align: center;
                                    background: rgba(255, 255, 255, 0.1);
                                    backdrop-filter: blur(10px);
                                    border-radius: 20px;
                                    padding: 3rem 2rem;
                                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                                    border: 1px solid rgba(255, 255, 255, 0.2);
                                    max-width: 500px;
                                    width: 90%;
                                }
                                h1 {
                                    color: white;
                                    font-size: 2.5rem;
                                    margin-bottom: 1rem;
                                    font-weight: 300;
                                    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                                }
                                p {
                                    color: rgba(255, 255, 255, 0.9);
                                    font-size: 1.1rem;
                                    line-height: 1.6;
                                    margin-bottom: 1.5rem;
                                }
                                .buttons {
                                    display: flex;
                                    gap: 1rem;
                                    justify-content: center;
                                    flex-wrap: wrap;
                                    margin-top: 2rem;
                                }
                                a {
                                    display: inline-block;
                                    padding: 12px 24px;
                                    background: rgba(255, 255, 255, 0.2);
                                    color: white;
                                    text-decoration: none;
                                    border-radius: 25px;
                                    border: 1px solid rgba(255, 255, 255, 0.3);
                                    transition: all 0.3s ease;
                                    font-weight: 500;
                                }
                                a:hover {
                                    background: rgba(255, 255, 255, 0.3);
                                    transform: translateY(-2px);
                                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
                                }
                                .icon {
                                    font-size: 4rem;
                                    margin-bottom: 1rem;
                                    opacity: 0.8;
                                }
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <div class="icon">🔒</div>
                                <h1>Access Denied</h1>
                                <p>You must be a staff member to access the admin panel.</p>
                                <p>Please contact an administrator if you need access.</p>
                                <div class="buttons">
                                    <a href="/accounts/login/">Login</a>
                                    <a href="/">Go to Main Site</a>
                                </div>
                            </div>
                        </body>
                        </html>
                        '''
                    )
                else:
                    # User is not logged in, redirect to main login
                    return redirect('/accounts/login/?next=' + request.path)
            return view(request, *args, **kwargs)
        
        if not cacheable:
            inner = never_cache(inner)
        return inner

# Create custom admin site instance
admin_site = CustomAdminSite(name='custom_admin')

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

@admin.register(Widget, site=admin_site)
class WidgetAdmin(admin.ModelAdmin):
    list_display = ('title', 'link', 'order', 'open_in_new_tab')
    list_editable = ('order', 'open_in_new_tab')
    ordering = ('order',)

@admin.register(Service, site=admin_site)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)

@admin.register(Thread, site=admin_site)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_author_display', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'created_by__username', 'author_name')

class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1

@admin.register(Post, site=admin_site)
class PostAdmin(admin.ModelAdmin):
    list_display = ('thread', 'get_author_display', 'created_at')
    list_filter = ('created_at', 'thread')
    search_fields = ('content', 'author__username', 'author_name')
    inlines = [AttachmentInline]
    form = PostForm

@admin.register(Attachment, site=admin_site)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('post', 'file', 'uploaded_at')
    list_filter = ('uploaded_at',)

class NoteInline(admin.TabularInline):
    model = Note
    extra = 0

@admin.register(Folder, site=admin_site)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('name','parent','order')
    inlines = [NoteInline]

@admin.register(Note, site=admin_site)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title','folder','created_by','created_at')
    list_filter = ('folder',)
    search_fields = ('title','content')

@admin.register(Document, site=admin_site)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'uploaded_at', 'is_visible', 'get_file_extension')
    list_filter = ('is_visible', 'uploaded_at', 'uploaded_by')
    search_fields = ('title', 'description')
    readonly_fields = ('uploaded_at',)

admin_site.register(WidgetGroup)

# Register Django's built-in authentication models
admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)

# Register other useful Django models
@admin.register(Session, site=admin_site)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'expire_date')
    list_filter = ('expire_date',)
    readonly_fields = ('session_key', 'session_data', 'expire_date')

@admin.register(ContentType, site=admin_site)
class ContentTypeAdmin(admin.ModelAdmin):
    list_display = ('app_label', 'model')
    list_filter = ('app_label',)
    search_fields = ('app_label', 'model')