from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    HomeView,
    ForumListView,
    ForumDetailView,
    PostCreateView,
    notes_ui,
    notes_tree,
    note_content,
    create_folder,
    create_note,
    delete_node,
    rename_folder,
    rename_note,
    update_note,
    move_node,
    applications_view,
    thread_manage,  # <-- add this
    about_us_view,  # <-- add this
)

urlpatterns = [
    # Core pages
    path('', HomeView.as_view(), name='dashboard_home'),

    # Applications page
    path('applications/', applications_view, name='applications'),

    # Forum pages
    path('forum/', ForumListView.as_view(), name='forum_list'),
    path('forum/manage/', thread_manage, name='thread_manage'),
    path('forum/<int:pk>/', ForumDetailView.as_view(), name='forum_detail'),
    path('forum/<int:pk>/post/', PostCreateView.as_view(), name='forum_post'),

    # Note‑taking UI
    path('notes/', notes_ui, name='notes_ui'),

    # Note‑taking JSON APIs
    path('api/notes/tree/', notes_tree, name='notes_tree'),
    path('api/notes/create_folder/', create_folder, name='create_folder'),
    path('api/notes/create_note/', create_note, name='create_note'),
    path('api/notes/delete/', delete_node, name='delete_node'),
    path('api/notes/folder/<int:folder_id>/rename/', rename_folder, name='rename_folder'),
    path('api/notes/note/<int:note_id>/rename/', rename_note, name='rename_note'),
    path('api/notes/note/<int:note_id>/', note_content, name='note_content'),
    path('api/notes/note/<int:note_id>/update/', update_note, name='note_update'),
    path('api/notes/move/', move_node, name='move_node'),

    # About us page
    path('about/', about_us_view, name='about_us'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)