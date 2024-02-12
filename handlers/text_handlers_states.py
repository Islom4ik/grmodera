# Обработчики текстовых данных:
import asyncio
import json
import time
from decimal import Decimal
from data.loader import bot, dp, FSMContext, State, Message, config
from database.database import collection, ObjectId
from states_scenes.scene import MySceneStates
from time import sleep
from keyboards.inline_keyboards import *
from data.configs import *
from aiogram import types
from aiogram.types.chat_permissions import ChatPermissions
from handlers import commands
from admin import admin
from datetime import datetime
from data.texts import *
import traceback

@dp.message_handler(content_types=[types.ContentType.NEW_CHAT_MEMBERS])
async def new_chat_member_greatings(ctx: Message):
    try:
        if ctx['new_chat_member']['is_bot'] == True:
            if ctx['new_chat_member']['username'] == t_bot_user:
                is_valid_chat = await collection.find_one_and_update({'settings': {"$elemMatch": {'chat_id': str(ctx.chat.id)}}}, {'$push': {'chats': str(ctx.chat.id)}})
                if is_valid_chat != None: return await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')}, {'$push': {'groups': str(ctx.chat.id)}})

        if ctx["new_chat_member"]['id'] == 5982267286:
            return await ctx.delete()

        db = await collection.find_one({"chats": f"{ctx.chat.id}"})
        if db == None: return
        try:
            if await blocked(db['user_id']):
                return
        except:
            pass
        index_of_chat = await get_dict_index(db, ctx.chat.id)
        settings_of_chat = db['settings'][index_of_chat]
        if 'users' not in settings_of_chat: await collection.find_one_and_update({"chats": f"{ctx.chat.id}"}, {"$set": {f'settings.{index_of_chat}.users': []}})
        if 'noname' in db['settings'][index_of_chat]:
            if db['settings'][index_of_chat]['noname'] == True and 'username' not in ctx["new_chat_member"]:
                await bot.kick_chat_member(ctx.chat.id, ctx["new_chat_member"]['id'])
                await bot.unban_chat_member(ctx.chat.id, ctx["new_chat_member"]['id'])
                if db['settings'][index_of_chat]['system_notice']['active'] == True: await bot.delete_message(ctx.chat.id, ctx.message_id)
                msg = await ctx.answer(f'Пользователь <a href="tg://user?id={ctx["new_chat_member"]["id"]}">{ctx["new_chat_member"]["first_name"]}</a>, не был(а) впущен(а) в группу из-за отсутствия юзернейма')
                return asyncio.create_task(delete_message(10, [msg.message_id], msg.chat.id))

        if db['settings'][index_of_chat]['system_notice']['active'] == True: await bot.delete_message(ctx.chat.id, ctx.message_id)
        member_name = f'<a href="tg://user?id={ctx["new_chat_member"]["id"]}">{ctx["new_chat_member"]["first_name"]}</a>'

        text = f"Приветствуем, <b>{member_name}</b>!\n\nПрежде чем размещать свои объявления, пожалуйста, ознакомься с правилами. Они доступны по команде /rules"
        if db['settings'][index_of_chat]['greeting'] != 'None':
            text = db['settings'][index_of_chat]['greeting'].replace("{member_name}", member_name)

        trash = await ctx.answer(text)
        await collection.find_one_and_update({"chats": f"{ctx.chat.id}"}, {"$push": {f'settings.{index_of_chat}.users': {"id": ctx["new_chat_member"]["id"], 'l_msg': await get_msk_unix(), 'j_t': await get_msk_unix()}}})
        asyncio.create_task(delete_message(30, [trash.message_id], ctx.chat.id))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))
        print('---------------')

@dp.message_handler(content_types=[types.ContentType.LEFT_CHAT_MEMBER])
async def left_chat_member(ctx: Message):
    try:
        if ctx.left_chat_member.username == t_bot_user and ctx.left_chat_member.is_bot == True:
            await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')}, {'$pull': {'groups': str(ctx.chat.id)}})
            return await collection.find_one_and_update({'chats': str(ctx.chat.id)}, {'$pull': {'chats': str(ctx.chat.id)}})

        if ctx.left_chat_member.id == 5982267286:
            return await ctx.delete()

        db = await collection.find_one({"chats": f"{ctx.chat.id}"})
        if db == None: return
        if await blocked(db['user_id']):
            return

        index_of_chat = await get_dict_index(db, ctx.chat.id)
        settings_of_chat = db['settings'][index_of_chat]
        if 'users' not in settings_of_chat: await collection.find_one_and_update({"chats": f"{ctx.chat.id}"}, {
            "$set": {f'settings.{index_of_chat}.users': []}})
        if db['settings'][index_of_chat]['system_notice']['active'] == True: await bot.delete_message(ctx.chat.id, ctx.message_id)
        await collection.find_one_and_update({"chats": f"{ctx.chat.id}"},
                                       {"$pull": {f'settings.{index_of_chat}.users': {"id": ctx["left_chat_participant"]["id"]}}})
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text'], state=MySceneStates.greeting_change_text_scene)
async def greeting_scene(ctx: Message, state: FSMContext):
    try:
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        await collection.find_one_and_update({"user_id": ctx.from_user.id}, {"$set": {f"settings.{index_of_chat}.greeting": ctx.text, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
        db = await collection.find_one({"user_id": ctx.from_user.id})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')
        await bot.send_message(ctx.chat.id, text=f'Успешное изменение ✅')
        await state.finish()
        text = f'Приветствуем, <b>{str("{member_name}")}</b>!\n\nПрежде чем размещать свои объявления, пожалуйста, ознакомься с правилами. Они доступны по команде /rules'
        if db["settings"][index_of_chat]['greeting'] != 'None': text = db["settings"][index_of_chat]['greeting']
        await bot.send_message(ctx.chat.id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Приветственное сообщение:</b>\n{text}',
                                    reply_markup=await generate_text_editing_page())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text'], state=MySceneStates.rules_change_text_scene)
async def rules_scene(ctx: Message, state: FSMContext):
    try:
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        await collection.find_one_and_update({"user_id": ctx.from_user.id}, {"$set": {f"settings.{index_of_chat}.rules": ctx.text, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
        db = await collection.find_one({"user_id": ctx.from_user.id})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')
        await bot.send_message(ctx.chat.id, text=f'Успешное изменение ✅')
        await state.finish()
        text = '<i>Правила отсутствуют</i>'
        if db["settings"][index_of_chat]['rules'] != 'None': text = db["settings"][index_of_chat]['rules']
        await bot.send_message(ctx.chat.id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Правила чата:</b>\n{text}',
                                    reply_markup=await generate_rules_editing_page())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text'], state=MySceneStates.afk_change_text_scene)
async def afk_scene(ctx: Message, state: FSMContext):
    try:
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        await collection.find_one_and_update({"user_id": ctx.from_user.id}, {"$set": {f"settings.{index_of_chat}.afk.warning": ctx.parse_entities(as_html=True), f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
        db = await collection.find_one({"user_id": ctx.from_user.id})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')
        await bot.send_message(ctx.chat.id, text=f'Успешное изменение ✅')
        text = f'Текст сообщения отсутствует 🤷‍♂'
        timer = '60'
        if 'timer' not in db['settings'][index_of_chat]['afk']:
            await collection.find_one_and_update({"user_id": ctx.from_user.id}, {"$set": {f'settings.{index_of_chat}.afk.timer': 'None'}})
        elif db['settings'][index_of_chat]['afk']['timer'] != 'None': timer = db['settings'][index_of_chat]['afk']['timer']
        if db['settings'][index_of_chat]['afk']['warning'] != 'None': text = db['settings'][index_of_chat]['afk']['warning']
        await state.finish()
        await bot.send_message(ctx.chat.id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Ворчун:</b>\nЕсли в чате никто не пишет <b>{timer}</b> секунд, то выводит сообщение:\n\n{text}',
                                    reply_markup=await generate_block_afk_show(db['user_id'], index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text'], state=MySceneStates.skromniytimer_change_scene)
async def skromniytimer_change_scene(ctx: Message, state: FSMContext):
    try:
        if ctx.text.isdigit() != True: return await ctx.answer('✋ Введите целое число:')
        if ctx.text[0] == '0' and len(ctx.text) > 1: return await ctx.answer('✋ Значение не может быть таким, введите значение заново:')
        if int(ctx.text) > 180: return await ctx.answer('✋ Значение не может быть больше 180, введите значение заново:')
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        await collection.find_one_and_update({"user_id": ctx.from_user.id}, {"$set": {f"settings.{index_of_chat}.skromniy.timer": int(ctx.text), f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
        db = await collection.find_one({"user_id": ctx.from_user.id})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')
        await bot.send_message(ctx.chat.id, text=f'Успешное изменение ✅')
        timer = 180
        if db['settings'][index_of_chat]['skromniy']['timer'] != 0: timer = db['settings'][index_of_chat]['skromniy']['timer']
        text = f'Гостевой режим, {timer} минут тишины.'
        if 'warning' in db['settings'][index_of_chat]['skromniy']:
            if db['settings'][index_of_chat]['skromniy']['warning'] != 'None': text = db['settings'][index_of_chat]['skromniy']['warning']
        await state.finish()
        await bot.send_message(ctx.chat.id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Гость:</b>\nЗапрещает новым пользователям говорить в течении <b>{timer}</b> минут.\n\n<b>Текст при срабатывании функции:</b>\n{text}',
                                    reply_markup=await generate_skromniy_show(db['user_id'], index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text'], state=MySceneStates.skromniyw_change_scene)
async def skromniyw_change_scene(ctx: Message, state: FSMContext):
    try:
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        await collection.find_one_and_update({"user_id": ctx.from_user.id}, {"$set": {f"settings.{index_of_chat}.skromniy.warning": ctx.text, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
        db = await collection.find_one({"user_id": ctx.from_user.id})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')
        await bot.send_message(ctx.chat.id, text=f'Успешное изменение ✅')
        timer = 180
        if db['settings'][index_of_chat]['skromniy']['timer'] != 0: timer = db['settings'][index_of_chat]['skromniy']['timer']
        text = f'Гостевой режим, {timer} минут тишины.'
        if 'warning' in db['settings'][index_of_chat]['skromniy']:
            if db['settings'][index_of_chat]['skromniy']['warning'] != 'None': text = db['settings'][index_of_chat]['skromniy']['warning']
        await state.finish()
        await bot.send_message(ctx.chat.id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Гость:</b>\nЗапрещает новым пользователям говорить в течении <b>{timer}</b> минут.\n\n<b>Текст при срабатывании функции:</b>\n{text}',
                                    reply_markup=await generate_skromniy_show(db['user_id'], index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text'], state=MySceneStates.tixiychastimer_change_scene)
async def tixiychastimer_change_scene(ctx: Message, state: FSMContext):
    try:
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        if db['tixchascall'] == 'id':
            pattern = r'^(?:[0-2][0-9]|3[0-1])\.(?:0[1-9]|1[0-2])\.\d{4} (?:[01][0-9]|2[0-3]):[0-5][0-9]-(?:[01][0-9]|2[0-3]):[0-5][0-9]$'
            if re.match(pattern, ctx.text) == None: return await ctx.answer('✋ Укажите промежуток времени в правильном формате, как в примере выше:')
            await collection.find_one_and_update({"user_id": ctx.from_user.id}, {"$set": {f"settings.{index_of_chat}.updated_date": await get_msk_unix()}, "$push": {f"settings.{index_of_chat}.tixiychas.timers": {"time": ctx.text, 't_i': 'В указанную дату'}}})
        else:
            pattern = r'^(?:[01]\d|2[0-3]):[0-5]\d-(?:[01]\d|2[0-3]):[0-5]\d$'
            if re.match(pattern, ctx.text) == None: return await ctx.answer('✋ Укажите промежуток времени в правильном формате, как в примере выше:')
            if db['tixchascall'] == 'ed':
                await collection.find_one_and_update({"user_id": ctx.from_user.id}, {"$set": {f"settings.{index_of_chat}.updated_date": await get_msk_unix()}, "$push": {f"settings.{index_of_chat}.tixiychas.timers": {"time": ctx.text, 't_i': 'Каждый день'}}})
            else: await collection.find_one_and_update({"user_id": ctx.from_user.id}, {"$set": {f"settings.{index_of_chat}.updated_date": await get_msk_unix()}, "$push": {f"settings.{index_of_chat}.tixiychas.timers": {"time": ctx.text, 't_i': 'В выходные'}}})


        db = await collection.find_one({"user_id": ctx.from_user.id})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')
        await bot.send_message(ctx.chat.id, text=f'Успешное изменение ✅')
        timers = 'Нет указанных промежутков'
        if len(db['settings'][index_of_chat]['tixiychas']['timers']) != 0:
            timers = ''
            for i in db['settings'][index_of_chat]['tixiychas']['timers']:
                timers += f'{i["t_i"]}: {i["time"]};\n'
        await state.finish()
        await bot.send_message(ctx.chat.id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Тихий час:</b>\nЗапрещает пользователям писать в указанный промежуток времени\n\n<b>Ваши промежутки:</b>\n{timers}',
                                    reply_markup=await generate_tixiychas_show(db['user_id'], index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))



@dp.message_handler(content_types=['text'], state=MySceneStates.blocked_resources_add)
async def blocked_resources_add_scene(ctx: Message, state: FSMContext):
    try:
        domains_array = ctx.text.replace(' ', '').split(',')
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)

        # if domains_array in db['settings'][index_of_chat]['block_resources']['r_list']: return await ctx.answer('⚠ В вашем списке запрещенных доменных расширений уже имеются некоторые введенные вами расширения.\n\nВведите доменные расширения, которые хотите заблокировать через запятую:')

        for i in domains_array:
            try:
                if i in db['settings'][index_of_chat]['block_resources']['r_list']: return await ctx.answer(
                    '✋ Вы пытаетесь добавить уже существующий запрет, введите запрет, которого нет в вашем списке:')
                await collection.find_one_and_update({"user_id": ctx.from_user.id},
                                               {'$push': {f'settings.{index_of_chat}.block_resources.r_list': i}, '$set': {f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            except Exception as e:
                traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))
        db = await collection.find_one({"user_id": ctx.from_user.id})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')
        await bot.send_message(ctx.chat.id, text=f'Успешное изменение ✅')
        await state.finish()
        blocked_reses = ", ".join(db["settings"][index_of_chat]["block_resources"]["r_list"])
        if len(db["settings"][index_of_chat]["block_resources"]["r_list"]) == 0: blocked_reses = 'Нету'
        await bot.send_message(ctx.chat.id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nЗаблокированные ресурсы:\n<b>{", ".join(db["settings"][index_of_chat]["block_resources"]["r_list"])}</b>', reply_markup=await generate_add_b_resources())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text'], state=MySceneStates.wordsfilter_add_scene)
async def wordsfilter_add_scene(ctx: Message, state: FSMContext):
    try:
        words = ctx.text.replace(' ,', ',').replace(', ', ',').split(',')
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)


        for word in words:
            db = await collection.find_one({"user_id": db['user_id']})
            if word in db['settings'][index_of_chat]['msg_filter']['mfilters']:
                await ctx.answer(f'✋ Слово <b>{word}</b> не было добавлено в список запретов, т.к уже в списке.')
                continue
            await collection.find_one_and_update({"user_id": ctx.from_user.id},
                                           {'$push': {f'settings.{index_of_chat}.msg_filter.mfilters': word}, '$set': {f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})

        db = await collection.find_one({"user_id": ctx.from_user.id})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')
        await bot.send_message(ctx.chat.id, text=f'Успешное изменение ✅')
        await state.finish()
        blist = 'Нету'
        if len(db["settings"][index_of_chat]["msg_filter"]["mfilters"]) != 0: blist = ", ".join(db["settings"][index_of_chat]["msg_filter"]["mfilters"])
        await bot.send_message(ctx.chat.id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Заполните необходимые для блокировки слова:</b>\n\n<b>Ваш список запретов:</b>\n{blist}', reply_markup=await generate_wordsfilter_show(db['user_id'], index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text'], state=MySceneStates.wordsfilter_rem_scene)
async def wordsfilter_rem_scene(ctx: Message, state: FSMContext):
    try:
        words = ctx.text.replace(' ,', ',').replace(', ', ',').split(',')
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)

        for word in words:
            db = await collection.find_one({"user_id": db['user_id']})
            if word not in db['settings'][index_of_chat]['msg_filter']['mfilters']:
                await ctx.answer(f'✋ Данного слова нет в списке запретов: <b>{word}</b>, неудалено')
                continue
            await collection.find_one_and_update({"user_id": ctx.from_user.id},
                                           {'$pull': {f'settings.{index_of_chat}.msg_filter.mfilters': word}, '$set': {f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
        db = await collection.find_one({"user_id": ctx.from_user.id})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')
        await bot.send_message(ctx.chat.id, text=f'Успешное изменение ✅')
        await state.finish()
        blist = 'Нету'
        if len(db["settings"][index_of_chat]["msg_filter"]["mfilters"]) != 0: blist = ", ".join(db["settings"][index_of_chat]["msg_filter"]["mfilters"])
        await bot.send_message(ctx.chat.id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Заполните необходимые для блокировки слова:</b>\n\n<b>Ваш список запретов:</b>\n{blist}', reply_markup=await generate_wordsfilter_show(db['user_id'], index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text'], state=MySceneStates.blocked_resources_remove)
async def blocked_resources_remove_scene(ctx: Message, state: FSMContext):
    try:
        domains_array = ctx.text.replace(' ', '').split(',')
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)

        for i in domains_array:
            try:
                if i not in db['settings'][index_of_chat]['block_resources']['r_list']: return await ctx.answer('✋ Вы пытаетесь удалить несуществующий запрет, введите запрет, который есть в вашем списке:')
                await collection.find_one_and_update({"user_id": ctx.from_user.id},
                                               {'$pull': {f'settings.{index_of_chat}.block_resources.r_list': i}, "$set": {f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            except Exception as e:
                traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))
        db = await collection.find_one({"user_id": ctx.from_user.id})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')
        await bot.send_message(ctx.chat.id, text=f'Успешное изменение ✅')
        await state.finish()
        blocked_reses = ", ".join(db["settings"][index_of_chat]["block_resources"]["r_list"])
        if len(db["settings"][index_of_chat]["block_resources"]["r_list"]) == 0: blocked_reses = 'Нету'
        await bot.send_message(ctx.chat.id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nЗаблокированные ресурсы:\n<b>{", ".join(db["settings"][index_of_chat]["block_resources"]["r_list"])}</b>', reply_markup=await generate_add_b_resources())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.message_handler(content_types=['text'], state=MySceneStates.blocked_syms_add)
async def blocked_syms_add_scene(ctx: Message, state: FSMContext):
    try:
        syms_array = ctx.text.replace(' ', '').split(',')
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)

        for i in syms_array:
            try:
                if i in db['settings'][index_of_chat]['blocked_syms']: return await ctx.answer(
                    '✋ Вы пытаетесь добавить уже существующий фильтр, введите символ, которого нет в вашем списке:')
                await collection.find_one_and_update({"user_id": ctx.from_user.id},
                                               {'$push': {f'settings.{index_of_chat}.blocked_syms': i}, '$set': {f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            except Exception as e:
                traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))
        db = await collection.find_one({"user_id": ctx.from_user.id})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')
        await bot.send_message(ctx.chat.id, text=f'Успешное изменение ✅')
        await state.finish()
        list = 'Нету'
        if len(db["settings"][index_of_chat]["blocked_syms"]) != 0: list = ", ".join(db["settings"][index_of_chat]["blocked_syms"])
        await bot.send_message(ctx.chat.id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Ваш список символов:</b>\n{list}\n\n<b>Выберите действие:</b>', reply_markup=await generate_add_b_syms())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text'], state=MySceneStates.blocked_syms_remove)
async def blocked_syms_remove_scene(ctx: Message, state: FSMContext):
    try:
        syms_array = ctx.text.replace(' ', '').split(',')
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)

        for i in syms_array:
            try:
                if i not in db['settings'][index_of_chat]['blocked_syms']: return await ctx.answer('✋ Вы пытаетесь удалить несуществующий фильтр, введите символ, который есть в вашем списке:')
                await collection.find_one_and_update({"user_id": ctx.from_user.id},
                                               {'$pull': {f'settings.{index_of_chat}.blocked_syms': i}, "$set": {f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            except Exception as e:
                traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))
        db = await collection.find_one({"user_id": ctx.from_user.id})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')
        await bot.send_message(ctx.chat.id, text=f'Успешное изменение ✅')
        await state.finish()
        list = 'Нету'
        if len(db["settings"][index_of_chat]["blocked_syms"]) != 0: list = ", ".join(db["settings"][index_of_chat]["blocked_syms"])
        await bot.send_message(ctx.chat.id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Ваш список символов:</b>\n{list}\n\n<b>Выберите действие:</b>', reply_markup=await generate_add_b_syms())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.message_handler(content_types=['text'], state=MySceneStates.banwarning_change_text_scene)
async def banwarning_change_text(ctx: Message, state: FSMContext):
    try:
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)

        await collection.find_one_and_update({"user_id": ctx.from_user.id},
                                       {'$set': {f'settings.{index_of_chat}.warning_ban': ctx.text, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')
        await bot.send_message(ctx.chat.id, text=f'Успешное изменение ✅')
        db = await collection.find_one({"user_id": ctx.from_user.id})
        await state.finish()
        ban = t_ban
        kick = t_kick
        unban = t_unban
        if db["settings"][index_of_chat]["warning_ban"] != 'None': ban = db["settings"][index_of_chat]["warning_ban"]
        if db["settings"][index_of_chat]["warning_kick"] != 'None': kick = db["settings"][index_of_chat]["warning_kick"]
        if db["settings"][index_of_chat]["unban_text"] != 'None': unban = db["settings"][index_of_chat]["unban_text"]
        await bot.send_message(chat_id=ctx.chat.id,
                               text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Уведомления пользователю при использовании команд:</b>\n\n<b>/ban</b>\n{ban}\n\n<b>/kick</b>\n{kick}\n\n<b>/unban</b>\n{unban}',
                               reply_markup=await generate_warning_editing_page())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text'], state=MySceneStates.kickwarning_change_text_scene)
async def kickwarning_change_text(ctx: Message, state: FSMContext):
    try:
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)

        await collection.find_one_and_update({"user_id": ctx.from_user.id},
                                       {'$set': {f'settings.{index_of_chat}.warning_kick': ctx.text, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')
        await bot.send_message(ctx.chat.id, text=f'Успешное изменение ✅')
        db = await collection.find_one({"user_id": ctx.from_user.id})
        await state.finish()
        ban = t_ban
        kick = t_kick
        unban = t_unban
        if db["settings"][index_of_chat]["warning_ban"] != 'None': ban = db["settings"][index_of_chat]["warning_ban"]
        if db["settings"][index_of_chat]["warning_kick"] != 'None': kick = db["settings"][index_of_chat]["warning_kick"]
        if db["settings"][index_of_chat]["unban_text"] != 'None': unban = db["settings"][index_of_chat]["unban_text"]
        await bot.send_message(chat_id=ctx.chat.id,
                               text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Уведомления пользователю при использовании команд:</b>\n\n<b>/ban</b>\n{ban}\n\n<b>/kick</b>\n{kick}\n\n<b>/unban</b>\n{unban}',
                               reply_markup=await generate_warning_editing_page())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text'], state=MySceneStates.unbantext_change_text_scene)
async def unban_change_text(ctx: Message, state: FSMContext):
    try:
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)

        await collection.find_one_and_update({"user_id": ctx.from_user.id},
                                       {'$set': {f'settings.{index_of_chat}.unban_text': ctx.text, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')
        await bot.send_message(ctx.chat.id, text=f'Успешное изменение ✅')
        db = await collection.find_one({"user_id": ctx.from_user.id})
        await state.finish()
        ban = t_ban
        kick = t_kick
        unban = t_unban
        if db["settings"][index_of_chat]["warning_ban"] != 'None': ban = db["settings"][index_of_chat]["warning_ban"]
        if db["settings"][index_of_chat]["warning_kick"] != 'None': kick = db["settings"][index_of_chat]["warning_kick"]
        if db["settings"][index_of_chat]["unban_text"] != 'None': unban = db["settings"][index_of_chat]["unban_text"]
        await bot.send_message(chat_id=ctx.chat.id,
                               text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Уведомления пользователю при использовании команд:</b>\n\n<b>/ban</b>\n{ban}\n\n<b>/kick</b>\n{kick}\n\n<b>/unban</b>\n{unban}',
                               reply_markup=await generate_warning_editing_page())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.message_handler(content_types=['text'], state=MySceneStates.antimatw_change_scene)
async def antimatw_change_scene(ctx: Message, state: FSMContext):
    try:
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)

        await collection.find_one_and_update({"user_id": ctx.from_user.id},
                                       {'$set': {f'settings.{index_of_chat}.msg_filter.mfilterw': ctx.text, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
        db = await collection.find_one({"user_id": ctx.from_user.id})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')
        await bot.send_message(ctx.chat.id, text=f'Успешное изменение ✅')
        await state.finish()
        bwords = ", ".join(db["settings"][index_of_chat]["msg_filter"]["mfilters"])
        await bot.send_message(chat_id=ctx.chat.id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Заполните необходимые для блокировки слова:</b>\n\n<b>Сообщение при нарушении:</b>\n{ctx.text}\n\n<b>Ваш список запретов:</b>\n{bwords}',
                                    reply_markup=await generate_block_resources_show(ctx.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text'], state=MySceneStates.resourcesw_change_scene)
async def resourcesw_change_text(ctx: Message, state: FSMContext):
    try:
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)

        await collection.find_one_and_update({"user_id": ctx.from_user.id},
                                       {'$set': {f'settings.{index_of_chat}.block_resources.warning': ctx.text, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
        db = await collection.find_one({"user_id": ctx.from_user.id})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')
        await bot.send_message(ctx.chat.id, text=f'Успешное изменение ✅')
        await state.finish()
        await bot.send_message(chat_id=ctx.chat.id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Сообщение при нарушении:</b>\n{ctx.text}',
                                    reply_markup=await generate_block_resources_show(ctx.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text'], state=MySceneStates.repostesw_change_scene)
async def repostesw_change_text(ctx: Message, state: FSMContext):
    try:
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)

        await collection.find_one_and_update({"user_id": ctx.from_user.id},
                                       {'$set': {f'settings.{index_of_chat}.block_repostes.warning': ctx.text, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
        db = await collection.find_one({"user_id": ctx.from_user.id})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')
        await bot.send_message(ctx.chat.id, text=f'Успешное изменение ✅')
        await state.finish()
        await bot.send_message(chat_id=ctx.chat.id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Сообщение при нарушении:</b>\n{ctx.text}',
                                    reply_markup=await generate_block_repostes_show(ctx.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text'], state=MySceneStates.pingw_change_scene)
async def pingw_change_text(ctx: Message, state: FSMContext):
    try:
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)

        await collection.find_one_and_update({"user_id": ctx.from_user.id},
                                       {'$set': {f'settings.{index_of_chat}.block_ping.warning': ctx.text, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
        db = await collection.find_one({"user_id": ctx.from_user.id})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')
        await bot.send_message(ctx.chat.id, text=f'Успешное изменение ✅')
        await state.finish()
        await bot.send_message(chat_id=ctx.chat.id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Сообщение при нарушении:</b>\n{ctx.text}',
                                    reply_markup=await generate_block_ping_show(ctx.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.message_handler(content_types=['text'], state=MySceneStates.donate_money_scene)
async def donate_money_set(ctx: Message, state: FSMContext):
    try:
        sum = ctx.text
        if sum.isdigit() == False: return await ctx.answer('✋ Введите целое число:')
        todigit = int(sum)
        if todigit < 100: return await ctx.answer('✋ Минимальная сумма оплаты <b>100</b>₽, введите сумму ещё раз:')
        if todigit > 100000000: return await ctx.answer('✋ Сумма доната не может быть больше <b>1 млн</b>, введите сумму ещё раз:')
        withdecimate = todigit * 100
        await collection.find_one_and_update({"user_id": ctx.from_user.id},
                                       {'$set': {'donate_money': withdecimate}})
        db = await collection.find_one({"user_id": ctx.from_user.id})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')
        await state.finish()
        await bot.send_message(chat_id=ctx.chat.id,
                                    text=f'💸 <b>Выберите способ оплаты:</b>',
                                    reply_markup=await generate_dpayment_method())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text'], state=MySceneStates.vorchun_timer_scene)
async def vorchun_timer_scene(ctx: Message, state: FSMContext):
    try:
        timer = ctx.text
        if timer.isdigit() == False: return await ctx.answer('✋ Значение должно быть целым числом, введите значение ещё раз:')
        todigit = int(timer)
        if todigit <= 0: return await ctx.answer('✋ Значение не может быть <b>0</b> или отрецательным, введите значение ещё раз:')
        if todigit > 100000000000000000: return await ctx.answer('✋ Значение слишком большое, введите значение ещё раз:')
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        await collection.find_one_and_update({"user_id": ctx.from_user.id},
                                       {'$set': {f'settings.{index_of_chat}.afk.timer': todigit, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
        db = await collection.find_one({"user_id": ctx.from_user.id})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')

        text = f'Текст сообщения отсутствует 🤷‍♂'
        timer = '60'
        if 'timer' not in db['settings'][index_of_chat]['afk']:
            await collection.find_one_and_update({"user_id": ctx.from_user.id}, {"$set": {f'settings.{index_of_chat}.afk.timer': 'None'}})
        elif db['settings'][index_of_chat]['afk']['timer'] != 'None': timer = db['settings'][index_of_chat]['afk']['timer']
        if db['settings'][index_of_chat]['afk']['warning'] != 'None': text = db['settings'][index_of_chat]['afk']['warning']
        await state.finish()
        await bot.send_message(ctx.chat.id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Ворчун:</b>\nЕсли в чате никто не пишет <b>{timer}</b> секунд, то выводит сообщение:\n\n{text}',
                               reply_markup=await generate_block_afk_show(db['user_id'], index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text'], state=MySceneStates.nofilelimit_change_scene)
async def antifludtimer_change_scene(ctx: Message, state: FSMContext):
    try:
        timer = ctx.text
        if timer.isdigit() == False: return await ctx.answer('✋ Значение должно быть целым числом, введите значение ещё раз:')
        todigit = int(timer)
        if todigit > 100000: return await ctx.answer('✋ Значение слишком большое, введите значение ещё раз:')
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        await collection.find_one_and_update({"user_id": ctx.from_user.id},
                                       {'$set': {f'settings.{index_of_chat}.nofile_show.limit': todigit, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
        db = await collection.find_one({"user_id": ctx.from_user.id})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')
        await ctx.answer(text=f'Успешное изменение ✅')
        await state.finish()
        limit = db['settings'][index_of_chat]['nofile_show']['limit']
        await bot.send_message(chat_id=ctx.chat.id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Нет файлам:</b>\nЗапрещает отправку любых типов файлов превышающих <b>{limit}</b> мб', reply_markup=await generate_nofile_show(ctx.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text'], state=MySceneStates.antifludtimer_change_scene)
async def antifludtimer_change_scene(ctx: Message, state: FSMContext):
    try:
        timer = ctx.text
        if timer.isdigit() == False: return await ctx.answer('✋ Значение должно быть целым числом, введите значение ещё раз:')
        todigit = int(timer)
        if todigit == 0: return await ctx.answer('✋ Значение не может быть <b>0</b>, введите значение ещё раз:')
        if todigit > 100000000: return await ctx.answer('✋ Значение слишком большое, введите значение ещё раз:')
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        await collection.find_one_and_update({"user_id": ctx.from_user.id},
                                       {'$set': {f'settings.{index_of_chat}.antiflud_block.timer': todigit, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
        db = await collection.find_one({"user_id": ctx.from_user.id})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')
        await ctx.answer(text=f'Успешное изменение ✅')
        await state.finish()
        timer = 0
        text = '✋ {member_name}, флуд запрещен!'
        if db['settings'][index_of_chat]['antiflud_block']['warning'] != 'None': text = db['settings'][index_of_chat]['antiflud_block']['warning']
        if db['settings'][index_of_chat]['antiflud_block']['timer'] != 0: timer = db['settings'][index_of_chat]['antiflud_block']['timer']
        await bot.send_message(chat_id=ctx.chat.id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Стоп флуд:</b>\nОтправка сообщений в чат с задержкой на <b>{timer}</b> сек.\n\n<b>Сообщение при нарушении:</b>\n{text}', reply_markup=await generate_antiflud_show(ctx.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text'], state=MySceneStates.antifludw_change_scene)
async def antifludw_change_scene(ctx: Message, state: FSMContext):
    try:
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)

        await collection.find_one_and_update({"user_id": ctx.from_user.id},
                                       {'$set': {f'settings.{index_of_chat}.antiflud_block.warning': ctx.text, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
        db = await collection.find_one({"user_id": ctx.from_user.id})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')
        await ctx.answer(text=f'Успешное изменение ✅')
        await state.finish()
        timer = 0
        text = '✋ {member_name}, флуд запрещен!'
        if db['settings'][index_of_chat]['antiflud_block']['warning'] != 'None': text = db['settings'][index_of_chat]['antiflud_block']['warning']
        if db['settings'][index_of_chat]['antiflud_block']['timer'] != 0: timer = db['settings'][index_of_chat]['antiflud_block']['timer']
        await bot.send_message(chat_id=ctx.chat.id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Стоп флуд:</b>\nОтправка сообщений в чат с задержкой на <b>{timer}</b> сек.\n\n<b>Сообщение при нарушении:</b>\n{text}', reply_markup=await generate_antiflud_show(ctx.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text'], state=MySceneStates.subchanel_add_scene)
async def subchanel_add_scene(ctx: Message, state: FSMContext):
    try:
        text = ctx.text.replace(' ', '')
        pattern = re.compile(r"https://t\.me/.*")
        channel_usern = ''
        if text[0] == '@':
            channel_usern = ctx.text
        elif pattern.match(text):
            channel_usern = f"@{ctx.text.replace('https://t.me/', '')}"
        else:
            return await ctx.answer('✋ Не правильный формат, введите UserName канала ещё раз(Пример - @test):')

        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        channel = ''
        try:
            channel = await bot.get_chat(channel_usern)
        except Exception as e:
            return await ctx.answer('🫤 Канал не найден, введите UserName канала ещё раз:')

        if channel.type not in ['channel', 'supergroup']: return await ctx.answer('🫤 Канал не найден, введите User Name канала ещё раз:')
        await collection.find_one_and_update({"user_id": ctx.from_user.id},
                                       {'$set': {f"settings.{index_of_chat}.updated_date": await get_msk_unix()}, "$push": {f'settings.{index_of_chat}.subscribe_show.channels': {"id": channel.id, 'title': channel.title, 'user_name': channel.username}}})
        db = await collection.find_one({"user_id": ctx.from_user.id})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')
        await ctx.answer(text=f'Канал <b>{channel.title}</b> успешно добавлен в список ✅\n\n‼ Для того чтобы функция правильно работала, вам не обходимо добавить бота в данный канал')
        await state.finish()
        channels_len = len(db['settings'][index_of_chat]['subscribe_show']['channels'])
        await bot.send_message(chat_id=ctx.chat.id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Подписать:</b>\nЕсли пользователь делает попытку писать в чат что-либо, то он видит сообщение:\n\n✋ member_name, чтобы продолжить общение в нашем чате, Вам необходимо:\n\n<b>Ваших каналов:</b> {channels_len}', reply_markup=await generate_subscribe_show(ctx.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text'], state=MySceneStates.paydialadd_scene)
async def paydialadd_scene(ctx: Message, state: FSMContext):
    try:
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)

        await collection.find_one_and_update({"user_id": ctx.from_user.id},
                                       {'$set': {f"settings.{index_of_chat}.updated_date": await get_msk_unix()}, "$push": {f'settings.{index_of_chat}.subscribe_show.paydialogue.payment_methods': {"payment_name": ctx.text, "info": 'None'}}})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')
        await ctx.answer(text=f'Успешное изменение ✅')
        await state.finish()
        await bot.send_message(chat_id=ctx.chat.id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b> Реквизиты', reply_markup=await generate_paydialoguepaydata_show(ctx.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text'], state=MySceneStates.paydialaddinfo_scene)
async def paydialaddinfo_scene(ctx: Message, state: FSMContext):
    try:
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)

        await collection.find_one_and_update({"user_id": ctx.from_user.id}, {'$set': {f"settings.{index_of_chat}.updated_date": await get_msk_unix(), f'settings.{index_of_chat}.subscribe_show.paydialogue.payment_methods.{db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["pmediting"]}.info': ctx.parse_entities(as_html=True)}})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')
        await ctx.answer(text=f'Успешное изменение ✅')
        await state.finish()
        db = await collection.find_one({"user_id": ctx.from_user.id})
        info = "Нету"
        pname = db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["payment_methods"][db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["pmediting"]]["payment_name"]
        if db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["payment_methods"][db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["pmediting"]]["info"] != 'None': info = db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["payment_methods"][db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["pmediting"]]["info"]
        await bot.send_message(chat_id=ctx.chat.id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b>\n\n<a href="https://{db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["pmediting"]}.com">💳</a> <b>Реквизит</b>: {pname}\n\n<b>Условия</b>:\n{info}', reply_markup=await generate_paydialoguepmethmanage())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text'], state=MySceneStates.paydialtarifadd_scene)
async def paydialtarifadd_scene(ctx: Message, state: FSMContext):
    try:
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)

        if db['settings'][index_of_chat]['subscribe_show']['paydialogue']['paydialtarifadd_step'] == 1:
            if not ctx.text.isdigit() or int(ctx.text) == 0: return await ctx.answer('✋ Значение должно быть числом и больше нуля')

            for i in db['settings'][index_of_chat]['subscribe_show']['paydialogue']['tarif_plans']:
                if i['days'] == int(ctx.text): return await ctx.answer('✋ Такое значение уже существует в ваших тарифах')

            try:
                await bot.delete_message(ctx.chat.id, db['quatback'])
            except:
                print('err - scene deletion (NOT Important)')

            quatback = await ctx.answer(text='📋 Введите цену в рублях:', reply_markup=await generate_back_paydialtarif())
            return await collection.find_one_and_update({"user_id": ctx.from_user.id}, {'$set': {"quatback": quatback.message_id, f'settings.{index_of_chat}.subscribe_show.paydialogue.paydialtarifadd_step': 2, f'settings.{index_of_chat}.subscribe_show.paydialogue.paydialtarifadd_data.days': int(ctx.text)}})
        else:
            pattern = r'^\d+(\.\d+)?$'
            if bool(re.match(pattern, ctx.text)) == False: return await ctx.answer('✋ Значение не может быть отрицательным и должно быть числом')
            try:
                await bot.delete_message(ctx.chat.id, db['quatback'])
            except:
                print('err - scene deletion (NOT Important)')
            await ctx.answer('Добавлено ✅')
            await collection.find_one_and_update({"user_id": ctx.from_user.id}, {'$set': {f'settings.{index_of_chat}.subscribe_show.paydialogue.paydialtarifadd_data.price': float(ctx.text)}})
            db = await collection.find_one({"user_id": ctx.from_user.id})
            await collection.find_one_and_update({"user_id": ctx.from_user.id}, {'$set': {f"settings.{index_of_chat}.updated_date": await get_msk_unix()}, "$push": {f'settings.{index_of_chat}.subscribe_show.paydialogue.tarif_plans': db['settings'][index_of_chat]['subscribe_show']['paydialogue']['paydialtarifadd_data']}})

        await state.finish()
        db = await collection.find_one_and_update({"user_id": ctx.from_user.id}, {'$unset': {f'settings.{index_of_chat}.subscribe_show.paydialogue.paydialtarifadd_step': "", f'settings.{index_of_chat}.subscribe_show.paydialogue.paydialtarifadd_data': ""}})
        await bot.send_message(chat_id=ctx.chat.id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b>', reply_markup=await generate_paydialogue_show(ctx.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text'], state=MySceneStates.paydialtarifedit_days_scene)
async def paydialtarifedit_days_scene(ctx: Message, state: FSMContext):
    try:
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)

        if not ctx.text.isdigit() or int(ctx.text) == 0: return await ctx.answer('✋ Значение должно быть числом и больше нуля')

        for i in db['settings'][index_of_chat]['subscribe_show']['paydialogue']['tarif_plans']:
            if i['days'] == int(ctx.text): return await ctx.answer('✋ Такое значение уже существует в ваших тарифах')

        tarif_id = db['settings'][index_of_chat]['subscribe_show']['paydialogue']["paydialtarifid"]
        tarif_index_id = await get_padialtarifindexid(db, index_of_chat, tarif_id)
        await collection.find_one_and_update({"user_id": ctx.from_user.id}, {'$set': {f"settings.{index_of_chat}.updated_date": await get_msk_unix(), f'settings.{index_of_chat}.subscribe_show.paydialogue.tarif_plans.{tarif_index_id}.days': int(ctx.text)}})

        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')

        await state.finish()
        db = await collection.find_one({"user_id": ctx.from_user.id})
        await bot.send_message(chat_id=ctx.chat.id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b>\n\n<a href="https://{db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["tarif_plans"][tarif_index_id]["days"]}.com">📦</a> <b>Тариф на</b>: {db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["tarif_plans"][tarif_index_id]["days"]} дней\n\n<b>Цена</b>:\n{db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["tarif_plans"][tarif_index_id]["price"]}', reply_markup=await generate_paydialoguetarifmanage())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text'], state=MySceneStates.paydialtarifedit_price_scene)
async def paydialtarifedit_price_scene(ctx: Message, state: FSMContext):
    try:
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)

        pattern = r'^\d+(\.\d+)?$'
        if bool(re.match(pattern, ctx.text)) == False: return await ctx.answer('✋ Значение не может быть отрицательным и должно быть числом')

        tarif_id = db['settings'][index_of_chat]['subscribe_show']['paydialogue']["paydialtarifid"]
        tarif_index_id = await get_padialtarifindexid(db, index_of_chat, tarif_id)
        await collection.find_one_and_update({"user_id": ctx.from_user.id}, {'$set': {f"settings.{index_of_chat}.updated_date": await get_msk_unix(), f'settings.{index_of_chat}.subscribe_show.paydialogue.tarif_plans.{tarif_index_id}.price': float(ctx.text)}})

        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')

        await state.finish()
        db = await collection.find_one({"user_id": ctx.from_user.id})
        await bot.send_message(chat_id=ctx.chat.id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b>\n\n<a href="https://{db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["tarif_plans"][tarif_index_id]["days"]}.com">📦</a> <b>Тариф на</b>: {db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["tarif_plans"][tarif_index_id]["days"]} дней\n\n<b>Цена</b>:\n{db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["tarif_plans"][tarif_index_id]["price"]}', reply_markup=await generate_paydialoguetarifmanage())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text'], state=MySceneStates.get_rmsginterval_scene)
async def get_rmsginterval_scene(ctx: Message, state: FSMContext):
    try:
        pattern = r'^(\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]) (0\d|1\d|2[0-3]):([0-5]\d):([0-5]\d))_(\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]) (0\d|1\d|2[0-3]):([0-5]\d):([0-5]\d))$'

        if re.match(pattern, ctx.text) == None: return await ctx.answer('✋ Введите интервал в правильном формате <b><a href="https://telegra.ph/YYYY-MM-DD-HHMMSS-12-30">YYYY-MM-DD HH:MM:SS_YYYY-MM-DD HH:MM:SS</a></b>:')
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)

        offsets = ctx.text.split('_')
        offsets_converted = sorted([await convert_to_unix_timestamp_msk(offsets[0]), await convert_to_unix_timestamp_msk(offsets[1])])
        chat_inf = await bot.get_chat(db['settings'][index_of_chat]['chat_id'])
        asyncio.create_task(delete_chat_messages(db['settings'][index_of_chat]['chat_id'], chat_inf.invite_link, [offsets_converted[0], offsets_converted[1]]))
        trash = await ctx.answer(text='✅ Удаление в процессе...')
        asyncio.create_task(delete_message(5, [trash.message_id], ctx.chat.id))
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')

        await state.finish()
        await bot.send_message(chat_id=ctx.chat.id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Удалить сообщения:</b>', reply_markup=await generate_remmessages_show(ctx.from_user.id))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.message_handler(content_types=['text'], state=MySceneStates.paydial_giveperm)
async def scene_paydial_giveperm(ctx: Message, state: FSMContext):
    try:
        if ctx.text[0] != '@': return await ctx.answer('✋ Юзернейм должен начинаться с <b>"@"</b>')
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        await ctx.answer('Подождите...')
        index_of_chat = await get_dict_index(db, group_id)
        userid = 0
        try:
            userid = await resolve_username_to_user_id(ctx.text.replace('@', ''))
            userid = userid[0]
        except:
            return await ctx.answer('✋ Такого юзернейма нет, введите юзернейм ещё раз:')

        user_dict_index = await get_chat_user_dict_index(db, userid, index_of_chat)
        if user_dict_index == None: return await ctx.answer('✋ Данного пользователя нет в вашем чате, введите юзернейм ещё раз:')

        collection.find_one_and_update({'user_id': ctx.from_user.id}, {"$set": {'paydial_givepermindex': user_dict_index}})
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')

        await state.finish()
        quatback = await bot.send_message(chat_id=ctx.chat.id, text=f'<a href="https://{group_id}.id">⏳</a> Введите количество дней:', reply_markup=await generate_back_paydialgiveperm())
        await MySceneStates.paydial_giveperdays.set()
        await collection.find_one_and_update({"user_id": ctx.from_user.id}, {'$set': {"quatback": quatback.message_id}})
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text'], state=MySceneStates.paydial_giveperdays)
async def scene_paydial_giveperdays(ctx: Message, state: FSMContext):
    try:
        if ctx.text.isdigit() == False or int(ctx.text) == 0: return await ctx.answer('✋ Значение должно быть числом и больше 0')
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        end_data = await calculate_end_date(int(ctx.text))
        collection.find_one_and_update({'user_id': ctx.from_user.id}, {"$set": {f'settings.{index_of_chat}.users.{db["paydial_givepermindex"]}.paydialogue_payed': True, f'settings.{index_of_chat}.users.{db["paydial_givepermindex"]}.paydialogue_payed_for': end_data[1]}, "$push": {f"settings.{index_of_chat}.subscribe_show.paydialogue.customers": {'id': db['settings'][index_of_chat]['users'][db['paydial_givepermindex']]['id'], 'paydialogue_payed_for': end_data[1]}}})
        await ctx.answer(f'✅ Доступ открыт до {end_data[0]}')
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')

        await state.finish()
        await bot.send_message(chat_id=ctx.chat.id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b>', reply_markup=await generate_paydialogue_show(ctx.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['photo', 'video'], state=MySceneStates.get_afkmedia_scene)
async def get_afkmedia_scene(ctx: Message, state: FSMContext):
    try:

        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)

        if db['vorchunmedia_issended'] == True: return

        if ctx.photo:
            await collection.find_one_and_update({"user_id": ctx.from_user.id}, {'$set': {f"settings.{index_of_chat}.afk.media": {"file_id": ctx.photo.pop().file_id, "type": 'Фото'}}})
        else:
            await collection.find_one_and_update({"user_id": ctx.from_user.id}, {'$set': {f"settings.{index_of_chat}.afk.media": {"file_id": ctx.video.file_id, "type": 'Видео'}}})

        await collection.find_one_and_update({"user_id": ctx.from_user.id}, {'$set': {'vorchunmedia_issended': True}})

        await ctx.answer(text='✅ Изменено')
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')

        db = await collection.find_one({"user_id": ctx.from_user.id})
        await state.finish()
        text = f'Текст сообщения отсутствует 🤷‍♂'
        timer = '2700'
        media = 'Нету'
        if 'timer' not in db['settings'][index_of_chat]['afk']:
            await collection.find_one_and_update({"chats": group_id}, {"$set": {f'settings.{index_of_chat}.afk.timer': 'None'}})
        elif db['settings'][index_of_chat]['afk']['timer'] != 'None':
            timer = db['settings'][index_of_chat]['afk']['timer']
        if db['settings'][index_of_chat]['afk']['warning'] != 'None': text = db['settings'][index_of_chat]['afk']['warning']
        if db['settings'][index_of_chat]['afk']['media'] != 'None': media = db['settings'][index_of_chat]['afk']['media']['type']
        await bot.send_message(chat_id=ctx.chat.id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Ворчун:</b>\nЕсли в чате никто не пишет <b>{timer}</b> секунд, то выводит сообщение:\n\n{text}\n\n<b>Медия:</b> {media}', reply_markup=await generate_block_afk_show(db['user_id'], index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['photo', 'video', 'document'], state=MySceneStates.paydialuser_pay)
async def paydialuser_pay(ctx: Message, state: FSMContext):
    try:
        udb = await collection.find_one({"user_id": ctx.from_user.id})
        db = await collection.find_one({"chats": udb["paydial_group"]})
        index_of_chat = await get_dict_index(db, udb['paydial_group'])
        tarif_dict_index = await get_padialtarifindexid(db, index_of_chat, udb["paydial_tarif"])
        chat_name = ''
        try:
            chat = await bot.get_chat(udb['paydial_group'])
            chat_name = chat.title
        except:
            pass

        if ctx.photo:
            await bot.send_photo(chat_id=db['user_id'], photo=ctx.photo.pop().file_id, caption=f'<a href="https://{udb["paydial_group"]}.id">🎤</a> Новый запрос на проверку оплаты для доступа в чат\n\n<a href="https://{udb["paydial_pmeth"]}.{udb["paydial_tarif"]}.com">👤</a> <b>Никнейм участника:</b> <a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a>\n<b>Чат</b>: {chat_name}\n\n<b>Метод оплаты</b>: {db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["payment_methods"][udb["paydial_pmeth"]]["payment_name"]}\n<b>Количество дней:</b> {db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["tarif_plans"][tarif_dict_index]["days"]} дней\n<b>Цена</b>: {db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["tarif_plans"][tarif_dict_index]["price"]} ₽', reply_markup=await generate_paydialuserpay_acchoice(ctx.from_user.id))
        elif ctx.document and ctx.document.mime_type == "application/pdf":
            await bot.send_document(chat_id=db['user_id'], document=ctx.document.file_id, caption=f'<a href="https://{udb["paydial_group"]}.id">🎤</a> Новый запрос на проверку оплаты для доступа в чат\n\n<a href="https://{udb["paydial_pmeth"]}.{udb["paydial_tarif"]}.com">👤</a> <b>Никнейм участника:</b> <a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a>\n<b>Чат</b>: {chat_name}\n\n<b>Метод оплаты</b>: {db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["payment_methods"][udb["paydial_pmeth"]]["payment_name"]}\n<b>Количество дней:</b> {db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["tarif_plans"][tarif_dict_index]["days"]} дней\n<b>Цена</b>: {db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["tarif_plans"][tarif_dict_index]["price"]} ₽', reply_markup=await generate_paydialuserpay_acchoice(ctx.from_user.id))
        else:
            await bot.send_video(chat_id=db['user_id'], video=ctx.video.file_id, caption=f'<a href="https://{udb["paydial_group"]}.id">🎤</a> Новый запрос на проверку оплаты для доступа в чат\n\n<a href="https://{udb["paydial_pmeth"]}.{udb["paydial_tarif"]}.com">👤</a> <b>Никнейм участника:</b> <a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a>\n<b>Чат</b>: {chat_name}\n\n<b>Метод оплаты</b>: {db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["payment_methods"][udb["paydial_pmeth"]]["payment_name"]}\n<b>Количество дней:</b> {db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["tarif_plans"][tarif_dict_index]["days"]} дней\n<b>Цена</b>: {db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["tarif_plans"][tarif_dict_index]["price"]} ₽', reply_markup=await generate_paydialuserpay_acchoice(ctx.from_user.id))

        await ctx.answer(text='✅ Доказательства отправлены, ожидайте...')
        try:
            await bot.delete_message(ctx.chat.id, udb['quatback'])
        except:
            print('err - scene deletion (NOT Important)')

        await state.finish()
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types='text', state=MySceneStates.paydial_editwarning)
async def paydial_editwarning(ctx: Message, state: FSMContext):
    try:
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        text = ctx.parse_entities(as_html=True)
        await collection.find_one_and_update({'user_id': ctx.from_user.id}, {"$set": {f'settings.{index_of_chat}.subscribe_show.paydialogue.warning': text}})

        await ctx.answer(text='Изменено ✅')
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')

        await state.finish()
        await ctx.answer(text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b>\n\n<b>Сообщение при нарушении:</b>\n{text}', reply_markup=await generate_paydialogue_show(ctx.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types='text', state=MySceneStates.subscribe_editwarning)
async def subscribe_editwarning(ctx: Message, state: FSMContext):
    try:
        db = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        text = ctx.parse_entities(as_html=True)
        await collection.find_one_and_update({'user_id': ctx.from_user.id}, {"$set": {f'settings.{index_of_chat}.subscribe_show.warning': text}})

        await ctx.answer(text='Изменено ✅')
        try:
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except:
            print('err - scene deletion (NOT Important)')

        await state.finish()

        channels_len = len(db['settings'][index_of_chat]['subscribe_show']['channels'])
        await ctx.answer(text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Подписать:</b>\nЕсли пользователь делает попытку писать в чат что-либо, то он видит сообщение:\n\n{text}\n\n<b>Ваших каналов:</b> {channels_len}', reply_markup=await generate_subscribe_show(ctx.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))



@dp.message_handler(content_types='text', state=MySceneStates.paydialuser_getemail)
async def paydialuser_getemail(ctx: Message, state: FSMContext):
    try:
        udb = await collection.find_one({"user_id": ctx.from_user.id})
        group_id = udb['paydial_group']
        db = await collection.find_one({"chats": group_id})
        index_of_chat = await get_dict_index(db, group_id)
        pattern = re.compile(r".*@gmail\.com$")
        gmail = ctx.text.replace(' ', '')
        if pattern.match(gmail) == None: return await ctx.answer(text='✋ Не правильный формат, введите gmail ещё раз: (Пример: example@gmail.com)')

        try:
            await bot.delete_message(ctx.chat.id, udb['quatback'])
        except:
            print('err - scene deletion (NOT Important)')

        await MySceneStates.paydial_yooauto.set()
        chat_name = ''
        try:
            chat = await bot.get_chat(group_id)
            chat_name = chat.title
        except:
            pass

        index_of_chat = await get_dict_index(db, group_id)
        tarif_index_id = await get_padialtarifindexid(db, index_of_chat, udb["paydial_tarif"])
        amount = db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["tarif_plans"][tarif_index_id]["price"]
        days = db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["tarif_plans"][tarif_index_id]["days"]
        url, pid = create_paydial_payment(amount=amount, days=days, gmail=gmail)
        await collection.find_one_and_update({"user_id": ctx.from_user.id}, {'$set': {"paydial_yoo_pid": pid}})
        await MySceneStates.paydial_yooauto.set()
        return await bot.send_message(chat_id=ctx.chat.id, text=f'<a href="https://{group_id}.id">🎤</a> <b>Плати Говори:</b> {chat_name}\n\n🔓 Доступ к чату на {days} дней\n\nВот ссылка на оплату:', reply_markup=await generate_paydialogueuser_yoopay(url, amount))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.message_handler(content_types=['text', 'photo', 'audio', 'video', 'voice', 'document'])
async def message_staff(ctx: Message):
    try:
        if ctx.chat.type == 'group' or ctx.chat.type == 'supergroup':
            db = await collection.find_one({"chats": f'{ctx.chat.id}'})
            if db == None: return

            try:
                if await blocked(db['user_id']):
                    return
            except:
                pass

            index_of_chat = await get_dict_index(db, ctx.chat.id)
            settings_of_chat = db['settings'][index_of_chat]
            if 'users' not in settings_of_chat: await collection.find_one_and_update({"chats": f"{ctx.chat.id}"}, {
                "$set": {f'settings.{index_of_chat}.users': []}})
            users_count = await bot.get_chat_members_count(ctx.chat.id)
            db = await collection.find_one_and_update({'chats': f'{ctx.chat.id}'}, {
                "$set": {f"settings.{index_of_chat}.last_msg": datetime.now().strftime('%H:%M:%S'),
                         f"settings.{index_of_chat}.users_count": users_count, f"settings.{index_of_chat}.bot_send_afk": False}})
            get_user = await get_chat_user_dict_index(db, ctx.from_user.id, index_of_chat)
            if get_user == None: await collection.find_one_and_update({'chats': f'{ctx.chat.id}'}, {"$push": {f'settings.{index_of_chat}.users': {"id": ctx.from_user.id, 'l_msg': await get_msk_unix(), 'paydialogue_payed': False, 'paydialogue_payed_for': 'None'}}})
            else: await collection.find_one_and_update({'chats': f'{ctx.chat.id}'}, {"$set": {f'settings.{index_of_chat}.users.{get_user}.l_msg': await get_msk_unix()}})
            db = await collection.find_one({'chats': f'{ctx.chat.id}'})
            get_user = await get_chat_user_dict_index(db, ctx.from_user.id, index_of_chat)
            if 'paydialogue_payed' not in db['settings'][index_of_chat]['users'][get_user]: await collection.find_one_and_update({'chats': f'{ctx.chat.id}'}, {'$set': {f'settings.{index_of_chat}.users.{get_user}.paydialogue_payed': False, 'paydialogue_payed_for': 'None'}})
            db = await collection.find_one({'chats': f'{ctx.chat.id}'})
            if db['settings'][index_of_chat]['users'][get_user]['paydialogue_payed'] == True:
                curent_unix = await get_msk_unix()
                payedfor_unix = db['settings'][index_of_chat]['users'][get_user]['paydialogue_payed_for']
                if curent_unix > payedfor_unix:
                    await collection.find_one_and_update({'chats': f'{ctx.chat.id}'}, {'$set': {f'settings.{index_of_chat}.users.{get_user}.paydialogue_payed': False}, "$pull": {f'settings.{index_of_chat}.subscribe_show.paydialogue.customers': {'id': ctx.from_user.id}}})
            db = await collection.find_one({'chats': f'{ctx.chat.id}'})
            adb = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
            if users_count > adb['limit_to_users'] and db['settings'][index_of_chat]['lic'] == False:
                if 'lic_warn' not in db['settings'][index_of_chat]: await collection.find_one_and_update({'chats': f'{ctx.chat.id}'}, {
                "$set": {f"settings.{index_of_chat}.lic_warn": False}})
                db = await collection.find_one({'chats': f'{ctx.chat.id}'})
                if db['settings'][index_of_chat]['lic_warn'] == False:
                    await bot.send_message(db['user_id'],
                                           f'Вы превысили Бесплатный лимит подписчиков на группу. Чтобы продолжить использовать бота, необходимо приобрести лицензию на чат в настройках чата - <b>{ctx.chat.title}</b>',
                                           reply_markup=await generate_mychats_button(), disable_notification=False)
                    return await collection.find_one_and_update({'chats': f'{ctx.chat.id}'}, {
                        "$set": {f"settings.{index_of_chat}.lic_warn": True}})

            if 'subscribe_show' in db['settings'][index_of_chat] and 'paydialogue' not in db['settings'][index_of_chat]['subscribe_show'] and ctx.from_user.id != db['user_id'] or ctx.from_user.id != db['user_id'] and 'paydialogue' in db['settings'][index_of_chat]['subscribe_show'] and db['settings'][index_of_chat]['subscribe_show']['paydialogue']['active'] == False and db['settings'][index_of_chat]['users'][get_user]['paydialogue_payed'] == False:
                if db['settings'][index_of_chat]['subscribe_show']['active'] == True:
                    if len(db['settings'][index_of_chat]['subscribe_show']['channels']) != 0:
                        valid_channels = []
                        botd = await bot.get_me()
                        botid = botd.id
                        for i in db['settings'][index_of_chat]['subscribe_show']['channels']:
                            is_bot_in = await bot.get_chat_member(i['id'], botid)
                            if is_bot_in.status != 'left': valid_channels.append({"id": i['id'], 'title': i['title'], 'user_name': i['user_name']})

                        if len(valid_channels) != 0:
                            channels_left = []
                            user_is_started = await collection.find_one({"user_id": ctx.from_user.id})
                            for i in valid_channels:
                                user_in = await bot.get_chat_member(i['id'], ctx.from_user.id)
                                if user_in.status == 'left': channels_left.append({"id": i['id'], 'title': i['title'], 'user_name': i['user_name']})

                            if len(channels_left) != 0:
                                if user_is_started == None: channels_left.append('bot')
                                await ctx.delete()
                                text = f'<b><a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a></b>, чтобы продолжить общение в нашем чате, вам необходимо подписаться на следующие каналы:'
                                if 'warning' in db['settings'][index_of_chat]['subscribe_show'] and db['settings'][index_of_chat]['subscribe_show']['warning'] != 'None':
                                    text = db['settings'][index_of_chat]['subscribe_show']['warning']
                                trash = await ctx.answer(text.replace("{member_name}", f'<b><a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a></b>'), reply_markup=await generate_channels_tosbleft(channels_left, ctx.chat.id))
                                return asyncio.create_task(delete_message(15, [trash.message_id], trash.chat.id))

            elif 'subscribe_show' in db['settings'][index_of_chat] and 'paydialogue' in db['settings'][index_of_chat]['subscribe_show'] and db['settings'][index_of_chat]['subscribe_show']['active'] == False and ctx.from_user.id != db['user_id'] and db['settings'][index_of_chat]['users'][get_user]['paydialogue_payed'] == False:
                if db['settings'][index_of_chat]['subscribe_show']['paydialogue']['active'] == True and len(db['settings'][index_of_chat]['subscribe_show']['paydialogue']['tarif_plans']) != 0 and len(db['settings'][index_of_chat]['subscribe_show']['paydialogue']['payment_methods']) != 0:
                    botd = await bot.get_me()
                    botid = botd.id
                    actions_left = []
                    user_is_started = await collection.find_one({"user_id": ctx.from_user.id})
                    if db['settings'][index_of_chat]['users'][get_user]['paydialogue_payed'] == False: actions_left.append('paydialogue')

                    if len(actions_left) != 0:
                        if user_is_started == None: actions_left.append('bot')
                        await ctx.delete()
                        text = f'<b><a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a></b>, чтобы продолжить общение в нашем чате, вам необходимо оплатить доступ к чату:'
                        if 'warning' in db['settings'][index_of_chat]['subscribe_show']['paydialogue'] and db['settings'][index_of_chat]['subscribe_show']['paydialogue']['warning'] != 'None':
                            text = db['settings'][index_of_chat]['subscribe_show']['paydialogue']['warning']
                        trash = await ctx.answer(text.replace("{member_name}", f'<b><a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a></b>'), reply_markup=await generate_channels_tosbleft(actions_left, chat_id=ctx.chat.id))
                        return asyncio.create_task(delete_message(15, [trash.message_id], trash.chat.id))
            elif 'subscribe_show' in db['settings'][index_of_chat] and db['settings'][index_of_chat]['subscribe_show']['active'] == True and db['settings'][index_of_chat]['subscribe_show']['paydialogue']['active'] == True and db['settings'][index_of_chat]['users'][get_user]['paydialogue_payed'] == False and ctx.from_user.id != db['user_id']:
                valid_channels = []
                botd = await bot.get_me()
                botid = botd.id
                for i in db['settings'][index_of_chat]['subscribe_show']['channels']:
                    is_bot_in = await bot.get_chat_member(i['id'], botid)
                    if is_bot_in.status != 'left': valid_channels.append({"id": i['id'], 'title': i['title'], 'user_name': i['user_name']})

                channels_left = []
                user_is_started = await collection.find_one({"user_id": ctx.from_user.id})
                if db['settings'][index_of_chat]['users'][get_user]['paydialogue_payed'] == False and len(db['settings'][index_of_chat]['subscribe_show']['paydialogue']['tarif_plans']) != 0 and len(db['settings'][index_of_chat]['subscribe_show']['paydialogue']['payment_methods']) != 0: channels_left.append('paydialogue')

                if len(valid_channels) != 0:
                    for i in valid_channels:
                        user_in = await bot.get_chat_member(i['id'], ctx.from_user.id)
                        if user_in.status == 'left': channels_left.append({"id": i['id'], 'title': i['title'], 'user_name': i['user_name']})
                if len(channels_left) != 0:
                    for i in channels_left:
                        if str(type(i)).split("'")[1] == 'dict':
                            if user_is_started == None: channels_left.append('bot')
                            await ctx.delete()
                            text = f'<b><a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a></b>, чтобы продолжить общение в нашем чате, вам необходимо подписаться на следующие каналы или оплатить доступ:'
                            if 'warning' in db['settings'][index_of_chat]['subscribe_show']['paydialogue'] and db['settings'][index_of_chat]['subscribe_show']['paydialogue']['warning'] != 'None':
                                text = db['settings'][index_of_chat]['subscribe_show']['paydialogue']['warning']
                            trash = await ctx.answer(text.replace("{member_name}", f'<b><a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a></b>'), reply_markup=await generate_channels_tosbleft(channels_left, ctx.chat.id))
                            return asyncio.create_task(delete_message(15, [trash.message_id], trash.chat.id))


            if 'skromniy' in db['settings'][index_of_chat] and 'j_t' in db['settings'][index_of_chat]['users'][get_user]:
                if db['settings'][index_of_chat]['skromniy']['active'] == True and db['settings'][index_of_chat]['skromniy']['timer'] >= 0:
                    restriction_time = (await get_msk_unix() - db['settings'][index_of_chat]['users'][get_user]['j_t']) // 60
                    timer = 180
                    if db['settings'][index_of_chat]['skromniy']['timer'] != 0: timer = db['settings'][index_of_chat]['skromniy']['timer']
                    left = max(0, timer - restriction_time)
                    if restriction_time < timer:
                        await ctx.delete()
                        text = f'Гостевой режим, {left} минут тишины.'
                        if 'warning' in db['settings'][index_of_chat]['skromniy']:
                            if db['settings'][index_of_chat]['skromniy']['warning'] != 'None': text = db['settings'][index_of_chat]['skromniy']['warning'].replace('{time_left}', f'<b>{left}</b>').replace('{member_name}', ctx.from_user.first_name)
                        trash = await ctx.answer(text)
                        return asyncio.create_task(delete_message(10, [trash.message_id], trash.chat.id))

            if 'tixiychas' in db['settings'][index_of_chat] and ctx.from_user.id != db['user_id']:
                if db['settings'][index_of_chat]['tixiychas']['active'] == True and len(db['settings'][index_of_chat]['tixiychas']['timers']) != 0:
                    if await is_current_time_in_range(db['settings'][index_of_chat]['tixiychas']['timers']):
                        await ctx.delete()
                        text = f'🤫 Тсс! <b><a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a></b>, в чате тихий час'
                        trash = await ctx.answer(text)
                        return asyncio.create_task(delete_message(10, [trash.message_id], trash.chat.id))


            # and db['user_id'] not in adb['admins'] and db['user_id'] != int(config['MAIN_ADMIN_ID'])
            if db['settings'][index_of_chat]['block_repostes']['active'] == True:
                if ctx.forward_from or ctx.forward_from_chat:
                    await ctx.delete()
                    warning_text = f'✋ <a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a>, вы нарушаете наши правила! Репосты запрещены!'
                    if db['settings'][index_of_chat]['block_repostes']['warning'] != 'None':
                        warning_text = db['settings'][index_of_chat]['block_repostes']['warning'].replace("{member_name}", ctx.from_user.first_name)
                    return await ctx.answer(warning_text)

            if db['settings'][index_of_chat]['block_ping']['active'] == True:
                if ctx.text:
                    mentions = await check_mentions(ctx.text)
                    entitle_user_index = await get_user_dict_index(ctx.entities)
                    if mentions[0] == True or entitle_user_index != None:
                        if mentions[1] == f'@{ctx.from_user.username}': return
                        if entitle_user_index != None:
                            if ctx.entities[entitle_user_index].user.id == ctx.from_user.id: return

                        await ctx.delete()
                        warning_text = f'✋ <a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a>, вы нарушаете наши правила! Пинг запрещен!'
                        if db['settings'][index_of_chat]['block_ping']['warning'] != 'None':
                            warning_text = db['settings'][index_of_chat]['block_ping']['warning'].replace("{member_name}", ctx.from_user.first_name)
                        return await ctx.answer(warning_text)
                    elif db['settings'][index_of_chat]['block_ping']['s_m'] == True:
                        if await has_split_mention(ctx.text):
                            await ctx.delete()
                            warning_text = f'✋ <a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a>, вы нарушаете наши правила! Пинг запрещен!'
                            if db['settings'][index_of_chat]['block_ping']['warning'] != 'None':
                                warning_text = db['settings'][index_of_chat]['block_ping']['warning'].replace("{member_name}", ctx.from_user.first_name)
                            return await ctx.answer(warning_text)
                    # elif db['settings'][index_of_chat]['block_ping']['forbtoenter'] == True:
                    #     if not ctx.from_user.username and not ctx.from_user.
                    #     if has_split_mention(ctx.text):
                    #         await ctx.delete()
                    #         warning_text = f'✋ <a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a>, вы нарушаете наши правила! Пинг запрещен!'
                    #         if db['settings'][index_of_chat]['block_ping']['warning'] != 'None':
                    #             warning_text = db['settings'][index_of_chat]['block_ping']['warning'].replace("{member_name}", ctx.from_user.first_name)
                    #         return await ctx.answer(warning_text)
                if ctx.caption:
                    mentions = await check_mentions(ctx.caption)
                    entitle_user_index = await get_user_dict_index(ctx.caption)
                    if mentions[0] == True or entitle_user_index != None:
                        if mentions[1] == f'@{ctx.from_user.username}': return
                        if entitle_user_index != None:
                            if ctx.caption_entities[entitle_user_index].user.id == ctx.from_user.id: return

                        await ctx.delete()
                        warning_text = f'✋ <a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a>, вы нарушаете наши правила! Пинг запрещен!'
                        if db['settings'][index_of_chat]['block_ping']['warning'] != 'None':
                            warning_text = db['settings'][index_of_chat]['block_ping']['warning'].replace("{member_name}", ctx.from_user.first_name)
                        return await ctx.answer(warning_text)
                    elif db['settings'][index_of_chat]['block_ping']['s_m'] == True:
                        if await has_split_mention(ctx.caption):
                            await ctx.delete()
                            warning_text = f'✋ <a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a>, вы нарушаете наши правила! Пинг запрещен!'
                            if db['settings'][index_of_chat]['block_ping']['warning'] != 'None':
                                warning_text = db['settings'][index_of_chat]['block_ping']['warning'].replace("{member_name}", ctx.from_user.first_name)
                            return await ctx.answer(warning_text)


            if db['settings'][index_of_chat]['block_resources']['active'] == True:
                if ctx.text:
                    if len(db['settings'][index_of_chat]['block_resources']['r_list']) == 0: return
                    if await contains_external_links(ctx.text, db['settings'][index_of_chat]['block_resources']['r_list']):
                        await ctx.delete()
                        warning_text = f'✋ <a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a>, вы нарушаете наши правила! Запрещены любые ссылки!'
                        if db['settings'][index_of_chat]['block_resources']['warning'] != 'None':
                            warning_text = db['settings'][index_of_chat]['block_resources']['warning'].replace("{member_name}", ctx.from_user.first_name)
                        return await ctx.answer(warning_text)
                    elif await check_tolink_entitle(ctx.entities, db['settings'][index_of_chat]['block_resources']['r_list']) == True:
                        await ctx.delete()
                        warning_text = f'✋ <a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a>, вы нарушаете наши правила! Запрещены любые ссылки!'
                        if db['settings'][index_of_chat]['block_resources']['warning'] != 'None':
                            warning_text = db['settings'][index_of_chat]['block_resources']['warning'].replace("{member_name}", ctx.from_user.first_name)
                        return await ctx.answer(warning_text)
                if ctx.caption:
                    if len(db['settings'][index_of_chat]['block_resources']['r_list']) == 0: return
                    if await contains_external_links(ctx.caption, db['settings'][index_of_chat]['block_resources']['r_list']):
                        await ctx.delete()
                        warning_text = f'✋ <a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a>, вы нарушаете наши правила! Запрещены любые ссылки!'
                        if db['settings'][index_of_chat]['block_resources']['warning'] != 'None':
                            warning_text = db['settings'][index_of_chat]['block_resources']['warning'].replace("{member_name}", ctx.from_user.first_name)
                        return await ctx.answer(warning_text)
                    elif await check_tolink_entitle(ctx.caption_entities, db['settings'][index_of_chat]['block_resources']['r_list']) == True:
                        await ctx.delete()
                        warning_text = f'✋ <a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a>, вы нарушаете наши правила! Запрещены любые ссылки!'
                        if db['settings'][index_of_chat]['block_resources']['warning'] != 'None':
                            warning_text = db['settings'][index_of_chat]['block_resources']['warning'].replace("{member_name}", ctx.from_user.first_name)
                        return await ctx.answer(warning_text)


            if 'msg_filter' in db['settings'][index_of_chat]:
                if db['settings'][index_of_chat]['msg_filter']['italic'] == True:
                    if ctx.text:
                        entitle_indx = await get_entitle_dict_index(ctx.entities, 'italic')
                        if entitle_indx != None:
                            await ctx.delete()
                            return await ctx.answer('✋ В чате запрещено писать курсивом')
                    if ctx.caption:
                        entitle_indx = await get_entitle_dict_index(ctx.caption_entities, 'italic')
                        if entitle_indx != None:
                            await ctx.delete()
                            return await ctx.answer('✋ В чате запрещено писать курсивом')

                if db['settings'][index_of_chat]['msg_filter']['bold'] == True:
                    if ctx.text:
                        entitle_indx = await get_entitle_dict_index(ctx.entities, 'bold')
                        if entitle_indx != None:
                            await ctx.delete()
                            return await ctx.answer('✋ В чате запрещено писать жирным шрифтом')
                    if ctx.caption:
                        entitle_indx = await get_entitle_dict_index(ctx.caption_entities, 'bold')
                        if entitle_indx != None:
                            await ctx.delete()
                            return await ctx.answer('✋ В чате запрещено писать жирным шрифтом')

                if db['settings'][index_of_chat]['msg_filter']['capslock'] == True:
                    if ctx.text:
                        words_lists = ctx.text.replace('_', ' ').split(' ')
                        for i in words_lists:
                            if i.isupper():
                                await ctx.delete()
                                await ctx.answer('✋ В чате запрещено капсить')
                                break
                    if ctx.caption:
                        words_lists = ctx.caption.split(' ')
                        for i in words_lists:
                            if i.isupper():
                                await ctx.delete()
                                await ctx.answer('✋ В чате запрещено капсить')
                                break

                if 'mfiltersa' in db['settings'][index_of_chat]['msg_filter'] and db['settings'][index_of_chat]['msg_filter']['mfiltersa'] == True:
                    if ctx.text:
                        if await text_check_filters(db['settings'][index_of_chat]['msg_filter']['mfilters'], ctx.text) == True:
                            await ctx.delete()
                            text = f'✋ <b><a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a></b>, у нас запрещена нецензурная лексика!'
                            if db['settings'][index_of_chat]['msg_filter']['mfilterw'] != 'None': text = db['settings'][index_of_chat]['msg_filter']['mfilterw'].replace('{member_name}', f'<b><a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a></b>')
                            trash = await ctx.answer(text)
                            return asyncio.create_task(delete_message(10, [trash.message_id], ctx.chat.id))
                    if ctx.caption:
                        if await text_check_filters(db['settings'][index_of_chat]['msg_filter']['mfilters'], ctx.caption) == True:
                            await ctx.delete()
                            text = f'✋ <b><a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a></b>, у нас запрещена нецензурная лексика!'
                            if db['settings'][index_of_chat]['msg_filter']['mfilterw'] != 'None': text = db['settings'][index_of_chat]['msg_filter']['mfilterw'].replace('{member_name}', f'<b><a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a></b>')
                            trash = await ctx.answer(text)
                            return asyncio.create_task(delete_message(10, [trash.message_id], ctx.chat.id))


            if 'antiflud_block' in db['settings'][index_of_chat]:
                if db['settings'][index_of_chat]['antiflud_block']['active'] == True:
                    user_data_index = get_user
                    if user_data_index != None:
                        user_unix = db['settings'][index_of_chat]['users'][user_data_index]['l_msg']
                        curent_msk = await get_msk_unix()
                        math = curent_msk - user_unix
                        if math < db['settings'][index_of_chat]['antiflud_block']['timer']:
                            await ctx.delete()
                            text = f'✋ <a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a>, флудить запрещено!'
                            if db['settings'][index_of_chat]['antiflud_block']['warning'] != 'None': text = db['settings'][index_of_chat]['antiflud_block']['warning'].replace('{member_name}', f'✋ <a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a>')
                            await ctx.answer(text)

            if 'nofile_show' in db['settings'][index_of_chat]:
                if db['settings'][index_of_chat]['nofile_show']['active'] == True:
                    bite_limit = db['settings'][index_of_chat]['nofile_show']['limit'] * 1024 * 1024
                    text = 'Вы превысили ограничение веса файла данного чата. Лимит до: {l} мб'
                    if db['settings'][index_of_chat]['nofile_show']['limit'] == 0: text = '✋ В чате запрещено отправлять любые файлы'
                    if ctx.document:
                        file_size = ctx.document.file_size
                        if file_size > bite_limit:
                            await ctx.delete()
                            return await ctx.answer(text.replace('{l}', f'<b>{db["settings"][index_of_chat]["nofile_show"]["limit"]}</b>'))
                    elif ctx.photo:
                        file_size = ctx.photo[0].file_size
                        if file_size > bite_limit:
                            await ctx.delete()
                            return await ctx.answer(text.replace('{l}', f'<b>{db["settings"][index_of_chat]["nofile_show"]["limit"]}</b>'))
                    elif ctx.video:
                        file_size = ctx.video.file_size
                        if file_size > bite_limit:
                            await ctx.delete()
                            return await ctx.answer(text.replace('{l}', f'<b>{db["settings"][index_of_chat]["nofile_show"]["limit"]}</b>'))
                    elif ctx.audio:
                        file_size = ctx.audio.file_size
                        if file_size > bite_limit:
                            await ctx.delete()
                            return await ctx.answer(text.replace('{l}', f'<b>{db["settings"][index_of_chat]["nofile_show"]["limit"]}</b>'))

    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))
