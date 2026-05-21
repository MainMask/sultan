import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sultan.settings')
django.setup()

from aiogram import Router, F
import io
import csv

from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, BufferedInputFile
from aiogram.filters import CommandStart, Command
from asgiref.sync import sync_to_async
from django.utils import timezone
from django.db.models import Sum, Count

from core.models import User, Athlete, Trainer, Training
from bot.keyboards import inline_menu_trainer, inline_menu_athlete, back_to_menu

MONTHS_RU = {
    1: 'январь', 2: 'февраль', 3: 'март', 4: 'апрель',
    5: 'май', 6: 'июнь', 7: 'июль', 8: 'август',
    9: 'сентябрь', 10: 'октябрь', 11: 'ноябрь', 12: 'декабрь',
}

router = Router()


# --- Async DB helpers ---

@sync_to_async
def get_user_by_telegram(telegram_id: int):
    try:
        return User.objects.get(username=f'tg_{telegram_id}')
    except User.DoesNotExist:
        return None


@sync_to_async
def get_trainer(linked_to):
    try:
        return Trainer.objects.get(pk=linked_to)
    except Trainer.DoesNotExist:
        return None


@sync_to_async
def get_athlete(linked_to):
    try:
        return Athlete.objects.select_related('group', 'trainer').get(pk=linked_to)
    except Athlete.DoesNotExist:
        return None


@sync_to_async
def get_last_trainings_for_athlete(athlete_pk, limit=5):
    return list(
        Training.objects.filter(athlete_id=athlete_pk)
        .select_related('exercise')
        .order_by('-date')[:limit]
    )


@sync_to_async
def get_last_trainings_for_trainer(trainer_pk, limit=10):
    return list(
        Training.objects.filter(athlete__trainer_id=trainer_pk)
        .select_related('exercise', 'athlete')
        .order_by('-date')[:limit]
    )


@sync_to_async
def get_athlete_month_stats(athlete_pk):
    today = timezone.localdate()
    month_start = today.replace(day=1)
    return Training.objects.filter(
        athlete_id=athlete_pk,
        date__gte=month_start,
        date__lte=today,
    ).aggregate(cnt=Count('id'), total_duration=Sum('duration'))


@sync_to_async
def get_trainer_month_stats(trainer_pk):
    today = timezone.localdate()
    month_start = today.replace(day=1)
    athletes_count = Athlete.objects.filter(trainer_id=trainer_pk).count()
    trainings_count = Training.objects.filter(
        athlete__trainer_id=trainer_pk,
        date__gte=month_start,
        date__lte=today,
    ).count()
    return athletes_count, trainings_count


@sync_to_async
def get_trainer_athletes(trainer_pk):
    return list(
        Athlete.objects.filter(trainer_id=trainer_pk)
        .select_related('group')
        .order_by('full_name')
    )


@sync_to_async
def get_athlete_month_trainings(athlete_pk):
    today = timezone.localdate()
    month_start = today.replace(day=1)
    return list(
        Training.objects.filter(
            athlete_id=athlete_pk,
            date__gte=month_start,
            date__lte=today,
        ).select_related('exercise').order_by('date')
    )


@sync_to_async
def get_trainer_month_trainings(trainer_pk):
    today = timezone.localdate()
    month_start = today.replace(day=1)
    return list(
        Training.objects.filter(
            athlete__trainer_id=trainer_pk,
            date__gte=month_start,
            date__lte=today,
        ).select_related('exercise', 'athlete').order_by('athlete__full_name', 'date')
    )


# --- Formatting ---

def _fmt_training(t) -> str:
    line = f'• {t.date.strftime("%d.%m.%Y")} | {t.exercise.name}'
    details = []
    if t.sets:
        details.append(f'{t.sets}×{t.reps or "?"}')
    if t.weight:
        details.append(f'{t.weight} кг')
    if t.duration:
        details.append(f'{t.duration} мин')
    if details:
        line += '  —  ' + ', '.join(details)
    return line


# --- Handlers ---

async def _remove_reply_keyboard(message: Message):
    """Удаляет старую reply-клавиатуру невидимым сообщением."""
    msg = await message.answer('…', reply_markup=ReplyKeyboardRemove())
    await msg.delete()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = await get_user_by_telegram(message.from_user.id)
    await _remove_reply_keyboard(message)

    if not user:
        await message.answer(
            '👋 Добро пожаловать в <b>SULTAN</b>!\n\n'
            'Ваш Telegram-аккаунт не привязан к системе.\n'
            f'Сообщите администратору ваш ID: <code>{message.from_user.id}</code>'
        )
        return

    if user.is_trainer():
        trainer = await get_trainer(user.linked_to) if user.linked_to else None
        name = trainer.full_name if trainer else user.username
        await message.answer(
            f'👋 Привет, тренер <b>{name}</b>!\n\nВыберите раздел:',
            reply_markup=inline_menu_trainer(),
        )
    elif user.is_athlete():
        athlete = await get_athlete(user.linked_to) if user.linked_to else None
        name = athlete.full_name if athlete else user.username
        await message.answer(
            f'👋 Привет, <b>{name}</b>!\n\nВыберите раздел:',
            reply_markup=inline_menu_athlete(),
        )
    else:
        await message.answer(f'👋 Привет, администратор <b>{user.username}</b>!')


@router.message(Command('results'))
async def cmd_results(message: Message):
    user = await get_user_by_telegram(message.from_user.id)
    if not user:
        await message.answer(
            f'❌ Аккаунт не привязан. Ваш ID: <code>{message.from_user.id}</code>'
        )
        return

    if user.is_athlete():
        if not user.linked_to:
            await message.answer('Профиль атлета не найден.')
            return
        trainings = await get_last_trainings_for_athlete(user.linked_to)
        if not trainings:
            await message.answer('📋 У вас пока нет тренировок.', reply_markup=back_to_menu())
            return
        lines = '\n'.join(_fmt_training(t) for t in trainings)
        await message.answer(f'📋 <b>Последние тренировки:</b>\n\n{lines}', reply_markup=back_to_menu())

    elif user.is_trainer():
        if not user.linked_to:
            await message.answer('Профиль тренера не найден.')
            return
        trainings = await get_last_trainings_for_trainer(user.linked_to)
        if not trainings:
            await message.answer('📋 Нет последних тренировок.', reply_markup=back_to_menu())
            return
        lines = '\n'.join(
            f'<b>{t.athlete.full_name}</b>\n{_fmt_training(t)}' for t in trainings
        )
        await message.answer(f'📋 <b>Последние тренировки атлетов:</b>\n\n{lines}', reply_markup=back_to_menu())
    else:
        await message.answer('Эта команда недоступна для администратора.')


@router.message(Command('stats'))
async def cmd_stats(message: Message):
    user = await get_user_by_telegram(message.from_user.id)
    if not user:
        await message.answer(
            f'❌ Аккаунт не привязан. Ваш ID: <code>{message.from_user.id}</code>'
        )
        return

    today = timezone.localdate()
    month_label = f'{MONTHS_RU[today.month]} {today.year}'

    if user.is_athlete():
        if not user.linked_to:
            await message.answer('Профиль не найден.')
            return
        stats = await get_athlete_month_stats(user.linked_to)
        cnt = stats['cnt'] or 0
        dur = stats['total_duration'] or 0
        await message.answer(
            f'📊 <b>Статистика за {month_label}:</b>\n\n'
            f'🏋️ Тренировок: <b>{cnt}</b>\n'
            f'⏱ Общее время: <b>{dur} мин</b>',
            reply_markup=back_to_menu(),
        )
    elif user.is_trainer():
        if not user.linked_to:
            await message.answer('Профиль не найден.')
            return
        athletes_count, trainings_count = await get_trainer_month_stats(user.linked_to)
        await message.answer(
            f'📊 <b>Статистика за {month_label}:</b>\n\n'
            f'👥 Атлетов: <b>{athletes_count}</b>\n'
            f'🏋️ Тренировок в этом месяце: <b>{trainings_count}</b>',
            reply_markup=back_to_menu(),
        )
    else:
        await message.answer('Статистика администратора недоступна через бота.')


@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer(
        '📖 <b>Команды:</b>\n\n'
        '/start — главное меню\n'
        '/results — последние тренировки\n'
        '/stats — статистика за текущий месяц',
        reply_markup=back_to_menu(),
    )


# --- Callback handlers ---

@router.callback_query(F.data == 'menu')
async def cb_menu(callback: CallbackQuery):
    await callback.answer()
    user = await get_user_by_telegram(callback.from_user.id)
    if not user:
        await callback.message.answer('❌ Аккаунт не привязан.')
        return

    if user.is_trainer():
        trainer = await get_trainer(user.linked_to) if user.linked_to else None
        name = trainer.full_name if trainer else user.username
        await callback.message.answer(
            f'👋 Привет, тренер <b>{name}</b>!\n\nВыберите раздел:',
            reply_markup=inline_menu_trainer(),
        )
    elif user.is_athlete():
        athlete = await get_athlete(user.linked_to) if user.linked_to else None
        name = athlete.full_name if athlete else user.username
        await callback.message.answer(
            f'👋 Привет, <b>{name}</b>!\n\nВыберите раздел:',
            reply_markup=inline_menu_athlete(),
        )


@router.callback_query(F.data == 'results')
async def cb_results(callback: CallbackQuery):
    await callback.answer()
    user = await get_user_by_telegram(callback.from_user.id)
    if not user:
        await callback.message.answer('❌ Аккаунт не привязан.')
        return

    if user.is_athlete():
        if not user.linked_to:
            await callback.message.answer('Профиль атлета не найден.', reply_markup=back_to_menu())
            return
        trainings = await get_last_trainings_for_athlete(user.linked_to)
        if not trainings:
            await callback.message.answer('📋 У вас пока нет тренировок.', reply_markup=back_to_menu())
            return
        lines = '\n'.join(_fmt_training(t) for t in trainings)
        await callback.message.answer(f'📋 <b>Последние тренировки:</b>\n\n{lines}', reply_markup=back_to_menu())

    elif user.is_trainer():
        if not user.linked_to:
            await callback.message.answer('Профиль тренера не найден.', reply_markup=back_to_menu())
            return
        trainings = await get_last_trainings_for_trainer(user.linked_to)
        if not trainings:
            await callback.message.answer('📋 Нет последних тренировок.', reply_markup=back_to_menu())
            return
        lines = '\n'.join(
            f'<b>{t.athlete.full_name}</b>\n{_fmt_training(t)}' for t in trainings
        )
        await callback.message.answer(
            f'📋 <b>Последние тренировки атлетов:</b>\n\n{lines}',
            reply_markup=back_to_menu(),
        )


@router.callback_query(F.data == 'stats')
async def cb_stats(callback: CallbackQuery):
    await callback.answer()
    user = await get_user_by_telegram(callback.from_user.id)
    if not user:
        await callback.message.answer('❌ Аккаунт не привязан.')
        return

    today = timezone.localdate()
    month_label = f'{MONTHS_RU[today.month]} {today.year}'

    if user.is_athlete():
        if not user.linked_to:
            await callback.message.answer('Профиль не найден.', reply_markup=back_to_menu())
            return
        stats = await get_athlete_month_stats(user.linked_to)
        cnt = stats['cnt'] or 0
        dur = stats['total_duration'] or 0
        await callback.message.answer(
            f'📊 <b>Статистика за {month_label}:</b>\n\n'
            f'🏋️ Тренировок: <b>{cnt}</b>\n'
            f'⏱ Общее время: <b>{dur} мин</b>',
            reply_markup=back_to_menu(),
        )
    elif user.is_trainer():
        if not user.linked_to:
            await callback.message.answer('Профиль не найден.', reply_markup=back_to_menu())
            return
        athletes_count, trainings_count = await get_trainer_month_stats(user.linked_to)
        await callback.message.answer(
            f'📊 <b>Статистика за {month_label}:</b>\n\n'
            f'👥 Атлетов: <b>{athletes_count}</b>\n'
            f'🏋️ Тренировок в этом месяце: <b>{trainings_count}</b>',
            reply_markup=back_to_menu(),
        )


@router.callback_query(F.data == 'my_athletes')
async def cb_my_athletes(callback: CallbackQuery):
    await callback.answer()
    user = await get_user_by_telegram(callback.from_user.id)
    if not user or not user.is_trainer():
        await callback.message.answer('❌ Команда доступна только тренерам.')
        return
    if not user.linked_to:
        await callback.message.answer('Профиль тренера не найден.', reply_markup=back_to_menu())
        return
    athletes = await get_trainer_athletes(user.linked_to)
    if not athletes:
        await callback.message.answer('У вас нет атлетов.', reply_markup=back_to_menu())
        return
    lines = '\n'.join(
        f'• {a.full_name}' + (f' [{a.group.name}]' if a.group else '')
        for a in athletes
    )
    await callback.message.answer(
        f'👥 <b>Ваши атлеты ({len(athletes)}):</b>\n\n{lines}',
        reply_markup=back_to_menu(),
    )


@router.callback_query(F.data == 'report')
async def cb_report(callback: CallbackQuery):
    await callback.answer()
    user = await get_user_by_telegram(callback.from_user.id)
    if not user:
        await callback.message.answer('❌ Аккаунт не привязан.')
        return

    today = timezone.localdate()
    month_label = f'{MONTHS_RU[today.month]} {today.year}'

    output = io.StringIO()
    writer = csv.writer(output)

    if user.is_athlete():
        if not user.linked_to:
            await callback.message.answer('Профиль не найден.', reply_markup=back_to_menu())
            return
        trainings = await get_athlete_month_trainings(user.linked_to)
        if not trainings:
            await callback.message.answer('📋 Тренировок за этот месяц нет.', reply_markup=back_to_menu())
            return
        writer.writerow(['Дата', 'Упражнение', 'Подходы', 'Повторения', 'Вес (кг)', 'Длительность (мин)'])
        for t in trainings:
            writer.writerow([t.date, t.exercise.name, t.sets or '', t.reps or '', t.weight or '', t.duration or ''])
        filename = f'report_{today.strftime("%Y_%m")}.csv'

    elif user.is_trainer():
        if not user.linked_to:
            await callback.message.answer('Профиль не найден.', reply_markup=back_to_menu())
            return
        trainings = await get_trainer_month_trainings(user.linked_to)
        if not trainings:
            await callback.message.answer('📋 Тренировок за этот месяц нет.', reply_markup=back_to_menu())
            return
        writer.writerow(['Атлет', 'Дата', 'Упражнение', 'Подходы', 'Повторения', 'Вес (кг)', 'Длительность (мин)'])
        for t in trainings:
            writer.writerow([t.athlete.full_name, t.date, t.exercise.name, t.sets or '', t.reps or '', t.weight or '', t.duration or ''])
        filename = f'report_trainer_{today.strftime("%Y_%m")}.csv'
    else:
        await callback.message.answer('Отчёт недоступен для администратора.')
        return

    csv_bytes = output.getvalue().encode('utf-8-sig')  # BOM для корректного открытия в Excel
    await callback.message.answer_document(
        BufferedInputFile(csv_bytes, filename=filename),
        caption=f'📊 Отчёт за {month_label}',
        reply_markup=back_to_menu(),
    )
