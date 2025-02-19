import aiosqlite as sql

# Нам нужны базы данных для:
# 1. Хранения информации об избранных командах каждого пользователя.
# 2. Хренения информации о клубах и командах в целом, по их видам спорта.
# 3. Хранения сообщений для их очистки. - Не уверен, что они нужны.

# Ключи для трансфера. Если убрать строчку, то в новой бд категория не добавится
to_transfer = {'football': 'Футбол',
                 'volleyball': 'Волейбол',
                 'figureskating': 'Фигурное катание',
                 'biathlon': 'Биатлон',
                 'hockey': 'Хоккей',
                 'basketball': 'Баскетбол',
                 'tennis': 'Теннис'}

to_sport_subtype = {'counterstrike': 'Counterstrike',
                    'dota2': 'Dota 2',
                    'rally': 'Ралли',
                    'f1': 'Формула 1',
                    'gp2': 'Формула 2',
                    'moto': 'Мотоспорт',
                    'otherauto': 'Другие авто',
                    'snooker': 'Снукер',
                    '': '',
                    'aqua': 'Плавание',
                    'dakar': 'Дакар',
                    'others': 'Прочее'}

# Создание баз данных
async def create_databases():
    async with sql.connect('botbase.db') as db:
        await db.execute('CREATE TABLE IF NOT EXISTS bottable '
                         '(id INTEGER PRIMARY KEY AUTOINCREMENT,'
                         'tg_id INTEGER NOT NULL,'
                         'club VARCHAR(70) NOT NULL,'
                         'UNIQUE(tg_id, club))')
        await db.commit()

        await db.execute('CREATE TABLE IF NOT EXISTS fullclubs '
                         '(id INTEGER PRIMARY KEY AUTOINCREMENT,'
                         'sport_type VARCHAR(20) NOT NULL,'
                         'sport_subtype VARCHAR(20),'
                         'club VARCHAR(70) NOT NULL,'
                         'UNIQUE(sport_type, sport_subtype, club))')
        await db.commit()


async def add_to_fullclubs(dicts=[]):
    async with sql.connect('botbase.db') as db:
        async with db.execute('SELECT club FROM fullclubs') as cursor:
            teams = [i[0].replace('u39', "\'") for i in await cursor.fetchall()]
            to_add = []
            for i in dicts:
                if isinstance(i['team2'], list):
                    for j in i['team2']:
                        if j not in teams:
                            to_add.append([i['sport_type'], to_sport_subtype[i['sport_subtype']], j.replace("\'", 'u39')])
                else:
                    if i['team1'].find(" / ") == -1:
                        if i["team1"] not in teams:
                            to_add.append([i['sport_type'], to_sport_subtype[i['sport_subtype']], i['team1'].replace("\'", 'u39')])
                    else:
                        first, second = i['team1'].split(" / ")
                        if first not in teams:
                            to_add.append([i['sport_type'], to_sport_subtype[i['sport_subtype']], first.replace("\'", 'u39')])
                        if second not in teams:
                            to_add.append([i['sport_type'], to_sport_subtype[i['sport_subtype']], second.replace("\'", 'u39')])
                    if i['team2'].find(" / ") == -1:
                        if i["team2"] not in teams:
                            to_add.append([i['sport_type'], to_sport_subtype[i['sport_subtype']], i['team2'].replace("\'", 'u39')])
                    else:
                        first, second = i['team2'].split(" / ")
                        if first not in teams:
                            to_add.append([i['sport_type'], to_sport_subtype[i['sport_subtype']], first.replace("\'", 'u39')])
                        if second not in teams:
                            to_add.append([i['sport_type'], to_sport_subtype[i['sport_subtype']], second.replace("\'", 'u39')])

        for i in to_add:
            await db.execute('''INSERT INTO fullclubs (sport_type, sport_subtype, club)
                VALUES ('{}', '{}', '{}')'''.format(i[0], i[1], i[2]))
            await db.commit()



async def transfer():
    try:
        async with sql.connect('botbase_1.db') as db:
                async with db.execute('SELECT sport_type, club FROM allclubs') as cursor:
                    sport_team = [[i[0], i[1].replace("\'", 'u39')] for i in await cursor.fetchall()]
                async with db.execute('SELECT tg_id, club FROM bottable') as cursor:
                    tg_team = [[i[0], i[1].replace("\'", 'u39')] for i in await cursor.fetchall()]

        async with sql.connect('botbase.db') as db:
            for i in sport_team:
                if i[0] in to_transfer.keys():
                    await db.execute('''INSERT INTO fullclubs (sport_type, sport_subtype, club)
                    VALUES ('{}', '{}', '{}')'''.format(to_transfer[i[0]], '', i[1]))
                    await db.commit()
                elif i[0] in to_transfer.values():
                    await db.execute('''INSERT INTO fullclubs (sport_type, sport_subtype, club)
                    VALUES ('{}', '{}', '{}')'''.format(i[0], '', i[1]))
                    await db.commit()

            for i in tg_team:
                await db.execute('''INSERT INTO bottable (tg_id, club)
                    VALUES ('{}', '{}')'''.format(i[0], i[1]))
                await db.commit()
    except:
        nothing = ''
    try:
        async with sql.connect('botbase_1.db') as db:
                async with db.execute('SELECT sport_type, sport_subtype, club FROM fullclubs') as cursor:
                    sport_team = [[i[0], i[1], i[2].replace("\'", 'u39')] for i in await cursor.fetchall()]
                async with db.execute('SELECT tg_id, club FROM bottable') as cursor:
                    tg_team = [[i[0], i[1].replace("\'", 'u39')] for i in await cursor.fetchall()]

        async with sql.connect('botbase.db') as db:
            for i in sport_team:
                if i[0] in to_transfer.keys():
                    await db.execute('''INSERT INTO fullclubs (sport_type, sport_subtype, club)
                    VALUES ('{}', '{}', '{}')'''.format(to_transfer[i[0]], i[1], i[2]))
                    await db.commit()
                elif i[0] in to_transfer.values():
                    await db.execute('''INSERT INTO fullclubs (sport_type, sport_subtype, club)
                    VALUES ('{}', '{}', '{}')'''.format(i[0], '', i[1]))
                    await db.commit()

            for i in tg_team:
                await db.execute('''INSERT INTO bottable (tg_id, club)
                    VALUES ('{}', '{}')'''.format(i[0], i[1]))
                await db.commit()
    except:
        nothing = ''


async def get_from_fullclubs(choosed_league):
    async with sql.connect('botbase.db') as db:
        async with db.execute("""SELECT club FROM fullclubs WHERE sport_type = '{}'""".format(choosed_league)) as cursor:
            print('get_from_fullclubs')
            ans = [i[0].replace("u39", "\'") for i in await cursor.fetchall()]
            # print(ans)
            return ans


async def get_from_bottable(id, club=1):
    async with sql.connect('botbase.db') as db:
        async with db.execute("""SELECT club FROM bottable WHERE tg_id = '{}'""".format(id)) as cursor:
            print('get_from_bottable')
            # print([i[0].replace("u39", "\'") for i in await cursor.fetchall()])
            full_answer = [i[0].replace("u39", "\'") for i in await cursor.fetchall()]
            answer = []
            if club != 1:
                for i in full_answer:
                    if i.lower() == club:
                        answer.append(i)
                return answer
            else:
                return full_answer



async def insert_into_bottable(id, club):
    async with sql.connect('botbase.db') as db:
        await db.execute("""INSERT INTO bottable (tg_id, club, club_low) VALUES ("{}", "{}", "{}")""".format(id, club.replace("\'", "u39"), club.replace("\'", "u39").lower()))
        await db.commit()


async def delete_from_bottable(club):
    async with sql.connect('botbase.db') as db:
        await db.execute("""DELETE FROM bottable WHERE club = '{}'""".format(club.replace("\'", "u39")))
        await db.commit()



async def db_main(dicts=[]):
    await create_databases()
    await add_to_fullclubs(dicts)
    print("ready dbs")
