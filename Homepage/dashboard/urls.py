from django.urls import path
from .views import (
    HomeView,
    ApplicationsView,
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
)

urlpatterns = [
    # Core pages
    path('', HomeView.as_view(), name='dashboard_home'),
    path('applications/', ApplicationsView.as_view(), name='applications'),

    # Forum pages
    path('forum/', ForumListView.as_view(), name='forum_list'),
    path('forum/<int:pk>/', ForumDetailView.as_view(), name='forum_detail'),
    path('forum/<int:pk>/post/', PostCreateView.as_view(), name='forum_post'),

    # Note‑taking UI
    path('notetaking/', notes_ui, name='notes_ui'),

    # Note‑taking JSON APIs
    path('api/notes/tree/', notes_tree, name='notes_tree'),
    path('api/notes/create_folder/', create_folder, name='create_folder'),
    path('api/notes/create_note/', create_note, name='create_note'),
    path('api/notes/delete/', delete_node, name='delete_node'),
    path('api/notes/folder/<int:folder_id>/rename/', rename_folder, name='rename_folder'),
    path('api/notes/note/<int:note_id>/rename/', rename_note, name='rename_note'),
    path('api/notes/note/<int:note_id>/', note_content, name='note_content'),
    path('api/notes/note/<int:note_id>/update/', update_note, name='note_update'),
]