# -*- coding: utf-8 -*-
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.executor import start_polling
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 345927677

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Главное меню
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(KeyboardButton("📸 Записаться"))
main_kb.add(KeyboardButton("👤 Обо мне"))
main_kb.add(KeyboardButton("📁 Портфолио"))
main_kb.add(KeyboardButton("🌐 Соцсети"))
main_kb.add(KeyboardButton("💬 Частые вопросы"))
main_kb.add(KeyboardButton("💲 Стоимость"))
main_kb.add(KeyboardButton("📞 Связаться"))

# Клавиатуры
people_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("1", "2", "3+")
gender_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("👩 Женщина", "👨 Мужчина")
idea_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Да, есть", "Нет, помоги придумать")
location_kb = ReplyKeyboardMarkup(resize_keyboard=True)
location_kb.add("🏠 Студия", "🌳 Природа")
location_kb.add("🌇 Город", "📍 Моя локация", "Другое")
purpose_kb = ReplyKeyboardMarkup(resize_keyboard=True)
purpose_kb.add("💖 Для себя", "📲 Для соцсетей")
purpose_kb.add("💼 Деловой портрет", "🏁 В подарок", "Другое")

# Состояния
class BookingForm(StatesGroup):
    name = State()
    people = State()
    gender = State()
    age = State()
    purpose = State()
    idea = State()
    location = State()
    date = State()

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "Привет! Я помощник Вячеслава📸\nГотова помочь тебе записаться на съёмку, ответить на вопросы и связаться с фотографом.",
        reply_markup=main_kb
    )

@dp.message_handler(lambda m: m.text == "📸 Записаться")
async def booking_start(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if data.get("date"):
        gender = data.get("gender", "")
        suffix = "а" if "жен" in gender.lower() else ""
        await message.answer(f"Ты точно хочешь заполнить анкету второй раз{suffix}?", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add("Да", "Нет"))
        return
    if not data.get("name"):
        await message.answer("Как тебя зовут?")
        await BookingForm.name.set()
    else:
        await message.answer("Сколько человек будет на съёмке?", reply_markup=people_kb)
        await BookingForm.people.set()

@dp.message_handler(lambda m: m.text in ["Да", "Нет"])
async def confirm_restart(message: types.Message, state: FSMContext):
    if message.text == "Да":
        data = await state.get_data()
        await state.finish()
        await state.update_data(name=data.get("name"))
        await message.answer("Сколько человек будет на съёмке?", reply_markup=people_kb)
        await BookingForm.people.set()
    else:
        await message.answer("Хорошо, если что — я рядом)", reply_markup=main_kb)

@dp.message_handler(state=BookingForm.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(f"Приятно познакомиться, {message.text}! Сколько человек будет на съёмке?", reply_markup=people_kb)
    await BookingForm.people.set()

@dp.message_handler(state=BookingForm.people)
async def get_people(message: types.Message, state: FSMContext):
    await state.update_data(people=message.text)
    await message.answer("Пол участника(ов)?", reply_markup=gender_kb)
    await BookingForm.gender.set()

@dp.message_handler(state=BookingForm.gender)
async def get_gender(message: types.Message, state: FSMContext):
    await state.update_data(gender=message.text)
    await message.answer("Сколько тебе лет?", reply_markup=ReplyKeyboardRemove())
    await BookingForm.age.set()

@dp.message_handler(state=BookingForm.age)
async def get_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Для чего тебе нужны фотографии?", reply_markup=purpose_kb)
    await BookingForm.purpose.set()

@dp.message_handler(state=BookingForm.purpose)
async def get_purpose(message: types.Message, state: FSMContext):
    await state.update_data(purpose=message.text)
    await message.answer("Есть идея для съёмки?", reply_markup=idea_kb)
    await BookingForm.idea.set()

@dp.message_handler(state=BookingForm.idea)
async def get_idea(message: types.Message, state: FSMContext):
    await state.update_data(idea=message.text)
    await message.answer("Где хочешь провести съёмку?", reply_markup=location_kb)
    await BookingForm.location.set()

@dp.message_handler(state=BookingForm.location)
async def get_location(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    await message.answer("Укажи удобную для тебя дату 📅", reply_markup=ReplyKeyboardRemove())
    await BookingForm.date.set()

@dp.message_handler(state=BookingForm.date)
async def get_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)
    data = await state.get_data()
    user = message.from_user
    contact = f"@{user.username}" if user.username else f"https://t.me/{user.id}"

    text = (
        f"📸 Новая заявка на фотосессию!\n\n"
        f"👤 Имя: {data['name']}\n"
        f"👥 Кол-во: {data['people']}\n"
        f"♀️ Пол: {data['gender']}\n"
        f"🎂 Возраст: {data['age']}\n"
        f"🎯 Цель: {data['purpose']}\n"
        f"💡 Идея: {data['idea']}\n"
        f"📍 Локация: {data['location']}\n"
        f"📅 Дата: {data['date']}\n"
        f"📱 Контакт: {contact}"
    )

    await message.answer("Спасибо! Я всё записала, скоро свяжусь с тобой 🙂", reply_markup=main_kb)
    try:
        await bot.send_message(chat_id=OWNER_ID, text=text)
    except Exception as e:
        logging.error(f"Не удалось отправить владельцу: {e}")

    await state.finish()

@dp.message_handler(lambda m: m.text == "💬 Частые вопросы")
async def show_faq(message: types.Message):
    await message.answer(
        "📋 Частые вопросы:\n\n"
        "💲 <b>Сколько фотографий я получу?</b>\n"
        "В зависимости от задачи и идеи, ты получишь до 40 тщательно отобранных снимков. Я не отдаю всё подряд — только лучшие кадры, в которых есть история и ты.\n\n"
        "💄 <b>Какие есть услуги?</b>\n"
        "— Помощь с идеей, образом и локацией, выбором студии — включено в стоимость\n"
        "— Аренда студии — оплачивается отдельно\n"
        "— Макияж и укладка, стилист, декоратор, у меня большая команда профессионалов - рассчитывается индивидуально\n\n"
        "🌍 <b>Возможна ли съёмка в другом городе?</b>\n"
        "Конечно! Всё обсуждаемо, я не ограничен одним регионом!",
        parse_mode="HTML"
    )

@dp.message_handler(lambda m: m.text == "📁 Портфолио")
async def portfolio(message: types.Message):
    await message.answer("📷 Портфолио: https://btroot.ru/portraits")

@dp.message_handler(lambda m: m.text == "🌐 Соцсети")
async def socials(message: types.Message):
    await message.answer("📱 Мои соцсети:\n\n👉 <a href=\"https://www.instagram.com/btroot_photo\">Instagram</a>\n👉 <a href=\"https://vk.com/btroot_photo\">ВКонтакте</a>", parse_mode="HTML")

@dp.message_handler(lambda m: m.text == "👤 Обо мне")
async def about_me(message: types.Message):
    await message.answer(
        "Привет! Меня зовут Вячеслав.\n"
        "Я фотограф из Воронежа. Снимаю уже больше 14 лет.\n\n"
        "Когда-то всё началось просто — нравилось замечать красивое, ловить свет и настроение. Потом появились плёнка, ручная проявка, соцсети и первые заказы. За это время было всё: и портреты, и творческие съёмки, и свадьбы, и выписки из роддома, и даже выкупы в подъезде)\n\n"
        "Сейчас мне особенно интересно раскрывать человека в кадре. Не переделывать, не прятать — а наоборот, делать видимым то, что в тебе настоящее.\n"
        "Я помогаю с идеей, образом, локацией, продумываю всё до мелочей. Очень важна атмосфера — чтобы было спокойно, комфортно, по-настоящему.\n\n"
        "Если тебе близок такой подход — пиши, с радостью поснимаем."
    )

@dp.message_handler(lambda m: m.text == "💲 Стоимость")
async def prices(message: types.Message):
    await message.answer(
        "<b>Стандартный пакет</b>\n"
        "5.000 р.\n"
        "Съемочное время — 1 час\n"
        "Помощь в подборе образа, локации\n"
        "Составление детальной идеи и концепции съемки\n"
        "10 — 20 фотографий в авторской ретуши, и это будут не дубли\n"
        "Один образ, несколько сцен\n"
        "Срок получения готовых фотографий от двух дней\n\n"
        "<b>Расширенный пакет</b>\n"
        "9.000 р.\n"
        "Съемочное время — 2 часа\n"
        "Помощь в подборе образа, локации\n"
        "Составление детальной идеи и концепции съемки\n"
        "До 40 фотографий в авторской ретуши\n"
        "Возможность сменить до 2 образов\n"
        "Срок получения готовых фотографий от двух дней",
        parse_mode="HTML"
    )

@dp.message_handler(lambda m: m.text == "📞 Связаться")
async def contact(message: types.Message):
    await message.answer("📢 Напиши фотографу напрямую: @btroot\nИли просто ответь на это сообщение 💌")

if __name__ == '__main__':
    print("Бот запущен ✅")
    start_polling(dp, skip_updates=True)