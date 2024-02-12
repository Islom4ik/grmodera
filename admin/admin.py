from data.loader import bot, dp, FSMContext, State, Message, config
from data.configs import *
from data.texts import *
from aiogram.types import CallbackQuery, ContentTypes
from database.database import collection, ObjectId
from states_scenes.scene import MySceneStates
import traceback
from keyboards.inline_keyboards import *
import asyncio
import re

@dp.callback_query_handler(lambda call: call.data == 'admin_edit_money')
async def answer_to_admin_emoney(call: CallbackQuery):
    try:
        db = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
        prices = ''
        unsortedp = db['price']
        positions = sorted(unsortedp, key=lambda x: int(x['period']))
        for i in positions:
            prices += f'🔹 {i["period"]} дней – {i["price"]}₽\n'
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                       text=f'💎 <b>Прайс-лист:</b>\n{prices}\nВыберите действие:',
                                       reply_markup=await generate_admin_price_edit_choice())
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'admin_edit_limits')
async def answer_to_admin_elimit(call: CallbackQuery):
    try:
        db = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'✋ <b>Лимиты:</b>\n\n<b>Демо режим до:</b> {db["limit_to_users"]} юзеров',
                                    reply_markup=await generate_admin_limit_edit_choice())
    except Exception as e:
        traceback.print_exc()

@dp.message_handler(commands=['admin'])
async def react_to_admin(ctx: Message):
    try:
        await ctx.delete()
        db = await collection.find_one({'_id': ObjectId('64987b1eeed9918b13b0e8b4')})
        if ctx.from_user.id not in db['admins'] and ctx.from_user.id != int(config['MAIN_ADMIN_ID']): return await ctx.answer('🔒')
        await ctx.answer(f'Добро пожаловать в админку, <a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a>', reply_markup=await generate_admin_main_page(ctx.from_user.id))
        if int(config['MAIN_ADMIN_ID']) == ctx.from_user.id: return
        await bot.send_message(chat_id=config['MAIN_ADMIN_ID'], text=f'‼ <b>Новое посещение админки бота:</b>\n\n<b>Пользователь:</b> <a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a>\n<b>Время посещения:</b> только что')
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'admin_exit')
async def answer_to_admin_exit(call: CallbackQuery):
    try:
        await call.answer('😜 До новых встреч!')
        db = await collection.find_one({"user_id": call.from_user.id})
        if len(db['chats']) >= 1:
            lic = 'Лицензии нет'
            if db['lic'] != 'None': lic = db['lic']
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=f'👤 Ваш профиль:\n\n<b>Пользователь:</b> #{db["inlineid"]} - {db["register_data"]}\n<b>Username:</b> @{call.from_user.username}\n<b>Имя:</b> {call.from_user.first_name}\n<b>Чатов:</b> {len(db["chats"])}\n<b>Лицензий:</b> {db["lic"]}',
                                        reply_markup=await generate_add_button(), disable_web_page_preview=True)
        else:
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=t_start_text.format(bot_user=t_bot_user),
                                        reply_markup=await generate_add_button(), disable_web_page_preview=True)
    except Exception as e:
        traceback.print_exc()


@dp.callback_query_handler(lambda call: call.data == 'admins_spravkas')
async def answer_to_admins_spravkas(call: CallbackQuery):
    try:
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='ℹ Выберите функцию для изменения справки:', reply_markup=await generate_admins_spravkas())
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'back_from_admins_spravka_show')
async def answer_to_admcanc_adminspravscene(call: CallbackQuery):
    try:
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='ℹ Выберите функцию для изменения справки:', reply_markup=await generate_admins_spravkas())
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'admcanc_adminspravscene', state=MySceneStates.spravka_edit_scene)
async def answer_to_admcanc_adminspravscene(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        user_db = await collection.find_one({'user_id': call.from_user.id})
        db = await collection.find_one({'_id': ObjectId('64987b1eeed9918b13b0e8b4')})
        spravka_index = user_db['sprvindxed']
        text = 'ℹ Информации нет'
        if db['spravka'][spravka_index]['info'] != 'None': text = db['spravka'][spravka_index]['info']
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'ℹ <b>Справка:</b> {db["spravka"][spravka_index]["n"]}\n\n{text}', reply_markup=await generate_admin_spravka_show())
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: 'sprvd' in call.data)
async def answer_to_admins_sprvd(call: CallbackQuery):
    try:
        call_data = call.data.split('_')[1]
        db = await collection.find_one({'_id': ObjectId('64987b1eeed9918b13b0e8b4')})
        spravka_index = await get_spravkas_dict_index(call_data)
        await collection.find_one_and_update({"user_id": call.from_user.id}, {'$set': {'sprvindxed': spravka_index}})
        text = 'ℹ Информации нет'
        if db['spravka'][spravka_index]['info'] != 'None': text = db['spravka'][spravka_index]['info']
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'📝 <b>Справка:</b> {db["spravka"][spravka_index]["n"]}\n\n{text}', reply_markup=await generate_admin_spravka_show())
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'sprvedit')
async def answer_to_admins_sprvedit(call: CallbackQuery):
    try:
        user_db = await collection.find_one({'user_id': call.from_user.id})
        db = await collection.find_one({'_id': ObjectId('64987b1eeed9918b13b0e8b4')})
        spravka_index = user_db['sprvindxed']
        await MySceneStates.spravka_edit_scene.set()
        text = 'ℹ Информации нет'
        if db['spravka'][spravka_index]['info'] != 'None': text = await shorten_text(db['spravka'][spravka_index]['info'], 250)
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        adminback = await bot.send_message(chat_id=call.message.chat.id, text=f'📝 <b>Нынешний текст справки:</b>\n\n{text}\n\n<b>Введите текст для замены:</b>', reply_markup=await admin_back_from_sprav_scene())
        await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')}, {'$set': {'adminback': adminback.message_id}})
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'admins_manager')
async def answer_to_admins_manager(call: CallbackQuery):
    try:
        db = await collection.find_one({'_id': ObjectId('64987b1eeed9918b13b0e8b4')})
        admins = []
        for i in db['admins']:
            try:
                user = await bot.get_chat(i)
                admins.append(f'<a href="tg://user?id={user.id}">{user.first_name}</a>')
            except ChatNotFound:
                await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')}, {"$pull": {'admins': i}})
                continue

        admins = '\n'.join(admins)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"🛂 <b>Список пользователей с доступом в админку:</b>\n{admins}\n\nВыберите действие:", reply_markup=await generate_admins_manager())
    except Exception as e:
        traceback.print_exc()


@dp.callback_query_handler(lambda call: call.data == 'back_from_admins_manager')
async def answer_to_back_from_admins_manager(call: CallbackQuery):
    try:
        await bot.edit_message_text(text=f'Добро пожаловать в админку, <a href="tg://user?id={call.from_user.id}">{call.from_user.first_name}</a>', chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await generate_admin_main_page(call.from_user.id))
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'back_from_admins_spravkas')
async def answer_to_back_from_admins_spravkas(call: CallbackQuery):
    try:
        await bot.edit_message_text(text=f'Добро пожаловать в админку, <a href="tg://user?id={call.from_user.id}">{call.from_user.first_name}</a>', chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await generate_admin_main_page(call.from_user.id))
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'admin_add')
async def answer_to_admin_add(call: CallbackQuery):
    try:
        await call.answer()
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        adminback = await bot.send_message(call.message.chat.id, '👮 Введите юзернейм или прямую сслку на пользователя:', reply_markup=await admin_back_from_add_admin())
        await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')}, {"$set": {'adminback': adminback.message_id}})
        await MySceneStates.add_admin.set()
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'admin_rem')
async def answer_to_admin_rem(call: CallbackQuery):
    try:
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='🪓 Выберите админа для снятия доступа к админке:', reply_markup=await generate_admins_rem())
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: 'remadm' in call.data)
async def answer_to_remadm(call: CallbackQuery):
    try:
        call_data = call.data.split('_')[1]
        await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')}, {"$pull": {'admins': int(call_data)}})
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await generate_admins_rem())
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'back_from_adminrem')
async def answer_to_back_from_adminrem(call: CallbackQuery):
    try:
        db = await collection.find_one({'_id': ObjectId('64987b1eeed9918b13b0e8b4')})
        admins = []
        for i in db['admins']:
            try:
                user = await bot.get_chat(i)
                admins.append(f'<a href="tg://user?id={user.id}">{user.first_name}</a>')
            except ChatNotFound:
                await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')}, {"$pull": {'admins': i}})
                continue

        admins = '\n'.join(admins)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"🛂 <b>Список пользователей с доступом в админку:</b>\n{admins}\n\nВыберите действие:", reply_markup=await generate_admins_manager())
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'admcanc_addaddmin', state=MySceneStates.add_admin)
async def answer_to_admcanc_addaddmin(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({'_id': ObjectId('64987b1eeed9918b13b0e8b4')})
        admins = []
        for i in db['admins']:
            try:
                user = await bot.get_chat(i)
                admins.append(f'<a href="tg://user?id={user.id}">{user.first_name}</a>')
            except ChatNotFound:
                await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')}, {"$pull": {'admins': i}})
                continue

        admins = '\n'.join(admins)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"🛂 <b>Список пользователей с доступом в админку:</b>\n{admins}\n\nВыберите действие:", reply_markup=await generate_admins_manager())
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'admin_post')
async def answer_to_admin_post(call: CallbackQuery):
    try:
        await call.answer()
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        adminback = await bot.send_message(call.message.chat.id, '💬 Отправьте сообщение, которое хотите отправить всем пользователям своего бота:', reply_markup=await admin_back_from_admin_post())
        await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')}, {"$set": {'adminback': adminback.message_id}})
        await MySceneStates.post_to_users.set()
    except Exception as e:
        traceback.print_exc()


@dp.callback_query_handler(lambda call: call.data == 'admcanc_adminpost', state=MySceneStates.post_to_users)
async def answer_to_admcanc_adminpost(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({'_id': ObjectId('64987b1eeed9918b13b0e8b4')})
        await bot.edit_message_text(text=f'Добро пожаловать в админку, <a href="tg://user?id={call.from_user.id}">{call.from_user.first_name}</a>', chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await generate_admin_main_page(call.from_user.id))
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'admcanc_adminedlimits', state=MySceneStates.aedit_limittousers_scene)
async def answer_to_admcanc_adminedlimits(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'✋ <b>Лимиты:</b>\n\n<b>Демо режим до:</b> {db["limit_to_users"]} юзеров',
                                    reply_markup=await generate_admin_limit_edit_choice())
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'admin_bot_stats')
@dp.callback_query_handler(lambda call: call.data == 'back_from_admusers_stats')
async def answer_to_admin_stats(call: CallbackQuery):
    try:
        db = await collection.find_one({'_id': ObjectId('64987b1eeed9918b13b0e8b4')})
        await bot.edit_message_text(text=f'📊 Общая статистика бота:\n\n<b>Кол-во пользователей:</b> {len(db["users"])}\n<b>Кол-во чатов с ботом:</b> {len(db["groups"])}\n<b>Кол-во купленных лицензий за все время:</b> {db["lics_buyed"]}\n<b>Кол-во заработанных денег за все время:</b> {db["earned"]}₽\n<b>Кол-во чатов с лицензией:</b> {len(db["chat_with_lics"])}', chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await generate_admin_return())
    except Exception as e:
        traceback.print_exc()



@dp.callback_query_handler(lambda call: call.data == 'admusersstats_idsearch')
async def answer_to_admusersstats_idsearch(call: CallbackQuery):
    try:
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        quatback = await bot.send_message(call.message.chat.id, '🪪 Введите id пользователя без #:', reply_markup=await generate_back_from_search_id())
        await collection.find_one_and_update({"user_id": call.from_user.id}, {'$set': {'quatback': quatback.message_id}})
        await MySceneStates.admin_search_id_query.set()
    except Exception as e:
        traceback.print_exc()

@dp.message_handler(content_types=['text'], state=MySceneStates.admin_search_id_query)
async def admin_search_id_query_scene(ctx: Message, state: FSMContext):
    try:
        if ctx.text.isdigit() != True: return await ctx.answer('✋ Введите id пользователя без #:')
        user = await collection.find_one({"inlineid": int(ctx.text)})
        if user == None: return await ctx.answer('🤷‍♂ Пользователь не найден, введите id еще раз:')

        if 'blocked' not in user: await collection.find_one_and_update({"user_id": user['user_id']}, {'$set': {'blocked': False}})
        name = 'Неизвестно'
        user_name = 'Нету'
        try:
            guser = await bot.get_chat(user['user_id'])
            name = await shorten_text(guser.first_name, 9)
            if guser.username: user_name = f'@{guser.username}'
        except Exception as e:
            traceback.print_exc()

        try:
            db = await collection.find_one({'user_id': ctx.from_user.id})
            await bot.delete_message(ctx.chat.id, db['quatback'])
        except Exception as e:
            traceback.print_exc()

        await state.finish()
        await ctx.answer(text=f'<a href="https://{user["user_id"]}.id">👤</a> <b>Пользователь:</b> <a href="tg://user?id={user["user_id"]}">{name}</a>\n\n<b>Данные:</b> #{user["inlineid"]} - {user["register_data"]}\n<b>Username:</b> {user_name}\n<b>Имя:</b> {name}\n<b>Чатов:</b> {len(user["chats"])}\n<b>Лицензий:</b> {user["lic"]}', reply_markup=await generate_user_info_show(user['user_id']))
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'back_from_search_id', state=MySceneStates.admin_search_id_query)
async def answer_to_back_from_search_id(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"user_id": call.from_user.id})
        await bot.send_message(call.message.chat.id, '👥 Пользователи:', reply_markup=await generate_admusers_select(db['adminusersstats_pc']))
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'admin_statsfinancs')
async def answer_to_admin_statsfinancs(call: CallbackQuery):
    try:
        adb = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
        pages = [adb['licsbuyedinfos'][i:i + 10] for i in range(0, len(adb['licsbuyedinfos']), 10)]
        current_page = 0 % len(pages)
        text = f'🧾 <b>Финансы:</b>\n\n'
        for info in pages[current_page]:
            if info == 'none': continue
            text += f'{info["info"]}\n\n'

        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=await generate_admin_statsfinancs(f'{current_page + 1} из {len(pages)}'))
        await collection.find_one_and_update({"user_id": call.from_user.id}, {"$set": {"adminstatsfinancsp": 0}})
    except Exception as e:
        traceback.print_exc()


@dp.callback_query_handler(lambda call: call.data == 'prev_financian_page')
async def answer_to_admin_statsusers(call: CallbackQuery):
    db = await collection.find_one({"user_id": call.from_user.id})
    if db['adminstatsfinancsp'] == 0: return await call.answer()
    currentp = db['adminstatsfinancsp'] - 1
    adb = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
    pages = [adb['licsbuyedinfos'][i:i + 10] for i in range(0, len(adb['licsbuyedinfos']), 10)]
    current_page = currentp % len(pages)
    text = f'🧾 <b>Финансы:</b>\n\n'
    for info in pages[current_page]:
        if info == 'none': continue
        text += f'{info["info"]}\n\n'

    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=await generate_admin_statsfinancs(f'{current_page + 1} из {len(pages)}'))
    await collection.find_one_and_update({"user_id": call.from_user.id}, {"$set": {"adminstatsfinancsp": currentp}})

@dp.callback_query_handler(lambda call: call.data == 'next_financian_page')
async def answer_to_admin_statsusers(call: CallbackQuery):
    db = await collection.find_one({"user_id": call.from_user.id})
    adb = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
    pages = [adb['licsbuyedinfos'][i:i + 10] for i in range(0, len(adb['licsbuyedinfos']), 10)]
    currentp = db['adminstatsfinancsp'] + 1
    if len(pages) == currentp: return await call.answer()
    current_page = currentp % len(pages)
    text = f'🧾 <b>Финансы:</b>\n\n'
    for info in pages[current_page]:
        if info == 'none': continue
        text += f'{info["info"]}\n\n'
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=await generate_admin_statsfinancs(f'{current_page + 1} из {len(pages)}'))
    await collection.find_one_and_update({"user_id": call.from_user.id}, {"$set": {"adminstatsfinancsp": currentp}})

@dp.callback_query_handler(lambda call: call.data == 'back_from_admin_statsfinancs')
async def answer_to_admin_statsusers(call: CallbackQuery):
    db = await collection.find_one({'_id': ObjectId('64987b1eeed9918b13b0e8b4')})
    await bot.edit_message_text(text=f'Добро пожаловать в админку, <a href="tg://user?id={call.from_user.id}">{call.from_user.first_name}</a>', chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await generate_admin_main_page(call.from_user.id))


@dp.callback_query_handler(lambda call: call.data == 'admin_statsusers')
async def answer_to_admin_statsusers(call: CallbackQuery):
    try:
        await bot.edit_message_text(text=f'👥 Пользователи:', chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await generate_admusers_select())
        await collection.find_one_and_update({"user_id": call.from_user.id}, {"$set": {'adminusersstats_pc': 0}})
    except Exception as e:
        traceback.print_exc()



@dp.callback_query_handler(lambda call: call.data == 'admusers_prev')
async def answer_to_admusers_prev(call: CallbackQuery):
    try:
        db = await collection.find_one({'user_id': call.from_user.id})
        current = db['adminusersstats_pc'] - 1
        if current == -1: return await call.answer()
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await generate_admusers_select(current_page=current))
        await collection.find_one_and_update({"user_id": call.from_user.id}, {"$set": {'adminusersstats_pc': current}})
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'admusers_next')
async def answer_to_admusers_next(call: CallbackQuery):
    try:
        db = await collection.find_one({'user_id': call.from_user.id})
        current = db['adminusersstats_pc'] + 1
        len_pages = await pagesusers_gen()
        if current >= len_pages: return await call.answer()
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await generate_admusers_select(current_page=current))
        await collection.find_one_and_update({"user_id": call.from_user.id}, {"$set": {'adminusersstats_pc': current}})
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: 'stuser' in call.data)
async def answer_to_stuser(call: CallbackQuery):
    try:
        call_data = call.data.split('_')[1]
        user = await collection.find_one({"user_id": int(call_data)})
        if user == None: return
        if 'blocked' not in user: await collection.find_one_and_update({"user_id": user['user_id']}, {'$set': {'blocked': False}})
        name = 'Неизвестно'
        user_name = 'Нету'
        try:
            guser = await bot.get_chat(call_data)
            name = await shorten_text(guser.first_name, 9)
            if guser.username: user_name = f'@{guser.username}'

        except Exception as e:
            traceback.print_exc()

        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<a href="https://{call_data}.id">👤</a> <b>Пользователь:</b> <a href="tg://user?id={call_data}">{name}</a>\n\n<b>Данные:</b> #{user["inlineid"]} - {user["register_data"]}\n<b>Username:</b> {user_name}\n<b>Имя:</b> {name}\n<b>Чатов:</b> {len(user["chats"])}\n<b>Лицензий:</b> {user["lic"]}', reply_markup=await generate_user_info_show(user['user_id']))
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'blockunblock')
async def answer_to_blockunblock(call: CallbackQuery):
    try:
        user_id_url = call.message.entities[0].url
        user_id = re.sub(r"\D", "", user_id_url)
        user = await collection.find_one({"user_id": int(user_id)})
        if user['blocked'] == True:
            await collection.find_one_and_update({"user_id": user['user_id']}, {'$set': {'blocked': False}})
            return await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await generate_user_info_show(user['user_id']))
        else:
            await collection.find_one_and_update({"user_id": user['user_id']}, {'$set': {'blocked': True}})
            return await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await generate_user_info_show(user['user_id']))

    except Exception as e:
        traceback.print_exc()


@dp.callback_query_handler(lambda call: call.data == 'lic_addparent')
async def answer_to_lic_remparent(call: CallbackQuery):
    try:
        user_id_url = call.message.entities[0].url
        user_id = re.sub(r"[^0-9-q]", "", user_id_url).split('q')[0]
        db = await collection.find_one({"user_id": call.from_user.id})
        group_id = re.sub(r"[^0-9-q]", "", user_id_url).split('q')[1]
        db = await collection.find_one({"user_id": int(user_id)})
        index_of_chat = await get_dict_index(db, group_id)
        if db['settings'][index_of_chat]['lic'] == True: return await call.answer('✋ В данном чате и так есть лицензия', show_alert=True)
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=call.message.chat.id, text='💎 Введите срок лицензии в днях:')
        await MySceneStates.addparent_lic_scene.set()
        await collection.find_one_and_update({'user_id': call.from_user.id}, {"$set": {'addparent_group_user': f'{user_id}_{group_id}'}})
    except Exception as e:
        traceback.print_exc()

@dp.message_handler(content_types=['text'], state=MySceneStates.addparent_lic_scene)
async def answer_to_addparent_lic_scene(ctx: Message, state: FSMContext):
    try:
        if ctx.text.isdigit() == False: return await ctx.answer('✋ Введите целые числа:')
        end = await calculate_end_date(int(ctx.text))
        db = await collection.find_one({"user_id": ctx.from_user.id})
        user_db = await collection.find_one({"user_id": int(db['addparent_group_user'].split('_')[0])})
        index_of_chat = await get_dict_index(user_db, db['addparent_group_user'].split('_')[1])
        adb = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
        alic = adb['active_lic'] + 1
        lics = user_db['lic'] + 1
        current_datetime = datetime.now(pytz.utc)
        moscow_tz = pytz.timezone('Europe/Moscow')
        current_datetime_moscow = current_datetime.astimezone(moscow_tz)
        formatted_datetime = current_datetime_moscow.strftime("%H:%M %d.%m.%Y")
        await collection.find_one_and_update({"user_id": user_db['user_id']}, {'$set': {"lic": lics, f'settings.{index_of_chat}.lic': True, f'settings.{index_of_chat}.lic_end': [end[0], end[1], ctx.text], f'settings.{index_of_chat}.lic_buyed_date': formatted_datetime}})
        await collection.find_one_and_update({"_id": ObjectId('64987b1eeed9918b13b0e8b4')}, {'$push': {'chat_with_lics': db['addparent_group_user'].split('_')[1]}, '$set': {'active_lic': alic}})
        chatname = '{Произошла ошибка при получении чата}'
        try:
            chat = await bot.get_chat(user_db['settings'][index_of_chat]['chat_id'])
            chatname = chat.title
        except Exception as e:
            print(e)
        await bot.send_message(chat_id=user_db['user_id'], text=f'💎 Вам выдана лицензия для группы <b>{chatname}</b> сроком на {ctx.text} дней.')
        await state.finish()

        user = await collection.find_one({'user_id': int(db["addparent_group_user"].split("_")[0])})
        active_func = ''
        if user['settings'][index_of_chat]['afk']['active'] == True: active_func += 'Ворчун, '
        if user['settings'][index_of_chat]['system_notice']['active'] == True: active_func += 'Удаление системных оповещений, '
        if user['settings'][index_of_chat]['block_repostes']['active'] == True: active_func += 'Блокировка репостов, '
        if user['settings'][index_of_chat]['block_ping']['active'] == True: active_func += 'Блокировка пинга, '
        if user['settings'][index_of_chat]['block_resources']['active'] == True: active_func += 'Блокировка внешних ресурсов, '
        if len(user['settings'][index_of_chat]['blocked_syms']) != 0: active_func += 'Блокировка символов в никнеймах, '
        if "msg_filter" in user['settings'][index_of_chat]:
            if user['settings'][index_of_chat]['msg_filter']['italic'] == True or user['settings'][index_of_chat]['msg_filter']['capslock'] == True or user['settings'][index_of_chat]['msg_filter']['bold'] == True:
                active_func += 'Фильтры: '
                filters = []
                if user['settings'][index_of_chat]['msg_filter']['italic'] == True:
                    filters.append('Italic; ')
                if user['settings'][index_of_chat]['msg_filter']['bold'] == True:
                    filters.append('Bold; ')
                if user['settings'][index_of_chat]['msg_filter']['capslock'] == True:
                    filters.append('Caps Lock; ')
                if len(filters) != 0:
                    active_func += ''.join(filters)
                else:
                    active_func += 'Нету; '
            if user['settings'][index_of_chat]['msg_filter']['mfiltersa'] == True:
                active_func += f'Фильтр слов, '
            if user['settings'][index_of_chat]['noname'] == True:
                active_func += f'Нет имени'

        lic = 'Без лицензии'
        if user['settings'][index_of_chat]['lic'] == True: lic = f'С лицензией / до {user["settings"][index_of_chat]["lic_end"][0]}'
        chat = 'Бот кикнут'
        try:
            gchat = await bot.get_chat(db["addparent_group_user"].split("_")[1])
            chat = gchat
        except:
            print('')

        await bot.send_message(chat_id=ctx.chat.id, text=f'<a href="https://{db["addparent_group_user"].split("_")[0]}q{db["addparent_group_user"].split("_")[1]}.id">👤</a> <b>Чат:</b> {await shorten_text(chat.title, 13)}\n\n<b>Участников:</b> {await chat.get_members_count()}\n<b>Лицензия:</b> {lic}\n\n<b>Активные функции:</b>\n{active_func}', reply_markup=await generate_userschat_actions())
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(error_traceback, e)

@dp.callback_query_handler(lambda call: call.data == 'lic_remparent')
async def answer_to_lic_remparent(call: CallbackQuery):
    try:
        user_id_url = call.message.entities[0].url
        user_id = re.sub(r"[^0-9-q]", "", user_id_url).split('q')[0]
        db = await collection.find_one({"user_id": call.from_user.id})
        group_id = re.sub(r"[^0-9-q]", "", user_id_url).split('q')[1]
        db = await collection.find_one({"user_id": int(user_id)})
        index_of_chat = await get_dict_index(db, group_id)
        if db['settings'][index_of_chat]['lic'] == False: return await call.answer('✋ В данном чате и так нет лицензии', show_alert=True)
        lic_count = db['lic'] - 1
        await collection.find_one_and_update({'user_id': db['user_id']}, {'$set': {f'settings.{index_of_chat}.lic': False, 'lic': lic_count}})
        adb = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
        alics = adb['active_lic'] - 1
        await collection.find_one_and_update({"_id": ObjectId('64987b1eeed9918b13b0e8b4')}, {'$set': {f'active_lic': alics}, "$pull": {'chat_with_lics': group_id}})
        chatname = '{Произошла ошибка при получении чата}'
        try:
            chat = await bot.get_chat(db['settings'][index_of_chat]['chat_id'])
            chatname = chat.title
        except Exception as e:
            print(e)
        await bot.send_message(chat_id=db['user_id'], text=f'💎 У Вас изъята лицензия к группе <b>{chatname}</b>. Причины уточняйте в поддержке бота.', reply_markup=await support())

        user = await collection.find_one({'user_id': int(user_id)})
        active_func = ''
        if user['settings'][index_of_chat]['afk']['active'] == True: active_func += 'Ворчун, '
        if user['settings'][index_of_chat]['system_notice']['active'] == True: active_func += 'Удаление системных оповещений, '
        if user['settings'][index_of_chat]['block_repostes']['active'] == True: active_func += 'Блокировка репостов, '
        if user['settings'][index_of_chat]['block_ping']['active'] == True: active_func += 'Блокировка пинга, '
        if user['settings'][index_of_chat]['block_resources']['active'] == True: active_func += 'Блокировка внешних ресурсов, '
        if len(user['settings'][index_of_chat]['blocked_syms']) != 0: active_func += 'Блокировка символов в никнеймах, '
        if user['settings'][index_of_chat]['msg_filter']['italic'] == True or user['settings'][index_of_chat]['msg_filter']['capslock'] == True or user['settings'][index_of_chat]['msg_filter']['bold'] == True:
            active_func += 'Фильтры: '
            filters = []
            if user['settings'][index_of_chat]['msg_filter']['italic'] == True:
                filters.append('Italic; ')
            if user['settings'][index_of_chat]['msg_filter']['bold'] == True:
                filters.append('Bold; ')
            if user['settings'][index_of_chat]['msg_filter']['capslock'] == True:
                filters.append('Caps Lock; ')
            if len(filters) != 0:
                active_func += ''.join(filters)
            else:
                active_func += 'Нету; '
        if user['settings'][index_of_chat]['msg_filter']['mfiltersa'] == True:
            active_func += f'Фильтр слов, '
        if user['settings'][index_of_chat]['noname'] == True:
            active_func += f'Нет имени'

        lic = 'Без лицензии'
        if user['settings'][index_of_chat]['lic'] == True: lic = f'С лицензией / до {user["settings"][index_of_chat]["lic_end"][0]}'
        chat = 'Бот кикнут'
        try:
            gchat = await bot.get_chat(group_id)
            chat = gchat
        except:
            print('')

        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<a href="https://{user_id}q{group_id}.id">👤</a> <b>Чат:</b> {await shorten_text(chat.title, 13)}\n\n<b>Участников:</b> {await chat.get_members_count()}\n<b>Лицензия:</b> {lic}\n\n<b>Активные функции:</b>\n{active_func}', reply_markup=await generate_userschat_actions())
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'userstat_groups')
@dp.callback_query_handler(lambda call: call.data == 'back_from_userschat_actions')
async def answer_to_userstat_groups(call: CallbackQuery):
    try:
        user_id_url = call.message.entities[0].url
        user_id = re.sub(r"[^0-9-q]", "", user_id_url)
        if len(user_id.split('q')) == 2: user_id = user_id.split('q')[0]
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<a href="https://{user_id}.id">👤</a> <b>Чаты пользователя:</b>', reply_markup=await generate_userstats_chats(user_id=user_id))
        await collection.find_one_and_update({'user_id': call.from_user.id}, {'$set': {'adminuserstatsgroup_pc': 0}})
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'usersstats_groups_next')
async def answer_to_usersstats_groups_next(call: CallbackQuery):
    try:
        user_id_url = call.message.entities[0].url
        user_id = re.sub(r"\D", "", user_id_url)
        db = await collection.find_one({'user_id': call.from_user.id})
        current = db['adminuserstatsgroup_pc'] + 1
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await generate_userstats_chats(user_id, current_page=current))
        await collection.find_one_and_update({'user_id': call.from_user.id}, {'$set': {'adminuserstatsgroup_pc': current}})
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'usersstats_groups_prev')
async def answer_to_usersstats_groups_prev(call: CallbackQuery):
    try:
        user_id_url = call.message.entities[0].url
        user_id = re.sub(r"\D", "", user_id_url)
        db = await collection.find_one({'user_id': call.from_user.id})
        current = db['adminuserstatsgroup_pc'] - 1
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await generate_userstats_chats(user_id, current_page=current))
        await collection.find_one_and_update({'user_id': call.from_user.id}, {'$set': {'adminuserstatsgroup_pc': current}})
    except Exception as e:
        traceback.print_exc()


@dp.callback_query_handler(lambda call: 'userstatschat' in call.data)
async def answer_to_userstatschat(call: CallbackQuery):
    try:
        user_id_url = call.message.entities[0].url
        user_id = re.sub(r"\D", "", user_id_url)
        user = await collection.find_one({'user_id': int(user_id)})
        group_id = call.data.split('_')[1]
        index_of_chat = await get_dict_index(user, group_id)
        active_func = ''
        if user['settings'][index_of_chat]['afk']['active'] == True: active_func += 'Ворчун, '
        if user['settings'][index_of_chat]['system_notice']['active'] == True: active_func += 'Удаление системных оповещений, '
        if user['settings'][index_of_chat]['block_repostes']['active'] == True: active_func += 'Блокировка репостов, '
        if user['settings'][index_of_chat]['block_ping']['active'] == True: active_func += 'Блокировка пинга, '
        if user['settings'][index_of_chat]['block_resources']['active'] == True: active_func += 'Блокировка внешних ресурсов, '
        if len(user['settings'][index_of_chat]['blocked_syms']) != 0: active_func += 'Блокировка символов в никнеймах, '
        if user['settings'][index_of_chat]['msg_filter']['italic'] == True or user['settings'][index_of_chat]['msg_filter']['capslock'] == True or user['settings'][index_of_chat]['msg_filter']['bold'] == True:
            active_func += 'Фильтры: '
            filters = []
            if user['settings'][index_of_chat]['msg_filter']['italic'] == True:
                filters.append('Italic; ')
            if user['settings'][index_of_chat]['msg_filter']['bold'] == True:
                filters.append('Bold; ')
            if user['settings'][index_of_chat]['msg_filter']['capslock'] == True:
                filters.append('Caps Lock; ')
            if len(filters) != 0: active_func += ''.join(filters)
            else: active_func += 'Нету; '
        if user['settings'][index_of_chat]['msg_filter']['mfiltersa'] == True:
            active_func += f'Фильтр слов, '
        if user['settings'][index_of_chat]['noname'] == True:
            active_func += f'Нет имени'

        lic = 'Без лицензии'
        if user['settings'][index_of_chat]['lic'] == True: lic = f'С лицензией / до {user["settings"][index_of_chat]["lic_end"][0]}'
        chat = 'Бот кикнут'
        try:
            gchat = await bot.get_chat(group_id)
            chat = gchat
        except:
            print('')

        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<a href="https://{user_id}q{group_id}.com">👤</a> <b>Чат:</b> {await shorten_text(chat.title, 13)}\n\n<b>Участников:</b> {await chat.get_members_count()}\n<b>Лицензия:</b> {lic}\n\n<b>Активные функции:</b>\n{active_func}', reply_markup=await generate_userschat_actions())
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'back_from_userstats_groups_chose')
async def answer_to_back_from_userstats_groups_chose(call: CallbackQuery):
    try:
        user_id_url = call.message.entities[0].url
        call_data = re.sub(r"\D", "", user_id_url)
        user = await collection.find_one({"user_id": int(call_data)})
        if user == None: return
        if 'blocked' not in user: await collection.find_one_and_update({"user_id": user['user_id']}, {'$set': {'blocked': False}})
        name = 'Неизвестно'
        user_name = 'Нету'
        try:
            guser = await bot.get_chat(call_data)
            name = await shorten_text(guser.first_name, 9)
            if guser.username: user_name = f'@{guser.username}'
        except Exception as e:
            traceback.print_exc()

        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<a href="https://{call_data}.id">👤</a> <b>Пользователь:</b> <a href="tg://user?id={call_data}">{name}</a>\n\n<b>Данные:</b> #{user["inlineid"]} - {user["register_data"]}\n<b>Username:</b> {user_name}\n<b>Имя:</b> {name}\n<b>Чатов:</b> {len(user["chats"])}\n<b>Лицензий:</b> {user["lic"]}', reply_markup=await generate_user_info_show(user['user_id']))
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'back_from_user_info')
async def back_from_user_info(call: CallbackQuery):
    try:
        db = await collection.find_one({"user_id": call.from_user.id})
        await bot.edit_message_text(text=f'👥 Пользователи:', chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await generate_admusers_select(db['adminusersstats_pc']))
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'admin_stats_back')
async def answer_to_admin_back(call: CallbackQuery):
    try:
        await call.answer()
        await bot.edit_message_text(text=f'Добро пожаловать в админку, <a href="tg://user?id={call.from_user.id}">{call.from_user.first_name}</a>', chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await generate_admin_main_page(call.from_user.id))
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'admin_deleteposition')
async def answer_to_admin_deleteposition(call: CallbackQuery):
    try:
        db = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
        if len(db['price']) == 0: return await bot.send_message(call.message.chat.id, call.message.message_id, text='⚠ Извините, но я не нашел ни одну позицию в базе данных')
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'⬇ <b>Выберите позицию которую хотите удалить:</b>', reply_markup=await generate_delete_positions())
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'admin_addposition')
async def answer_to_admin_admin_addposition(call: CallbackQuery):
    try:
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await MySceneStates.addposition_period_scene.set()
        adminback = await bot.send_message(chat_id=call.message.chat.id, text='✍ Введите срок действия лицензии в днях:', reply_markup=await admin_back_from_add_admin_position())
        await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')}, {"$set": {'adminback': adminback.message_id}})
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'admcanc_addaddminposition', state=MySceneStates.addposition_period_scene)
async def answer_to_admcanc_addaddminposition(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
        prices = ''
        unsortedp = db['price']
        positions = sorted(unsortedp, key=lambda x: int(x['period']))
        for i in positions:
            prices += f'🔹 {i["period"]} дней – {i["price"]}₽\n'
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'💎 <b>Прайс-лист:</b>\n{prices}\nВыберите действие:',
                                    reply_markup=await generate_admin_price_edit_choice())
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'admin_editposition')
async def answer_to_admin_admin_editposition(call: CallbackQuery):
    try:
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='⬇ Выберите позицию которую хотите изменить:', reply_markup=await generate_eidit_positions())
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: 'positedite' in call.data)
async def answer_to_admin_positedite(call: CallbackQuery):
    try:
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        db = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
        index_of_possition = None
        for index, item in enumerate(db['price']):
            if item.get("period") == call.data.split("_")[1]:
                index_of_possition = index
                break
        await bot.send_message(chat_id=call.message.chat.id, text=f'⬇ Выберите то, что бы вы хотели изменить в этой позиции:\n\n<b>{db["price"][index_of_possition]["period"]}</b> дней - <b>{db["price"][index_of_possition]["price"]}</b>₽', reply_markup=await generate_positedit())
        await collection.find_one_and_update({"_id": ObjectId('64987b1eeed9918b13b0e8b4')},
                                          {"$set": {"positindx": index_of_possition, "positeddays": 'None', "positedprice": 'None'}})
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'back_from_edit_limits')
async def answer_to_back_from_edits(call: CallbackQuery):
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'Добро пожаловать в админку, <a href="tg://user?id={call.from_user.id}">{call.from_user.first_name}</a>', reply_markup=await generate_admin_main_page(call.from_user.id))


@dp.callback_query_handler(lambda call: call.data == 'posited_days')
async def answer_to_admin_posited_days(call: CallbackQuery):
    try:
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await MySceneStates.posited_days_scene.set()
        adminback = await bot.send_message(call.message.chat.id, text='✍ Введите срок действия лицензии в днях:', reply_markup=await admin_back_from_add_admin_positedday())
        await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')}, {"$set": {'adminback': adminback.message_id}})
    except Exception as e:
        traceback.print_exc()


@dp.callback_query_handler(lambda call: call.data == 'admcanc_addaddminpositedday', state=MySceneStates.posited_days_scene)
async def answer_to_admcanc_addaddminpositedday(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
        index_of_possition = db['positindx']
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'⬇ Выберите то, что бы вы хотели изменить в этой позиции:\n\n<b>{db["price"][index_of_possition]["period"]}</b> дней - <b>{db["price"][index_of_possition]["price"]}</b>₽', reply_markup=await generate_positedit())
        await collection.find_one_and_update({"_id": ObjectId('64987b1eeed9918b13b0e8b4')},
                                       {"$set": {"positindx": index_of_possition, "positeddays": 'None', "positedprice": 'None'}})
    except Exception as e:
        traceback.print_exc()


@dp.callback_query_handler(lambda call: call.data == 'posited_price')
async def answer_to_admin_posited_price(call: CallbackQuery):
    try:
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await MySceneStates.posited_price_scene.set()
        adminback = await bot.send_message(call.message.chat.id, text='✍ Введите сумму которую заплатит пользователь при покупке(Значение должно быть в десятичном-float формате. Пример: 100.0 | 250.0):', reply_markup=await admin_back_from_add_admin_positedprice())
        await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')}, {"$set": {'adminback': adminback.message_id}})
    except Exception as e:
        traceback.print_exc()


@dp.callback_query_handler(lambda call: call.data == 'admcanc_addaddminpositedprice', state=MySceneStates.posited_price_scene)
async def answer_to_admcanc_addaddminpositedprice(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
        index_of_possition = db['positindx']
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'⬇ Выберите то, что бы вы хотели изменить в этой позиции:\n\n<b>{db["price"][index_of_possition]["period"]}</b> дней - <b>{db["price"][index_of_possition]["price"]}</b>₽', reply_markup=await generate_positedit())
        await collection.find_one_and_update({"_id": ObjectId('64987b1eeed9918b13b0e8b4')},
                                       {"$set": {"positindx": index_of_possition, "positeddays": 'None', "positedprice": 'None'}})
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'posited_cancel')
async def answer_to_admin_posited_cancel(call: CallbackQuery):
    try:
        db = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
        prices = ''
        unsortedp = db['price']
        positions = sorted(unsortedp, key=lambda x: int(x['period']))
        for i in positions:
            prices += f'🔹 {i["period"]} дней – {i["price"]}₽\n'
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await bot.send_message(chat_id=call.message.chat.id,
                             text=f'💎 <b>Прайс-лист:</b>\n{prices}\nВыберите действие:',
                             reply_markup=await generate_admin_price_edit_choice())
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'posited_accept')
async def answer_to_admin_posited_accept(call: CallbackQuery):
    try:
        db = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
        if db['positeddays'] == "None" and db['positedprice'] == "None": return await call.answer('Вы ещё ничего не изменили 😶',
                                                                              show_alert=True)
        if db['positeddays'] != 'None': await collection.find_one_and_update({"_id": ObjectId('64987b1eeed9918b13b0e8b4')}, {
            "$set": {f'price.{db["positindx"]}.period': db['positeddays']}})
        if db['positedprice'] != 'None': await collection.find_one_and_update({"_id": ObjectId('64987b1eeed9918b13b0e8b4')}, {
            "$set": {f'price.{db["positindx"]}.price': db['positedprice']}})
        await call.answer('Успешное изменение ✅')
        db = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
        prices = ''
        unsortedp = db['price']
        positions = sorted(unsortedp, key=lambda x: int(x['period']))
        for i in positions:
            prices += f'🔹 {i["period"]} дней – {i["price"]}₽\n'
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await bot.send_message(chat_id=call.message.chat.id,
                             text=f'💎 <b>Прайс-лист:</b>\n{prices}\nВыберите действие:',
                             reply_markup=await generate_admin_price_edit_choice())
    except Exception as e:
        traceback.print_exc()


@dp.callback_query_handler(lambda call: call.data == 'aedit_limittousers')
async def answer_to_admin_aedit_limittousers(call: CallbackQuery):
    try:
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await MySceneStates.aedit_limittousers_scene.set()
        adminback = await bot.send_message(call.message.chat.id, text='✍ Введите лимит пользователей на чаты, в которых отсутсвует лицензия:', reply_markup=await admin_back_from_admin_edlimits())
        await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')}, {"$set": {'adminback': adminback.message_id}})
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: 'positdelete' in call.data)
async def react_to_admin_positdelete(call: CallbackQuery):
    try:
        db = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
        index_of_possition = None
        for index, item in enumerate(db['price']):
            if item.get("period") == call.data.split("_")[1]:
                index_of_possition = index
                break

        if len(db['price']) == 1: return await call.answer('✋ В базе должна оставаться хотя бы одна позиция')

        await collection.find_one_and_update({"_id": ObjectId('64987b1eeed9918b13b0e8b4')}, {"$pull": {f'price': {"period": call.data.split("_")[1]}}})

        await call.answer('Успешное удаление позиции!')
        await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=await generate_delete_positions())
    except Exception as e:
        traceback.print_exc()

@dp.callback_query_handler(lambda call: call.data == 'back_to_edit_price')
async def answer_to_admin_back_to_edit_price(call: CallbackQuery):
    db = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
    prices = ''
    unsortedp = db['price']
    positions = sorted(unsortedp, key=lambda x: int(x['period']))
    for i in positions:
        prices += f'🔹 {i["period"]} дней – {i["price"]}₽\n'
    await call.answer()
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                   text=f'💎 <b>Прайс-лист:</b>\n{prices}\nВыберите действие:',
                                   reply_markup=await generate_admin_price_edit_choice())

@dp.callback_query_handler(lambda call: call.data == 'back_from_added_position')
async def answer_to_admin_back_from_added_position(call: CallbackQuery):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    db = await collection.find_one({'_id': ObjectId('64987b1eeed9918b13b0e8b4')})
    if call.from_user.id not in db['admins'] and call.from_user.id != int(
        config['MAIN_ADMIN_ID']): return await call.answer('🔒')
    await bot.send_message(chat_id=call.message.chat.id,
                           text=f'Добро пожаловать в админку, <a href="tg://user?id={call.from_user.id}">{call.from_user.first_name}</a>',
                           reply_markup=await generate_admin_main_page(call.from_user.id))

@dp.message_handler(content_types=['text'], state=MySceneStates.add_admin)
async def add_admin_scene(ctx: Message, state: FSMContext):
    try:
        user = ctx.text
        dicts_with_user_key = []

        pattern = r"https://t.me/([\w_]+)"

        if user[0] == '@':
            userid = await resolve_username_to_user_id(user.replace('@', ''))
            dicts_with_user_key.append(userid[0])
        elif re.search(pattern, user):
            usern = re.findall(pattern, user)[0]
            userid = await resolve_username_to_user_id(usern)
            dicts_with_user_key.append(userid[0])
        else:
            return await ctx.answer('👮 Введите юзернейм пользователя через @ или прямую ссылку на пользователя:')

        if len(dicts_with_user_key) == 0:
            trash = await ctx.answer('🪪 Пользователь не найден')
            await state.finish()
            db = await collection.find_one({'_id': ObjectId('64987b1eeed9918b13b0e8b4')})
            admins = []
            for i in db['admins']:
                try:
                    user = await bot.get_chat(i)
                    admins.append(f'<a href="tg://user?id={user.id}">{user.first_name}</a>')
                except ChatNotFound:
                    await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')}, {"$pull": {'admins': i}})
                    continue

            admins = '\n'.join(admins)
            await ctx.answer(text=f"🛂 <b>Список пользователей с доступом в админку:</b>\n{admins}\n\nВыберите действие:", reply_markup=await generate_admins_manager())
            return asyncio.create_task(delete_message(5, [trash.message_id, ctx.message_id], ctx.chat.id))

        db = await collection.find_one({'_id': ObjectId('64987b1eeed9918b13b0e8b4')})
        try:
            await bot.delete_message(ctx.chat.id, db['adminback'])
        except:
            print('err - scene deletion (NOT Important)')
        for i in dicts_with_user_key:
            if i in db['admins']: continue
            await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')}, {'$push': {'admins': i}})

        await ctx.answer('✅ Вы успешно выдали доступ к админке!')
        await state.finish()
        admins = []
        for i in db['admins']:
            try:
                user = await bot.get_chat(i)
                admins.append(f'<a href="tg://user?id={user.id}">{user.first_name}</a>')
            except ChatNotFound:
                await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')}, {"$pull": {'admins': i}})
                continue

        admins = '\n'.join(admins)
        await ctx.answer(text=f"🛂 <b>Список пользователей с доступом в админку:</b>\n{admins}\n\nВыберите действие:", reply_markup=await generate_admins_manager())
    except Exception as e:
        if e.args[0] == "'NoneType' object is not subscriptable":
            await ctx.answer('Пользователь не найден 🤷‍♂')
            await state.finish()
            db = await collection.find_one({'_id': ObjectId('64987b1eeed9918b13b0e8b4')})
            admins = []
            for i in db['admins']:
                try:
                    user = await bot.get_chat(i)
                    admins.append(f'<a href="tg://user?id={user.id}">{user.first_name}</a>')
                except ChatNotFound:
                    await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')}, {"$pull": {'admins': i}})
                    continue

            admins = '\n'.join(admins)
            await ctx.answer(text=f"🛂 <b>Список пользователей с доступом в админку:</b>\n{admins}\n\nВыберите действие:", reply_markup=await generate_admins_manager())

@dp.message_handler(content_types=['text'], state=MySceneStates.aedit_limittousers_scene)
async def aedit_limittousers_scene(ctx: Message, state: FSMContext):
    try:
        text = ctx.text
        if text.isdigit() == False or (len(text) >= 2 and text[0] == '0'): return await ctx.answer('✋ Значение должно быть целым числом, введите ещё раз:')
        toint = int(ctx.text)
        await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')}, {"$set": {"limit_to_users": toint}})
        await ctx.answer('Успешное изменение ✅')
        await state.finish()
        db = await collection.find_one({'_id': ObjectId('64987b1eeed9918b13b0e8b4')})
        try:
            await bot.delete_message(ctx.chat.id, db['adminback'])
        except:
            print('err - scene deletion (NOT Important)')
        await ctx.answer(text=f'✋ <b>Лимиты:</b>\n<b>Демо режим до:</b> {db["limit_to_users"]} юзеров', reply_markup=await generate_admin_limit_edit_choice())
    except Exception as e:
        traceback.print_exc()

@dp.message_handler(content_types=['text'], state=MySceneStates.spravka_edit_scene)
async def spravka_edit_scene(ctx: Message, state: FSMContext):
    try:
        db = await collection.find_one({'user_id': ctx.from_user.id})
        spravka_index = db['sprvindxed']
        stext = ctx.text
        if ctx.entities: stext = ctx.parse_entities(as_html=True)
        await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')}, {"$set": {f"spravka.{spravka_index}.info": stext}})
        await ctx.answer('Успешное изменение ✅')
        await state.finish()
        db = await collection.find_one({'_id': ObjectId('64987b1eeed9918b13b0e8b4')})
        try:
            await bot.delete_message(ctx.chat.id, db['adminback'])
        except:
            print('err - scene deletion (NOT Important)')

        text = 'ℹ Информации нет'
        if db['spravka'][spravka_index]['info'] != 'None': text = db['spravka'][spravka_index]['info']
        await ctx.answer(text=f'ℹ <b>Справка:</b> {db["spravka"][spravka_index]["n"]}\n\n{text}', reply_markup=await generate_admin_spravka_show())
    except Exception as e:
        traceback.print_exc()

@dp.message_handler(content_types=['text'], state=MySceneStates.posited_days_scene)
async def posited_days_scene(ctx: Message, state: FSMContext):
    try:
        text = ctx.text.replace('d', '').replace('д', '').replace('дней', '')
        if text.isdigit() == False:
            return await ctx.answer('✋ Значение должно быть числом\n\nВведите срок действия лицензии в днях:')

        db = await collection.find_one({'_id': ObjectId('64987b1eeed9918b13b0e8b4')})
        check = None
        for index, item in enumerate(db['price']):
            if item.get("period") == text:
                check = index
                break

        if check != None:
            return await ctx.answer('✋ В базе уже существует такая позиция с таким количеством дней\n\nВведите другое количество срока:')
        await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')}, {"$set": {"positeddays": text}})
        db = await collection.find_one({'_id': ObjectId('64987b1eeed9918b13b0e8b4')})
        try:
            await bot.delete_message(ctx.chat.id, db['adminback'])
        except:
            print('err - scene deletion (NOT Important)')
        await state.finish()
        if db["positedprice"] == 'None': return await ctx.answer(text=f'⬇ Выберите то, что бы вы хотели изменить в этой позиции:\n\n<b>{db["positeddays"]}</b> дней - <b>{db["price"][db["positindx"]]["price"]}</b>₽',
                               reply_markup=await generate_positedit())
        await ctx.answer(text=f'⬇ Выберите то, что бы вы хотели изменить в этой позиции:\n\n<b>{db["positeddays"]}</b> дней - <b>{db["positedprice"]}</b>₽',
                               reply_markup=await generate_positedit())
    except Exception as e:
        traceback.print_exc()

@dp.message_handler(content_types=['text'], state=MySceneStates.posited_price_scene)
async def posited_price_scene(ctx: Message, state: FSMContext):
    try:
        trahstext = ctx.text.replace('₽', '').replace('р', '').replace('рублей', '')
        text = remove_non_digits_and_dot(trahstext)
        check = has_decimal_point(text)
        if check == False:
            return await ctx.answer(
                '✋ Вы ввели значение в неправильном формате\n\nВведите сумму которую заплатит пользователь при покупке(Значение должно быть в десятичном-float формате. Пример: 100.0 | 250.0):')

        text_to_float = float(text)

        await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')},
                                       {"$set": {'positedprice': text_to_float}})
        await state.finish()
        db = await collection.find_one({'_id': ObjectId('64987b1eeed9918b13b0e8b4')})
        try:
            await bot.delete_message(ctx.chat.id, db['adminback'])
        except:
            print('err - scene deletion (NOT Important)')
        if db["positeddays"] == 'None': return await ctx.answer(text=f'⬇ Выберите то, что бы вы хотели изменить в этой позиции:\n\n<b>{db["price"][db["positindx"]]["period"]}</b> дней - <b>{db["positedprice"]}</b>₽',
                               reply_markup=await generate_positedit())
        await ctx.answer(text=f'⬇ Выберите то, что бы вы хотели изменить в этой позиции:\n\n<b>{db["positeddays"]}</b> дней - <b>{db["positedprice"]}</b>₽',
            reply_markup=await generate_positedit())
    except Exception as e:
        traceback.print_exc()

@dp.message_handler(content_types=['text'], state=MySceneStates.addposition_period_scene)
async def addposition_period_scene(ctx: Message, state: FSMContext):
    try:
        text = ctx.text.replace('d', '').replace('д', '').replace('дней', '')
        if text.isdigit() == False:
            return await ctx.answer('✋ Значение должно быть числом\n\nВведите срок действия лицензии в днях:')

        db = await collection.find_one({'_id': ObjectId('64987b1eeed9918b13b0e8b4')})
        check = None
        for index, item in enumerate(db['price']):
            if item.get("period") == text:
                check = index
                break

        if check != None:
            return await ctx.answer('✋ В базе уже существует такая позиция с таким количеством дней\n\nВведите другое количество срока:')
        db = await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')}, {"$push": {"price": {"period": text}}})
        try:
            await bot.delete_message(ctx.chat.id, db['adminback'])
        except:
            print('err - scene deletion (NOT Important)')
        await MySceneStates.addposition_price_scene.set()
        await ctx.answer('✍ А теперь введите сумму которую заплатит пользователь при покупке(Значение должно быть в десятичном-float формате. Пример: 100.0 | 250.0):')
    except Exception as e:
        traceback.print_exc()

def has_decimal_point(string):
    parts = string.split('.')
    return len(parts) == 2 and all(part.isdigit() for part in parts)

def remove_non_digits_and_dot(text):
    pattern = r'[^0-9.]'
    return re.sub(pattern, '', text)

@dp.message_handler(content_types=['text'], state=MySceneStates.addposition_price_scene)
async def addposition_price_scene(ctx: Message, state: FSMContext):
    try:
        trahstext = ctx.text.replace('₽', '').replace('р', '').replace('рублей', '')
        text = remove_non_digits_and_dot(trahstext)
        check = has_decimal_point(text)
        if check == False:
            return await ctx.answer(
                '✋ Вы ввели значение в неправильном формате\n\nВведите сумму которую заплатит пользователь при покупке(Значение должно быть в десятичном-float формате. Пример: 100.0 | 250.0):')

        text_to_float = float(text)
        db = await collection.find_one({'_id': ObjectId('64987b1eeed9918b13b0e8b4')})
        index_of_last_position = len(db["price"]) - 1
        try:
            await bot.delete_message(ctx.chat.id, db['adminback'])
        except:
            print('err - scene deletion (NOT Important)')
        db = await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')}, {"$set": {f"price.{index_of_last_position}.price": text_to_float}})
        try:
            await bot.delete_message(ctx.chat.id, db['adminback'])
        except:
            print('err - scene deletion (NOT Important)')
        await state.finish()
        await ctx.answer(f'Вы успешно добавили новую позицию:\n\n🆕 {db["price"][index_of_last_position]["period"]} дней - {text_to_float}₽', reply_markup=await generate_admin_return_main())
    except Exception as e:
        traceback.print_exc()

@dp.message_handler(content_types=ContentTypes.ANY, state=MySceneStates.post_to_users)
async def post_scene(ctx: Message, state: FSMContext):
    try:
        db = await collection.find_one({'_id': ObjectId('64987b1eeed9918b13b0e8b4')})
        msgidtoedit = await ctx.answer('🔄️ Ваше сообщение рассылается по всем пользователям')
        asyncio.create_task(message_to_users(ctx, db['users'], msgidtoedit.message_id))
        try:
            await bot.delete_message(ctx.chat.id, db['adminback'])
        except:
            print('err - scene deletion (NOT Important)')
        await state.finish()
        await ctx.answer(text=f'Добро пожаловать в админку, <a href="tg://user?id={ctx.from_user.id}">{ctx.from_user.first_name}</a>',
                               reply_markup=await generate_admin_main_page(ctx.from_user.id))
    except Exception as e:
        traceback.print_exc()

async def message_to_users(ctx, users: list, id):
    try:
        for i in users:
            try:
                if i == ctx.chat.id: continue
                await bot.copy_message(i, from_chat_id=ctx.chat.id, message_id=ctx.message_id)
                await asyncio.sleep(0.4)
            except:
                print('msg_t_users - user blocked the bot')
        await bot.edit_message_text('Отправка завершена ✅', ctx.chat.id, id)
    except Exception as e:
        traceback.print_exc()

@dp.message_handler(commands=['user_to_id'])
async def convert_to_id(ctx: Message):
    try:
        args = ctx.text.split(' ')
        if len(args) == 1: return await ctx.answer(
            'Пример: <i>/user_to_id @username</i>')
        if len(args) > 2: return await ctx.answer(
            f'Я принимаю только 1 аргумент, а в вашем тексте их <b>{len(args) - 1}</b>. Пример: <i>/user_to_id @username</i>')
        if args[1][0] != '@': return await ctx.answer(
            'Я принимаю только юзернейм. Пример: <i>/user_to_id @username</i>')

        try:
            global userid
            userid = await resolve_username_to_user_id(args[1].replace('@', ''))
            await ctx.answer(
                f'<b>👤 Пользователь:</b> <a href="tg://user?id={userid[0]}">{userid[1]}</a>\n\n<b>ID:</b> <code>{userid[0]}</code>')
        except:
            print('')

        if userid == None: return await ctx.answer('🔎 Пользователь не найден')
    except Exception as e:
        traceback.print_exc()


