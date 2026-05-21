from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.models import User, Trainer, Group, Athlete, Exercise


EXERCISES = [
    ('Приседания со штангой', 'strength', 'кг', 'Базовое упражнение для ног и ягодиц'),
    ('Жим лёжа', 'strength', 'кг', 'Базовое упражнение для грудных мышц'),
    ('Становая тяга', 'strength', 'кг', 'Базовое упражнение для спины и ног'),
    ('Подтягивания', 'strength', 'повт.', 'Упражнение для мышц спины'),
    ('Жим стоя', 'strength', 'кг', 'Жим штанги над головой'),
    ('Бег', 'cardio', 'км', 'Кардиоупражнение'),
    ('Велосипед', 'cardio', 'км', 'Кардиоупражнение на велотренажёре'),
    ('Прыжки со скакалкой', 'speed', 'мин', 'Скоростное упражнение'),
    ('Растяжка', 'flexibility', 'мин', 'Комплекс растяжки'),
    ('Планка', 'endurance', 'сек', 'Упражнение на выносливость кора'),
    ('Бёрпи', 'endurance', 'повт.', 'Комплексное функциональное упражнение'),
    ('Техника рывка', 'technical', 'кг', 'Тяжелоатлетическое упражнение'),
]

TRAINERS = [
    ('Иванов Алексей Сергеевич', 'Тяжёлая атлетика', 8, '+7 (900) 123-45-67'),
    ('Петрова Мария Владимировна', 'Кардио и фитнес', 5, '+7 (900) 765-43-21'),
]

GROUPS = [
    ('Начинающие', None, 'beginner', 20),
    ('Продвинутые', None, 'advanced', 15),
]


class Command(BaseCommand):
    help = 'Заполнение БД начальными данными: упражнения, группы, тренеры, admin-пользователь'

    def handle(self, *args, **options):
        with transaction.atomic():
            self._create_admin()
            trainers = self._create_trainers()
            self._create_groups(trainers)
            self._create_exercises()

        self.stdout.write(self.style.SUCCESS('✓ Начальные данные успешно загружены'))

    def _create_admin(self):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                password='admin123',
                role='admin',
                email='admin@sultan.local',
            )
            self.stdout.write('  ✓ Создан пользователь admin (пароль: admin123)')
        else:
            self.stdout.write('  — Пользователь admin уже существует')

    def _create_trainers(self):
        trainers = []
        for full_name, spec, exp, phone in TRAINERS:
            trainer, created = Trainer.objects.get_or_create(
                full_name=full_name,
                defaults={'specialization': spec, 'experience': exp, 'phone': phone},
            )
            if created:
                # Создаём пользователя-тренера
                login = 'trainer_' + full_name.split()[1].lower()
                if not User.objects.filter(username=login).exists():
                    user = User.objects.create_user(
                        username=login,
                        password='trainer123',
                        role='trainer',
                        linked_to=trainer.pk,
                    )
                self.stdout.write(f'  ✓ Создан тренер: {full_name} (логин: {login}, пароль: trainer123)')
            trainers.append(trainer)
        return trainers

    def _create_groups(self, trainers):
        for i, (name, _, level, max_count) in enumerate(GROUPS):
            trainer = trainers[i % len(trainers)] if trainers else None
            group, created = Group.objects.get_or_create(
                name=name,
                defaults={'trainer': trainer, 'level': level, 'max_count': max_count},
            )
            if created:
                self.stdout.write(f'  ✓ Создана группа: {name}')

                # Создаём демо-атлета
                today = timezone.localdate()
                athlete = Athlete.objects.create(
                    full_name=f'Демо Атлет {i + 1}',
                    group=group,
                    trainer=trainer,
                    enrolled_at=today,
                )
                login = f'athlete_{i + 1}'
                if not User.objects.filter(username=login).exists():
                    User.objects.create_user(
                        username=login,
                        password='athlete123',
                        role='athlete',
                        linked_to=athlete.pk,
                    )
                self.stdout.write(f'    ✓ Создан атлет: {athlete.full_name} (логин: {login}, пароль: athlete123)')

    def _create_exercises(self):
        count = 0
        for name, load_type, unit, desc in EXERCISES:
            _, created = Exercise.objects.get_or_create(
                name=name,
                defaults={'load_type': load_type, 'unit': unit, 'description': desc},
            )
            if created:
                count += 1
        self.stdout.write(f'  ✓ Добавлено упражнений: {count}')
