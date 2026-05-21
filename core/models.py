from django.contrib.auth.models import AbstractUser
from django.db import models


ROLE_ADMIN = 'admin'
ROLE_TRAINER = 'trainer'
ROLE_ATHLETE = 'athlete'

ROLE_CHOICES = [
    (ROLE_ADMIN, 'Администратор'),
    (ROLE_TRAINER, 'Тренер'),
    (ROLE_ATHLETE, 'Атлет'),
]

LOAD_TYPE_CHOICES = [
    ('strength', 'Силовая'),
    ('cardio', 'Кардио'),
    ('flexibility', 'Гибкость'),
    ('speed', 'Скоростная'),
    ('endurance', 'Выносливость'),
    ('technical', 'Техническая'),
]

LEVEL_CHOICES = [
    ('beginner', 'Начинающий'),
    ('intermediate', 'Средний'),
    ('advanced', 'Продвинутый'),
]

REPORT_TYPE_CHOICES = [
    ('group', 'Групповой'),
    ('individual', 'Индивидуальный'),
    ('attendance', 'Посещаемость'),
    ('personal', 'Личный'),
]


class User(AbstractUser):
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=ROLE_ATHLETE,
        verbose_name='Роль',
    )
    linked_to = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Связан с ID',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def is_admin(self):
        return self.role == ROLE_ADMIN

    def is_trainer(self):
        return self.role == ROLE_TRAINER

    def is_athlete(self):
        return self.role == ROLE_ATHLETE

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'


class Trainer(models.Model):
    full_name = models.CharField(max_length=200, verbose_name='ФИО')
    specialization = models.CharField(max_length=200, verbose_name='Специализация')
    experience = models.PositiveSmallIntegerField(verbose_name='Стаж (лет)', default=0)
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')

    class Meta:
        verbose_name = 'Тренер'
        verbose_name_plural = 'Тренеры'
        ordering = ['full_name']

    def __str__(self):
        return self.full_name


class Group(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='groups',
        verbose_name='Тренер',
    )
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default='beginner',
        verbose_name='Уровень',
    )
    max_count = models.PositiveSmallIntegerField(default=20, verbose_name='Макс. кол-во атлетов')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ['name']

    def __str__(self):
        return self.name

    def athlete_count(self):
        return self.athletes.count()


class Athlete(models.Model):
    full_name = models.CharField(max_length=200, verbose_name='ФИО')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='athletes',
        verbose_name='Группа',
    )
    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='athletes',
        verbose_name='Тренер',
    )
    enrolled_at = models.DateField(null=True, blank=True, verbose_name='Дата зачисления')

    class Meta:
        verbose_name = 'Атлет'
        verbose_name_plural = 'Атлеты'
        ordering = ['full_name']

    def __str__(self):
        return self.full_name


class Exercise(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    load_type = models.CharField(
        max_length=20,
        choices=LOAD_TYPE_CHOICES,
        verbose_name='Тип нагрузки',
    )
    unit = models.CharField(max_length=30, verbose_name='Единица измерения')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Упражнение'
        verbose_name_plural = 'Упражнения'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.get_load_type_display()})'


class Training(models.Model):
    athlete = models.ForeignKey(
        Athlete,
        on_delete=models.CASCADE,
        related_name='trainings',
        verbose_name='Атлет',
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.PROTECT,
        related_name='trainings',
        verbose_name='Упражнение',
    )
    date = models.DateField(verbose_name='Дата')
    sets = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Подходы')
    reps = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Повторения')
    weight = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Вес (кг)',
    )
    duration = models.PositiveIntegerField(null=True, blank=True, verbose_name='Длительность (мин)')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    is_locked = models.BooleanField(default=False, verbose_name='Заблокировано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Тренировка'
        verbose_name_plural = 'Тренировки'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'{self.athlete} — {self.exercise} ({self.date})'


class Report(models.Model):
    athlete = models.ForeignKey(
        Athlete,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reports',
        verbose_name='Атлет',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports',
        verbose_name='Группа',
    )
    period_start = models.DateField(verbose_name='Начало периода')
    period_end = models.DateField(verbose_name='Конец периода')
    type = models.CharField(
        max_length=20,
        choices=REPORT_TYPE_CHOICES,
        verbose_name='Тип отчёта',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    format = models.CharField(max_length=10, default='xlsx', verbose_name='Формат')
    file_path = models.CharField(max_length=500, blank=True, verbose_name='Путь к файлу')

    class Meta:
        verbose_name = 'Отчёт'
        verbose_name_plural = 'Отчёты'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_type_display()} {self.period_start}–{self.period_end}'
