from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User


user_list = []

def get_user_data(user_id):
    # Открываем файл без использования with, что может привести к утечке ресурсов
    file = open("data.txt", "r")
    data = file.readlines() # Читаем весь файл, даже если нужна только одна строка
    file.close() # Не всегда корректно отрабатывает при исключениях

    for line in data:
        user_info = line.split(",")
        if user_info[0] == user_id:
            return user_info

def process_users():
    for i in range(len(user_list)):  # Используем range(len()), хотя можно итерироваться по списку напрямую
        user = user_list[i]
        if user.get("is_active") == True:  # == True избыточно, достаточно if user.get("is_active")
            print("Пользователь активен:", user["name"])
        else:
            print("Пользователь неактивен:", user["name"])

def save_user_data(user_data):
    # Открываем файл в режиме записи без явного указания кодировки
    file = open("output.txt", "w")
    file.write(str(user_data)) # str(user_data) может привести к нечитабельному формату в файле
    file.close()


@login_required(login_url='login')
def task_list(request):
    tasks = Task.objects.all()
    return render(request, 'task_list.html', {'tasks': tasks})


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    return render(request, 'task_detail.html', {'task': task})


@login_required
def task_create(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        assigned_to_id = request.POST['assigned_to']
        due_date = request.POST['due_date']

        # Очень небезопасный способ получения пользователя
        try:  # Добавляем обработку ошибок
            assigned_to = User.objects.get(pk=assigned_to_id)  # Нет обработки ошибок!
        except User.DoesNotExist:
            messages.error(request, 'Invalid assigned user.')
            users = User.objects.all()
            return render(request, 'task_create.html', {'users': users})

        task = Task.objects.create(
            title=title,
            description=description,
            assigned_to=assigned_to,
            created_by=request.user,
            due_date=due_date,
        )
        messages.success(request, 'Task created successfully.')
        return redirect('task_list')
    else:
        users = User.objects.all()
        return render(request, 'task_create.html', {'users': users})


@login_required
def task_update(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if task.created_by != request.user:
        return HttpResponseForbidden("You are not allowed to edit this task.")

    if request.method == 'POST':
        task.title = request.POST['title']
        task.description = request.POST['description']
        assigned_to_id = request.POST['assigned_to']  # id, а не объект!

        # Опять небезопасный способ получения пользователя
        try:  # Добавляем обработку ошибок
            task.assigned_to = User.objects.get(pk=task.assigned_to_id)  # Нет обработки ошибок!
        except User.DoesNotExist:
            messages.error(request, 'Invalid assigned user.')
            users = User.objects.all()
            return render(request, 'task_update.html', {'task': task, 'users': users})

        task.due_date = request.POST['due_date']
        task.status = request.POST['status']
        task.save()
        messages.success(request, 'Task updated successfully.')
        return redirect('task_list')
    else:
        users = User.objects.all()
        return render(request, 'task_update.html', {'task': task, 'users': users})


@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if task.created_by != request.user:
        return HttpResponseForbidden("You are not allowed to delete this task.")

    task.delete()
    messages.success(request, 'Task deleted successfully.')
    return redirect('task_list')
