from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages  # Import messages for displaying error/success messages
from .models import Task
from .forms import TaskForm, UserLoginForm  # Import specific forms
from django.http import JsonResponse
from django.contrib.auth.models import User
from .forms import UserRegistrationForm
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm

def user_registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_login')  # Redirect to the login page after successful registration
    else:
        form = UserRegistrationForm()
    return render(request, 'todo/registration.html', {'form': form})
def user_login(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('task_list')  # Redirect to the task list page after login
        else:
            messages.error(request, 'Invalid username or password.')  # Use messages to display an error
    return render(request, 'todo/login.html', {'form': form}) 

def user_logout(request):
    logout(request)
    return redirect('task_list')

@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'todo/task_list.html', {'tasks': tasks})

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, 'Task created successfully.')  # Success message on task creation
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'todo/task_form.html', {'form': form})

@login_required
def task_update(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully.')  # Success message on task update
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'todo/task_form.html', {'form': form})

@login_required
def task_delete(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully.')  # Success message on task deletion
        return redirect('task_list')
    return render(request, 'todo/task_confirm_delete.html', {'task': task})

@login_required
def toggle_task(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)
    if request.method == 'POST':
        data = json.loads(request.body)
        task.completed = data['completed']
        task.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'}, status=400)
