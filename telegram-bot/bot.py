import sqlite3
from datetime import datetime, date
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
import asyncio
import os

TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

def init_db():
    conn = sqlite3.connect('budget.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            category TEXT,
            note TEXT,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_expense(user_id, amount, category, note=""):
    conn = sqlite3.connect('budget.db')
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO expenses (user_id, amount, category, note, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, amount, category, note, date.today().isoformat()))
    conn.commit()
    conn.close()

def get_sum(user_id, period):
    today = date.today()
    if period == 'day':
        start = today.isoformat()
    elif period == 'month':
        start = today.replace(day=1).isoformat()
    else:
        start = today.replace(month=1, day=1).isoformat()
    conn = sqlite3.connect('budget.db')
    cur = conn.cursor()
    cur.execute('''
        SELECT SUM(amount) FROM expenses 
        WHERE user_id = ? AND date >= ?
    ''', (user_id, start))
    result = cur.fetchone()[0]
    conn.close()
    return result if result else 0

init_db()

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "💰 Привет! Я твой финансовый помощник.\n\n"
        "Вводи расходы так:\n"
        "/add 500 еда\n"
        "/today - расходы за сегодня\n"
        "/month - за этот месяц\n"
        "/year - за этот год"
    )

@dp.message(Command("add"))
async def add(message: Message):
    args = message.text.split(maxsplit=2)
    if len(args) < 2:
        await message.answer("❌ Напиши: /add 500 еда")
        return
    try:
        amount = float(args[1])
    except:
        await message.answer("❌ Сумма должна быть числом")
        return
    category = args[2].split()[0] if len(args) > 2 else "Прочее"
    note = " ".join(args[2].split()[1:]) if len(args) > 2 and len(args[2].split()) > 1 else ""
    add_expense(message.from_user.id, amount, category, note)
    await message.answer(f"✅ Записано: {amount} ₽ ({category})")

@dp.message(Command("today"))
async def today(message: Message):
    total = get_sum(message.from_user.id, 'day')
    await message.answer(f"📅 Сегодня потрачено: {total} ₽")

@dp.message(Command("month"))
async def month(message: Message):
    total = get_sum(message.from_user.id, 'month')
    await message.answer(f"📆 За этот месяц: {total} ₽")

@dp.message(Command("year"))
async def year(message: Message):
    total = get_sum(message.from_user.id, 'year')
    await message.answer(f"📈 За этот год: {total} ₽")

async def main():
    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())
