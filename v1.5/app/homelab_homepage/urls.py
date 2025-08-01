from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView, TemplateView
from django.conf import settings
from django.conf.urls.static import static
from dashboard.admin import admin_site

urlpatterns = [
    # Redirect root URL to dashboard home (now public)
    path('', RedirectView.as_view(pattern_name='dashboard_home', permanent=False)),
    path('admin/', admin_site.urls),
    # Built-in auth views for login/logout
    path('accounts/', include('django.contrib.auth.urls')),
    # Main dashboard routes
    path('dashboard/', include('dashboard.urls')),
    # Simple note-taking page (if needed directly)
    path('note/', TemplateView.as_view(template_name='dashboard/notetaking.html'), name='notetaking'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)