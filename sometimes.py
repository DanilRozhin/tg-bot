import asyncio
import re
import string
import random
from ForData import *

from datetime import *
from aiogram import *
from aiogram.filters import *
from aiogram.types import *
from aiogram.filters.callback_data import *
from aiogram.utils.keyboard import *
from aiogram.fsm.state import *
from aiogram.fsm.context import FSMContext

# Токен для работы бота
TOKEN = '7777928656:AAH1iOOrjFJyDgkn46lYG8P3C2aLsAK-9gE'

# Инициализация бота, диспетчер и роутер
bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Инициализация клавиатуры
builder = ReplyKeyboardBuilder()
builder.add(KeyboardButton(text='Просмотреть результаты матчей'))
builder.add(KeyboardButton(text='Добавить в избранное'))
builder.add(KeyboardButton(text='Удалить из избранного'))
builder.add(KeyboardButton(text='Матчи избранных сегодня'))
builder.adjust(2)

# Инициализация запрещённых для ввода слов
FORBIDDEN = ['drop', 'table', 'delete', 'create', 'update', 'select', 'set', '*', 'tg_id', 'bottable', 'botclubs', 'allclubs', 'fullclubs']

choosed_league = ''

# Подготовка текста для кнопок о выводе матчей в определённом виде спорта
SPORTS = ['Футбол', 'Волейбол', 'Регби', 'Футзал', 'Биатлон', 'Хоккей', 'ММА', 'Киберспорт', 'Баскетбол', 'Теннис', 'Формула 1', 'Прочие']
pattern = '' # '|'.join(["(" + str(sport) + ")" for sport in SPORTS])
for i in SPORTS:
    pattern += f'({i})|'
pattern = pattern[:-1:]

# Подготовка текста для кнопок добавления в избранное в определённом виде спорта
SPORTS_TO_ADD = {'Футбол': 'football',
                 'Волейбол': 'volleyball',
                 'Фигурное катание': 'figureskating',
                 'Биатлон': 'biathlon',
                 'Хоккей': 'hockey',
                 'Киберспорт': 'cybersport',
                 'Баскетбол': 'basketball',
                 'Теннис': 'tennis',
                 'Формула 1': 'auto',
                 'Прочие': 'other'}
add_pattern = ''
for j in SPORTS_TO_ADD.keys():
    add_pattern += f'({j})|'
add_pattern = add_pattern[:-1:]


# Класс для создания кнопок видов спорта
class MyCallback(CallbackData, prefix='my'):
    name: str
    id: str

# Класс для создания кнопок видов спорта в избранном
class SecondCallback(CallbackData, prefix='second'):
    name_add: str
    id_add: str

# Класс для сбора ответов на функции добавления в избранное и удаление из избранного
class Form(StatesGroup):
    league = State()
    club = State()
    deleting = State()
    add_club = State()

# Создание клавиатуры для просмотра матчей за сегодняшний день
async def create_keyboard():
    builder = InlineKeyboardBuilder()
    builder_id = 1
    for sport in SPORTS:
        builder.button(
        text=sport,
        callback_data=MyCallback(name=sport, id=str(builder_id))
    )
        builder_id += 1
    return builder.adjust(2).as_markup()

# Создание клавиатуры для добавления в избранное
async def add_keyboard():
    add_builder = InlineKeyboardBuilder()
    add_builder_id = 1
    for sport in SPORTS_TO_ADD:
        add_builder.button(
            text = sport,
            callback_data=SecondCallback(name_add=sport, id_add=str(add_builder_id))
        )
        add_builder_id += 1
    return add_builder.adjust(2).as_markup()


# Добавление в избранное, выбор спорта
@dp.callback_query(SecondCallback.filter(re.fullmatch(pattern=add_pattern, string=str(F.name))))
async def second_callback_foo(query: CallbackQuery, callback_data: SecondCallback, state: FSMContext):
    await query.message.answer(f'Выбрано: {callback_data.name_add}')
    global choosed_league
    choosed_league = callback_data.name_add
    await query.message.answer(f'Напишите команду/спортсмена для добавления в избранное')
    await state.set_state(Form.add_club)

# Добавление в избранное, выбор клуба/спортсмена
@router.message(Form.add_club)
async def cmd_add_club(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    global choosed_league
    # print(choosed_league)
    # sport_type_db = SPORTS_TO_ADD[choosed_league]
    checking = message.text.split()
    for w in checking:
        if w.lower() in FORBIDDEN:
            await message.answer('Попробуйте заново.')
            return
    sub_result = await get_from_fullclubs(choosed_league)
    # print(choosed_league)
    # print('sub_result', sub_result)
    # print(result)
    # print(message.text)
    needed_club = []
    for i in range(len(sub_result)):
        if sub_result[i].lower() == message.text.lower().strip():
            needed_club.append([sub_result[i], sub_result[i].lower()])
    my_res = await get_from_bottable(message.chat.id)
    my_res_low = []
    for m in range(len(my_res)):
        my_res_low.append(my_res[m].lower())
    # print(my_res)
    # print(my_res_low)
    # print(needed_club)
    if message.text.lower() in my_res_low:
        await message.answer(f'{my_res[my_res_low.index(message.text.lower())]} уже есть в избранных')
    elif needed_club:
        if needed_club[0][1] == message.text.lower().strip():
            await insert_into_bottable(message.chat.id, needed_club[0][0])
            await message.answer(f'Добавлено: {needed_club[0][0]}.')
    else:
        await message.answer('Не найдено. Попробуйте еще раз.')
    choosed_league = ''

# Сбор и вывод информации о событиях на сегодня
@dp.callback_query(MyCallback.filter(re.fullmatch(pattern=pattern, string=str(F.name))))
async def my_callback_foo(query: CallbackQuery, callback_data: MyCallback):
    global url
    if url:
        answer, cnt = await view_dicts(callback_data.name)
        # print(answer)
        for i in answer:
            if len(i) != 0:
                await query.message.answer(i)
        await query.message.answer(f'{callback_data.name}\nКоличество событий на сегодня: {str(cnt)}.')

# Добавление основных кнопок в бота
@dp.message(CommandStart())
async def reply_builder(message: Message):
    await message.answer(
        "Привет! Я буду помогать тебе следить за миром спорта.",
        reply_markup=builder.as_markup(resize_keyboard=True),
        parse_mode='HTML'
    )


# Вывод данных об избранных клубах/командах
@router.message(F.text == 'Матчи избранных сегодня')
async def cmd_today_like(message: Message):
    global result, url
    # print(result)
    if not result:
        page_text = await get_page(url)
        await make_dicts(page_text, url[-2:] + "." + url[-5:-3])
        answer, cnt = await view_dicts(message.chat.id)
        for i in answer:
            if len(i) != 0:
                await message.answer(i, parse_mode="HTML")
        await message.answer(f'Количество событий с участием избранных сегодня: {str(cnt)}.')
    else:
        answer, cnt = await view_dicts(message.chat.id)
        for i in answer:
            if len(i) != 0:
                await message.answer(i, parse_mode="HTML")
        await message.answer(f'Количество событий с участием избранных сегодня: {str(cnt)}.')

# Кнопка для удаления из избранного
@router.message(F.text == 'Удалить из избранного')
async def cmd_delete(message: Message, state: FSMContext):
    my_clubs = await get_from_bottable(message.chat.id)
    sms_del = ''
    for cd in my_clubs:
        sms_del += cd + '\n'
    if len(sms_del) > 0:
        await message.reply('Выберите клуб, который нужно удалить:' + '\n\n' + sms_del)
        await state.set_state(Form.deleting)
    else:
        await message.reply('Нет клубов в избранном.')


# Удаление клуба из избранных в бд
@router.message(Form.deleting)
async def cmd_del_club(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    checking = message.text.split()
    for w in checking:
        if w.lower() in FORBIDDEN:
            await message.answer('Попробуйте заново.')
            return

    my_clubs = await get_from_bottable(message.chat.id, message.text.lower())
    if my_clubs:
        await delete_from_bottable(my_clubs[0])
        await message.answer(f'Удалено: {my_clubs[0]}.')
    else:
        await message.answer('Нет избранных клубов/спортсменов с таким названием.')



# Добавление клуба в избарнное - вывод лиг
@router.message(F.text == 'Добавить в избранное')
async def cmd_add(message: Message, state: FSMContext):
    # await state.set_state(Form.league)
    await message.reply('Выберите вид спорта:', reply_markup= await add_keyboard())


# Кнопка для вывода матчей за текущий день
@router.message(F.text == 'Просмотреть результаты матчей')
async def cmd_results(message: Message):
    await message.reply("Выберите спорт для просмотра результатов сегодняшних матчей:", reply_markup= await create_keyboard())


async def view_dicts(sport):
    global result, to_update
    sub_result = sorted(result, key=lambda x: x['time'])
    matches = []
    part = ''
    cnt = 0
    if isinstance(sport, str):
        for event in range(len(sub_result)):
            if sport in ['Авто', 'Фигурное катание', 'Биатлон']:
                if sub_result[event]['sport_type'] == sport:
                    part += sub_result[event]['time'] + ', ' + sub_result[event]['status'] + '\n' + sub_result[event]['team1'] + '\n\n'
                    cnt += 1
                if len(part) >= 4000:
                    matches.append(part)
                    part = ''
            else:
                if sub_result[event]['sport_type'] == sport:
                    part += sub_result[event]['time'] + ', ' + sub_result[event]['status'] + '\n' + sub_result[event]['team1'] + ' ' + sub_result[event]['score'] + ' ' + sub_result[event]['team2'] + '\n\n'
                    cnt += 1
                if len(part) >= 4000:
                    matches.append(part)
                    part = ''
        matches.append(part)
        sub_result = []
        return matches, cnt
    else:
        there_is = []
        user_clubs = await get_from_bottable(int(sport))
        for event in range(len(sub_result)):
            for c in user_clubs:
                # if c in sub_result[event]['team1'] or c in sub_result[event]['team2']:
            # if sub_result[event]['team1'] in user_clubs or sub_result[event]['team2'] in user_clubs:
                if type(sub_result[event]['team2']) not in [list]:
                    m = sub_result[event]['time'] + ', ' + sub_result[event]['status'] + '\n' + sub_result[event]['team1'] + ' ' + sub_result[event]['score'] + ' ' + sub_result[event]['team2'] + '\n\n'
                    if sub_result[event]['team1'].find(" / ") == -1:
                        if (sub_result[event]['team1'].startswith(c) or sub_result[event]['team2'].startswith(c)) and m not in there_is:
                            part += m
                            cnt += 1
                            there_is.append(m)
                        if sub_result[event]['team1'].startswith(c) or sub_result[event]['team2'].startswith(c):
                            part = part.replace(c, '<b>' + c + '</b>')
                        if len(part) >= 4000:
                            # await bot.send_message(chat_id=user_id, text=matches)
                            matches.append(part)
                            part = ''
                    else:
                        first, second = sub_result[event]['team1'].split(" / ")
                        third, fourth = sub_result[event]['team2'].split(" / ")
                        if (first.startswith(c) or second.startswith(c) or third.startswith(c) or fourth.startswith(c)) and m not in there_is:
                            part += m
                            cnt += 1
                            there_is.append(m)
                        if first.startswith(c) or second.startswith(c) or third.startswith(c) or fourth.startswith(c):
                            part = part.replace(c, '<b>' + c + '</b>')
                        if len(part) >= 4000:
                            # await bot.send_message(chat_id=user_id, text=matches)
                            matches.append(part)
                            part = ''
                else:
                    if c in sub_result[event]['team2']:
                        m = sub_result[event]['time'] + ', ' + sub_result[event]['status'] + '\n' + sub_result[event]['team1']
                        if m not in there_is:
                            there_is.append(m)
                            part += m + '\n\n'
                            cnt += 1
                        part = part.replace(m, m + '\n' + '<b>' + c + '</b>', 1)
                        # m = sub_result[event]['time'] + ', ' + sub_result[event]['status'] + '\n' + sub_result[event]['team1'] + '\n' + c + '\n\n'
                        # part += m
                        # cnt += 1
        matches.append(part)
        # sub_result = []
        return matches, cnt

    # print(*sub_result, sep="\n")
    # print("\n\nTo update:")
    # print(*to_update, sep="\n")

async def update_cycle():
    global result, to_update, almost_ready
    while True:
        now = datetime.now()
        almost_ready = []
        if now.minute % 5 == 0:
            async with asyncio.TaskGroup() as tg:
                for i in range(len(to_update)):
                    tg.create_task(update_line(i, now))

            almost_ready.sort(reverse=True)
            for i in almost_ready:
                to_update.pop(i)

        now = datetime.now()

        if now.hour * 60 + now.minute >= 2100 * 60:
            await dp.stop_polling()
            await bot.close()
            break

        await asyncio.sleep((5 - now.minute % 5) * 60 - now.second - now.microsecond / 1000000)

# Обработка неподходящих сообщений
exc = string.ascii_letters + string.digits + string.punctuation + 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
lst_exc = [str(i) for i in exc]

# Функция обработки неподходящих сообщений
@router.message(F.text[0].lower().in_(lst_exc))
async def cmd_exception_fifth(message: Message):
    rand_msg = ['Я не такой разговорчивый, но могу помочь со списком избранных!',
                'Как смотришь на то, чтоб я показал тебе сегодняшние матчи?',
                'Может быть, подберешь себе любимые команды?',
                'Когда-нибудь мы сможем поговорить с тобой! Но сейчас предлагаю посмотреть сегодняшние матчи!',
                'Ты можешь использовать кнопки для разговора со мной!']
    await message.answer(
        random.choice(rand_msg),
        reply_markup=builder.as_markup(resize_keyboard=True),
    )

# Запуск функций
async def main():
    await data_main()
    async with asyncio.TaskGroup() as tg:
        tg.create_task(update_cycle())
        tg.create_task(dp.start_polling(bot))

if __name__ == '__main__':
    asyncio.run(main())
