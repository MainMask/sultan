from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator

from core.models import User, Trainer, Group, Athlete
from core.forms import UserCreateForm, UserEditForm, TrainerForm, GroupForm
from core.decorators import admin_required, trainer_required


@admin_required
def user_list(request):
    qs = User.objects.all().order_by('username')
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_panel/user_list.html', {'page_obj': page})


@admin_required
def user_create(request):
    form = UserCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            form.save()
        messages.success(request, 'Пользователь создан')
        return redirect('user_list')
    return render(request, 'admin_panel/user_form.html', {'form': form, 'title': 'Создать пользователя'})


@admin_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = UserEditForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            form.save()
        messages.success(request, f'Пользователь {user.username} обновлён')
        return redirect('user_list')
    return render(request, 'admin_panel/user_form.html', {'form': form, 'title': f'Редактировать: {user.username}', 'obj': user})


@admin_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, 'Нельзя удалить собственную учётную запись')
        return redirect('user_list')
    if request.method == 'POST':
        with transaction.atomic():
            user.delete()
        messages.success(request, 'Пользователь удалён')
        return redirect('user_list')
    return render(request, 'admin_panel/user_confirm_delete.html', {'obj': user})


@trainer_required
def trainer_list(request):
    qs = Trainer.objects.all()
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_panel/trainer_list.html', {'page_obj': page})


@admin_required
def trainer_create(request):
    form = TrainerForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            form.save()
        messages.success(request, 'Тренер добавлен')
        return redirect('trainer_list')
    return render(request, 'admin_panel/trainer_form.html', {'form': form, 'title': 'Добавить тренера'})


@admin_required
def trainer_edit(request, pk):
    trainer = get_object_or_404(Trainer, pk=pk)
    form = TrainerForm(request.POST or None, instance=trainer)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            form.save()
        messages.success(request, 'Тренер обновлён')
        return redirect('trainer_list')
    return render(request, 'admin_panel/trainer_form.html', {'form': form, 'trainer': trainer, 'title': 'Редактировать тренера'})


@admin_required
def trainer_delete(request, pk):
    trainer = get_object_or_404(Trainer, pk=pk)
    if request.method == 'POST':
        with transaction.atomic():
            trainer.delete()
        messages.success(request, 'Тренер удалён')
        return redirect('trainer_list')
    return render(request, 'admin_panel/trainer_confirm_delete.html', {'obj': trainer})


@trainer_required
def group_list(request):
    user = request.user
    if user.is_admin():
        qs = Group.objects.select_related('trainer').all()
    else:
        trainer = None
        if user.linked_to:
            try:
                trainer = Trainer.objects.get(pk=user.linked_to)
            except Trainer.DoesNotExist:
                pass
        qs = Group.objects.filter(trainer=trainer).select_related('trainer')
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'group/list.html', {'page_obj': page})


@trainer_required
def group_create(request):
    form = GroupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            form.save()
        messages.success(request, 'Группа создана')
        return redirect('group_list')
    return render(request, 'group/form.html', {'form': form, 'title': 'Создать группу'})


@trainer_required
def group_edit(request, pk):
    group = get_object_or_404(Group, pk=pk)
    form = GroupForm(request.POST or None, instance=group)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            form.save()
        messages.success(request, 'Группа обновлена')
        return redirect('group_list')
    return render(request, 'group/form.html', {'form': form, 'group': group, 'title': 'Редактировать группу'})


@admin_required
def group_delete(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        with transaction.atomic():
            group.delete()
        messages.success(request, 'Группа удалена')
        return redirect('group_list')
    return render(request, 'group/confirm_delete.html', {'group': group})
