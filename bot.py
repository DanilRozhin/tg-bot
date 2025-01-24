import asyncio
import requests
import datetime
from bs4 import BeautifulSoup

from aiogram import *
from aiogram.filters import *
from aiogram.types import *

TOKEN = '7777928656:AAGCd2EEuEZwszefm6OPDoPiqPEe__-qfpU'

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
        await bot.send_message(1232626150, 'Real Madrid is probably playing today')
        # await bot.send_message(418223763, 'Real Madrid is probably playing today')
    # await bot.send_message(418223763, 'Купи автору печенек')
    await bot.send_message(1232626150, 'Код выполнен')
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
