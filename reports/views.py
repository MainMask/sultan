import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.conf import settings
from django.db import transaction
from django.core.paginator import Paginator
from django.utils import timezone

from core.models import Report, Athlete
from core.decorators import trainer_required
from .forms import GroupReportForm, AthleteReportForm, AttendanceReportForm, PersonalReportForm
from .generators import (
    generate_group_report, generate_athlete_report,
    generate_attendance_report, generate_personal_report,
)


def _save_report_file(buf, filename) -> str:
    reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    filepath = os.path.join(reports_dir, filename)
    with open(filepath, 'wb') as f:
        f.write(buf.read())
    return os.path.join('reports', filename)


@login_required
def report_list(request):
    user = request.user
    if user.is_admin():
        qs = Report.objects.select_related('athlete', 'group').all()
    elif user.is_trainer():
        from core.models import Trainer
        trainer = None
        if user.linked_to:
            try:
                trainer = Trainer.objects.get(pk=user.linked_to)
            except Trainer.DoesNotExist:
                pass
        athletes = Athlete.objects.filter(trainer=trainer) if trainer else Athlete.objects.none()
        qs = Report.objects.filter(athlete__in=athletes).select_related('athlete', 'group') | \
             Report.objects.filter(group__trainer=trainer).select_related('athlete', 'group')
        qs = qs.distinct()
    else:
        athlete = None
        if user.linked_to:
            try:
                athlete = Athlete.objects.get(pk=user.linked_to)
            except Athlete.DoesNotExist:
                pass
        qs = Report.objects.filter(athlete=athlete) if athlete else Report.objects.none()

    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'reports/list.html', {'page_obj': page})


@login_required
def report_create(request):
    user = request.user
    report_type = request.GET.get('type', 'group')
    athlete_pk = request.GET.get('athlete')

    forms_map = {
        'group': GroupReportForm,
        'individual': AthleteReportForm,
        'attendance': AttendanceReportForm,
        'personal': PersonalReportForm,
    }
    FormClass = forms_map.get(report_type, GroupReportForm)
    initial = {}
    if athlete_pk and report_type in ('individual', 'personal'):
        initial['athlete'] = athlete_pk

    form = FormClass(request.POST or None, initial=initial)

    if user.is_athlete():
        report_type = 'personal'
        form = PersonalReportForm(request.POST or None)
        if hasattr(form.fields, 'athlete'):
            form.fields['athlete'].widget = form.fields['athlete'].hidden_widget()

    if request.method == 'POST' and form.is_valid():
        cd = form.cleaned_data
        ts = timezone.now().strftime('%Y%m%d_%H%M%S')

        try:
            if report_type == 'group':
                buf = generate_group_report(
                    cd['group'].pk, cd['period_start'], cd['period_end'], cd.get('group_by', 'athlete')
                )
                filename = f'group_{cd["group"].pk}_{ts}.xlsx'
                file_path = _save_report_file(buf, filename)
                with transaction.atomic():
                    report = Report.objects.create(
                        group=cd['group'], period_start=cd['period_start'],
                        period_end=cd['period_end'], type='group', file_path=file_path,
                    )

            elif report_type == 'individual':
                buf = generate_athlete_report(
                    cd['athlete'].pk, cd['period_start'], cd['period_end']
                )
                filename = f'athlete_{cd["athlete"].pk}_{ts}.xlsx'
                file_path = _save_report_file(buf, filename)
                with transaction.atomic():
                    report = Report.objects.create(
                        athlete=cd['athlete'], period_start=cd['period_start'],
                        period_end=cd['period_end'], type='individual', file_path=file_path,
                    )

            elif report_type == 'attendance':
                buf = generate_attendance_report(
                    cd['group'].pk, cd['period_start'], cd['period_end']
                )
                filename = f'attendance_{cd["group"].pk}_{ts}.xlsx'
                file_path = _save_report_file(buf, filename)
                with transaction.atomic():
                    report = Report.objects.create(
                        group=cd['group'], period_start=cd['period_start'],
                        period_end=cd['period_end'], type='attendance', file_path=file_path,
                    )

            else:
                athlete = cd.get('athlete')
                if user.is_athlete() and user.linked_to:
                    athlete = Athlete.objects.get(pk=user.linked_to)
                if not athlete:
                    messages.error(request, 'Укажите атлета для личного отчёта')
                    return render(request, 'reports/form.html', {'form': form, 'report_type': report_type})

                buf = generate_personal_report(
                    athlete.pk, cd['period_start'], cd['period_end'],
                    cd.get('group_by', 'week'), cd.get('exercise_type', ''),
                )
                filename = f'personal_{athlete.pk}_{ts}.xlsx'
                file_path = _save_report_file(buf, filename)
                with transaction.atomic():
                    report = Report.objects.create(
                        athlete=athlete, period_start=cd['period_start'],
                        period_end=cd['period_end'], type='personal', file_path=file_path,
                    )

            messages.success(request, 'Отчёт успешно сформирован')
            return redirect('reports:report_download', pk=report.pk)

        except Exception as e:
            messages.error(request, f'Ошибка при генерации отчёта: {e}')

    report_type_labels = {
        'group': 'Групповой отчёт',
        'individual': 'Индивидуальный отчёт',
        'attendance': 'Посещаемость',
        'personal': 'Личный отчёт',
    }
    return render(request, 'reports/form.html', {
        'form': form,
        'report_type': report_type,
        'report_type_label': report_type_labels.get(report_type, ''),
    })


@login_required
def report_download(request, pk):
    report = get_object_or_404(Report, pk=pk)
    user = request.user

    if user.is_athlete() and (not report.athlete or report.athlete.pk != user.linked_to):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    filepath = os.path.join(settings.MEDIA_ROOT, report.file_path)
    if not os.path.exists(filepath):
        raise Http404('Файл отчёта не найден')

    filename = os.path.basename(filepath)
    response = FileResponse(open(filepath, 'rb'), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@trainer_required
def report_delete(request, pk):
    report = get_object_or_404(Report, pk=pk)
    if request.method == 'POST':
        filepath = os.path.join(settings.MEDIA_ROOT, report.file_path)
        if os.path.exists(filepath):
            os.remove(filepath)
        with transaction.atomic():
            report.delete()
        messages.success(request, 'Отчёт удалён')
        return redirect('reports:report_list')
    return render(request, 'reports/confirm_delete.html', {'report': report})
