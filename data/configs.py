import asyncio
import uuid
from data.loader import papp, config
from pyrogram.raw.functions.contacts import ResolveUsername
from data.loader import bot
from data.texts import *
import keyboards.inline_keyboards as inline_keyboards
from database.database import collection, ObjectId
from datetime import datetime, timedelta, timezone
from aiogram.utils.exceptions import ChatNotFound, BotKicked, BotBlocked
from aiogram.types import CallbackQuery, InlineKeyboardButton
import yookassa
from yookassa import Configuration
import time
import pytz
import re
import traceback

async def is_current_time_in_range(times:list):
    try:
        answ = False
        for time in times:
            if time['t_i'] == 'В указанную дату':
                if await get_msk_date() == time['time'].split(' ')[0]:
                    str = time['time'].split(' ')[1].split('-')
                    start_str, end_str = str[0], str[1]
                    moscow_tz = pytz.timezone('Europe/Moscow')
                    current_time = datetime.now(moscow_tz).time()
                    start_time = datetime.strptime(start_str, '%H:%M').time()
                    end_time = datetime.strptime(end_str, '%H:%M').time()
                    if start_time <= current_time <= end_time:
                        answ = True
                        break
                    else: continue
                else: continue

            if time['t_i'] == 'В выходные':
                if await is_weekend() == True:
                    str = time['time'].split('-')
                    start_str, end_str = str[0], str[1]
                    moscow_tz = pytz.timezone('Europe/Moscow')
                    current_time = datetime.now(moscow_tz).time()
                    start_time = datetime.strptime(start_str, '%H:%M').time()
                    end_time = datetime.strptime(end_str, '%H:%M').time()
                    if start_time <= current_time <= end_time:
                        answ = True
                        break
                    else: continue
                else: continue

            str = time['time'].split('-')
            start_str, end_str = str[0], str[1]
            moscow_tz = pytz.timezone('Europe/Moscow')
            current_time = datetime.now(moscow_tz).time()
            start_time = datetime.strptime(start_str, '%H:%M').time()
            end_time = datetime.strptime(end_str, '%H:%M').time()
            if start_time <= current_time <= end_time:
                answ = True
                break
            else:
                continue

        return answ
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

def create_paydial_payment(amount, days, gmail):
    try:
        yookassa.Configuration.account_id = config['account_id']
        yookassa.Configuration.secret_key = config['secret_key']
        idempotence_key = str(uuid.uuid4())
        payment = yookassa.Payment.create({
            "amount": {
                "value": amount,
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"https://t.me/{t_bot_user}"
            },
            "receipt": {
                "customer": {
                    "email": gmail
                },
                "items": [{
                    "description": f"Доступ к чату на {days} дней",
                    "amount": {
                        "value": amount,
                        "currency": "RUB"
                    },
                    "vat_code": 1,
                    "quantity": 1
                }]
            },
            "description": f"Доступ к чату на {days} дней",
            "capture": True
        }, idempotence_key)

        url = payment.confirmation.confirmation_url
        return url, payment.id
    except:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

def paydial_getpaymentstatus(pid):
    try:
        status = yookassa.Payment.find_one(pid)
        if status.status == 'succeeded':
            return True
        else:
            return False
    except:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

def cancel_paydial_payment(pid):
    try:
        cancelst = yookassa.Payment.cancel(pid)
    except:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

async def is_weekend():
    current_date = datetime.today()
    return current_date.weekday() in [5, 6]

async def get_chat_name(group_id):
    try:
        chat = await bot.get_chat(group_id)
        return f'<a href="{chat.invite_link}">{chat.title}</a>'
    except:
        return 'NoName'

# async def get_chat_users():
#     async with papp:
#         async for user in papp.get_chat_members(chat_id=-1001749926117):
#             print(user)

async def notify_adbout_ban(user_id, group):
    try:
        async with papp:
            user = await papp.get_chat(user_id)
            await papp.send_message(chat_id=user_id, text=f'<b>{user.first_name}</b>, вы были заблокированы в группе <b>{group}</b> :(')
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

async def get_vorchun_last_msg(chat_id, index_of_chat, invite_link):
    try:
        db = await collection.find_one({"chats": str(chat_id)})
        text = f'{t_start_text.format(bot_user=t_bot_user)}\n\n<b>Функция:</b> "Ворчун"'
        if db['settings'][index_of_chat]['afk']['warning'] != 'None': text = db['settings'][index_of_chat]['afk']['warning']
        answ = False
        in_chat = await bot.get_chat_member(chat_id, user_id=5982267286)
        async with papp:
            if in_chat.status == 'left':
                chat = await papp.join_chat(invite_link)

            async for message in papp.get_chat_history(chat_id=chat_id, limit=1):
                if message.from_user.id == 6371385454 or message.from_user.id == 6224863552:
                    answ = True

            return answ
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

async def get_paydialcustomers(users_dict, page:int, index_of_chat, group_id, msg_id, chat_id, update_date, clb=None):
    try:
        udikt = []
        maximum = page * 10
        users_found = 0
        for i in users_dict:
            if users_found < maximum:
                username = 'Неизвестно'
                try:
                    user = await bot.get_chat(i["id"])
                    username = user.first_name
                except:
                    pass
                udikt.append({"un": username, "ui": i["id"], "end": [i["paydialogue_payed_for"], await format_unix_to_date(i["paydialogue_payed_for"])]})
                users_found += 1
            else:
                break

        udikt = [udikt[i:i + 10] for i in range(0, len(udikt), 10)]

        if len(udikt) != 0 and page >= 1 and (len(udikt) != (page - 1) and len(udikt) > (page - 1)):
            await collection.find_one_and_update({'user_id': chat_id}, {"$set": {f'settings.{index_of_chat}.paydialcuspage': page}})
            await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=update_date, chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b> Купили\n\nАктивность / Имя пользователя / Дата окончания доступа', reply_markup=await inline_keyboards.generate_paydialogue_customers(False, udikt[page - 1], len(udikt), page))
        elif page < 1 or len(udikt) >= page or not (len(udikt) != (page - 1) and len(udikt) > (page - 1)) and len(udikt) != 0:
            await bot.answer_callback_query(clb)
        else:
            await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=update_date, chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b> Купили\n\nНет покупателей', reply_markup=await inline_keyboards.generate_paydialogue_customers(True))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

async def is_chat_in(chat_id):
    db = await collection.find_one({"chats": str(chat_id)})
    if db != None: return True
    else: return False

async def get_msk_unix():
    tz_msk = timezone(timedelta(hours=3))
    current_time_msk = datetime.now(tz_msk)
    unix_time_msk = int(current_time_msk.timestamp())
    return unix_time_msk

async def update_time(unix_time):
    dt_utc = datetime.fromtimestamp(unix_time, timezone.utc)
    dt_msk = dt_utc + timedelta(hours=3)
    formatted_time = dt_msk.strftime("%d.%m.%Y в %H:%M")
    return formatted_time

async def convert_to_unix_timestamp_msk(date_string):
    msk_timezone = pytz.timezone('Europe/Moscow')
    datetime_object = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    datetime_object_msk = msk_timezone.localize(datetime_object)
    unix_timestamp = int(datetime_object_msk.timestamp())
    return unix_timestamp

async def format_unix_to_date(unix_timestamp):
    dt_utc = datetime.utcfromtimestamp(unix_timestamp)
    utc_timezone = pytz.timezone('UTC')
    dt_utc = utc_timezone.localize(dt_utc)
    msk_timezone = pytz.timezone('Europe/Moscow')
    dt_msk = dt_utc.astimezone(msk_timezone)
    formatted_date = dt_msk.strftime('%d.%m.%Y')
    return formatted_date

async def subtract_days_from_unix_time(unix_time, days_to_subtract):
    msk_timezone = pytz.timezone('Europe/Moscow')
    datetime_object_utc = datetime.utcfromtimestamp(unix_time)
    datetime_object_msk = msk_timezone.localize(datetime_object_utc)
    new_datetime_object_msk = datetime_object_msk - timedelta(days=days_to_subtract)
    new_unix_time = int(new_datetime_object_msk.timestamp())
    return new_unix_time

async def delete_chat_messages(chat_id, invite_link, offtest):
    try:
        async with papp:
            in_chat = await bot.get_chat_member(chat_id, user_id=5982267286)
            if in_chat.status == 'left' or in_chat.status == 'kicked':
                await bot.unban_chat_member(chat_id=chat_id, user_id=5982267286, only_if_banned=False)
                chat = await papp.join_chat(invite_link)

            try:
                await bot.promote_chat_member(user_id=5982267286, chat_id=chat_id, can_delete_messages=True, can_edit_messages=True, can_manage_chat=True)
            except Exception as e:
                pass

            msgs_ids = []

            async for message in papp.get_chat_history(chat_id=chat_id):
                message_unix = await convert_to_unix_timestamp_msk(str(message.date))
                if offtest[1] >= message_unix >= offtest[0]:
                    msgs_ids.append(message.id)

            await papp.delete_messages(chat_id, msgs_ids)
            db = await collection.find_one({"chats": chat_id})
            await bot.send_message(db['user_id'], text=f'✅ Удаление завершено. <b>Удалено:</b> {len(msgs_ids)}')
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

async def get_last_msgdate(chat_id, invite_link):
    try:
        async with papp:
            in_chat = await bot.get_chat_member(chat_id, user_id=5982267286)
            if in_chat.status == 'left' or in_chat.status == 'kicked':
                await bot.unban_chat_member(chat_id=chat_id, user_id=5982267286, only_if_banned=False)
                chat = await papp.join_chat(invite_link)

            async for message in papp.get_chat_history(chat_id=chat_id, limit=1):
                return str(message.date)
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

async def calculate_end_date(days):
    tz_moscow = pytz.timezone('Europe/Moscow')
    current_datetime = datetime.now()
    formatted_date = current_datetime.strftime("%d.%m.%Y")
    start_date = datetime.strptime(formatted_date, "%d.%m.%Y")
    start_date = tz_moscow.localize(start_date)
    end_date = start_date + timedelta(days=days)
    formatted_date_with_time = end_date.strftime("%H:%M %d.%m.%Y")
    # ЮНИКС тайм
    new_datetime = current_datetime + timedelta(days=days)
    unix_time = int(time.mktime(new_datetime.timetuple()))
    return [formatted_date_with_time, unix_time]



async def blocked(user_id:int):
    user = await collection.find_one({'user_id': int(user_id)})
    answ = False
    if user != None:
        if 'blocked' in user:
            if user['blocked'] == True:
                answ = True
        else: answ = False
    return answ

async def add_time_to_unix(unix_time, time_string):
    time_in_seconds = 0

    if time_string.endswith('d'):
        days = int(time_string[:-1])
        time_in_seconds = days * 24 * 60 * 60
    elif time_string.endswith('h'):
        hours = int(time_string[:-1])
        time_in_seconds = hours * 60 * 60
    elif time_string.endswith('m'):
        minutes = int(time_string[:-1])
        time_in_seconds = minutes * 60
    elif time_string.endswith('s'):
        seconds = int(time_string[:-1])
        time_in_seconds = seconds

    new_unix_time = unix_time + time_in_seconds
    return new_unix_time


async def has_split_mention(input_text):
    pattern = r"@\s+\w+"
    mentions = re.findall(pattern, input_text)
    return bool(mentions)

async def send_error_log(error):
    async with papp:
        await papp.send_message(chat_id=5103314362, text=error)

async def get_dict_index(database, groupid):
    index_of_chat = 0
    for index, item in enumerate(database['settings']):
        if item.get("chat_id") == str(groupid):
            index_of_chat = index
            break
    return index_of_chat

async def get_spravkas_dict_index(func: str):
    index_of_dict = None
    db = await collection.find_one({'_id': ObjectId('64987b1eeed9918b13b0e8b4')})
    for index, item in enumerate(db['spravka']):
        if item.get("func") == func:
            index_of_dict = index
            break
    return index_of_dict

async def get_padialtarifindexid(db, index_of_chat, tarif_id):
    index_of_dict = None
    for index, item in enumerate(db['settings'][index_of_chat]['subscribe_show']['paydialogue']['tarif_plans']):
        if item.get("days") == tarif_id:
            index_of_dict = index
            break
    return index_of_dict

async def check_tolink_entitle(entitles, br):
    answ = False
    for entitle in entitles:
        if entitle['type'] == 'text_link':
            for b in br:
                if b in entitle['url']:
                    answ = True
                    break
    return answ

async def get_user_dict_index(dict):
    index_dict = None
    for index, obj in enumerate(dict):
        if "type" in obj and obj["type"] == 'text_mention':
            index_dict = index
    return index_dict

async def text_check_filters(filters:list, text:str):
    text_list = text.lower().split(' ')
    filters_lower = [item.lower() for item in filters]
    answ = False
    for word in text_list:
        if word in filters_lower:
            answ = True
            break
    return answ

async def pagesusers_gen(buttons_per_page=10):
    try:
        db = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
        inline_buttons = []
        for user in db['users']:
            try:
                chat = await bot.get_chat(user)
                udb = await collection.find_one({'user_id': user})
                inline_buttons.append(InlineKeyboardButton(text=f'{chat.first_name} - {len(udb["settings"])} | 💎 {udb["lic"]}', callback_data=f'stuser_{user}'))
            except ChatNotFound:
                continue
            except BotBlocked:
                continue

        pages = [inline_buttons[i:i + buttons_per_page] for i in range(0, len(inline_buttons), buttons_per_page)]
        return len(pages)
    except Exception as e:
        print(e)

async def get_entitle_dict_index(dict, entitle):
    index_dict = None
    for index, obj in enumerate(dict):
        if "type" in obj and obj["type"] == entitle:
            index_dict = index
    return index_dict

async def shorten_text(text, max_length):
    if len(text) > max_length:
        return text[:max_length] + "..."
    else:
        return text

async def get_chat_user_dict_index(db, user_id, indexofchat):
    index_dict = None
    for index, item in enumerate(db['settings'][indexofchat]['users']):
        if item.get("id") == user_id:
            index_dict = index
            break
    return index_dict

async def days_since_unix_time(unix_time):
    current_time_unix = await get_msk_unix()
    time_difference_seconds = current_time_unix - unix_time
    days_difference = int(time_difference_seconds / (60 * 60 * 24))
    return days_difference

async def get_msk_time():
    msk = pytz.timezone('Europe/Moscow')
    current_time = datetime.now(msk)
    formatted_time = current_time.strftime('%d.%m.%y %H:%M')
    return formatted_time

async def get_msk_date():
    moscow_tz = pytz.timezone('Europe/Moscow')
    current_time = datetime.now(moscow_tz)
    day = current_time.day
    month = current_time.month
    year = current_time.year
    formatted_date = f"{day:02d}.{month:02d}.{year}"
    return formatted_date

async def get_price_index(days):
    index_of_price = 0
    db = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
    for index, item in enumerate(db['price']):
        if item.get("period") == str(days):
            index_of_price = index
            break
    return index_of_price

async def resolve_username_to_user_id(username: str):
    try:
        async with papp:
            r = await papp.invoke(ResolveUsername(username=username))
            if r.users:
                return [r.users[0].id, r.users[0].first_name]
            return None
    except Exception as e:
        print(e)

async def delete_message(timer_s, message_ids: list, chat_id):
    try:
        await asyncio.sleep(timer_s)
        for i in message_ids:
            try:
                await bot.delete_message(chat_id, i)
            except Exception as e:
                print(e)
            await asyncio.sleep(1)

    except Exception as e:
        print('error delete')

async def contains_external_links(text: str, blocked_domains: list):
    try:
        for substring in blocked_domains:
            if substring in text:
                return True
        return False
    except Exception as e:
        print(e)

async def contains_syms(name: str, blocked_syms: list):
    try:
        cont = False
        for sym in blocked_syms:
            if sym in name:
                cont = True
                break

        return cont
    except Exception as e:
        print(e)

async def trim_array(arr, num_elements_to_keep):
    if len(arr) > num_elements_to_keep:
        arr = arr[:num_elements_to_keep]
    return arr

async def check_mentions(text):
    try:
        pattern = r"(@\w+)"
        matches = re.findall(pattern, text)

        if matches:
            return [True, matches[0]]
        else:
            return [False, ""]
    except Exception as e:
        print(e)


async def time_diff(time1, time2):
    fmt = "%H:%M:%S"
    datetime1 = datetime.strptime(time1, fmt)
    datetime2 = datetime.strptime(time2, fmt)
    difference = datetime2 - datetime1
    seconds = difference.total_seconds()
    return int(seconds)


async def active():
    while True:
        chat_ids = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
        chat_ids = chat_ids['groups']
        for chat_id in chat_ids:
            try:
                botid = await bot.get_me()
                try:
                    await bot.get_chat_member(chat_id=chat_id, user_id=botid.id)
                except ChatNotFound:
                    continue
                except BotKicked:
                    continue
                except BotBlocked:
                    continue

                if len(chat_ids) == 0:
                    await asyncio.sleep(0.05)
                    continue


                db = await collection.find_one({'chats': chat_id})
                if await blocked(db['user_id']):
                    return
                if db == None: continue
                index_of_chat = await get_dict_index(db, chat_id)

                if db['settings'][index_of_chat]['afk']['active'] == False: continue
                if db['settings'][index_of_chat]['bot_send_afk'] == True: continue
                if 'timer' not in db['settings'][index_of_chat]['afk']: await collection.find_one_and_update({'chats': chat_id}, {"$set": {f'settings.{index_of_chat}.afk.timer': 'None'}})
                db = await collection.find_one({'chats': chat_id})
                dif = await time_diff(db['settings'][index_of_chat]['last_msg'], datetime.now().strftime('%H:%M:%S'))
                timer = 2700
                if db['settings'][index_of_chat]['afk']['timer'] != 'None': timer = db['settings'][index_of_chat]['afk']['timer']
                if dif >= timer:
                    try:
                        user_in = await bot.get_chat_member(chat_id, user_id=5982267286)
                        if user_in.status == 'left' or user_in.status == 'kicked':
                            await bot.unban_chat_member(chat_id=chat_id, user_id=5982267286, only_if_banned=False)
                        link = await bot.get_chat(chat_id=chat_id)
                        already_sended = await get_vorchun_last_msg(chat_id, index_of_chat, link.invite_link)
                        if already_sended == True:
                            continue
                    except Exception as e:
                        print(e)


                    # text = f'{t_start_text.format(bot_user=t_bot_user)}\n\n<b>Функция:</b> "Ворчун"' text = db['settings'][index_of_chat]['afk']['warning']
                    if db['settings'][index_of_chat]['afk']['warning'] == 'None' and db['settings'][index_of_chat]['afk']['media'] != 'None':
                        if db['settings'][index_of_chat]['afk']['media']['type'] == 'Фото':
                            await bot.send_photo(chat_id=chat_id, photo=db['settings'][index_of_chat]['afk']['media']['file_id'])
                        else:
                            await bot.send_video(chat_id=chat_id, video=db['settings'][index_of_chat]['afk']['media']['file_id'])
                    elif db['settings'][index_of_chat]['afk']['warning'] != 'None' and db['settings'][index_of_chat]['afk']['media'] == 'None':
                        await bot.send_message(chat_id=chat_id, text=db['settings'][index_of_chat]['afk']['warning'])
                    else:
                        if db['settings'][index_of_chat]['afk']['media']['type'] == 'Фото':
                            await bot.send_photo(chat_id=chat_id, photo=db['settings'][index_of_chat]['afk']['media']['file_id'], caption=db['settings'][index_of_chat]['afk']['warning'])
                        else:
                            await bot.send_video(chat_id=chat_id, video=db['settings'][index_of_chat]['afk']['media']['file_id'], caption=db['settings'][index_of_chat]['afk']['warning'])

                    await collection.find_one_and_update({'chats': chat_id}, {"$set": {f'settings.{index_of_chat}.bot_send_afk': True}})

                await asyncio.sleep(0.05)
            except Exception as e:
                traceback.print_exc()
                asyncio.create_task(send_error_log(traceback.format_exc()))

        await asyncio.sleep(5)

loop = asyncio.get_event_loop()
loop.create_task(active())

async def active_lic_end_func():
    while True:
        chat_ids = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
        chat_ids = chat_ids['chat_with_lics']
        for chat_id in chat_ids:
            try:
                if len(chat_ids) == 0:
                    await asyncio.sleep(0.05)
                    continue


                db = await collection.find_one({'settings': {"$elemMatch": {'chat_id': chat_id}}})
                if db == None: continue
                index_of_chat = await get_dict_index(db, chat_id)

                if db['settings'][index_of_chat]['lic'] == False: continue
                unix_ending = db['settings'][index_of_chat]['lic_end'][1]
                chat = 'Неизвестно'
                try:
                    chat_inf = await bot.get_chat(chat_id)
                    chat = chat_inf.title
                except ChatNotFound:
                    print('')
                except BotKicked:
                    print('')
                current_unix = await get_msk_unix()
                if current_unix >= unix_ending:
                    adb = await collection.find_one({'_id': ObjectId('64987b1eeed9918b13b0e8b4')})
                    active_lics_count = adb['active_lic'] - 1
                    lic_count = db['lic'] - 1
                    await collection.find_one_and_update({'settings': {"$elemMatch": {'chat_id': chat_id}}}, {'$set': {f'settings.{index_of_chat}.lic': False, 'lic': lic_count}})
                    await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')}, {'$set': {'active_lic': active_lics_count}, '$pull': {'chat_with_lics': chat_id}})
                    try:
                        await bot.send_message(chat_id=db['user_id'], text=f'⏳ <b>Срок лицензии истек:</b>\n\n<b>Чат:</b> {chat}\n\nДля приобретения новой лицензии, перейдите в настройки чата:', reply_markup=await inline_keyboards.generate_mychats_button())
                    except Exception as e:
                        print(e)

                await asyncio.sleep(0.05)
            except Exception as e:
                traceback.print_exc()
                asyncio.create_task(send_error_log(traceback.format_exc()))

        await asyncio.sleep(5)

loop.create_task(active_lic_end_func())