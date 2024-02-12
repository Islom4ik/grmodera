# Обработчики команд:
import asyncio
import re
import time
import pytz
from data.loader import bot, dp, FSMContext, State, Message
from database.database import collection, ObjectId
from aiogram.utils.exceptions import BotKicked, BotBlocked, ChatNotFound
from states_scenes.scene import MySceneStates
from keyboards.inline_keyboards import *
from time import sleep
from data.configs import *
from datetime import datetime
from data.texts import *
import traceback

@dp.message_handler(commands=['start'])
async def start_help_command_handler(ctx: Message):
    try:
        if ctx.chat.type == 'group' or ctx.chat.type == 'supergroup':
            if ctx['from']['username'] == 'GroupAnonymousBot': return await ctx.answer('🤷‍♂ Извините, Аноним мы уважаем ваше решение но мы не можем идентифицировать создателя группы пока тот является анонимом...\n\nПопросим вас выключить анонимность на пару минут и следовать инструкция бота, но а позже вы сможете обратно включить анонимность и управлять ботом в личных сообщениях!')
            admins = await bot.get_chat_administrators(ctx.chat.id)
            creator_id = next((obj for obj in admins if obj["status"] == "creator"), None).user.id
            if await blocked(creator_id):
                return await ctx.answer('🔒 Извините, создатель чата заблокирован в боте')
            for me in admins:
                if me.user.username == t_bot_user:
                    if me.can_change_info == True and me.can_manage_chat == True and me.can_delete_messages == True and me.can_restrict_members == True and me.can_invite_users == True and me.can_promote_members == True:
                        trash = await ctx.answer(
                            '🤖 Вы выполнили корректные действия.\n\nНажмите кнопку "Настроить бота"',
                            reply_markup=await generate_settings_button(f'{ctx.chat.id}_{creator_id}'))
                        return asyncio.create_task(delete_message(10, [trash.message_id, ctx.message_id], ctx.chat.id))
                    else:
                        return await ctx.answer(
                            '🤖 Здравствуйте! Я бот-админ и могу администрировать данный чат.\n\nВыдайте мне все права администратора:\n- Управлять группой\n- Удаление сообщений\n- Изменение сообщений\n- Блокировать участников\n- Добовлять участников\n- Управлять пользователями\n- Добавление администраторов',
                            reply_markup=await generate_check_admin_rights())
            else:
                return await ctx.answer(
                    '🤖 Здравствуйте! Я бот-админ и могу администрировать данный чат.\n\nВыдайте мне все права администратора:\n- Управлять группой\n- Удаление сообщений\n- Изменение сообщений\n- Блокировать участников\n- Добовлять участников\n- Управлять пользователями\n- Добавление администраторов',
                    reply_markup=await generate_check_admin_rights())

        if '/start settings_' in ctx.text:
            call_data = ctx.text.replace('/start ', '')
            call_datas = call_data.split('_')
            try:
                chat_admins = await bot.get_chat_administrators(call_datas[1])
                chat_owner = next((obj for obj in chat_admins if obj["status"] == "creator"), None).user.id

                if ctx.from_user.id != chat_owner:
                    await ctx.answer('⚠ Извините у вас недостаточно прав чтобы изменять настройки для данного чата')
                    await asyncio.sleep(1)
                else:
                    user_db = await collection.find_one({"user_id": ctx.from_user.id})
                    if user_db == None:
                        admindb = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
                        generate_user_data_id = admindb['users_count'] + 1
                        await collection.insert_one(
                            {"user_id": ctx.from_user.id, "register_data": datetime.now().strftime("%d.%m.%Y"),
                             "inlineid": generate_user_data_id, "blocked": False, "manual_msg": False, "manual_s": False, "chats": [], "settings": [], "lic": 0})
                        await collection.find_one_and_update({"_id": ObjectId('64987b1eeed9918b13b0e8b4')},
                                                       {"$set": {"users_count": generate_user_data_id},
                                                        "$push": {"users": ctx.from_user.id}})
                        user_db = await collection.find_one({"user_id": ctx.from_user.id})
                    if call_datas[1] not in user_db['chats']:
                        insettings = False
                        for chat in user_db['settings']:
                            if chat['chat_id'] == call_datas[1]:
                                insettings = True
                                break
                        if insettings == True:
                            await collection.find_one_and_update({"_id": ObjectId('64987b1eeed9918b13b0e8b4')},
                                                           {"$push": {"groups": call_datas[1]}})
                            await collection.find_one_and_update({"user_id": ctx.from_user.id}, {
                                "$push": {"chats": call_datas[1]}})
                        else:
                            await collection.find_one_and_update({"user_id": ctx.from_user.id}, {"$push": {"chats": call_datas[1], "settings": {"chat_id": call_datas[1], "updated_date": await get_msk_unix(), "users": [], "lic": False, "lic_end": 'None', "lic_buyed_date": 'None', "rules": 'None', "greeting": 'None', "warning_ban": 'None', "warning_kick": 'None', "unban_text": 'None', "warning_resources": 'None', "warning_repostes": 'None', "warning_ping": 'None', 'afk': {'active': False, 'media': "None", 'warning': "None"}, 'system_notice': {'active': False}, 'block_repostes': {'active': False, 'warning': 'None'}, "block_ping": {'active': False, 'warning': 'None'}, 'block_resources': {'active': False, 'warning': 'None', "r_list": [".com", ".ru"]}, "blocked_syms": [], 'noname': False, 'msg_filter': {'italic': False, 'bold': False, 'capslock': False, "mfilters": []}}}})
                            await collection.find_one_and_update({"_id": ObjectId('64987b1eeed9918b13b0e8b4')}, {"$push": {"groups": call_datas[1]}})
                    db = await collection.find_one({"chats": call_datas[1]})
                    index_of_chat = await get_dict_index(db, call_datas[1])
                    if db['settings'][index_of_chat]['lic'] == True: return await ctx.answer(t_settings.format(group_id=call_datas[1], bot_user=t_bot_user, upd_time=await update_time(db['settings'][index_of_chat]['updated_date']), chat_name=await get_chat_name(call_datas[1])), reply_markup=await generate_settings(True))
                    return await ctx.answer(t_settings.format(group_id=call_datas[1], bot_user=t_bot_user, upd_time=await update_time(db['settings'][index_of_chat]['updated_date']), chat_name=await get_chat_name(call_datas[1])), reply_markup=await generate_settings())
            except BotKicked:
                await ctx.answer('⚠ Извините, у меня нет доступа в настройки данного чата.')
            except BotBlocked:
                await ctx.answer(
                    '⚠ Извините, у меня нет доступа в настройки данного чата.')
            except ChatNotFound:
                await ctx.answer(
                    '⚠ Извините, у меня нет доступа в настройки данного чата.')

        if '/start paydial_' in ctx.text:
            db = await collection.find_one({"user_id": ctx.from_user.id})
            if db == None:
                admindb = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
                generate_user_data_id = admindb['users_count'] + 1
                await collection.insert_one({"user_id": ctx.from_user.id, "blocked": False, "manual_s": False, "manual_msg": False, "register_data": datetime.now().strftime("%d.%m.%Y"), "inlineid": generate_user_data_id, "chats": [], "settings": [], "lic": 0})
                await collection.find_one_and_update({"_id": ObjectId('64987b1eeed9918b13b0e8b4')},
                                               {"$set": {"users_count": generate_user_data_id},
                                                "$push": {"users": ctx.from_user.id}})

            call_data = ctx.text.replace('/start ', '')
            call_datas = call_data.split('_')
            chat_name = ''
            try:
                chat = await bot.get_chat(call_datas[1])
                chat_name = chat.title
            except:
                pass
            return await ctx.answer(f'<a href="https://{call_datas[1]}.id">🎤</a> <b>Плати говори:</b> {chat_name}\n\nВыберите тариф:', reply_markup=await generate_paydialogueuser_tarifs(call_datas[1]))



        db = await collection.find_one({"user_id": ctx.from_user.id})
        if db == None:
            admindb = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
            generate_user_data_id = admindb['users_count'] + 1
            await collection.insert_one({"user_id": ctx.from_user.id, "blocked": False, "manual_s": False, "manual_msg": False, "register_data": datetime.now().strftime("%d.%m.%Y"), "inlineid": generate_user_data_id, "chats": [], "settings": [], "lic": 0})
            await collection.find_one_and_update({"_id": ObjectId('64987b1eeed9918b13b0e8b4')},
                                           {"$set": {"users_count": generate_user_data_id},
                                            "$push": {"users": ctx.from_user.id}})

        db = await collection.find_one({"user_id": ctx.from_user.id})
        if len(db['chats']) >= 1:
            lic = 'Лицензии нет'
            if db['lic'] != 'None': lic = db['lic']
            await ctx.answer(
                text=f'👤 Ваш профиль:\n\n<b>Пользователь:</b> #{db["inlineid"]} - {db["register_data"]}\n<b>Username:</b> @{ctx.from_user.username}\n<b>Имя:</b> {ctx.from_user.first_name}\n<b>Чатов:</b> {len(db["chats"])}\n<b>Лицензий:</b> {db["lic"]}',
                reply_markup=await generate_add_button())
        else:
            await ctx.answer(t_start_text.format(bot_user=t_bot_user), reply_markup=await generate_add_button())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(commands=['update'])
async def update(ctx: Message):
    if ctx.from_user.id != 5103314362: return
    await ctx.answer('Идет обновление...')
    await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')}, {'$pull': {"spravka": {'func': 'paydialogue'}}})
    await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')}, {'$pull': {"spravka": {'func': 'paydialogue'}}})
    await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')}, {'$push': {"spravka": {'func': 'paydialogue', 'info': 'None', 'n': 'Плати Говори'}}})
    await ctx.answer('Завершено ✅')

@dp.message_handler(commands=['on', 'off'])
async def handler_to_ban(ctx: Message):
    try:
        await ctx.delete()
        if ctx.chat.type == 'group' or ctx.chat.type == 'supergroup':
            admins = await bot.get_chat_administrators(ctx.chat.id)
            creator_id = next((obj for obj in admins if obj["status"] == "creator"), None).user.id
            db = await collection.find_one({"user_id": creator_id})
            index_of_chat = await get_dict_index(db, ctx.chat.id)
            if 'is_on' not in db['settings'][index_of_chat]: await collection.find_one_and_update({"user_id": creator_id}, {"$set": {f'settings.{index_of_chat}.is_on': True}})
            db = await collection.find_one({"user_id": creator_id})
            if ctx.text == '/on':
                if db['settings'][index_of_chat]['is_on'] == True:
                    trash = await ctx.answer('✋ Бот уже включен')
                    return asyncio.create_task(delete_message(10, [trash.message_id], trash.chat.id))
                await collection.find_one_and_update({"user_id": creator_id}, {"$set": {f'settings.{index_of_chat}.is_on': True}})
                trash = await ctx.answer('🟢 Бот включен')
                return asyncio.create_task(delete_message(10, [trash.message_id], trash.chat.id))
            else:
                if db['settings'][index_of_chat]['is_on'] == False:
                    trash = await ctx.answer('✋ Бот уже выключен')
                    return asyncio.create_task(delete_message(10, [trash.message_id], trash.chat.id))
                await collection.find_one_and_update({"user_id": creator_id}, {"$set": {f'settings.{index_of_chat}.is_on': False}})
                trash = await ctx.answer('🔴 Бот выключен')
                return asyncio.create_task(delete_message(10, [trash.message_id], trash.chat.id))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(commands=['ban'])
async def handler_to_ban(ctx: Message):
    try:
        if ctx.chat.type == 'group' or ctx.chat.type == 'supergroup':
            trash = ''
            if ctx['from']['username'] == 'GroupAnonymousBot':
                trash = await ctx.answer(
                '🤷‍♂ Извините, Аноним мы уважаем ваше решение, но мы не можем идентифицировать вас и ваши прова пока вы являетесь анонимом...\n\nПопросим вас выключить анонимность на пару минут и использовать данную команду, а позже вы сможете обратно включить анонимность!')
                return asyncio.create_task(delete_message(15, [trash.message_id, ctx.message_id], trash.chat.id))
            admins = await bot.get_chat_administrators(ctx.chat.id)
            creator_id = next((obj for obj in admins if obj["status"] == "creator"), None).user.id
            if await blocked(creator_id):
                return await ctx.answer('🔒 Извините, создатель чата заблокирован в боте')
            isadmin = False
            for user in admins:
                if user.user.id == ctx.from_user.id and (user.status == 'creator' or user.status == 'administrator') and user.can_restrict_members == True:
                    isadmin = True

                    if ctx.reply_to_message:
                        await bot.ban_chat_member(ctx.reply_to_message.chat.id, ctx.reply_to_message.from_user.id)
                        asyncio.create_task(notify_adbout_ban(ctx.reply_to_message.from_user.id, ctx.chat.title))
                        banned = await collection.find_one({"user_id": creator_id})
                        text = t_ban.format(member_name=f'<b><a href="tg://user?id={ctx.reply_to_message.from_user.id}">{ctx.reply_to_message.from_user.first_name}</a></b>', admin=f'<b>{ctx.from_user.first_name}</b>')
                        index = await get_dict_index(banned, ctx.chat.id)
                        if banned['settings'][index]['warning_ban'] != 'None':
                            text = banned['settings'][index]['warning_ban'].replace('{member_name}', f'<b><a href="tg://user?id={ctx.reply_to_message.from_user.id}">{ctx.reply_to_message.from_user.first_name}</a></b>').replace('{admin}', f'<b>{ctx.from_user.first_name}</b>')

                        await ctx.answer(text)
                        await bot.delete_message(ctx.chat.id, ctx.reply_to_message.message_id)
                        break

                    args = ctx.text.split(' ')
                    if len(args) == 1:
                        trash = await ctx.answer('⚠ Введите пользователя, которого нужно забанить, следуя примеру ниже:\n\n<i>ban @username</i>')
                        asyncio.create_task(delete_message(8, [trash.message_id, ctx.message_id], ctx.chat.id))
                        break
                    args.pop(0)

                    await collection.find_one_and_update({"user_id": creator_id}, {"$set": {"baned": []}})

                    dicts_with_user_key = []
                    for item in ctx.entities:
                        if 'user' in item:
                            dicts_with_user_key.append(item.user.id)
                            await collection.find_one_and_update({"user_id": creator_id}, {"$push": {"baned": f'<b><a href="tg://user?id={item.user.id}">{item.user.first_name}</a></b>'}})

                    pattern = r"https://t.me/([\w_]+)"
                    for i in args:
                        if i[0] == '@':
                            userid = await resolve_username_to_user_id(i.replace('@', ''))
                            dicts_with_user_key.append(userid[0])
                            await collection.find_one_and_update({"user_id": creator_id}, {
                                "$push": {"baned": f'<b><a href="tg://user?id={userid[0]}">{userid[1]}</a></b>'}})
                        elif re.search(pattern, i):
                            user = re.findall(pattern, i)[0]
                            userid = await resolve_username_to_user_id(user)
                            dicts_with_user_key.append(userid[0])
                            await collection.find_one_and_update({"user_id": creator_id}, {
                                "$push": {"baned": f'<b><a href="tg://user?id={userid[0]}">{userid[1]}</a></b>'}})


                    if len(dicts_with_user_key) == 0:
                        trash = await ctx.answer('🪪 Пользователь не найден')
                        return asyncio.create_task(delete_message(5, [trash.message_id, ctx.message_id], ctx.chat.id))


                    for i in dicts_with_user_key:
                        asyncio.create_task(notify_adbout_ban(i, ctx.chat.title))
                        await bot.ban_chat_member(ctx.chat.id, i)

                    banned = await collection.find_one({"user_id": creator_id})
                    text = t_ban.format(member_name=", ".join(banned["baned"]), admin=f'<b>{ctx.from_user.first_name}</b>')
                    index = await get_dict_index(banned, ctx.chat.id)
                    if banned['settings'][index]['warning_ban'] != 'None':
                        text = banned['settings'][index]['warning_ban'].replace('{member_name}', ", ".join(banned["baned"])).replace('{admin}', f'<b>{ctx.from_user.first_name}</b>')
                    await ctx.answer(text)
                    break

            if isadmin == False:
                trash = await ctx.answer('⚠ У вас не достаточно прав для использования данной команды')
                asyncio.create_task(delete_message(5, [trash.message_id], ctx.chat.id))

            asyncio.create_task(delete_message(5, [ctx.message_id], ctx.chat.id))
        else:
            await ctx.delete()

    except Exception as e:
        trash = ''
        if e.args[0] == 'Telegram says: [400 USERNAME_NOT_OCCUPIED] - The username is not occupied by anyone (caused by "contacts.ResolveUsername")':
            trash = await ctx.answer('🪪 Пользователь не найден')
        if e.args[0] == "Can't remove chat owner":
            trash = await ctx.answer('⚠ Вы не можете забанить основателя группы')
        if e.args[0] == "User is an administrator of the chat":
            trash = await ctx.answer('⚠ Вы не можете забанить администраторов чата\n\nЭто может сделать только создатель группы в ручную')
        if e.args[0] == 'Can\'t restrict self':
            trash = await ctx.answer('🤖 Ха-Ха-Ха... Я сам себя банить собрался?')
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))
        asyncio.create_task(delete_message(8, [trash.message_id, ctx.message_id], ctx.chat.id))


@dp.message_handler(commands=['unban'])
async def handler_to_unban(ctx: Message):
    try:
        if ctx.chat.type == 'group' or ctx.chat.type == 'supergroup':
            trash = ''
            if ctx['from']['username'] == 'GroupAnonymousBot':
                trash = await ctx.answer(
                '🤷‍♂ Извините, Аноним мы уважаем ваше решение, но мы не можем идентифицировать вас и ваши прова пока вы являетесь анонимом...\n\nПопросим вас выключить анонимность на пару минут и использовать данную команду, а позже вы сможете обратно включить анонимность!')
                return asyncio.create_task(delete_message(15, [trash.message_id, ctx.message_id], trash.chat.id))
            admins = await bot.get_chat_administrators(ctx.chat.id)
            creator_id = next((obj for obj in admins if obj["status"] == "creator"), None).user.id
            if await blocked(creator_id):
                return await ctx.answer('🔒 Извините, создатель чата заблокирован в боте')
            isadmin = False
            for user in admins:
                if user.user.id == ctx.from_user.id and (user.status == 'creator' or user.status == 'administrator') and user.can_restrict_members == True:
                    isadmin = True
                    args = ctx.text.split(' ')
                    if args[1] == f'@{t_bot_user}':
                        trash = await ctx.reply('Кхм-Кхм...')
                        return asyncio.create_task(delete_message(6, [trash.message_id, ctx.message_id], trash.chat.id))

                    if len(args) == 1:
                        trash = await ctx.answer('⚠ Введите пользователя, которого нужно разбанить, следуя примеру ниже:\n\n<i>unban @username</i>')
                        asyncio.create_task(delete_message(8, [trash.message_id, ctx.message_id], ctx.chat.id))
                        break
                    args.pop(0)

                    await collection.find_one_and_update({"user_id": creator_id}, {"$set": {"unbaned": []}})

                    dicts_with_user_key = []
                    pattern = r"https://t.me/([\w_]+)"
                    for i in args:
                        if i[0] == '@':
                            userid = await resolve_username_to_user_id(i.replace('@', ''))
                            userc = ''
                            try:
                                userc = await bot.get_chat_member(chat_id=ctx.chat.id, user_id=userid[0])
                                if userc.status == 'kicked':
                                    dicts_with_user_key.append(userid[0])
                                    await collection.find_one_and_update({"user_id": creator_id}, {
                                        "$push": {"unbaned": f'<b><a href="tg://user?id={userid[0]}">{userid[1]}</a></b>'}})
                                else:
                                    trash = await ctx.answer(
                                        f'⚠ Участник <b><a href="tg://user?id={userid[0]}">{userid[1]}</a></b> не заблокирован')
                                    asyncio.create_task(
                                        delete_message(10, [trash.message_id, ctx.message_id], ctx.chat.id))
                            except:
                                print('')
                        elif re.search(pattern, i):
                            user = re.findall(pattern, i)[0]
                            userid = await resolve_username_to_user_id(user)
                            try:
                                userc = await bot.get_chat_member(chat_id=ctx.chat.id, user_id=userid[0])
                                if userc.status == 'kicked':
                                    dicts_with_user_key.append(userid[0])
                                    await collection.find_one_and_update({"user_id": creator_id}, {
                                        "$push": {"unbaned": f'<b><a href="tg://user?id={userid[0]}">{userid[1]}</a></b>'}})
                                else:
                                    trash = await ctx.answer(
                                        f'⚠ Участник <b><a href="tg://user?id={userid[0]}">{userid[1]}</a></b> не заблокирован')
                                    asyncio.create_task(
                                        delete_message(10, [trash.message_id, ctx.message_id], ctx.chat.id))
                            except:
                                print('')
                    if len(dicts_with_user_key) == 0:
                        trash = await ctx.answer('🪪 Пользователь не найден. Введите пользователя, которого нужно разбанить, следуя примеру ниже:\n\n<i>unban @username</i>')
                        return asyncio.create_task(delete_message(10, [trash.message_id, ctx.message_id], ctx.chat.id))


                    for i in dicts_with_user_key:
                        unban = await bot.unban_chat_member(ctx.chat.id, i, only_if_banned=False)

                    unbaned = await collection.find_one({"user_id": creator_id})
                    text = t_unban.format(member_name=", ".join(unbaned["unbaned"]), admin=f'<b>{ctx.from_user.first_name}</b>')
                    index = await get_dict_index(unbaned, ctx.chat.id)
                    if unbaned['settings'][index]['unban_text'] != 'None':
                        text = unbaned['settings'][index]['unban_text'].replace('{member_name}', ", ".join(unbaned["unbaned"])).replace('{admin}', f'<b>{ctx.from_user.first_name}</b>')

                    await ctx.answer(text)

                    break

            if isadmin == False:
                trash = await ctx.answer('⚠ У вас не достаточно прав для использования данной команды')
                asyncio.create_task(delete_message(5, [trash.message_id], ctx.chat.id))

            asyncio.create_task(delete_message(5, [ctx.message_id], ctx.chat.id))
        else:
            await ctx.delete()
    except Exception as e:
        trash = ''
        if e.args[
            0] == 'Telegram says: [400 USERNAME_NOT_OCCUPIED] - The username is not occupied by anyone (caused by "contacts.ResolveUsername")':
            trash = await ctx.answer('🪪 Пользователь не найден')
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))
        asyncio.create_task(delete_message(5, [trash.message_id, ctx.message_id], ctx.chat.id))

@dp.message_handler(commands=['kick'])
async def handler_to_kick(ctx: Message):
    try:
        if ctx.chat.type == 'group' or ctx.chat.type == 'supergroup':
            trash = ''
            if ctx['from']['username'] == 'GroupAnonymousBot':
                trash = await ctx.answer(
                '🤷‍♂ Извините, Аноним мы уважаем ваше решение, но мы не можем идентифицировать вас и ваши прова пока вы являетесь анонимом...\n\nПопросим вас выключить анонимность на пару минут и использовать данную команду, а позже вы сможете обратно включить анонимность!')
                return asyncio.create_task(delete_message(15, [trash.message_id, ctx.message_id], trash.chat.id))
            admins = await bot.get_chat_administrators(ctx.chat.id)
            creator_id = next((obj for obj in admins if obj["status"] == "creator"), None).user.id
            if await blocked(creator_id):
                return await ctx.answer('🔒 Извините, создатель чата заблокирован в боте')
            isadmin = False
            for user in admins:
                if user.user.id == ctx.from_user.id and (
                        user.status == 'creator' or user.status == 'administrator') and user.can_restrict_members == True:
                    isadmin = True

                    db = await collection.find_one({'chats': str(ctx.chat.id)})
                    index_of_chat = await get_dict_index(db, str(ctx.chat.id))
                    if ctx.reply_to_message:
                        await bot.kick_chat_member(ctx.reply_to_message.chat.id, ctx.reply_to_message.from_user.id)
                        await bot.unban_chat_member(ctx.reply_to_message.chat.id, ctx.reply_to_message.from_user.id)
                        text = t_kick.format(member_name=f'<b><a href="tg://user?id={ctx.reply_to_message.from_user.id}">{ctx.reply_to_message.from_user.first_name}</a></b>', admin=f'<b>{ctx.from_user.first_name}</b>')
                        if db['settings'][index_of_chat]['warning_kick'] != 'None': text = db['settings'][index_of_chat]['warning_kick'].replace('{member_name}', f'<b><a href="tg://user?id={ctx.reply_to_message.from_user.id}">{ctx.reply_to_message.from_user.first_name}</a></b>').replace('{admin}', f'<b>{ctx.from_user.first_name}</b>')
                        await ctx.answer(text)
                        await bot.delete_message(ctx.chat.id, ctx.reply_to_message.message_id)
                        break


                    args = ctx.text.split(' ')
                    if len(args) == 1:
                        trash = await ctx.answer(
                            '⚠ Введите пользователя, которого нужно кикнуть, следуя примеру ниже:\n\n<i>kick @username</i>')
                        asyncio.create_task(delete_message(8, [trash.message_id, ctx.message_id], ctx.chat.id))
                        break
                    args.pop(0)

                    await collection.find_one_and_update({"user_id": creator_id}, {"$set": {"kicked": []}})

                    dicts_with_user_key = []
                    for item in ctx.entities:
                        if 'user' in item:
                            dicts_with_user_key.append(item.user.id)
                            await collection.find_one_and_update({"user_id": creator_id}, {"$push": {
                                "kicked": f'<b><a href="tg://user?id={item.user.id}">{item.user.first_name}</a></b>'}})

                    pattern = r"https://t.me/([\w_]+)"
                    for i in args:
                        if i[0] == '@':
                            userid = await resolve_username_to_user_id(i.replace('@', ''))
                            dicts_with_user_key.append(userid[0])
                            await collection.find_one_and_update({"user_id": creator_id}, {
                                "$push": {"kicked": f'<b><a href="tg://user?id={userid[0]}">{userid[1]}</a></b>'}})
                        elif re.search(pattern, i):
                            user = re.findall(pattern, i)[0]
                            userid = await resolve_username_to_user_id(user)
                            dicts_with_user_key.append(userid[0])
                            await collection.find_one_and_update({"user_id": creator_id}, {
                                "$push": {"kicked": f'<b><a href="tg://user?id={userid[0]}">{userid[1]}</a></b>'}})

                    if len(dicts_with_user_key) == 0:
                        trash = await ctx.answer('🪪 Пользователь не найден')
                        return asyncio.create_task(delete_message(5, [trash.message_id, ctx.message_id], ctx.chat.id))

                    for i in dicts_with_user_key:
                        await bot.kick_chat_member(ctx.chat.id, i)
                        await bot.unban_chat_member(ctx.chat.id, i)

                    kicked = await collection.find_one({"user_id": creator_id})
                    text = t_kick.format(member_name=", ".join(kicked["kicked"]), admin=f'<b>{ctx.from_user.first_name}</b>')
                    index = await get_dict_index(kicked, ctx.chat.id)
                    if kicked['settings'][index]['warning_kick'] != 'None':
                        text = kicked['settings'][index]['warning_kick'].replace('{member_name}', ", ".join(kicked["kicked"])).replace('{admin}', f'<b>{ctx.from_user.first_name}</b>')

                    await ctx.answer(text)
                    break

            if isadmin == False:
                trash = await ctx.answer('⚠ У вас не достаточно прав для использования данной команды')
                asyncio.create_task(delete_message(5, [trash.message_id], ctx.chat.id))

            asyncio.create_task(delete_message(5, [ctx.message_id], ctx.chat.id))
        else:
            await ctx.delete()
    except Exception as e:
        trash = ''
        if e.args[
            0] == 'Telegram says: [400 USERNAME_NOT_OCCUPIED] - The username is not occupied by anyone (caused by "contacts.ResolveUsername")':
            trash = await ctx.answer('🪪 Пользователь не найден')
        if e.args[0] == "Can't remove chat owner":
            trash = await ctx.answer('⚠ Вы не можете забанить основателя группы')
        if e.args[0] == "User is an administrator of the chat":
            trash = await ctx.answer(
                '⚠ Вы не можете забанить администраторов чата\n\nЭто может сделать только создатель группы в ручную')
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))
        asyncio.create_task(delete_message(5, [trash.message_id, ctx.message_id], ctx.chat.id))

timezone = pytz.timezone('Europe/Moscow')

# @dp.message_handler(commands=['mute'])
# async def handler_to_ban(ctx: Message):
#     try:
#         if ctx.chat.type == 'group' or ctx.chat.type == 'supergroup':
#             admins = await bot.get_chat_administrators(ctx.chat.id)
#             isadmin = False
#             for user in admins:
#                 if user.user.id == ctx.from_user.id and (user.status == 'creator' or user.status == 'administrator') and user.can_restrict_members == True:
#                     isadmin = True
#
#                     args = ctx.text.split(' ')
#                     if len(args) > 4:
#                         trash = await ctx.answer(
#                             '⚠ Вы ввели неправильную структуру команды. Ниже приведена правильная структура команды:\n\n<i>mute @username until reason</i>\n\nuntil(365d|1h|1m|30s) -> Время, через которое будет снят мут. (необязательно указывать дату снятия мута, если хотите замутить пользователя навсегда)\nreason -> Причина мута')
#                         asyncio.create_task(delete_message(15, [trash.message_id, ctx.message_id], ctx.chat.id))
#                         break
#
#                     if ctx.reply_to_message:
#                         rargs = ctx.text.split(' ')
#                         if len(rargs) > 3:
#                             trash = await ctx.answer(
#                                 '⚠ Вы ввели неправильную структуру команды. Если вы отвечаете на сообщение пользователя которого нужно замутить, то структура команды:\n\n<i>mute until\n\nuntil(365d|1h|1m|30s) -> Время, через которое будет снят мут. (необязательно указывать дату снятия мута, если хотите замутить пользователя навсегда)</i>')
#                             asyncio.create_task(delete_message(15, [trash.message_id, ctx.message_id], ctx.chat.id))
#                             break
#                         elif len(rargs) == 3:
#                             if re.search(r"[dhms]", rargs[1]):
#                                 await bot.restrict_chat_member(ctx.reply_to_message.chat.id,
#                                                                ctx.reply_to_message.from_user.id, can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False, until_date=add_time_to_unix(int(datetime.now(timezone).timestamp()), rargs[1]))
#
#                                 await ctx.answer(
#                                     f'👨🏻‍⚖ Администратор <b>{ctx.from_user.first_name}</b> замутил <a href="tg://user?id={ctx.reply_to_message.from_user.id}">{ctx.reply_to_message.from_user.first_name}</a> по причине:\n<i>{"".join(args)}</i>')
#                                 break
#                         else:
#                             await bot.restrict_chat_member(ctx.reply_to_message.chat.id,
#                                                           ctx.reply_to_message.from_user.id,)
#                             await ctx.answer(
#                                 f'👨🏻‍⚖ Администратор <b>{ctx.from_user.first_name}</b> замутил <a href="tg://user?id={ctx.reply_to_message.from_user.id}">{ctx.reply_to_message.from_user.first_name}</a>')
#                             break
#
#                     creator_id = next((obj for obj in admins if obj["status"] == "creator"), None).user.id
#                     await collection.find_one_and_update({"user_id": creator_id}, {"$set": {"baned": []}})
#
#                     dicts_with_user_key = []
#                     for item in ctx.entities:
#                         if 'user' in item:
#                             dicts_with_user_key.append(item.user.id)
#                             await collection.find_one_and_update({"user_id": creator_id}, {"$push": {"baned": f'<a href="tg://user?id={item.user.id}">{item.user.first_name}</a>'}})
#
#                     pattern = r"https://t.me/([\w_]+)"
#                     for i in args:
#                         if i[0] == '@':
#                             userid = await resolve_username_to_user_id(i.replace('@', ''))
#                             dicts_with_user_key.append(userid[0])
#                             await collection.find_one_and_update({"user_id": creator_id}, {
#                                 "$push": {"baned": f'<a href="tg://user?id={userid[0]}">{userid[1]}</a>'}})
#                         elif re.search(pattern, i):
#                             user = re.findall(pattern, i)[0]
#                             userid = await resolve_username_to_user_id(user)
#                             dicts_with_user_key.append(userid[0])
#                             await collection.find_one_and_update({"user_id": creator_id}, {
#                                 "$push": {"baned": f'<a href="tg://user?id={userid[0]}">{userid[1]}</a>'}})
#
#
#                     if len(dicts_with_user_key) == 0:
#                         trash = await ctx.answer('🪪 Пользователь не найден')
#                         return asyncio.create_task(delete_message(5, [trash.message_id, ctx.message_id], ctx.chat.id))
#
#
#                     for i in dicts_with_user_key:
#                         await bot.ban_chat_member(ctx.chat.id, i)
#
#                     banned = await collection.find_one({"user_id": creator_id})
#                     await ctx.answer(f'👨🏻‍⚖ Администратор <b>{ctx.from_user.first_name}</b> забанил {", ".join(banned["baned"])} за систематические нарушения правил!')
#                     break
#
#             if isadmin == False:
#                 trash = await ctx.answer('⚠ У вас не достаточно прав для использования данной команды')
#                 asyncio.create_task(delete_message(5, [trash.message_id], ctx.chat.id))
#
#             asyncio.create_task(delete_message(5, [ctx.message_id], ctx.chat.id))
#
#     except Exception as e:
#         trash = ''
#         if e.args[0] == 'Telegram says: [400 USERNAME_NOT_OCCUPIED] - The username is not occupied by anyone (caused by "contacts.ResolveUsername")':
#             trash = await ctx.answer('🪪 Пользователь не найден')
#         if e.args[0] == "Can't remove chat owner":
#             trash = await ctx.answer('⚠ Вы не можете забанить основателя группы')
#         if e.args[0] == "User is an administrator of the chat":
#             trash = await ctx.answer('⚠ Вы не можете забанить администраторов чата\n\nЭто может сделать только создатель группы в ручную')
#         if e.args[0] == 'Can\'t restrict self':
#             trash = await ctx.answer('🤖 Ха-Ха-Ха... Я сам себя банить собрался?')
#         traceback.print_exc()
#         asyncio.create_task(delete_message(5, [trash.message_id, ctx.message_id], ctx.chat.id))

@dp.message_handler(commands=['rules'])
async def answer_to_rules(ctx: Message):
    try:
        if ctx.chat.type == 'group' or ctx.chat.type == 'supergroup':
            db = await collection.find_one({"chats": f"{ctx.chat.id}"})
            index_of_chat = await get_dict_index(db, ctx.chat.id)

            trash = ''

            if db['settings'][index_of_chat]['rules'] == 'None':
                admins = await bot.get_chat_administrators(ctx.chat.id)
                creator_id = next((obj for obj in admins if obj["status"] == "creator"), None).user.id
                if await blocked(creator_id):
                    return await ctx.answer('🔒 Извините, создатель чата заблокирован в боте')
                trash = await ctx.answer(
                    "⚠ Правила чата отсутствуют!\n\nДля того чтобы изменить правила, перейдите в настройки бота через команду /settings или по кнопке ниже:",
                    reply_markup=await generate_settings_button(f"{ctx.chat.id}_{creator_id}"))
            else:
                trash = await ctx.answer(db['settings'][index_of_chat]['rules'])

            asyncio.create_task(delete_message(150, [trash.message_id, ctx.message_id], ctx.chat.id))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(commands=['settings'])
async def answer_to_settings(ctx: Message):
    try:
        if ctx.chat.type == 'group' or ctx.chat.type == 'supergroup':
            trash = ''
            if ctx['from']['username'] == 'GroupAnonymousBot':
                trash = await ctx.answer(
                '🤷‍♂ Извините, Аноним мы уважаем ваше решение, но мы не можем идентифицировать создателя группы пока вы являетесь анонимом...\n\nПопросим вас выключить анонимность на пару минут и использовать команду, а позже вы сможете обратно включить анонимность!')
                return asyncio.create_task(delete_message(15, [trash.message_id, ctx.message_id], trash.chat.id))
            admins = await bot.get_chat_administrators(ctx.chat.id)
            creator_id = next((obj for obj in admins if obj["status"] == "creator"), None).user.id
            if await blocked(creator_id):
                return await ctx.answer('🔒 Извините, создатель чата заблокирован в боте')
            trash = await ctx.answer('Для того чтобы изменить настройки, перейдите в бота по кнопке ниже:',
                             reply_markup=await generate_settings_button(f"{ctx.chat.id}_{creator_id}"))
            asyncio.create_task(delete_message(6, [trash.message_id, ctx.message_id], ctx.chat.id))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))