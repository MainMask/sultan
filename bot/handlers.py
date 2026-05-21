import os
import sys
import django

# Инициализация Django ORM внутри бота
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sultan.settings')
django.setup()

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from django.utils import timezone
from django.db.models import Sum, Count

from core.models import User, Athlete, Trainer, Training
from .keyboards import main_menu_trainer, main_menu_athlete

router = Router()


def _get_user_by_telegram(telegram_id: int):
    """Ищет пользователя Django по telegram_id, сохранённому в first_name как маркер."""
    # telegram_id хранится в поле User.username как 'tg_<id>' при регистрации через бота
    try:
        return User.objects.get(username=f'tg_{telegram_id}')
    except User.DoesNotExist:
        return None


def _format_training(t) -> str:
    parts = [f'• {t.date.strftime("%d.%m.%Y")} | {t.exercise.name}']
    details = []
    if t.sets:
        details.append(f'{t.sets}×{t.reps or "?"}')
    if t.weight:
        details.append(f'{t.weight} кг')
    if t.duration:
        details.append(f'{t.duration} мин')
    if details:
        parts.append('  ' + ', '.join(details))
    return '\n'.join(parts)


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = _get_user_by_telegram(message.from_user.id)
    if not user:
        await message.answer(
            '👋 Добро пожаловать в SULTAN!\n\n'
            'Ваш аккаунт не привязан к системе.\n'
            'Обратитесь к администратору для привязки Telegram-аккаунта.\n\n'
            'ℹ️ Команды:\n/results — последние тренировки\n/stats — статистика за месяц'
        )
        return

    if user.is_trainer():
        await message.answer(
            f'👋 Привет, тренер!\nВы вошли как {user.username}.',
            reply_markup=main_menu_trainer(),
        )
    elif user.is_athlete():
        athlete = None
        if user.linked_to:
            try:
                athlete = Athlete.objects.get(pk=user.linked_to)
            except Athlete.DoesNotExist:
                pass
        name = athlete.full_name if athlete else user.username
        await message.answer(
            f'👋 Привет, {name}!\nДобро пожаловать в SULTAN.',
            reply_markup=main_menu_athlete(),
        )
    else:
        await message.answer(f'👋 Привет, администратор {user.username}!')


@router.message(Command('results'))
@router.message(F.text.in_(['🏋️ Мои последние тренировки', '🏋️ Последние тренировки']))
async def cmd_results(message: Message):
    user = _get_user_by_telegram(message.from_user.id)
    if not user:
        await message.answer('❌ Аккаунт не привязан. Обратитесь к администратору.')
        return

    if user.is_athlete():
        if not user.linked_to:
            await message.answer('Профиль атлета не найден.')
            return
        try:
            athlete = Athlete.objects.get(pk=user.linked_to)
        except Athlete.DoesNotExist:
            await message.answer('Профиль атлета не найден.')
            return
        trainings = Training.objects.filter(athlete=athlete).select_related('exercise').order_by('-date')[:5]
        if not trainings:
            await message.answer('📋 У вас пока нет тренировок.')
            return
        text = '📋 *Последние 5 тренировок:*\n\n'
        text += '\n\n'.join(_format_training(t) for t in trainings)

    elif user.is_trainer():
        trainer = None
        if user.linked_to:
            try:
                trainer = Trainer.objects.get(pk=user.linked_to)
            except Trainer.DoesNotExist:
                pass
        athletes = Athlete.objects.filter(trainer=trainer) if trainer else Athlete.objects.none()
        trainings = Training.objects.filter(athlete__in=athletes).select_related('exercise', 'athlete').order_by('-date')[:10]
        if not trainings:
            await message.answer('📋 Нет последних тренировок.')
            return
        text = '📋 *Последние тренировки ваших атлетов:*\n\n'
        for t in trainings:
            text += f'👤 {t.athlete.full_name}\n{_format_training(t)}\n\n'
    else:
        await message.answer('Эта команда недоступна для администратора.')
        return

    await message.answer(text, parse_mode='Markdown')


@router.message(Command('stats'))
@router.message(F.text.in_(['📈 Моя статистика', '📈 Статистика за месяц']))
async def cmd_stats(message: Message):
    user = _get_user_by_telegram(message.from_user.id)
    if not user:
        await message.answer('❌ Аккаунт не привязан.')
        return

    today = timezone.localdate()
    month_start = today.replace(day=1)

    if user.is_athlete():
        if not user.linked_to:
            await message.answer('Профиль атлета не найден.')
            return
        try:
            athlete = Athlete.objects.get(pk=user.linked_to)
        except Athlete.DoesNotExist:
            await message.answer('Профиль не найден.')
            return

        stats = Training.objects.filter(
            athlete=athlete, date__gte=month_start, date__lte=today,
        ).aggregate(
            cnt=Count('id'),
            total_duration=Sum('duration'),
        )
        cnt = stats['cnt'] or 0
        dur = stats['total_duration'] or 0
        await message.answer(
            f'📊 *Статистика за {today.strftime("%B %Y")}:*\n\n'
            f'🏋️ Тренировок: *{cnt}*\n'
            f'⏱ Общее время: *{dur} мин*',
            parse_mode='Markdown',
        )

    elif user.is_trainer():
        trainer = None
        if user.linked_to:
            try:
                trainer = Trainer.objects.get(pk=user.linked_to)
            except Trainer.DoesNotExist:
                pass
        athletes = Athlete.objects.filter(trainer=trainer) if trainer else Athlete.objects.none()
        stats = Training.objects.filter(
            athlete__in=athletes, date__gte=month_start, date__lte=today,
        ).aggregate(cnt=Count('id'))
        await message.answer(
            f'📊 *Статистика группы за {today.strftime("%B %Y")}:*\n\n'
            f'👥 Атлетов: *{athletes.count()}*\n'
            f'🏋️ Тренировок в этом месяце: *{stats["cnt"] or 0}*',
            parse_mode='Markdown',
        )
    else:
        await message.answer('Статистика администратора недоступна через бота.')


@router.message(F.text == 'ℹ️ Помощь')
async def cmd_help(message: Message):
    await message.answer(
        '📖 *Доступные команды:*\n\n'
        '/start — начало работы\n'
        '/results — последние тренировки\n'
        '/stats — статистика за текущий месяц\n\n'
        'Полный доступ к системе: откройте веб-интерфейс SULTAN.',
        parse_mode='Markdown',
    )


@router.message(F.text == '📊 Мои атлеты')
async def cmd_my_athletes(message: Message):
    user = _get_user_by_telegram(message.from_user.id)
    if not user or not user.is_trainer():
        await message.answer('❌ Команда доступна только тренерам.')
        return

    trainer = None
    if user.linked_to:
        try:
            trainer = Trainer.objects.get(pk=user.linked_to)
        except Trainer.DoesNotExist:
            pass

    athletes = Athlete.objects.filter(trainer=trainer).order_by('full_name') if trainer else Athlete.objects.none()
    if not athletes:
        await message.answer('У вас нет атлетов.')
        return

    text = f'👥 *Ваши атлеты ({athletes.count()}):*\n\n'
    for a in athletes:
        text += f'• {a.full_name}'
        if a.group:
            text += f' [{a.group.name}]'
        text += '\n'

    await message.answer(text, parse_mode='Markdown')
