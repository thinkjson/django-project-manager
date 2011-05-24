from projects.models import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.contrib import messages

@login_required
def projects_overview(request):
    """Show all projects, as well as important tasks and upcoming milestones"""
    projects = Project.objects.filter(authorized_users=request.user)\
        .order_by('name')
    assigned_projects = Project.objects.filter(task__assigned_to=request.user)\
        .exclude(authorized_users = request.user)\
        .distinct(Project).order_by('name')
    important_tasks = Task.objects.filter(assigned_to=request.user, \
        project__isnull=False, due_date__isnull=False, completed=False).order_by('due_date')[:20]
    title = "Projects"
    
    return render_to_response("projects_overview.html", locals(), \
        context_instance=RequestContext(request))

@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        form = ConfirmationForm(request.POST)
        if form.is_valid() and 'ok' in form.cleaned_data and form.cleaned_data['ok'] == True:
            project.delete()
            return HttpResponseRedirect(reverse('projects.views.projects_overview'))
    else:
        message = "Are you sure you want to delete `%s`?" % project.name
        messages.info(request, message)
        form = ConfirmationForm()
    return  render_to_response('add_project.html', locals(), \
        context_instance=RequestContext(request))

@login_required
def show_project(request, project_id):
    """Show the details of a project"""
    project = get_object_or_404(Project, pk=project_id)
    tasks = Task.objects.filter(project__id=project_id).order_by('completed', 'due_date')
    team = ""
    for member in project.authorized_users.all():
        team += member.get_full_name()
        if member == request.user:
            authorized = True
    title = project.name
    return render_to_response("project_detail.html", locals(), \
        context_instance=RequestContext(request))

@login_required
def add_project(request, project_id=0):
    """Allows users to add new projects."""
    if request.method == 'POST':
        if project_id != 0:
            project = get_object_or_404(Project, pk=project_id)
            form = ProjectForm(request.POST, instance=project)
        else:
            form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.save()
            form.save_m2m()
            project.authorized_users.add(request.user)
            if project.id == 0:
                return HttpResponseRedirect(reverse('projects.views.projects_overview'))
            else:
                return HttpResponseRedirect(reverse('projects.views.show_project', \
                    kwargs = { 'project_id': project.id } ))
    else:
        if project_id != 0:
            project = get_object_or_404(Project, pk=project_id)
            form = ProjectForm(instance=project)
        else:
            form = ProjectForm()
    title = "Projects - New Project"
    return render_to_response('add_project.html', locals(), \
        context_instance=RequestContext(request))

@login_required
def edit_task(request, project_id, task_id=0):
    """Allows users to add new tasks."""
    project = get_object_or_404(Project, pk=project_id, authorized_users=request.user)
    if task_id != 0:
        # Edit task
        title = "Projects - Edit Task"
        task = get_object_or_404(Task, pk=task_id)
        if request.method == 'POST':
            form = TaskForm(project_id, request.POST, instance=task)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('projects.views.show_project', \
                    kwargs = { 'project_id': project_id } ))
        else:
            form = TaskForm(project_id, instance=task)
    else:
        # Add new task
        title = "Projects - New Task"
        if request.method == 'POST':
            form = TaskForm(project_id, request.POST)
            if form.is_valid():
                task = form.save(commit=False)
                task.project = project
                task.save()
                task.assigned_by = request.user
                if task.assigned_to.count() == 0:
                    task.assigned_to.add(request.user)
                return HttpResponseRedirect(reverse('projects.views.show_project', \
                    kwargs = { 'project_id': project_id } ))
        else:
            form = TaskForm(project_id)
    return render_to_response('add_project.html', locals(), \
        context_instance=RequestContext(request))