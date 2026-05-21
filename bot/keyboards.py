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
