from django import forms
from core.models import Athlete, Group, LOAD_TYPE_CHOICES, REPORT_TYPE_CHOICES

GROUP_BY_CHOICES = [
    ('athlete', 'По атлету'),
    ('date', 'По дате'),
]

PERIOD_GROUP_CHOICES = [
    ('week', 'По неделям'),
    ('month', 'По месяцам'),
]


class GroupReportForm(forms.Form):
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label='Группа',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    period_start = forms.DateField(
        label='Начало периода',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    period_end = forms.DateField(
        label='Конец периода',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    group_by = forms.ChoiceField(
        choices=GROUP_BY_CHOICES,
        label='Группировка',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    def clean(self):
        cd = super().clean()
        if cd.get('period_start') and cd.get('period_end'):
            if cd['period_start'] > cd['period_end']:
                raise forms.ValidationError('Дата начала должна быть раньше даты окончания')
        return cd


class AthleteReportForm(forms.Form):
    athlete = forms.ModelChoiceField(
        queryset=Athlete.objects.all(),
        label='Атлет',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    period_start = forms.DateField(
        label='Начало периода',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    period_end = forms.DateField(
        label='Конец периода',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )

    def clean(self):
        cd = super().clean()
        if cd.get('period_start') and cd.get('period_end'):
            if cd['period_start'] > cd['period_end']:
                raise forms.ValidationError('Дата начала должна быть раньше даты окончания')
        return cd


class AttendanceReportForm(forms.Form):
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label='Группа',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    period_start = forms.DateField(
        label='Начало периода',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    period_end = forms.DateField(
        label='Конец периода',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )

    def clean(self):
        cd = super().clean()
        if cd.get('period_start') and cd.get('period_end'):
            if cd['period_start'] > cd['period_end']:
                raise forms.ValidationError('Дата начала должна быть раньше даты окончания')
        return cd


class PersonalReportForm(forms.Form):
    athlete = forms.ModelChoiceField(
        queryset=Athlete.objects.all(),
        label='Атлет',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    period_start = forms.DateField(
        label='Начало периода',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    period_end = forms.DateField(
        label='Конец периода',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    group_by = forms.ChoiceField(
        choices=PERIOD_GROUP_CHOICES,
        label='Группировка',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    exercise_type = forms.ChoiceField(
        choices=[('', 'Все типы')] + list(LOAD_TYPE_CHOICES),
        required=False,
        label='Тип упражнения',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    def clean(self):
        cd = super().clean()
        if cd.get('period_start') and cd.get('period_end'):
            if cd['period_start'] > cd['period_end']:
                raise forms.ValidationError('Дата начала должна быть раньше даты окончания')
        return cd
