from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from core.models import Athlete, Trainer, Training
from core.forms import AthleteForm
from core.decorators import trainer_required


@login_required
def athlete_list(request):
    user = request.user
    if user.is_admin():
        qs = Athlete.objects.select_related('group', 'trainer')
    elif user.is_trainer():
        trainer = None
        if user.linked_to:
            try:
                trainer = Trainer.objects.get(pk=user.linked_to)
            except Trainer.DoesNotExist:
                pass
        qs = Athlete.objects.filter(trainer=trainer).select_related('group', 'trainer')
    else:
        qs = Athlete.objects.none()

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(full_name__icontains=q)

    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'athlete/list.html', {'page_obj': page, 'q': q})


@trainer_required
def athlete_create(request):
    form = AthleteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            form.save()
        messages.success(request, 'Атлет добавлен')
        return redirect('athlete_list')
    return render(request, 'athlete/form.html', {'form': form, 'title': 'Добавить атлета'})


@trainer_required
def athlete_edit(request, pk):
    athlete = get_object_or_404(Athlete, pk=pk)
    form = AthleteForm(request.POST or None, instance=athlete)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            form.save()
        messages.success(request, 'Данные атлета обновлены')
        return redirect('athlete_list')
    return render(request, 'athlete/form.html', {'form': form, 'athlete': athlete, 'title': 'Редактировать атлета'})


@login_required
def athlete_detail(request, pk):
    athlete = get_object_or_404(Athlete.objects.select_related('group', 'trainer'), pk=pk)
    user = request.user

    if user.is_athlete() and user.linked_to != athlete.pk:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    trainings = Training.objects.filter(athlete=athlete).select_related('exercise').order_by('-date')[:20]
    return render(request, 'athlete/detail.html', {'athlete': athlete, 'trainings': trainings})


@trainer_required
def athlete_delete(request, pk):
    athlete = get_object_or_404(Athlete, pk=pk)
    if request.method == 'POST':
        with transaction.atomic():
            athlete.delete()
        messages.success(request, 'Атлет удалён')
        return redirect('athlete_list')
    return render(request, 'athlete/confirm_delete.html', {'athlete': athlete})
