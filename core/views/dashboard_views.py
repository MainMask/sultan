from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils import timezone

from core.models import Athlete, Trainer, Group, Training, Exercise, User


@login_required
def dashboard_view(request):
    user = request.user

    if user.is_admin():
        context = {
            'athletes_count': Athlete.objects.count(),
            'trainers_count': Trainer.objects.count(),
            'groups_count': Group.objects.count(),
            'exercises_count': Exercise.objects.count(),
            'trainings_today': Training.objects.filter(date=timezone.localdate()).count(),
            'users_count': User.objects.count(),
            'recent_trainings': Training.objects.select_related('athlete', 'exercise').order_by('-created_at')[:10],
        }
        return render(request, 'dashboard/admin.html', context)

    if user.is_trainer():
        trainer = None
        if user.linked_to:
            try:
                trainer = Trainer.objects.get(pk=user.linked_to)
            except Trainer.DoesNotExist:
                pass

        athletes = Athlete.objects.filter(trainer=trainer) if trainer else Athlete.objects.none()
        context = {
            'trainer': trainer,
            'athletes_count': athletes.count(),
            'trainings_today': Training.objects.filter(
                athlete__in=athletes, date=timezone.localdate()
            ).count(),
            'recent_trainings': Training.objects.filter(athlete__in=athletes).select_related(
                'athlete', 'exercise'
            ).order_by('-date', '-created_at')[:10],
            'athletes': athletes[:5],
        }
        return render(request, 'dashboard/trainer.html', context)

    if user.is_athlete():
        athlete = None
        if user.linked_to:
            try:
                athlete = Athlete.objects.get(pk=user.linked_to)
            except Athlete.DoesNotExist:
                pass

        trainings = Training.objects.filter(athlete=athlete).select_related('exercise') if athlete else Training.objects.none()
        context = {
            'athlete': athlete,
            'trainings_count': trainings.count(),
            'recent_trainings': trainings.order_by('-date', '-created_at')[:10],
        }
        return render(request, 'dashboard/athlete.html', context)

    return redirect('login')
