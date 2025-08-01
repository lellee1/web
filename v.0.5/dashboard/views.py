import json, requests, logging
from collections import defaultdict
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.forms import inlineformset_factory
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import Widget, WidgetGroup, Thread, Post, Attachment, Folder, Note, WidgetForm
from .admin import PostForm
from django import forms
from django.urls import reverse


# 1) Dashboard pages
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'

class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['title']

class ForumListView(LoginRequiredMixin, ListView):
    model = Thread
    template_name = 'dashboard/forum/thread_list.html'
    context_object_name = 'threads'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editmode'] = self.request.GET.get('editmode')
        context['thread_form'] = ThreadForm()
        context['show_new_thread'] = self.request.GET.get('new_thread')
        if self.request.GET.get('edit_thread'):
            context['edit_thread'] = get_object_or_404(Thread, pk=self.request.GET.get('edit_thread'))
            context['thread_form'] = ThreadForm(instance=context['edit_thread'])
        return context

class ForumDetailView(LoginRequiredMixin, DetailView):
    model = Thread
    template_name = 'dashboard/forum/thread_detail.html'

class PostCreateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        thread = get_object_or_404(Thread, pk=pk)
        form = PostForm()
        formset = inlineformset_factory(Post, Attachment, fields=('file',), extra=1)()  # Only one attachment
        # Show thread detail with reply form at the bottom
        return render(request, 'dashboard/forum/thread_detail.html', {
            'object': thread,
            'form': form,
            'formset': formset,
            'show_reply_form': True,
        })
    def post(self, request, pk):
        thread = get_object_or_404(Thread, pk=pk)
        form = PostForm(request.POST)
        formset = inlineformset_factory(Post, Attachment, fields=('file',), extra=1)(request.POST, request.FILES)  # Only one attachment
        if form.is_valid() and formset.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.thread = thread
            post.save()
            formset.instance = post
            formset.save()
            return redirect('forum_detail', pk=thread.pk)
        # On error, show thread detail with reply form and errors
        return render(request, 'dashboard/forum/thread_detail.html', {
            'object': thread,
            'form': form,
            'formset': formset,
            'show_reply_form': True,
        })

@login_required
def thread_manage(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            form = ThreadForm(request.POST)
            if form.is_valid():
                thread = form.save(commit=False)
                thread.created_by = request.user
                thread.save()
        elif action == 'edit':
            thread_id = request.POST.get('thread_id')
            thread = get_object_or_404(Thread, pk=thread_id)
            form = ThreadForm(request.POST, instance=thread)
            if form.is_valid():
                form.save()
        elif action == 'delete':
            thread_id = request.POST.get('thread_id')
            thread = get_object_or_404(Thread, pk=thread_id)
            thread.delete()
            from django.urls import reverse
            return redirect(reverse('forum_list') + '?editmode=1')
        # Always redirect back to forum list (no editmode for new thread)
        from django.urls import reverse
        return redirect(reverse('forum_list'))
    return redirect('forum_list')

# 2) Note-taking UIs and APIs
@login_required
def notes_ui(request):
    return render(request,'dashboard/notetaking.html')

@login_required
def notes_tree(request):
    def build(node):
        data = []
        for f in node.children.all():
            data.append({'id': f'folder_{f.id}', 'text': f.name, 'children': build(f)})
        for n in node.notes.all():
            data.append({'id': f'note_{n.id}', 'icon': 'jstree-file', 'text': n.title})
        return data

    root_folders = Folder.objects.filter(parent__isnull=True, created_by=request.user)
    resp = []
    for f in root_folders:
        resp.append({'id': f'folder_{f.id}', 'text': f.name, 'children': build(f)})
    return JsonResponse(resp, safe=False)

@login_required
def note_content(request, note_id):
    note = get_object_or_404(Note, pk=note_id)
    return JsonResponse({'content':note.content})

# CRUD endpoints for note-taking
@csrf_exempt
@login_required
def create_folder(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logging.warning(f"create_folder data: {data}")
            parent_id = data.get('parent')
            name = data.get('name', 'New Folder')
            parent = Folder.objects.filter(id=parent_id, created_by=request.user).first() if parent_id else None
            folder = Folder.objects.create(name=name, parent=parent, created_by=request.user)
            return JsonResponse({'id': folder.id, 'name': folder.name})
        except Exception as e:
            logging.error(f"create_folder error: {e}")
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)

@login_required
@csrf_exempt
def create_note(request):
    if request.method!='POST': return HttpResponseBadRequest()
    data = json.loads(request.body)
    folder = get_object_or_404(Folder, pk=data.get('folder'))
    n = Note.objects.create(
        folder=folder,
        title=data.get('title','Untitled'),
        content='',
        created_by=request.user
    )
    return JsonResponse({'id':n.id, 'text':n.title})

@login_required
@csrf_exempt
def delete_node(request):
    if request.method!='POST': return HttpResponseBadRequest()
    data=json.loads(request.body); kind,pk=data.get('id').split('_',1)
    if kind=='folder': Folder.objects.filter(pk=pk).delete()
    elif kind=='note': Note.objects.filter(pk=pk).delete()
    else: return HttpResponseBadRequest()
    return JsonResponse({'status':'ok'})

@login_required
@csrf_exempt
def rename_folder(request, folder_id):
    if request.method!='POST': return HttpResponseBadRequest()
    data=json.loads(request.body)
    f=get_object_or_404(Folder,pk=folder_id)
    f.name=data.get('name',f.name); f.save()
    return JsonResponse({'status':'ok'})

@login_required
@csrf_exempt
def rename_note(request, note_id):
    if request.method!='POST': return HttpResponseBadRequest()
    data=json.loads(request.body)
    n=get_object_or_404(Note,pk=note_id)
    n.title=data.get('name',n.title); n.save()
    return JsonResponse({'status':'ok'})

@login_required
@csrf_exempt
def update_note(request, note_id):
    if request.method!='POST': return HttpResponseBadRequest()
    data=json.loads(request.body)
    n=get_object_or_404(Note,pk=note_id,created_by=request.user)
    n.title=data.get('title',n.title); n.content=data.get('content',n.content); n.save()
    return JsonResponse({'status':'ok'})

@csrf_exempt
@login_required
def move_node(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    data = json.loads(request.body)
    kind, pk = data.get('id').split('_', 1)
    new_parent = data.get('parent')
    parent_id = None
    if new_parent and new_parent.startswith('folder_'):
        parent_id = int(new_parent.split('_')[1])
    if kind == 'folder':
        folder = get_object_or_404(Folder, pk=pk, created_by=request.user)
        folder.parent_id = parent_id
        folder.save()
    elif kind == 'note':
        note = get_object_or_404(Note, pk=pk, created_by=request.user)
        note.folder_id = parent_id
        note.save()
    else:
        return JsonResponse({'error': 'Invalid node type'}, status=400)
    return JsonResponse({'status': 'ok'})

class WidgetGroupForm(forms.ModelForm):
    class Meta:
        model = WidgetGroup
        fields = ['name']

def applications_view(request):
    widgets = Widget.objects.select_related('group').all()
    form = WidgetForm()
    group_form = WidgetGroupForm()
    edit_widget = None
    all_groups = WidgetGroup.objects.all()

    # Handle add/edit/delete widget and add/delete group
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            form = WidgetForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "Widget added.")
                from django.urls import reverse
                return redirect(reverse('applications') + '?editmode=1')
        elif action == 'edit':
            widget_id = request.POST.get('widget_id')
            edit_widget = get_object_or_404(Widget, pk=widget_id)
            form = WidgetForm(request.POST, request.FILES, instance=edit_widget)
            if form.is_valid():
                form.save()
                messages.success(request, "Widget updated.")
                from django.urls import reverse
                return redirect(reverse('applications') + '?editmode=1')
        elif action == 'delete':
            widget_id = request.POST.get('widget_id')
            widget = get_object_or_404(Widget, pk=widget_id)
            widget.delete()
            messages.success(request, "Widget deleted.")
            from django.urls import reverse
            return redirect(reverse('applications') + '?editmode=1')
        elif action == 'add_group':
            group_form = WidgetGroupForm(request.POST)
            if group_form.is_valid():
                group_form.save()
                messages.success(request, "Widget group added.")
                from django.urls import reverse
                return redirect(reverse('applications') + '?editmode=1')
        elif action == 'delete_group':
            group_id = request.POST.get('group_id')
            group_obj = WidgetGroup.objects.filter(id=group_id).first()
            if group_obj:
                if not Widget.objects.filter(group=group_obj).exists():
                    group_obj.delete()
                    messages.success(request, f"Widget group '{group_obj.name}' deleted.")
                else:
                    messages.error(request, "Cannot delete group: it is not empty.")
            else:
                messages.error(request, "Widget group not found.")
            from django.urls import reverse
            return redirect(reverse('applications') + '?editmode=1')
        else:
            messages.error(request, "Unknown action.")

    # If editing, populate form with widget data
    if request.GET.get('edit'):
        edit_widget = get_object_or_404(Widget, pk=request.GET.get('edit'))
        form = WidgetForm(instance=edit_widget)

    # Group widgets by WidgetGroup name, sorted by group name and widget order
    groups = {}
    for widget in widgets:
        group_name = widget.group.name if widget.group else "Other"
        groups.setdefault(group_name, []).append(widget)
    # Sort groups by name
    sorted_groups = dict(sorted(groups.items(), key=lambda x: x[0].lower()))
    # Sort widgets in each group by order
    for k in sorted_groups:
        sorted_groups[k] = sorted(sorted_groups[k], key=lambda w: w.order)

    return render(request, 'dashboard/applications.html', {
        'groups': sorted_groups,
        'form': form,
        'group_form': group_form,
        'edit_widget': edit_widget,
        'messages': messages.get_messages(request),
        'all_groups': all_groups,
    })