import asyncio
import requests
import datetime
import os
from bs4 import BeautifulSoup

from aiogram import *
from aiogram.filters import *
from aiogram.types import *

TOKEN = os.getenv('TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Hello!')

@dp.message()
async def cmd_text(message: Message):
    user_id = message.chat.id
    try:
        await message.answer(message.text)
    except:
        await message.answer('Sorry, I can\'t understand this message yet')

async def main():
    today_date = datetime.date.today()

    url = 'https://www.championat.com/stat/#' + str(today_date)
    response = requests.get(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    })
    bs = str(BeautifulSoup(response.text, 'lxml'))
    if 'Реал Мадрид' in bs:
        await bot.send_message(1232626150, 'Real Madrid maybe playing today')
    # await bot.send_message(418223763, 'Плановое выполнение скрипта, сообщите автору об успешном выполнении программы')
    await bot.send_message(1232626150, 'Код выполнен')
    # await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
