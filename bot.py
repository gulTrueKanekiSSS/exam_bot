import datetime

from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from data_base import db, Birthday
from keyboards import moves, moves_with_nt


bot = Bot(token='6024132241:AAFGnX1FE7E2S7T1mqC_mad8JrQ2yDv_Wcw')
dp = Dispatcher(bot, storage=MemoryStorage())


class BirthdayWait(StatesGroup):
    wait_notice_name = State()
    wait_photo = State()
    wait_txt = State()


class UpdateRecord(StatesGroup):
    wait_notice = State()
    wait_move = State()
    wait_txt_new_notice = State()


@dp.message_handler(commands=['start'])
async def welcome_message(message: types.Message):
    await bot.send_sticker(message.from_user.id, sticker='CAACAgQAAxkBAAJG02R4TlHesVWCgD0ob2oD-1fwaniPAAK9CQACelwRUzpqVCTmeOrfLwQ')
    await bot.send_message(message.from_user.id,
                           'Приветствую тебя в нашем боте по сохранению дат дней рождения, <strong>вот список того что ты можешь сделать: Создать запись, удалить, редактировать, смотреть свои замтеки</strong>\nЧтобы их менять, перейди в свои записи, выбери существующую и что ты хочешь с ней сделать',
                           parse_mode='html',
                           reply_markup=moves
                           )


@dp.message_handler(Text(equals="Добавить запись"))
async def choose_name(message: types.Message, state=FSMContext):
    await state.set_state(BirthdayWait.wait_notice_name.state)
    await message.answer('Введи имя друга:')


@dp.message_handler(content_types=['text'], state=BirthdayWait.wait_notice_name)
async def ok(message: types.Message, state=FSMContext):
    await state.update_data(friend_name=message.text)
    await state.set_state(BirthdayWait.wait_photo.state)
    skip = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    skip.add('Пропустить')
    await bot.send_message(message.from_user.id, 'Прикрепите фотографию вашего друга, вы можете пропустить этап', reply_markup=skip)


@dp.message_handler(content_types=['photo', 'text'], state=BirthdayWait.wait_photo)
async def save_photo_friend(message:types.Message, state: FSMContext):
    if message.text == 'Пропустить':
        await state.update_data(choose_photo=None)
        await state.set_state(BirthdayWait.wait_txt.state)
        await message.answer('Укажи поздравление:')
    elif message.text:
        await message.answer("Пожалуйста введите текст или пропустите этап")
    else:
        await state.update_data(choose_photo=message.photo)
        await state.set_state(BirthdayWait.wait_txt.state)
        await message.answer('Укажи поздравление:')


@dp.message_handler(content_types=['text'], state=BirthdayWait.wait_txt)
async def save_notice(message: types.Message, state=FSMContext):
    await state.update_data(friend_congratulations=message.text)
    data = await state.get_data()
    try:
        data_for_db = {
            'owner': message.from_user.username,
            'owner_id': message.from_user.id,
            'friend_name': data.get('friend_name'),
            'friend_congratulations': data.get('friend_congratulations'),
            'photo': data.get('choose_photo')[-1]['file_id']
        }
    except TypeError:
        data_for_db = {
            'owner': message.from_user.username,
            'owner_id': message.from_user.id,
            'friend_name': data.get('friend_name'),
            'friend_congratulations': data.get('friend_congratulations'),
            'photo': None
        }

    friend = Birthday(**data_for_db)
    with db.session.begin():
        db.session.add(friend)
    await message.answer('Я все записал', reply_markup=moves)
    await state.finish()


@dp.message_handler(Text(equals="Мои записи"))
async def patch_notice(message: types.Message, state: FSMContext):
    with db.session.begin():
        birthdays = db.session.query(Birthday).filter(Birthday.owner_id == message.from_user.id).all()
        db.session.close()
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    if len(birthdays) == 0:
        await message.answer('У тебя пока что нету заметок о днях рождения', reply_markup=moves)
    else:
        for birthday in birthdays:
            records_for_user = KeyboardButton(text=birthday.friend_name)
            kb.add(records_for_user)
        await state.set_state(UpdateRecord.wait_notice.state)
        await message.answer('Вот такие заметки o днях рождения у тебя сейчас имеются', reply_markup=kb)


@dp.message_handler(content_types=['text'], state=UpdateRecord.wait_notice)
async def decide_notice(message: types.Message, state: FSMContext):
    await state.update_data(friend_name=message.text)
    await state.set_state(UpdateRecord.wait_move.state)
    with db.session.begin():
        birthday = db.session.query(Birthday).filter(Birthday.friend_name == message.text).all()
        db.session.close()
    try:
        if birthday[0].photo is not None:
            await bot.send_photo(message.from_user.id ,photo=f'{birthday[0].photo}', caption=f'<strong>Вот ваша заметка дня рождения {birthday[0].friend_name}:</strong>\n\n{birthday[0].friend_congratulations}', parse_mode='html')
            await message.answer(f'Выбери дальнейшее действие:', reply_markup=moves_with_nt)
        else:
            await message.answer(f'<strong>Вот ваша заметка дня рождения {birthday[0].friend_name}:</strong>\n\n{birthday[0].friend_congratulations}', parse_mode='html')
            await message.answer(f'Выбери дальнейшее действие:', reply_markup=moves_with_nt)
    except Exception as e:
        print(e)
        await message.answer('у тебя нету такой заметки о дне рождения')


@dp.message_handler(content_types=['text'], state=UpdateRecord.wait_move)
async def decide_move(message: types.Message, state: FSMContext):
    await state.update_data(move=message.text)
    data = await state.get_data()
    if message.text == 'Удалить':
        with db.session.begin():
            db.session.delete(db.session.query(Birthday).filter(Birthday.friend_name == data.get('friend_name'))[0])
            db.session.commit()
        await message.answer('Готово', reply_markup=moves)
        await state.finish()
    elif message.text == 'Редактировать':
        await state.set_state(UpdateRecord.wait_txt_new_notice.state)
        with db.session.begin():
            birthday = db.session.query(Birthday).filter(Birthday.friend_name == data.get('friend_name')).all()
            await message.answer('Скопируй текст своего поздравления, отредактируй и отправь снова')
            await message.answer(f'{birthday[0].friend_congratulations}')
    elif message.text == 'Посмотреть':
        with db.session.begin():
            birthday = db.session.query(Birthday).filter(Birthday.friend_name == data.get('friend_name')).all()
            if birthday[0] is not None:
                await bot.send_photo(message.from_user.id, photo=f'{birthday[0].photo}',
                                     caption=f'<strong>Вот ваша заметка дня рождения {birthday[0].friend_name}:</strong>\n\n{birthday[0].friend_congratulations}',
                                     parse_mode='html',
                                     reply_markup=moves)

                await state.finish()
            else:
                await message.answer(f'{birthday[0].friend_congratulations}', reply_markup=moves)
                await state.finish()
    else:
        await message.answer('Таких команд у меня нету', reply_markup=moves)
        await state.finish()


@dp.message_handler(content_types=['text'], state=UpdateRecord.wait_txt_new_notice)
async def wait_new_notice(message: types.Message, state: FSMContext):
    await state.update_data(new_txt=message.text)
    data = await state.get_data()
    with db.session.begin():
        birthday = db.session.query(Birthday).filter(Birthday.friend_name == data.get('friend_name')).all()
        print(birthday[0])
        birthday[0].friend_congratulations = data.get('new_txt')
        db.session.commit()
    await message.answer('Готово', reply_markup=moves)
    await state.finish()



if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True)
