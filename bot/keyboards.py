from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_trainer() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='📊 Мои атлеты'), KeyboardButton(text='🏋️ Последние тренировки')],
            [KeyboardButton(text='📈 Статистика за месяц'), KeyboardButton(text='ℹ️ Помощь')],
        ],
        resize_keyboard=True,
    )


def main_menu_athlete() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='🏋️ Мои последние тренировки')],
            [KeyboardButton(text='📈 Моя статистика'), KeyboardButton(text='ℹ️ Помощь')],
        ],
        resize_keyboard=True,
    )


def inline_menu_trainer() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📊 Мои атлеты', callback_data='my_athletes')],
        [InlineKeyboardButton(text='🏋️ Последние тренировки', callback_data='results')],
        [InlineKeyboardButton(text='📈 Статистика за месяц', callback_data='stats')],
        [InlineKeyboardButton(text='📥 Отчёт за месяц (CSV)', callback_data='report')],
    ])


def inline_menu_athlete() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🏋️ Мои тренировки', callback_data='results')],
        [InlineKeyboardButton(text='📈 Моя статистика', callback_data='stats')],
        [InlineKeyboardButton(text='📥 Скачать отчёт (CSV)', callback_data='report')],
    ])


def back_to_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='↩️ Главное меню', callback_data='menu')],
    ])
