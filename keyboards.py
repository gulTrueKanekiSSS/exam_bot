from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

moves = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
move_1 = KeyboardButton(text="Добавить запись")
move_2 = KeyboardButton(text="Мои записи")
move_3 = KeyboardButton(text="Курс валют")
moves.add(move_1, move_2, move_3)

moves_with_nt = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
item_1 = KeyboardButton(text='Удалить')
item_2 = KeyboardButton(text='Редактировать')
item_3 = KeyboardButton(text='Посмотреть')
moves_with_nt.add(item_3, item_2, item_1)

valutes = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
valute_1 = KeyboardButton(text='USD')
valute_2 = KeyboardButton(text='EUR')
valutes.add(valute_1, valute_2)

is_true = ReplyKeyboardMarkup(resize_keyboard=True)
closed = KeyboardButton(text='Закончить отслеживание курса валюты')