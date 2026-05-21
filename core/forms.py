from django import forms
from django.utils import timezone
from .models import Training, Exercise, Athlete, Trainer, Group, User


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Логин',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Логин'}),
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}),
    )


class TrainingForm(forms.ModelForm):
    class Meta:
        model = Training
        fields = ['athlete', 'exercise', 'date', 'sets', 'reps', 'weight', 'duration', 'comment']
        widgets = {
            'athlete': forms.Select(attrs={'class': 'form-select'}),
            'exercise': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'sets': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'reps': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.5'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'athlete': 'Атлет',
            'exercise': 'Упражнение',
            'date': 'Дата',
            'sets': 'Подходы',
            'reps': 'Повторения',
            'weight': 'Вес (кг)',
            'duration': 'Длительность (мин)',
            'comment': 'Комментарий',
        }
        error_messages = {
            'athlete': {'required': 'Выберите атлета'},
            'exercise': {'required': 'Выберите упражнение'},
            'date': {'required': 'Укажите дату тренировки'},
        }

    def __init__(self, *args, trainer=None, **kwargs):
        super().__init__(*args, **kwargs)
        if trainer:
            self.fields['athlete'].queryset = Athlete.objects.filter(trainer=trainer)
        if not self.initial.get('date') and not self.data.get('date'):
            self.fields['date'].initial = timezone.localdate()

    def clean_sets(self):
        sets = self.cleaned_data.get('sets')
        if sets is not None and sets < 1:
            raise forms.ValidationError('Количество подходов должно быть не менее 1')
        return sets

    def clean_reps(self):
        reps = self.cleaned_data.get('reps')
        if reps is not None and reps < 1:
            raise forms.ValidationError('Количество повторений должно быть не менее 1')
        return reps

    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight is not None and weight < 0:
            raise forms.ValidationError('Вес не может быть отрицательным')
        return weight

    def clean_duration(self):
        duration = self.cleaned_data.get('duration')
        if duration is not None and duration < 1:
            raise forms.ValidationError('Длительность должна быть не менее 1 минуты')
        return duration


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name', 'load_type', 'unit', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'load_type': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'name': 'Название',
            'load_type': 'Тип нагрузки',
            'unit': 'Единица измерения',
            'description': 'Описание',
        }
        error_messages = {
            'name': {'required': 'Введите название упражнения'},
            'load_type': {'required': 'Выберите тип нагрузки'},
            'unit': {'required': 'Введите единицу измерения'},
        }


class AthleteForm(forms.ModelForm):
    class Meta:
        model = Athlete
        fields = ['full_name', 'birth_date', 'group', 'trainer', 'enrolled_at']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'group': forms.Select(attrs={'class': 'form-select'}),
            'trainer': forms.Select(attrs={'class': 'form-select'}),
            'enrolled_at': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'full_name': 'ФИО',
            'birth_date': 'Дата рождения',
            'group': 'Группа',
            'trainer': 'Тренер',
            'enrolled_at': 'Дата зачисления',
        }
        error_messages = {
            'full_name': {'required': 'Введите ФИО атлета'},
        }


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'trainer', 'level', 'max_count']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'trainer': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'max_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
        labels = {
            'name': 'Название группы',
            'trainer': 'Тренер',
            'level': 'Уровень',
            'max_count': 'Макс. кол-во атлетов',
        }
        error_messages = {
            'name': {'required': 'Введите название группы'},
        }


class TrainerForm(forms.ModelForm):
    class Meta:
        model = Trainer
        fields = ['full_name', 'specialization', 'experience', 'phone']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'experience': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'full_name': 'ФИО',
            'specialization': 'Специализация',
            'experience': 'Стаж (лет)',
            'phone': 'Телефон',
        }
        error_messages = {
            'full_name': {'required': 'Введите ФИО тренера'},
        }


class UserCreateForm(forms.ModelForm):
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    password_confirm = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = User
        fields = ['username', 'role', 'linked_to']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'linked_to': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': 'Логин',
            'role': 'Роль',
            'linked_to': 'ID тренера/атлета',
        }

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get('password')
        pw2 = cleaned.get('password_confirm')
        if pw and pw2 and pw != pw2:
            raise forms.ValidationError({'password_confirm': 'Пароли не совпадают'})
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class TrainingFilterForm(forms.Form):
    athlete = forms.ModelChoiceField(
        queryset=Athlete.objects.all(),
        required=False,
        empty_label='Все атлеты',
        label='Атлет',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    exercise = forms.ModelChoiceField(
        queryset=Exercise.objects.all(),
        required=False,
        empty_label='Все упражнения',
        label='Упражнение',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    date_from = forms.DateField(
        required=False,
        label='С',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    date_to = forms.DateField(
        required=False,
        label='По',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
