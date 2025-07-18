import json, requests
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.forms import inlineformset_factory
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Widget, Thread, Post, Attachment, Folder, Note

# 1) Dashboard pages
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'

class ApplicationsView(LoginRequiredMixin, ListView):
    model = Widget
    template_name = 'dashboard/applications.html'
    context_object_name = 'widgets'

class ForumListView(LoginRequiredMixin, ListView):
    model = Thread
    template_name = 'dashboard/forum/thread_list.html'
    context_object_name = 'threads'

class ForumDetailView(LoginRequiredMixin, DetailView):
    model = Thread
    template_name = 'dashboard/forum/thread_detail.html'

class PostCreateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        thread = get_object_or_404(Thread, pk=pk)
        form = PostForm()
        formset = inlineformset_factory(Post, Attachment, fields=('file',), extra=3)()
        return render(request,'dashboard/forum/post_form.html',{'form':form,'formset':formset,'thread':thread})
    def post(self, request, pk):
        thread = get_object_or_404(Thread, pk=pk)
        form = PostForm(request.POST)
        formset = inlineformset_factory(Post, Attachment, fields=('file',), extra=3)(request.POST,request.FILES)
        if form.is_valid() and formset.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.thread = thread
            post.save()
            formset.instance = post
            formset.save()
            return redirect('forum_detail',pk=thread.pk)
        return render(request,'dashboard/forum/post_form.html',{'form':form,'formset':formset,'thread':thread})

# 2) Note-taking UIs and APIs
@login_required
def notes_ui(request):
    return render(request,'dashboard/notetaking.html')

@login_required
def notes_tree(request):
    def build(node):
        data=[]
        for f in node.children.all(): data.append({'id':f'folder_{f.id}','text':f.name,'children':build(f)})
        for n in node.notes.all(): data.append({'id':f'note_{n.id}','icon':'jstree-file','text':n.title})
        return data
    root_folders = Folder.objects.filter(parent__isnull=True)
    resp = []
    for f in root_folders: resp.extend(build(f))
    return JsonResponse(resp,safe=False)

@login_required
def note_content(request, note_id):
    note = get_object_or_404(Note, pk=note_id)
    return JsonResponse({'content':note.content})

# CRUD endpoints for note-taking
@login_required
@csrf_exempt
def create_folder(request):
    if request.method!='POST': return HttpResponseBadRequest()
    data = json.loads(request.body)
    parent = Folder.objects.filter(pk=data.get('parent')).first() if data.get('parent') else None
    f = Folder.objects.create(
        name=data.get('name','New Folder'),
        parent=parent,
        created_by=request.user
    )
    return JsonResponse({'id':f.id, 'text':f.name})

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