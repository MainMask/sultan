from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from core.models import Exercise
from core.forms import ExerciseForm
from core.decorators import trainer_required


@login_required
def exercise_list(request):
    qs = Exercise.objects.all()
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(name__icontains=q)
    load_type = request.GET.get('load_type', '')
    if load_type:
        qs = qs.filter(load_type=load_type)

    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page'))

    from core.models import LOAD_TYPE_CHOICES
    return render(request, 'exercise/list.html', {
        'page_obj': page,
        'q': q,
        'load_type': load_type,
        'load_type_choices': LOAD_TYPE_CHOICES,
    })


@trainer_required
def exercise_create(request):
    form = ExerciseForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            form.save()
        messages.success(request, 'Упражнение добавлено')
        return redirect('exercise_list')
    return render(request, 'exercise/form.html', {'form': form, 'title': 'Добавить упражнение'})


@trainer_required
def exercise_edit(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)
    form = ExerciseForm(request.POST or None, instance=exercise)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            form.save()
        messages.success(request, 'Упражнение обновлено')
        return redirect('exercise_list')
    return render(request, 'exercise/form.html', {'form': form, 'exercise': exercise, 'title': 'Редактировать упражнение'})


@trainer_required
def exercise_delete(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)
    if request.method == 'POST':
        with transaction.atomic():
            exercise.delete()
        messages.success(request, 'Упражнение удалено')
        return redirect('exercise_list')
    return render(request, 'exercise/confirm_delete.html', {'exercise': exercise})
