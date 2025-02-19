from playwright.async_api import async_playwright
import datetime
import asyncio
from ForDBs import *


# Подготовка ссылки на сайт
today_date = datetime.date.today()
url = 'https://www.championat.com/stat/#' + str(today_date)

# Инициализация массива для данных и для данных требующих обновления, имён для словарей и триггеров для поиска информации
result = []
to_update = []
almost_ready = []
names = ["date", "time", "sport_type", "sport_subtype", "team1", "team2", "score", "status", "supref"]
triggers = ['<div class=\"mc-sport__title\">',                                                                          # 0
            '<div class=\"mc-sport-tournament__drop-block\">',                                                          # 1
            '/_',                                                                                                       # 2
            '/',                                                                                                        # 3
            '>',                                                                                                        # 4
            '<',                                                                                                        # 5
            '\"results-item__title-date\">',                                                                            # 6
            '__item _time\">',                                                                                          # 7
            '<div>',                                                                                                    # 8
            '</div>',                                                                                                   # 9
            '<span>',                                                                                                   # 10
            '<span class="table-item__name">',                                                                          # 11
            '</span>',                                                                                                  # 12
            '__team-name">',                                                                                            # 13
            '<div class="results-item__title-name">',                                                                   # 14  for MMA
            ' — ',                                                                                                      # 15  for MMA
            '"results-item__result-main"',                                                                              # 16
            'results-item__status',                                                                                     # 17
            'results-item__result',                                                                                     # 18 for MMA
            'results__status',                                                                                          # 19
            'tennis-results__set _goal',                                                                                # 20 for volleyball
            'a href=\"',                                                                                                # 21
            'noscript',                                                                                                 # 22
            'data-key="0"',                                                                                             # 23
            '</table>',                                                                                                 # 24
            'table-item__name">',                                                                                       # 25
            '"match-info__status">',                                                                                    # 26
            '"match-info__score-total">']                                                                               # 27


# Запуск браузера для получения кода сайта
async def get_page(surl):
    async with async_playwright() as p:
        while True:
            try:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                await page.goto(surl, timeout=0)
                page_text = await page.content()
                await browser.close()
                return page_text
            except:
                print('not now')
                await asyncio.sleep(300)


# Разделение кода страницы на виды спорта
async def make_dicts(string, curdate):
    global triggers
    string = string.split(triggers[22])[-3]
    async with asyncio.TaskGroup() as tg:
        for substring in (string.split(triggers[0]))[1:]:
            tg.create_task(get_sports(substring, curdate))


# Поиск видов спорта и разделение по лигам
async def get_sports(string, curdate):
    global triggers
    async with asyncio.TaskGroup() as tg:
        substring = string
        start = substring.find(triggers[4])
        end = substring.find(triggers[5], start)
        sport_type = substring[start + 1:end]
        for substring in string.split(triggers[1])[1:]:
            if sport_type not in ["Авто", "Киберспорт", "Прочие"]:
                sport_subtype = ''
            else:
                start = substring.find(triggers[2]) + 2
                end = substring.find(triggers[3], start)
                sport_subtype = substring[start:end]
            tg.create_task(
                    get_matches(substring, sport_type=sport_type, sport_subtype=sport_subtype, curdate=curdate))


# Поиск подвидов спорта и разделение на матчи, поиск ссылки для получения доп инфы
async def get_matches(string, sport_type, sport_subtype, curdate):
    global triggers
    async with asyncio.TaskGroup() as tg:
        for substring in string.split(triggers[21])[1:]:
            end = substring.find("\"")
            supref = "https://www.championat.com" + substring[:end]
            if supref.count("www") == 1:
                start = substring.find(triggers[6]) + len(triggers[6])
                if start == -1 + len(triggers[6]):
                    start = substring.find(triggers[7]) + len(triggers[7])
                    if start != -1 + len(triggers[7]):
                        tg.create_task(make_line(substring[start:], sport_type, sport_subtype, curdate, supref))
                else:
                    tg.create_task(make_line(substring[start:], sport_type, sport_subtype, curdate, supref))


# Разделение информации матча на дату, время, команды, счёт и статус
async def make_line(string, sport_type, sport_subtype, curdate, supref):
    global result, names, triggers
    substring = string
    line = dict()

    start = substring.find(triggers[8]) + 5
    end = substring.find(triggers[9])
    date_time = substring[start:end].strip()

    if triggers[10] in date_time:
        start = date_time.find(triggers[10]) + 6
        date = date_time[start: start + 5]
        time = date_time[start + 12:].strip()
    else:
        date = curdate
        time = date_time

    line[names[0]] = date
    line[names[1]] = time

    line[names[2]] = sport_type
    line[names[3]] = sport_subtype

    start = substring.find(triggers[11]) + len(triggers[11])
    if start != -1 + len(triggers[11]):
        end = substring.find(triggers[12], start)
    else:
        start = substring.find(triggers[13]) + len(triggers[13])
        if start == -1 + len(triggers[13]):
            start = substring.find(triggers[14]) + len(triggers[14])

        end = substring.find(triggers[9], start)

    teams = substring[start:end].strip()

    if teams.count(triggers[15]) == 1 and "(" not in teams:
        team1, team2 = teams.split(triggers[15])
    else:
        team1 = teams
        start = substring.find(triggers[11], end) + len(triggers[11])
        if start != -1 + len(triggers[11]):
            end = substring.find(triggers[12], start)
        else:
            start = substring.find(triggers[13], end) + len(triggers[13])
            end = substring.find(triggers[9], start)
        team2 = substring[start:end].strip()
        if start == -1 + len(triggers[13]):
            team2 = await get_participants(await get_page(supref))
    if sport_type == "Теннис":
        team1 = team1 if "(" not in team1 else team1[:team1.find("(")].strip()
        team2 = team2 if "(" not in team2 else team2[:team2.find("(")].strip()

    line[names[4]] = team1
    line[names[5]] = team2

    start = substring.find(triggers[17]) + len(triggers[17])
    if start != -1 + len(triggers[17]):
        start = substring.find(triggers[8], start) + len(triggers[8])
        end = substring.find(triggers[9], start)
        status = substring[start:end].strip()
    else:
        start = substring.find(triggers[19])
        start = substring.find(triggers[4], start) + len(triggers[4])
        end = substring.find(triggers[5], start)
        status = substring[start:end].strip()

    start = substring.find(triggers[16]) + len(triggers[16])
    if start != -1 + len(triggers[16]):
        start = substring.find(triggers[4], start) + len(triggers[4])
        end = substring.find(triggers[5], start)
        score = substring[start:end].strip()
    else:
        start = substring.find(triggers[20]) + len(triggers[20])
        if start != -1 + len(triggers[20]):
            start = substring.find(triggers[4], start) + len(triggers[4])
            end = substring.find(triggers[9], start)
            score1 = substring[start:end].strip()
            if not score1:
                score1 = 0
            start = substring.find(triggers[20], start) + len(triggers[20])
            start = substring.find(triggers[4], start) + len(triggers[4])
            end = substring.find(triggers[9], start)
            score2 = substring[start:end].strip()
            if not score2:
                score2 = 0
            score = f"{score1} : {score2}"
        else:
            start = substring.find(triggers[18]) + len(triggers[18])
            start = substring.find(triggers[4], start) + len(triggers[4])
            end = substring.find(triggers[9], start)
            score = substring[start:end].strip()

    if not score:
        score = "0 : 0"
        if not team2 or team2 == [] or isinstance(team2, list):
            score = ""

    line[names[6]] = score
    line[names[7]] = status
    line[names[8]] = supref

    index = len(result)
    result.append(line)
    if team2 == [] or status not in ["Окончено", "Окончен", "Отменён", "Перенесён"]:
        line["index"] = index
        to_update.append(line)


# Получение участников для соревнований "Авто", "Фигурное катание", "Лыжи", "Биатлон"
async def get_participants(page_text):
    start = page_text.rfind(triggers[23]) + len(triggers[23])
    if start != -1 + len(triggers[23]):
        end = page_text.find(triggers[24], start)
        participants = page_text[start:end]
        array_of_participants = [participant[:participant.find(triggers[5])].strip()
                                 for participant in participants.split(triggers[25])[1:]
                                 if "\n" not in participant[:participant.find(triggers[5])]]
        return array_of_participants
    return []


# Получение статуса матча/соревнования по его собственной странице (для обновления results)
async def get_status(page_text):
    start = page_text.find(triggers[26]) + len(triggers[26])
    end = page_text.find(triggers[9], start)
    status = page_text[start:end].strip()
    return status


# Получение результата матча/соревнования по его собственной странице (для обновления results)
async def get_score(page_text):
    start = page_text.find(triggers[27]) + len(triggers[27])
    if start == -1 + len(triggers[27]):
        end = page_text.find(triggers[9], start)
        prescore = page_text[start:end].strip()
        if triggers[12] not in prescore:
            if not prescore:
                prescore = "0 : 0"
            return prescore
        else:
            start = prescore.find(triggers[5])
            end = prescore.find(triggers[4])
            score = prescore[:start].strip() + " : " + prescore[end:].strip()
            if not score:
                score = "0 : 0"
            return score
    return "0 : 0"

# Обновление строки в списке для обновления
async def update_line(line, now):
    global result, to_update, almost_ready
    gamestart = to_update[line][names[1]].split(":")
    gametime = int(gamestart[0]) * 60 + int(gamestart[1])
    if now.strftime("%d.%m") != to_update[line][names[0]]:
        gametime += 24 * 60

    if not to_update[line][names[5]]:
        page_text = await get_page(to_update[line][names[8]])
        to_update[line][names[5]] = await get_participants(page_text)
        to_update[line][names[7]] = await get_status(page_text)
        result[to_update[line]["index"]][names[5]] = to_update[line][names[5]]
        result[to_update[line]["index"]][names[7]] = to_update[line][names[7]]
        await add_to_fullclubs(to_update[line])
    elif (to_update[line][names[6]] and
        to_update[line][names[7]] not in ["Окончено", "Окончен", "Отменён", "Перенесён"] and
        gametime < now.hour * 60 + now.minute):
        page_text = await get_page(to_update[line][names[8]])
        to_update[line][names[6]] = await get_score(page_text)
        to_update[line][names[7]] = await get_status(page_text)
        result[to_update[line]["index"]][names[6]] = to_update[line][names[6]]
        result[to_update[line]["index"]][names[7]] = to_update[line][names[7]]
    elif not to_update[line][names[6]] and to_update[line][names[7]] not in ["Окончено", "Окончен", "Отменён", "Перенесён"]:
        page_text = await get_page(to_update[line][names[8]])
        to_update[line][names[7]] = await get_status(page_text)
        result[to_update[line]["index"]][names[7]] = to_update[line][names[7]]

    if to_update[line][names[7]] in ["Окончено", "Окончен", "Отменён", "Перенесён"]:
        almost_ready.append(line)

async def data_main():
    global url
    print("start")
    page_text = await get_page(url)
    print("ready pages")
    await make_dicts(page_text, url[-2:] + "." + url[-5:-3])
    print("ready data")
    await db_main(result)
