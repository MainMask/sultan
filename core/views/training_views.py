from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied

from core.models import Training, Trainer, Athlete
from core.forms import TrainingForm, TrainingFilterForm
from core.decorators import trainer_required, admin_required


def _get_trainer(user):
    if user.linked_to:
        try:
            return Trainer.objects.get(pk=user.linked_to)
        except Trainer.DoesNotExist:
            pass
    return None


@login_required
def training_list(request):
    user = request.user
    filter_form = TrainingFilterForm(request.GET or None)

    if user.is_admin():
        qs = Training.objects.select_related('athlete', 'exercise', 'athlete__group')
    elif user.is_trainer():
        trainer = _get_trainer(user)
        athletes = Athlete.objects.filter(trainer=trainer) if trainer else Athlete.objects.none()
        qs = Training.objects.filter(athlete__in=athletes).select_related('athlete', 'exercise', 'athlete__group')
        filter_form.fields['athlete'].queryset = athletes
    else:
        athlete = None
        if user.linked_to:
            try:
                athlete = Athlete.objects.get(pk=user.linked_to)
            except Athlete.DoesNotExist:
                pass
        qs = Training.objects.filter(athlete=athlete).select_related('athlete', 'exercise') if athlete else Training.objects.none()

    if filter_form.is_valid():
        if filter_form.cleaned_data.get('athlete') and not user.is_athlete():
            qs = qs.filter(athlete=filter_form.cleaned_data['athlete'])
        if filter_form.cleaned_data.get('exercise'):
            qs = qs.filter(exercise=filter_form.cleaned_data['exercise'])
        if filter_form.cleaned_data.get('date_from'):
            qs = qs.filter(date__gte=filter_form.cleaned_data['date_from'])
        if filter_form.cleaned_data.get('date_to'):
            qs = qs.filter(date__lte=filter_form.cleaned_data['date_to'])

    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'training/list.html', {
        'page_obj': page,
        'filter_form': filter_form,
    })


@trainer_required
def training_create(request):
    user = request.user
    trainer = _get_trainer(user) if user.is_trainer() else None

    form = TrainingForm(request.POST or None, trainer=trainer)

    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            training = form.save(commit=False)
            training.save()
        messages.success(request, 'Тренировка успешно добавлена')
        return redirect('training_list')

    return render(request, 'training/form.html', {'form': form, 'title': 'Добавить тренировку'})


@trainer_required
def training_edit(request, pk):
    training = get_object_or_404(Training, pk=pk)

    if training.is_locked and not request.user.is_admin():
        messages.error(request, 'Эта запись заблокирована. Обратитесь к администратору для разблокировки.')
        return redirect('training_list')

    user = request.user
    trainer = _get_trainer(user) if user.is_trainer() else None

    form = TrainingForm(request.POST or None, instance=training, trainer=trainer)

    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            form.save()
        messages.success(request, 'Тренировка обновлена')
        return redirect('training_list')

    return render(request, 'training/form.html', {'form': form, 'training': training, 'title': 'Редактировать тренировку'})


@login_required
def training_delete(request, pk):
    training = get_object_or_404(Training, pk=pk)
    user = request.user

    if not user.is_admin() and not user.is_trainer():
        raise PermissionDenied

    if training.is_locked and not user.is_admin():
        messages.error(request, 'Нельзя удалить заблокированную запись')
        return redirect('training_list')

    if request.method == 'POST':
        with transaction.atomic():
            training.delete()
        messages.success(request, 'Тренировка удалена')
        return redirect('training_list')

    return render(request, 'training/confirm_delete.html', {'training': training})


@admin_required
def training_unlock(request, pk):
    training = get_object_or_404(Training, pk=pk)
    if request.method == 'POST':
        with transaction.atomic():
            training.is_locked = False
            training.save(update_fields=['is_locked'])
        messages.success(request, f'Запись от {training.date} разблокирована')
    return redirect('training_list')


@login_required
def training_detail(request, pk):
    training = get_object_or_404(Training.objects.select_related('athlete', 'exercise'), pk=pk)
    user = request.user

    if user.is_athlete():
        athlete_id = user.linked_to
        if training.athlete_id != athlete_id:
            raise PermissionDenied

    return render(request, 'training/detail.html', {'training': training})
