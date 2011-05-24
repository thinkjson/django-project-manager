from django.db import models
from django import forms
from django.contrib.auth.models import User
from datetime import date

class Project(models.Model):
    """Project definitions that include multiple milestones"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, help_text="Optional description of project")
    creation_date = models.DateTimeField(auto_now_add=True)
    authorized_users = models.ManyToManyField(User, null=True, blank=True,\
        help_text="These are users which have management authority over a project.")

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def health(self):
        today = date.today()
        unfinished_tasks = Task.objects.filter(project__id=self.id, completed=False).count()
        overdue_tasks = unfinished_tasks - Task.objects.filter(project__id=self.id, completed=False, due_date__lte=today).count()
        if unfinished_tasks > 0:
            return int((float(overdue_tasks)/float(unfinished_tasks))*100)
        else:
            return 100

    def health_description(self):
        health = self.health()
        if health < 50:
            return "High"
        elif health < 90:
            return "InProgress"
        elif health >= 90:
            return "Medium"

    def completed(self):
        finished_tasks = Task.objects.filter(project__id=self.id, completed=True).count()
        all_tasks = Task.objects.filter(project__id=self.id).count()
        if all_tasks > 0:
            return int((float(finished_tasks)/float(all_tasks))*100)
        else:
            return 100

    def completed_description(self):
        completed = self.completed()
        if completed < 50:
            return "High"
        elif completed < 90:
            return "InProgress"
        elif completed >= 90:
            return "Medium"

    def next_due_date(self):
        tasks_due = Task.objects.filter(project=self, completed=False, \
            due_date__isnull=False).order_by('due_date')
        if tasks_due.count() > 0:
            return tasks_due[0].due_date
        else:
            return None

    def is_completed(self):
        if self.completed() == 100:
            return True
        else:
            return False

class Task(models.Model):
    """Things that must be done in order to complete a project"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    project = models.ForeignKey('Project', \
        help_text="Project to which this task belongs",\
        null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(blank=True, null=True)
    dependencies = models.ManyToManyField('self', blank=True, null=True)
    assigned_by = models.ForeignKey(User, blank=True, null=True, related_name="assigned_by")
    assigned_to = models.ManyToManyField(User, blank=True, null=True, related_name="assigned_to")
    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def coding(self):
        if self.completed == True:
            return "neutral"
        else:
            return "Open"

class ConfirmationForm(forms.Form):
    ok = forms.BooleanField()

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'description', 'authorized_users',)

class TaskForm(forms.ModelForm):
    def __init__(self, project_id, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['dependencies'].queryset = Task.objects.filter(project__id=project_id)
        
    class Meta:
        model = Task
        fields = ('name', 'description', 'due_date', 'dependencies', 'assigned_to', 'completed',)