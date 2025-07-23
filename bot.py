import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

# Загружаем токен
load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")

# Твой Telegram ID (замени на свой)
OWNER_ID = 123456789

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Главное меню
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(KeyboardButton("📸 Записаться"))
main_kb.add(KeyboardButton("💬 Частые вопросы"))
main_kb.add(KeyboardButton("📞 Связаться"))

# Состояния анкеты
class BookingForm(StatesGroup):
    name = State()
    people = State()
    gender = State()
    age = State()
    purpose = State()
    concept = State()
    location = State()
    date = State()

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я бот фотографа из Воронежа 📷\n"
        "Готов помочь тебе записаться на съёмку, ответить на вопросы и связаться с фотографом 💛",
        reply_markup=main_kb
    )

@dp.message_handler(lambda message: message.text == "📸 Записаться")
async def start_booking(message: types.Message):
    await message.answer("Как тебя зовут?")
    await BookingForm.name.set()

@dp.message_handler(state=BookingForm.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько человек будет на съёмке?")
    await BookingForm.people.set()

@dp.message_handler(state=BookingForm.people)
async def get_people(message: types.Message, state: FSMContext):
    await state.update_data(people=message.text)
    await message.answer("Пол участника(ов)? (м/ж/другое)")
    await BookingForm.gender.set()

@dp.message_handler(state=BookingForm.gender)
async def get_gender(message: types.Message, state: FSMContext):
    gender_input = message.text.lower()
    await state.update_data(gender=gender_input)

    if "ж" in gender_input:
        await state.update_data(
            ending="а", gender_word="готова", decided="решила", describe="опиши"
        )
    elif "м" in gender_input:
        await state.update_data(
            ending="", gender_word="готов", decided="решил", describe="опиши"
        )
    else:
        await state.update_data(
            ending="(а)", gender_word="готов(а)", decided="решил(а)", describe="опиши"
        )

    await message.answer("Возраст?")
    await BookingForm.age.set()

@dp.message_handler(state=BookingForm.age)
async def get_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer(
        "Цель съёмки?\n\nВыбери или напиши:\n- для себя\n- для соцсетей\n- деловой портрет\n- в подарок\n- другое"
    )
    await BookingForm.purpose.set()

@dp.message_handler(state=BookingForm.purpose)
async def get_purpose(message: types.Message, state: FSMContext):
    await state.update_data(purpose=message.text)
    data = await state.get_data()
    await message.answer(
        f"Если есть концепция — {data['describe']}. "
        f"Если нет — я с радостью помогу продумать всё: от образа и одежды до настроения съёмки."
    )
    await BookingForm.concept.set()

@dp.message_handler(state=BookingForm.concept)
async def get_concept(message: types.Message, state: FSMContext):
    await state.update_data(concept=message.text)
    data = await state.get_data()
    await message.answer(
        f"Желаемое место съёмки? (студия, природа, или пока не {data['decided']} — помогу выбрать)"
    )
    await BookingForm.location.set()

@dp.message_handler(state=BookingForm.location)
async def get_location(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    await message.answer("Какая дата тебе удобна?")
    await BookingForm.date.set()

@dp.message_handler(state=BookingForm.date)
async def get_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)
    data = await state.get_data()

    summary = (
        f"📸 Новая заявка на фотосессию!\n\n"
        f"👤 Имя: {data['name']}\n"
        f"👥 Кол-во человек: {data['people']}\n"
        f"⚧ Пол: {data['gender']}\n"
        f"🎂 Возраст: {data['age']}\n"
        f"🎯 Цель: {data['purpose']}\n"
        f"🎨 Концепция: {data['concept']}\n"
        f"📍 Локация: {data['location']}\n"
        f"📅 Дата: {data['date']}"
    )

    # клиенту
    await message.answer(
        f"Спасибо! Я всё записал, скоро свяжусь с тобой. "
        f"Ты {data['gender_word']} к чудесной съёмке 😉",
        reply_markup=main_kb
    )
    await message.answer(summary)

    # тебе (фотографу)
    try:
        await bot.send_message(chat_id=OWNER_ID, text=summary)
    except Exception as e:
        logging.error(f"Не удалось отправить сообщение владельцу: {e}")

    await state.finish()

@dp.message_handler(lambda message: message.text == "💬 Частые вопросы")
async def common_questions(message: types.Message):
    await message.answer(
        "Вот что чаще всего спрашивают:\n\n"
        "📍 Где проходят съёмки?\n— В Воронеже и красивых природных локациях рядом\n\n"
        "⏱ Сколько длится?\n— Обычно 1–1.5 часа\n\n"
        "💄 Макияж включён?\n— Да! Работаю с профессиональной визажисткой\n\n"
        "💰 Сколько стоит?\n— Всё зависит от формата. Напиши — подберу вариант под тебя"
    )

@dp.message_handler(lambda message: message.text == "📞 Связаться")
async def contact(message: types.Message):
    await message.answer(
        "Ты можешь написать фотографу напрямую:\n\n"
        "📲 Telegram: @btroot\n"
        "💌 Или просто ответь на это сообщение!"
    )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)