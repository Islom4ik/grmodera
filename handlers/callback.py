# Обработчики нажатых, встроенных кнопок под сообщениями:
import asyncio
import time
import multiprocessing
import pytz
import re
import traceback
from decimal import Decimal
from data.loader import bot, dp, FSMContext, State, config
from database.database import collection, ObjectId
from states_scenes.scene import MySceneStates
from aiogram.types import CallbackQuery, ContentTypes, LabeledPrice, PreCheckoutQuery, Message
from aiogram.utils.exceptions import CantRestrictChatOwner, MessageNotModified
from aiogram.utils.exceptions import ChatNotFound, MigrateToChat
from data.configs import *
from data.texts import *
from keyboards.inline_keyboards import *
from datetime import datetime

@dp.callback_query_handler(lambda call: call.data == 'check_admingr')
async def check_admin_rght(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        if call.message.chat.type == 'group' or call.message.chat.type == 'supergroup':
            admins = await bot.get_chat_administrators(call.message.chat.id)
            for me in admins:
                if me.user.username == t_bot_user:
                    if me.can_manage_chat == True and me.can_delete_messages == True and me.can_restrict_members == True and me.can_invite_users == True and me.can_promote_members == True:
                        await bot.delete_message(call.message.chat.id, call.message.message_id)
                        admins = await bot.get_chat_administrators(call.message.chat.id)
                        creator_id = next((obj for obj in admins if obj["status"] == "creator"), None).user.id
                        await call.answer('Успех!', show_alert=False)
                        return await bot.send_message(call.message.chat.id,
                                                      '🤖 Вы выполнили корректные действия.\n\nНажмите кнопку "Настроить бота"',
                                                      reply_markup=await generate_settings_button(
                                                          f'{call.message.chat.id}_{creator_id}'))
                    else:
                        return await call.answer(
                            'К сожалению ничего не изменилось 😶 Я все ещё без прав.\n\nВыдайте все права и попробуйте снова!',
                            show_alert=True)
            else:
                return await call.answer(
                    'К сожалению ничего не изменилось 😶 Я все ещё без прав.\n\nВыдайте все права и попробуйте снова!',
                    show_alert=True)
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'settings_texts')
async def change_to_edit_page(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"chats": group_id})
        index_of_chat = await get_dict_index(db, group_id)
        await call.answer()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db['settings'][index_of_chat]['updated_date']), chat_name=await get_chat_name(group_id)),
                                    reply_markup=await generate_edit_text_settings())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'back_to_chose')
async def react_to_back(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"chats": group_id})
        index_of_chat = await get_dict_index(db, group_id)
        await call.answer()
        if db['settings'][index_of_chat]['lic'] == True: return await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db['settings'][index_of_chat]['updated_date']), chat_name=await get_chat_name(group_id)),
                                    reply_markup=await generate_settings(True))
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db['settings'][index_of_chat]['updated_date']), chat_name=await get_chat_name(group_id)),
                                    reply_markup=await generate_settings())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'done_btn')
async def react_to_done(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'⚙ Настройки чата завершена')
        db = await collection.find_one({"user_id": call.from_user.id})
        if len(db['chats']) >= 1:
            lic = 'Лицензии нет'
            if db['lic'] != 'None': lic = db['lic']
            await bot.send_message(chat_id=call.message.chat.id, text=f'👤 Ваш профиль:\n\n<b>Пользователь:</b> #{db["inlineid"]} - {db["register_data"]}\n<b>Username:</b> @{call.from_user.username}\n<b>Имя:</b> {call.from_user.first_name}\n<b>Чатов:</b> {len(db["chats"])}\n<b>Лицензий:</b> {db["lic"]}',
                                        reply_markup=await generate_add_button(), disable_web_page_preview=True)
        else:
            await bot.send_message(chat_id=call.message.chat.id,
                                        text=t_start_text.format(bot_user=t_bot_user),
                                        reply_markup=await generate_add_button(), disable_web_page_preview=True)
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'show_my_chats')
async def show_my_chats(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        db = await collection.find_one_and_update({"user_id": call.from_user.id}, {'$set': {"current_pg": 0}})
        if len(db['chats']) == 0:
            return await call.answer('У вас нет чатов :(', show_alert=True)

        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='🛢️ Выберите чат для настройки:', reply_markup=await generate_my_chats(user_id=db["user_id"]))
        await call.answer()
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'texts_greeting')
async def text_greeting_show(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"chats": str(group_id)})

        index_of_chat = await get_dict_index(db, group_id)

        text = f'Приветствуем, <b>{str("{member_name}")}</b>!\n\nПрежде чем размещать свои объявления, пожалуйста, ознакомься с правилами. Они доступны по команде /rules'

        await call.answer()
        if db["settings"][index_of_chat]['greeting'] != 'None': text = db["settings"][index_of_chat]['greeting']
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Приветственное сообщение:</b>\n{text}',
                                    reply_markup=await generate_text_editing_page())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'show_rules')
async def text_rules_show(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"chats": str(group_id)})

        index_of_chat = await get_dict_index(db, group_id)

        text = '<i>Правила отсутствуют</i>'

        await call.answer()
        if db["settings"][index_of_chat]['rules'] != 'None': text = db["settings"][index_of_chat]['rules']

        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Правила чата:</b>\n{text}',
                                        reply_markup=await generate_rules_editing_page())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'show_warning')
async def text_warning_show(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"chats": str(group_id)})

        index_of_chat = await get_dict_index(db, group_id)
        ban = t_ban
        kick = t_kick
        unban = t_unban
        if db["settings"][index_of_chat]["warning_ban"] != 'None': ban = db["settings"][index_of_chat]["warning_ban"]
        if db["settings"][index_of_chat]["warning_kick"] != 'None': kick = db["settings"][index_of_chat]["warning_kick"]
        if db["settings"][index_of_chat]["unban_text"] != 'None': unban = db["settings"][index_of_chat]["unban_text"]

        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Уведомления пользователю при использовании команд:</b>\n\n<b>/ban</b>\n{ban}\n\n<b>/kick</b>\n{kick}\n\n<b>/unban</b>\n{unban}',
                                    reply_markup=await generate_warning_editing_page())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))




@dp.callback_query_handler(lambda call: call.data == 'delete_chat_b')
async def delete_chat_b_react(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<a href="https://{group_id}.id">🟡</a> Вы точно хотите удалить бота с чата и настройки чата?', reply_markup=await generete_bot_delete_chat_question())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: 'deletechatbots' in call.data)
async def answer_to_deletechatbots(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        call_data = call.data.split('_')[1]
        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        if call_data == 'd':
            await collection.find_one_and_update({"user_id": db['user_id']}, {"$pull": {"chats": group_id, f"settings": {"chat_id": group_id}}})
            await collection.find_one_and_update({"_id": ObjectId('64987b1eeed9918b13b0e8b4')}, {"$pull": {"groups": group_id}})
            await call.bot.leave_chat(group_id)
            trash = await bot.send_message(chat_id=call.message.chat.id, text='Чат успешно удален ✅')
            asyncio.create_task(delete_message(30, [trash.message_id], trash.chat.id))
            await asyncio.sleep(1)
            db = await collection.find_one({"user_id": call.from_user.id})
            if len(db['chats']) >= 1:
                lic = 'Лицензии нет'
                if db['lic'] != 'None': lic = db['lic']
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'👤 Ваш профиль:\n\n<b>Пользователь:</b> #{db["inlineid"]} - {db["register_data"]}\n<b>Username:</b> @{call.from_user.username}\n<b>Имя:</b> {call.from_user.first_name}\n<b>Чатов:</b> {len(db["chats"])}\n<b>Лицензий:</b> {db["lic"]}',
                                            reply_markup=await generate_add_button(), disable_web_page_preview=True)
            else:
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=t_start_text.format(bot_user=t_bot_user),
                                            reply_markup=await generate_add_button(), disable_web_page_preview=True)
        else:
            if db['settings'][index_of_chat]['lic'] == True: return await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id)),
                                                                                                reply_markup=await generate_settings(True))
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id)),
                                        reply_markup=await generate_settings())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'formating')
async def format_btn_react(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        trash = await bot.send_message(call.message.chat.id, '💿 Используйте тэги, чтобы разнообразить Ваши обращения в адрес пользователей.\n\n{member_name} - имя участника(участников) чата с которым связан контекст бота;\n\n{admin} - имя администратора с которым связанно действие бота\n\n{time_left} - счетчик оставшегося времени')
        asyncio.create_task(delete_message(20, [trash.message_id], trash.chat.id))
        await call.answer()
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))



@dp.callback_query_handler(lambda call: call.data == 'skromniy_show')
async def skromniy_show(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"chats": str(group_id)})
        index_of_chat = await get_dict_index(db, group_id)

        if 'skromniy' not in db['settings'][index_of_chat]: await collection.find_one_and_update({"user_id": db['user_id']}, {"$set": {f'settings.{index_of_chat}.skromniy': {'active': False, 'timer': 180}}})
        db = await collection.find_one({"user_id": db['user_id']})
        timer = 180
        if db['settings'][index_of_chat]['skromniy']['timer'] != 0: timer = db['settings'][index_of_chat]['skromniy']['timer']
        text = f'Гостевой режим, {timer} минут тишины.'
        if 'warning' in db['settings'][index_of_chat]['skromniy']:
            if db['settings'][index_of_chat]['skromniy']['warning'] != 'None': text = db['settings'][index_of_chat]['skromniy']['warning']
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Гость:</b>\nЗапрещает новым пользователям говорить в течении <b>{timer}</b> минут.\n\n<b>Текст при срабатывании функции:</b>\n{text}',
                                    reply_markup=await generate_skromniy_show(db['user_id'], index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'back_from_tixiychas_chose_days')
@dp.callback_query_handler(lambda call: call.data == 'tixiychas_show')
async def tixiychas_show(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"chats": str(group_id)})
        index_of_chat = await get_dict_index(db, group_id)

        if 'tixiychas' not in db['settings'][index_of_chat]: await collection.find_one_and_update({"user_id": db['user_id']}, {"$set": {f'settings.{index_of_chat}.tixiychas': {'active': False, 'timers': []}}})
        db = await collection.find_one({"user_id": db['user_id']})
        timers = 'Нет указанных промежутков'
        if len(db['settings'][index_of_chat]['tixiychas']['timers']) != 0:
            timers = ''
            for i in db['settings'][index_of_chat]['tixiychas']['timers']:
                timers += f'{i["t_i"]}: {i["time"]};\n'
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Тихий час:</b>\nЗапрещает пользователям писать в указанный промежуток времени\n\n<b>Ваши промежутки:</b>\n{timers}',
                                    reply_markup=await generate_tixiychas_show(db['user_id'], index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'show_afk')
async def text_afk_show(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"chats": str(group_id)})

        index_of_chat = await get_dict_index(db, group_id)

        text = db["settings"][index_of_chat]['afk']

        await call.answer()
        if text == 'None':
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n<b>Уведомление при неактивности чата:</b>\n\nАууу... Что-то актива нет',
                                        reply_markup=await generate_block_afk_show(db['user_id'], index_of_chat))
        else:
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n<b>Уведомление при неактивности чата:</b>\n\n{text}',
                                        reply_markup=await generate_block_afk_show(db['user_id'], index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'back_from_wordsfilter_show')
async def back_from_wordsfilter_show(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        await edit_admins_settings(call)
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'msgfilter_show')
async def msgfilter_show(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"chats": str(group_id)})

        index_of_chat = await get_dict_index(db, group_id)

        if 'msg_filter' not in db["settings"][index_of_chat]: await collection.find_one_and_update({"chats": str(group_id)}, {'$set': {f'settings.{index_of_chat}.msg_filter': {'italic': False, 'bold': False, 'capslock': False, 'mfiltersa': False, "mfilters": []}}})
        italic = '✋ {member_name}, использовать только курсив выделение в тексте запрещено!'
        bold = '✋ {member_name}, использовать только жирное выделение в тексте запрещено!'
        caps = '✋ {member_name}, писать только заглавными в тексте запрещено!'
        #
        # db = await collection.find_one({"user_id": db['user_id']})
        # if db['settings'][index_of_chat]['msg_filter']['italic'] == True: italic = 'Включено'
        # if db['settings'][index_of_chat]['msg_filter']['bold'] == True: bold = 'Включено'
        # if db['settings'][index_of_chat]['msg_filter']['capslock'] == True: caps = 'Включено'

        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n<b>Фильтры текстовых сообщений:</b>\n\n<b>Фильтр "Italic" сообщений:</b>\n{italic}\n\n<b>Фильтр "Bold" сообщений:</b>\n{bold}\n\n<b>Фильтр "Caps Lock" сообщений:</b>\n{caps}',
                                    reply_markup=await generate_msg_filters_btns(db['user_id'], index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'words_filters_show')
async def answer_to_words_filters_show(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"chats": str(group_id)})
        index_of_chat = await get_dict_index(db, group_id)
        if 'mfiltersa' not in db["settings"][index_of_chat]['msg_filter']: await collection.find_one_and_update({"chats": str(group_id)}, {'$set': {f'settings.{index_of_chat}.msg_filter.mfiltersa': False}})
        if 'mfilterw' not in db["settings"][index_of_chat]['msg_filter']: await collection.find_one_and_update({"chats": str(group_id)}, {'$set': {f'settings.{index_of_chat}.msg_filter.mfilterw': 'None'}})
        db = await collection.find_one({"user_id": db['user_id']})
        blist = 'Нет запретов'
        if len(db["settings"][index_of_chat]['msg_filter']['mfilters']) != 0: blist = ', '.join(db["settings"][index_of_chat]['msg_filter']['mfilters'])
        text = '✋ {member_name}, у нас запрещена нецензурная лексика!'
        if db["settings"][index_of_chat]['msg_filter']['mfilterw'] != 'None': text = db["settings"][index_of_chat]['msg_filter']['mfilterw']
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Заполните необходимые для блокировки слова:</b>\n\n<b>Сообщение при нарушении:</b>\n{text}\n\n<b>Ваш список запретов:</b>\n{blist}',
                                    reply_markup=await generate_wordsfilter_show(db['user_id'], index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'wordsfilter_add')
async def answer_to_wordsfilter_add(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await MySceneStates.wordsfilter_add_scene.set()
        quatback = await bot.send_message(call.message.chat.id, '📋 Введите слово или слова, через запятую, которые вы хотите запретить:', reply_markup=await generate_back_msgfiltersadd())
        await collection.find_one_and_update({"user_id": call.from_user.id}, {"$set": {"chat_editing": group_id, 'quatback': quatback.message_id}})
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'wordsfilter_rem')
async def answer_to_wordsfilter_rem(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        blist = 'Запретов нет'
        if len(db['settings'][index_of_chat]['msg_filter']['mfilters']) == 0: return await call.answer('✋ Нечего удалять')
        else: blist = ', '.join(db['settings'][index_of_chat]['msg_filter']['mfilters'])
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await MySceneStates.wordsfilter_rem_scene.set()
        quatback = await bot.send_message(call.message.chat.id, f'📋 Введите слово или слова, через запятую, которые хотите удалить из вашего списка запретов\n\n<b>Ваш список запретов:</b> {blist}', reply_markup=await generate_back_msgfiltersrem())
        await collection.find_one_and_update({"user_id": call.from_user.id}, {"$set": {"chat_editing": group_id, 'quatback': quatback.message_id}})
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'back_from_msg_filters')
async def react_to_back_from_msg_filters(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        await edit_admins_settings(call)
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'back_to_show_page')
async def react_to_back_to_show(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"chats": group_id})
        index_of_chat = await get_dict_index(db, group_id)
        await call.answer()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nВыберите текст, который хотите посмотреть:',
                                    reply_markup=await generate_edit_text_settings())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: 'edit' in call.data)
async def scenes_editor(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        call_main = call.data.split('_')[1]
        group_id_url = call.message.entities[0].url
        group_id = int("-" + re.sub(r"\D", "", group_id_url))
        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)

        if call_main == 'greeting':
            await MySceneStates.greeting_change_text_scene.set()
            quatback = await bot.send_message(call.message.chat.id, '📋 Введите текст для приветствия новых участников чата:', reply_markup=await generate_back_gretedittext())
        elif call_main == 'rules':
            await MySceneStates.rules_change_text_scene.set()
            quatback = await bot.send_message(call.message.chat.id, '📋 Введите текст правил чата:', reply_markup=await generate_back_ruledittext())
        elif call_main == 'banwarning':
            await MySceneStates.banwarning_change_text_scene.set()
            quatback = await bot.send_message(call.message.chat.id, '📋 Введите текст, который будет отправлен после использования команды ban:', reply_markup=await generate_back_banedittext())
        elif call_main == 'kickwarning':
            await MySceneStates.kickwarning_change_text_scene.set()
            quatback = await bot.send_message(call.message.chat.id, '📋 Введите текст, который будет отправлен после использования команды kick:', reply_markup=await generate_back_kickedittext())
        elif call_main == 'unbantext':
            await MySceneStates.unbantext_change_text_scene.set()
            quatback = await bot.send_message(call.message.chat.id, '📋 Введите текст, который будет отправлен после использования команды unban:', reply_markup=await generate_back_unbanedittext())
        elif call_main == 'afkw':
            await MySceneStates.afk_change_text_scene.set()
            quatback = await bot.send_message(call.message.chat.id, '📋 Введите текст, который будет уведомлять чат при неактивности:', reply_markup=await generate_back_afkedittext())
        elif call_main == 'afkmedia':
            await MySceneStates.get_afkmedia_scene.set()
            quatback = await bot.send_message(call.message.chat.id, '🖼️ Отправьте фото или видео с сжатием:', reply_markup=await generate_back_afkeditmedia())
            await collection.find_one_and_update({"user_id": call.from_user.id}, {"$set": {"vorchunmedia_issended": False}})
        elif call_main == 'resourcesw':
            await MySceneStates.resourcesw_change_scene.set()
            quatback = await bot.send_message(call.message.chat.id, '📋 Введите новый текст предупреждения о нарушении:', reply_markup=await generate_back_resedittext())
        elif call_main == 'repostesw':
            await MySceneStates.repostesw_change_scene.set()
            quatback = await bot.send_message(call.message.chat.id, '📋 Введите новый текст предупреждения о нарушении:', reply_markup=await generate_back_repedittext())
        elif call_main == 'pingw':
            await MySceneStates.pingw_change_scene.set()
            quatback = await bot.send_message(call.message.chat.id, '📋 Введите новый текст предупреждения о нарушении:', reply_markup=await generate_back_pingedittext())
        elif call_main == 'afktimer':
            await MySceneStates.vorchun_timer_scene.set()
            quatback = await bot.send_message(call.message.chat.id, '📋 Введите значения таймера в секундах:', reply_markup=await generate_back_vtimer())
        elif call_main == 'antimatw':
            await MySceneStates.antimatw_change_scene.set()
            quatback = await bot.send_message(call.message.chat.id, 'Введите новый текст предупреждения о нарушении:', reply_markup=await generate_back_antimat())
        elif call_main == 'skromniyw':
            await MySceneStates.skromniyw_change_scene.set()
            quatback = await bot.send_message(call.message.chat.id, '📋 Введите новый текст предупреждения о гостевом режиме:', reply_markup=await generate_back_skromniywed())
        elif call_main == 'skromniytimer':
            await MySceneStates.skromniytimer_change_scene.set()
            quatback = await bot.send_message(call.message.chat.id, '📋 Введите количество минут, после истечения которых пользователь сможет писать в чате:', reply_markup=await generate_back_skromniytimer())
        elif call_main == 'antifludw':
            await MySceneStates.antifludw_change_scene.set()
            quatback = await bot.send_message(call.message.chat.id, '📋 Введите новый текст предупреждения о нарушении:', reply_markup=await generate_back_antifludscenes())
        elif call_main == 'antifludtimer':
            await MySceneStates.antifludtimer_change_scene.set()
            quatback = await bot.send_message(call.message.chat.id, '📋 Введите количество секунд, после истечения которых пользователь сможет писать в чате:', reply_markup=await generate_back_antifludscenes())
        elif call_main == 'nofilelimit':
            await MySceneStates.nofilelimit_change_scene.set()
            quatback = await bot.send_message(call.message.chat.id, '📋 Введите значение нового лимита:', reply_markup=await generate_back_nofilescenes())
        elif call_main == 'subscribecadd':
            await MySceneStates.subchanel_add_scene.set()
            quatback = await bot.send_message(call.message.chat.id, f'📋 Введите @UserName или прямую ссылку канала:', reply_markup=await generate_back_subchaneladd())
        elif call_main == 'paydialadd':
            if len(db['settings'][index_of_chat]['subscribe_show']['paydialogue']['payment_methods']) == 5:
                trash = await bot.send_message(chat_id=call.from_user.id, text='⚠ Извините, но вы не можете добавить больше 5-ти методов оплаты!')
                return asyncio.create_task(delete_message(8, [trash.message_id], call.from_user.id))
            await MySceneStates.paydialadd_scene.set()
            quatback = await bot.send_message(call.message.chat.id, f'📋 Введите название метода оплаты:', reply_markup=await generate_back_paydialpmethadd())
        elif call_main == 'paydialtarifdays':
            tarifid = int(call.message.entities[5].url.replace('https://', '').replace('.com/', ''))
            await collection.find_one_and_update({'user_id': call.from_user.id}, {'$set': {f'settings.{index_of_chat}.subscribe_show.paydialogue.paydialtarifid': tarifid}})
            await MySceneStates.paydialtarifedit_days_scene.set()
            quatback = await bot.send_message(call.message.chat.id, f'📋 Введите новое количество дней:', reply_markup=await generate_back_paydialtarifdataedit())
        elif call_main == 'paydialtarifprice':
            tarifid = int(call.message.entities[5].url.replace('https://', '').replace('.com/', ''))
            await collection.find_one_and_update({'user_id': call.from_user.id}, {'$set': {f'settings.{index_of_chat}.subscribe_show.paydialogue.paydialtarifid': tarifid}})
            await MySceneStates.paydialtarifedit_price_scene.set()
            quatback = await bot.send_message(call.message.chat.id, f'📋 Введите новую цену:', reply_markup=await generate_back_paydialtarifdataedit())
        elif call_main == 'paydialtarifwarning':
            await MySceneStates.paydial_editwarning.set()
            quatback = await bot.send_message(call.message.chat.id, f'📋 Введите новый текст предупреждения о нарушении:', reply_markup=await generate_back_paydialwarninged())
        elif call_main == 'subscrwarnedit':
            await MySceneStates.subscribe_editwarning.set()
            quatback = await bot.send_message(call.message.chat.id, f'📋 Введите новый текст предупреждения о нарушении:', reply_markup=await generate_back_subscrwarned())

        elif call_main == 'paydialpayinfo':
            await collection.find_one_and_update({'user_id': call.from_user.id}, {'$set': {f'settings.{index_of_chat}.subscribe_show.paydialogue.pmediting': int(call.message.entities[5].url.replace('https://', '').replace('.com/', ''))}})
            await MySceneStates.paydialaddinfo_scene.set()
            quatback = await bot.send_message(call.message.chat.id, f'📋 Введите информацию для пользователя:', reply_markup=await generate_back_paydialpminfoadd())
        elif call_main == 'paydialtarifdatas':
            tarifid = int(call.message.entities[5].url.replace('https://', '').replace('.com/', ''))
            for i in db['settings'][index_of_chat]["subscribe_show"]["paydialogue"]["tarif_plans"]:
                if i['days'] == tarifid:
                    return await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b>\n\n<a href="https://{i["days"]}.com">📦</a> <b>Тариф на</b>: {i["days"]} дней\n\n<b>Цена</b>:\n{i["price"]}\n\n<b>Что будем изменять?</b>', reply_markup=await generate_paydialtarifd_editchoice(tarifid))
            else:
                if len(db['settings'][index_of_chat]['subscribe_show']['paydialogue']['tarif_plans']) == 0:
                    return await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b>', reply_markup=await generate_paydialogue_show(call.from_user.id, index_of_chat))
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b> Тарифы', reply_markup=await generate_paydialoguetarifs_show(call.from_user.id, index_of_chat))
        elif call_main == 'paydialtarifadd':
            if len(db['settings'][index_of_chat]['subscribe_show']['paydialogue']['tarif_plans']) == 15:
                trash = await bot.send_message(chat_id=call.from_user.id, text='⚠ Извините, но вы не можете добавить больше 15-ти тарифов!')
                return asyncio.create_task(delete_message(8, [trash.message_id], call.from_user.id))
            await collection.find_one_and_update({'user_id': call.from_user.id}, {'$set': {f'settings.{index_of_chat}.subscribe_show.paydialogue.paydialtarifadd_step': 1, f'settings.{index_of_chat}.subscribe_show.paydialogue.paydialtarifadd_data': {}}})
            await MySceneStates.paydialtarifadd_scene.set()
            quatback = await bot.send_message(call.message.chat.id, f'📋 Введите количество дней:', reply_markup=await generate_back_paydialtarif())
        elif call_main == 'tixiychast':
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            return await bot.send_message(call.message.chat.id, f'<a href="https://{group_id}.id">😴</a> Выберите дни:', reply_markup=await generate_tixiychas_chose_days())
        elif call_main == 'deltixiychast':
            return await bot.send_message(call.message.chat.id, f'<a href="https://{group_id}.id">📝</a> Выберите интервал который хотите удалить:', reply_markup=await generate_tixiychas_del_times(call.from_user.id, group_id))
        else:
            return await call.answer()

        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await collection.find_one_and_update({"user_id": call.from_user.id}, {"$set": {"chat_editing": group_id, "quatback": quatback.message_id}})
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: 'tixday' in call.data)
async def answer_to_tixday(call: CallbackQuery):
   try:
       if await blocked(call.from_user.id):
           await bot.delete_message(call.message.chat.id, call.message.message_id)
           return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
       group_id_url = call.message.entities[0].url
       group_id = int("-" + re.sub(r"\D", "", group_id_url))
       if await is_chat_in(group_id) == False:
           await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
           return await show_start(call)
       db = await collection.find_one({"user_id": call.from_user.id})
       call_data = call.data.split('_')[1]
       index_of_chat = await get_dict_index(db, group_id)
       if len(db['settings'][index_of_chat]['tixiychas']['timers']) > 5: return await call.answer('✋ Извините, вы не можете добавлять более 5 промежутков', show_alert=True)
       await MySceneStates.tixiychastimer_change_scene.set()
       quatback = ''
       await bot.delete_message(call.message.chat.id, call.message.message_id)
       if call_data == 'id':
           quatback = await bot.send_message(chat_id=call.message.chat.id, text=f'📋 Введите промежуток времени в формате DD.MM.YYYY (от)HH:MM-(до)HH:MM\n\nHH - часы: 00 - 24;\nMM - минуты: 00 - 59;\nDD.MM.YYYY - дата\n\nПример: 10.10.2023 07:00-10:00 - в 10.10.2023 от 7 утра до 10 утра', reply_markup=await generate_back_tixtimers())
       else:
           quatback = await bot.send_message(chat_id=call.message.chat.id, text=f'📋 Введите промежуток времени в формате (от)HH:MM-(до)HH:MM\n\nHH - часы: 00 - 24;\nMM - минуты: 00-59;\n\nПример: 07:00-10:00 - от 7 утра до 10 утра', reply_markup=await generate_back_tixtimers())
       await collection.find_one_and_update({'user_id': call.from_user.id}, {"$set": {"tixchascall": call_data, "chat_editing": group_id, "quatback": quatback.message_id}})
   except Exception as e:
       traceback.print_exc()
       asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: 'deltix' in call.data)
async def answer_to_tixday(call: CallbackQuery):
   try:
       if await blocked(call.from_user.id):
           await bot.delete_message(call.message.chat.id, call.message.message_id)
           return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
       group_id_url = call.message.entities[0].url
       group_id = int("-" + re.sub(r"\D", "", group_id_url))
       if await is_chat_in(group_id) == False:
           await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
           return await show_start(call)
       db = await collection.find_one({"user_id": call.from_user.id})
       call_data = call.data.split('_')[1]
       index_of_chat = await get_dict_index(db, group_id)
       await collection.find_one_and_update({'user_id': call.from_user.id}, {"$pull": {f"settings.{index_of_chat}.tixiychas.timers": {"time": call_data}}})
       await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=await generate_tixiychas_del_times(call.from_user.id, group_id))
   except Exception as e:
       traceback.print_exc()
       asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'eback_paydialwarninged', state=MySceneStates.paydial_editwarning)
async def answer_to_eback_paydialwarninged(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"user_id": call.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        text = 'Нету'
        if 'warning' in db['settings'][index_of_chat]['subscribe_show']['paydialogue'] and db['settings'][index_of_chat]['subscribe_show']['paydialogue']['warning'] != 'None':
            text = db['settings'][index_of_chat]['subscribe_show']['paydialogue']['warning']
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b>\n\n<b>Сообщение при нарушении:</b>\n{text}', reply_markup=await generate_paydialogue_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'eback_subscrwarned', state=MySceneStates.subscribe_editwarning)
async def answer_to_eback_subscrwarned(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"user_id": call.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        text = '✋ member_name, чтобы продолжить общение в нашем чате, Вам необходимо:'
        if 'warning' in db['settings'][index_of_chat]['subscribe_show'] and db['settings'][index_of_chat]['subscribe_show']['warning'] != 'None':
            text = db['settings'][index_of_chat]['subscribe_show']['warning']

        channels_len = len(db['settings'][index_of_chat]['subscribe_show']['channels'])
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Подписать:</b>\nЕсли пользователь делает попытку писать в чат что-либо, то он видит сообщение:\n\n{text}\n\n<b>Ваших каналов:</b> {channels_len}', reply_markup=await generate_subscribe_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'eback_paydialtarif', state=MySceneStates.paydialtarifadd_scene)
async def answer_to_eback_paydialtarif(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"user_id": call.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        await collection.find_one_and_update({"user_id": call.from_user.id}, {'$unset': {f'settings.{index_of_chat}.subscribe_show.paydialogue.paydialtarifadd_step': "", f'settings.{index_of_chat}.subscribe_show.paydialogue.paydialtarifadd_data': ""}})
        text = 'Нету'
        if 'warning' in db['settings'][index_of_chat]['subscribe_show']['paydialogue'] and db['settings'][index_of_chat]['subscribe_show']['paydialogue']['warning'] != 'None':
            text = db['settings'][index_of_chat]['subscribe_show']['paydialogue']['warning']
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b>\n\n<b>Сообщение при нарушении:</b>\n{text}', reply_markup=await generate_paydialogue_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'eback_paydialtarifdataedit', state=MySceneStates.paydialtarifedit_days_scene)
@dp.callback_query_handler(lambda call: call.data == 'eback_paydialtarifdataedit', state=MySceneStates.paydialtarifedit_price_scene)
async def answer_to_eback_paydialtarifdataedit(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"user_id": call.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        tarifid = db['settings'][index_of_chat]['subscribe_show']['paydialogue']['paydialtarifid']
        await call.answer()
        for i in db['settings'][index_of_chat]["subscribe_show"]["paydialogue"]["tarif_plans"]:
            if i['days'] == tarifid:
                return await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b>\n\n<a href="https://{i["days"]}.com">📦</a> <b>Тариф на</b>: {i["days"]} дней\n\n<b>Цена</b>:\n{i["price"]}', reply_markup=await generate_paydialoguetarifmanage())
        else:
            text = 'Нету'
            if 'warning' in db['settings'][index_of_chat]['subscribe_show']['paydialogue'] and db['settings'][index_of_chat]['subscribe_show']['paydialogue']['warning'] != 'None':
                text = db['settings'][index_of_chat]['subscribe_show']['paydialogue']['warning']
            return await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b>\n\n<b>Сообщение при нарушении:</b>\n{text}', reply_markup=await generate_paydialogue_show(call.from_user.id, index_of_chat))

    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'eback_paydialadd', state=MySceneStates.paydialadd_scene)
async def answer_to_eback_paydialadd(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"user_id": call.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        await call.answer()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b> Реквизиты', reply_markup=await generate_paydialoguepaydata_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'eback_paydialpminfoadd', state=MySceneStates.paydialaddinfo_scene)
async def answer_to_eback_paydialpminfoadd(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"user_id": call.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        await call.answer()
        info = "Нету"
        pname = db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["payment_methods"][db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]['pmediting']]["payment_name"]
        if db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["payment_methods"][db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["pmediting"]]["info"] != 'None': info = db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["payment_methods"][db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["pmediting"]]["info"]
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b>\n\n<a href="https://{db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["pmediting"]}.com">💳</a> <b>Реквизит</b>: {pname}\n\n<b>Условия</b>:\n{info}', reply_markup=await generate_paydialoguepmethmanage())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'eback_rmsginterval', state=MySceneStates.get_rmsginterval_scene)
async def answer_to_eback_rmsginterval(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"user_id": call.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        await call.answer()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Удалить сообщения:</b>', reply_markup=await generate_remmessages_show(call.from_user.id))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'eback_subchaneladd', state=MySceneStates.subchanel_add_scene)
async def answer_to_eback_subchaneladd(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"user_id": call.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        text = '✋ member_name, чтобы продолжить общение в нашем чате, Вам необходимо:'
        if 'warning' in db['settings'][index_of_chat]['subscribe_show'] and db['settings'][index_of_chat]['subscribe_show']['warning'] != 'None':
            text = db['settings'][index_of_chat]['subscribe_show']['warning']

        channels_len = len(db['settings'][index_of_chat]['subscribe_show']['channels'])
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Подписать:</b>\nЕсли пользователь делает попытку писать в чат что-либо, то он видит сообщение:\n\n{text}\n\n<b>Ваших каналов:</b> {channels_len}', reply_markup=await generate_subscribe_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'eback_skromniytimer', state=MySceneStates.skromniytimer_change_scene)
@dp.callback_query_handler(lambda call: call.data == 'eback_skromniywed', state=MySceneStates.skromniyw_change_scene)
async def answer_to_eback_skromniytimer(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"user_id": call.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        await call.answer()
        timer = 180
        if db['settings'][index_of_chat]['skromniy']['timer'] != 0: text = db['settings'][index_of_chat]['skromniy']['timer']
        text = f'Гостевой режим, {timer} минут тишины.'
        if 'warning' in db['settings'][index_of_chat]['skromniy']:
            if db['settings'][index_of_chat]['skromniy']['warning'] != 'None': text = db['settings'][index_of_chat]['skromniy']['warning']
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Гость:</b>\nЗапрещает новым пользователям говорить в течении <b>{timer}</b> минут.\n\n<b>Текст при срабатывании функции:</b>\n{text}',
                                    reply_markup=await generate_skromniy_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'eback_antifludscenes', state=MySceneStates.antifludw_change_scene)
@dp.callback_query_handler(lambda call: call.data == 'eback_antifludscenes', state=MySceneStates.antifludtimer_change_scene)
async def answer_to_eback_tixtimers(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"user_id": call.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        timer = 0
        text = '✋ {member_name}, флуд запрещен!'
        if db['settings'][index_of_chat]['antiflud_block']['warning'] != 'None': text = db['settings'][index_of_chat]['antiflud_block']['warning']
        if db['settings'][index_of_chat]['antiflud_block']['timer'] != 0: timer = db['settings'][index_of_chat]['antiflud_block']['timer']
        await call.answer()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Стоп флуд:</b>\nОтправка сообщений в чат с задержкой на <b>{timer}</b> сек.\n\n<b>Сообщение при нарушении:</b>\n{text}', reply_markup=await generate_antiflud_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'eback_tixtimers', state=MySceneStates.tixiychastimer_change_scene)
async def answer_to_eback_tixtimers(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"user_id": call.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        await call.answer()
        timers = 'Нет указанных промежутков'
        if len(db['settings'][index_of_chat]['tixiychas']['timers']) != 0:
            timers = ''
            for i in db['settings'][index_of_chat]['tixiychas']['timers']:
                timers += f'{i["t_i"]}: {i["time"]};\n'
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Тихий час:</b>\nЗапрещает пользователям писать в указанный промежуток времени\n\n<b>Ваши промежутки:</b>\n{timers}',
                                    reply_markup=await generate_tixiychas_show(db['user_id'], index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'eback_nofilescenes', state=MySceneStates.nofilelimit_change_scene)
async def answer_to_eback_nofilescenes(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"user_id": call.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        await call.answer()
        limit = db['settings'][index_of_chat]['nofile_show']['limit']
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Нет файлам:</b>\nЗапрещает отправку любых типов файлов превышающих <b>{limit}</b> мб', reply_markup=await generate_nofile_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'eback_resedittext', state=MySceneStates.resourcesw_change_scene)
async def answer_to_eback_resedittext(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"user_id": call.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        await call.answer()
        text = t_default_res
        if db['settings'][index_of_chat]['block_resources']['warning'] != 'None': text = db['settings'][index_of_chat]['block_resources']['warning']
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Сообщение при нарушении:</b>\n{text}',
                                    reply_markup=await generate_block_resources_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'eback_antimat', state=MySceneStates.antimatw_change_scene)
async def answer_to_eback_antimat(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"user_id": call.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        await call.answer()
        text = '✋ {member_name}, у нас запрещена нецензурная лексика!'
        if db['settings'][index_of_chat]['msg_filter']['mfilterw'] != 'None': text = db['settings'][index_of_chat]['msg_filter']['mfilterw']
        bwords = ", ".join(db["settings"][index_of_chat]["msg_filter"]["mfilters"])
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Заполните необходимые для блокировки слова:</b>\n\n<b>Сообщение при нарушении:</b>\n{text}\n\n<b>Ваш список запретов:</b>\n{bwords}',
                                    reply_markup=await generate_block_resources_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'eback_repedittext', state=MySceneStates.repostesw_change_scene)
async def answer_to_eback_repedittext(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"user_id": call.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        await call.answer()
        text = t_default_rep
        if db['settings'][index_of_chat]['block_repostes']['warning'] != 'None': text = db['settings'][index_of_chat]['block_repostes']['warning']
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Сообщение при нарушении:</b>\n{text}',
                                    reply_markup=await generate_block_repostes_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'eback_pingedittext', state=MySceneStates.pingw_change_scene)
async def answer_to_eback_pingedittext(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"user_id": call.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        await call.answer()
        text = t_default_ping
        if db['settings'][index_of_chat]['block_ping']['warning'] != 'None': text = db['settings'][index_of_chat]['block_ping']['warning']
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Сообщение при нарушении:</b>\n{text}',
                                    reply_markup=await generate_block_ping_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'eback_addblock', state=MySceneStates.blocked_resources_add)
async def answer_to_eback_addblock(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"user_id": call.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        await call.answer()
        blocked_reses = ", ".join(db["settings"][index_of_chat]["block_resources"]["r_list"])
        if len(db["settings"][index_of_chat]["block_resources"]["r_list"]) == 0: blocked_reses = 'Нету'
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nЗаблокированные ресурсы:\n<b>{blocked_reses}</b>',
                                    reply_markup=await generate_add_b_resources(), disable_web_page_preview=True)
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'eback_remblock', state=MySceneStates.blocked_resources_remove)
async def answer_to_eback_remblock(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"user_id": call.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        await call.answer()
        blocked_reses = ", ".join(db["settings"][index_of_chat]["block_resources"]["r_list"])
        if len(db["settings"][index_of_chat]["block_resources"]["r_list"]) == 0: blocked_reses = 'Нету'
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nЗаблокированные ресурсы:\n<b>{blocked_reses}</b>',
                                    reply_markup=await generate_add_b_resources(), disable_web_page_preview=True)
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'eback_gretedittext', state=MySceneStates.greeting_change_text_scene)
async def answer_to_eback_gretedittext(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"user_id": call.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        await call.answer()
        text = f'Приветствуем, <b>{str("{member_name}")}</b>!\n\nПрежде чем размещать свои объявления, пожалуйста, ознакомься с правилами. Они доступны по команде /rules'
        if db["settings"][index_of_chat]['greeting'] != 'None': text = db["settings"][index_of_chat]['greeting']
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Приветственное сообщение:</b>\n{text}',
                                    reply_markup=await generate_text_editing_page())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))



@dp.callback_query_handler(lambda call: call.data == 'eback_ruledittext', state=MySceneStates.rules_change_text_scene)
async def answer_to_eback_ruledittext(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"user_id": call.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        await call.answer()
        text = '<i>Правила отсутствуют</i>'
        if db["settings"][index_of_chat]['rules'] != 'None': text = db["settings"][index_of_chat]['rules']
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Правила чата:</b>\n{text}',
                                    reply_markup=await generate_rules_editing_page())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'eback_donatemoney', state=MySceneStates.donate_money_scene)
async def answer_to_eback_donatemoney(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        await show_start(call)
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'eback_vtimer', state=MySceneStates.vorchun_timer_scene)
@dp.callback_query_handler(lambda call: call.data == 'eback_afkedittext', state=MySceneStates.afk_change_text_scene)
@dp.callback_query_handler(lambda call: call.data == 'eback_afkeditmedia', state=MySceneStates.get_afkmedia_scene)
@dp.callback_query_handler(lambda call: call.data == 'eback_afkeditmedia_delete', state=MySceneStates.get_afkmedia_scene)
async def answer_to_eback_afk(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"user_id": call.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        if len(call.data.split('_')) == 3: await collection.find_one_and_update({"user_id": call.from_user.id}, {'$set': {f'settings.{index_of_chat}.afk.media': 'None'}})
        db = await collection.find_one({"user_id": call.from_user.id})
        text = f'Текст сообщения отсутствует 🤷‍♂'
        timer = '60'
        media = 'Нету'
        if 'timer' not in db['settings'][index_of_chat]['afk']:
            await collection.find_one_and_update({"user_id": call.from_user.id}, {"$set": {f'settings.{index_of_chat}.afk.timer': 'None'}})
        elif db['settings'][index_of_chat]['afk']['timer'] != 'None':
            timer = db['settings'][index_of_chat]['afk']['timer']
        if db['settings'][index_of_chat]['afk']['warning'] != 'None': text = db['settings'][index_of_chat]['afk']['warning']
        if db['settings'][index_of_chat]['afk']['media'] != 'None': media = db['settings'][index_of_chat]['afk']['media']['type']
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Ворчун:</b>\nЕсли в чате никто не пишет <b>{timer}</b> секунд, то выводит сообщение:\n\n{text}\n\n<b>Медия:</b> {media}',
                                    reply_markup=await generate_block_afk_show(db['user_id'], index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'eback_addsyms', state=MySceneStates.blocked_syms_add)
async def answer_to_eback_addsyms(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"user_id": call.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        list = 'Нету'
        if len(db['settings'][index_of_chat]['blocked_syms']) != 0: list = ', '.join(
            db['settings'][index_of_chat]['blocked_syms'])
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Ваш список символов:</b>\n{list}\n\n<b>Выберите действие:</b>',
                                    reply_markup=await generate_add_b_syms())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'eback_removesyms', state=MySceneStates.blocked_syms_remove)
async def answer_to_eback_removesyms(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"user_id": call.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        list = 'Нету'
        if len(db['settings'][index_of_chat]['blocked_syms']) != 0: list = ', '.join(
            db['settings'][index_of_chat]['blocked_syms'])
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Ваш список символов:</b>\n{list}\n\n<b>Выберите действие:</b>',
                                    reply_markup=await generate_add_b_syms())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'eback_banedittext', state=MySceneStates.banwarning_change_text_scene)
@dp.callback_query_handler(lambda call: call.data == 'eback_kickedittext', state=MySceneStates.kickwarning_change_text_scene)
@dp.callback_query_handler(lambda call: call.data == 'eback_unbanedittext', state=MySceneStates.unbantext_change_text_scene)
async def answer_to_eback_patrul(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        db = await collection.find_one({"user_id": call.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        ban = t_ban
        kick = t_kick
        unban = t_unban
        if db["settings"][index_of_chat]["warning_ban"] != 'None': ban = db["settings"][index_of_chat]["warning_ban"]
        if db["settings"][index_of_chat]["warning_kick"] != 'None': kick = db["settings"][index_of_chat]["warning_kick"]
        if db["settings"][index_of_chat]["unban_text"] != 'None': unban = db["settings"][index_of_chat]["unban_text"]
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n<b>Сообщения, которые будут выводиться по вводу команд: /kick , /ban , /unban</b>\n\n<b>/ban</b>\n{ban}\n\n<b>/kick</b>\n{kick}\n\n<b>/unban</b>\n{unban}',
                                    reply_markup=await generate_warning_editing_page())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'eback_msgfiltersadd', state=MySceneStates.wordsfilter_add_scene)
@dp.callback_query_handler(lambda call: call.data == 'eback_msgfiltersrem', state=MySceneStates.wordsfilter_rem_scene)
async def answer_to_eback_msgfilters(call: CallbackQuery, state: FSMContext):
    try:
        db = await collection.find_one({"user_id": call.from_user.id})
        group_id = db['chat_editing']
        index_of_chat = await get_dict_index(db, group_id)
        blist = 'Нет запретов'
        if len(db["settings"][index_of_chat]['msg_filter']['mfilters']) != 0: blist = ', '.join(db["settings"][index_of_chat]['msg_filter']['mfilters'])
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Фильтр слов:</b>\n\n<b>Ваш список запретов:</b>\n{blist}',
                                    reply_markup=await generate_wordsfilter_show(db['user_id'], index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))
    await state.finish()

@dp.callback_query_handler(lambda call: call.data == 'settings_admins')
async def edit_admins_settings(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"chats": group_id})
        index_of_chat = await get_dict_index(db, group_id)
        await call.answer()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nВыберите функцию:', reply_markup=await generate_admins_settings())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'back_to_admin_page')
async def back_to_admin_page(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"chats": group_id})
        index_of_chat = await get_dict_index(db, group_id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nВыберите функцию:', reply_markup=await generate_admins_settings())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'block_resources_show')
async def react_to_block_resources_show(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})

        index_of_chat = await get_dict_index(db, group_id)
        await call.answer()
        text = t_default_res
        if db['settings'][index_of_chat]['block_resources']['warning'] != 'None': text = db['settings'][index_of_chat]['block_resources']['warning']
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Сообщение при нарушении:</b>\n{text}', reply_markup=await generate_block_resources_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'block_repostes_show')
async def react_to_block_repostes_show(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})

        index_of_chat = await get_dict_index(db, group_id)
        await call.answer()
        text = t_default_rep
        if db['settings'][index_of_chat]['block_repostes']['warning'] != 'None': text = db['settings'][index_of_chat]['block_repostes']['warning']
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Сообщение при нарушении:</b>\n{text}', reply_markup=await generate_block_repostes_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'system_notice_show')
async def react_to_system_notice_show(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})

        index_of_chat = await get_dict_index(db, group_id)
        await call.answer()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nСокрытие системных оповещений о входе и выходе пользователей.', reply_markup=await generate_system_notice_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'block_ping_show')
async def react_to_block_ping_show(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})

        index_of_chat = await get_dict_index(db, group_id)
        await call.answer()
        text = t_default_ping
        if db['settings'][index_of_chat]['block_ping']['warning'] != 'None': text = db['settings'][index_of_chat]['block_ping']['warning']
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Сообщение при нарушении:</b>\n{text}', reply_markup=await generate_block_ping_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'splitmention_show')
async def react_to_splitmention_show(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        if 's_m' not in db['settings'][index_of_chat]['block_ping']: await collection.find_one_and_update({"user_id": db['user_id']}, {'$set': {f'settings.{index_of_chat}.block_ping.s_m': False}})
        await call.answer()
        text = t_default_ping
        if db['settings'][index_of_chat]['block_ping']['warning'] != 'None': text = db['settings'][index_of_chat]['block_ping']['warning']
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>@ username:</b>\n\n<b>Сообщение при нарушении:</b>\n{text}', reply_markup=await generate_split_mention_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'forbtoenter_show')
async def react_to_forbtoenter_show(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        if 'forbtoenter' not in db['settings'][index_of_chat]['block_ping']: await collection.find_one_and_update({"user_id": db['user_id']}, {'$set': {f'settings.{index_of_chat}.block_ping.forbtoenter': False}})
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Вход запрещен:</b>\nЗапрещает отправку анонимного сообщения от лица канала пользователя', reply_markup=await generate_forbtoenter_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'nofile_show')
async def react_to_nofile_show(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        if 'nofile_show' not in db['settings'][index_of_chat]: await collection.find_one_and_update({"user_id": db['user_id']}, {'$set': {f'settings.{index_of_chat}.nofile_show': {'active': False, 'limit': 0}}})
        db = await collection.find_one({"user_id": call.from_user.id})
        limit = db['settings'][index_of_chat]['nofile_show']['limit']
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Нет файлам:</b>\nЗапрещает отправку любых типов файлов превышающих <b>{limit}</b> мб', reply_markup=await generate_nofile_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'remmessages_show')
async def react_to_remmessages_show(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Удалить сообщения:</b>', reply_markup=await generate_remmessages_show(call.from_user.id))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: 'rmmsgs' in call.data)
async def react_to_rmmsgs(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        call_data = call.data.split('_')[1]
        if call_data != 'set':
            await collection.find_one_and_update({"user_id": call.from_user.id}, {'$set': {f'settings.{index_of_chat}.rmmsgs_interval': call_data}})
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Вы уверены что хотите удалить сообщения?</b>', reply_markup=await generate_remmessages_agreement())
        else:
            await bot.delete_message(message_id=call.message.message_id, chat_id=call.message.chat.id)
            await MySceneStates.get_rmsginterval_scene.set()
            quatback = await bot.send_message(chat_id=call.message.chat.id, text=f'Введите интервал в формате <b><a href="https://telegra.ph/YYYY-MM-DD-HHMMSS-12-30">YYYY-MM-DD HH:MM:SS(от)_YYYY-MM-DD HH:MM:SS(до)</a></b>:', reply_markup=await generate_back_rmsginterval())
            await collection.find_one_and_update({"user_id": call.from_user.id}, {"$set": {"chat_editing": group_id, "quatback": quatback.message_id}})
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'back_from_remagreement')
async def react_to_back_from_remagreement(call: CallbackQuery):
    try:
        await react_to_remmessages_show(call)
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'remmessages_agreement')
async def react_to_remmessages_agreement(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        call_data = db['settings'][index_of_chat]['rmmsgs_interval']
        if call_data == 'days':
            chat_inf = await bot.get_chat(db['settings'][index_of_chat]['chat_id'])
            lastmsgdate = await get_last_msgdate(db['settings'][index_of_chat]['chat_id'], chat_inf.invite_link)
            lastmsgtounix = await convert_to_unix_timestamp_msk(lastmsgdate)
            fromunixt = await subtract_days_from_unix_time(lastmsgtounix, 1)
            asyncio.create_task(delete_chat_messages(db['settings'][index_of_chat]['chat_id'], chat_inf.invite_link, [fromunixt, lastmsgtounix]))
        elif call_data == 'week':
            chat_inf = await bot.get_chat(db['settings'][index_of_chat]['chat_id'])
            lastmsgdate = await get_last_msgdate(db['settings'][index_of_chat]['chat_id'], chat_inf.invite_link)
            lastmsgtounix = await convert_to_unix_timestamp_msk(lastmsgdate)
            fromunixt = await subtract_days_from_unix_time(lastmsgtounix, 7)
            asyncio.create_task(delete_chat_messages(db['settings'][index_of_chat]['chat_id'], chat_inf.invite_link, [fromunixt, lastmsgtounix]))
        else:
            chat_inf = await bot.get_chat(db['settings'][index_of_chat]['chat_id'])
            lastmsgdate = await get_last_msgdate(db['settings'][index_of_chat]['chat_id'], chat_inf.invite_link)
            lastmsgtounix = await convert_to_unix_timestamp_msk(lastmsgdate)
            fromunixt = await subtract_days_from_unix_time(lastmsgtounix, 30)
            asyncio.create_task(delete_chat_messages(db['settings'][index_of_chat]['chat_id'], chat_inf.invite_link, [fromunixt, lastmsgtounix]))

        trash = await bot.send_message(chat_id=call.from_user.id, text='✅ Удаление в процессе...')
        asyncio.create_task(delete_message(5, [trash.message_id], call.message.chat.id))
        await asyncio.sleep(2)
        await react_to_remmessages_show(call)
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'back_from_paydialuser_pmethod')
async def react_to_back_from_paydialuser_pmethod(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        chat_name = ''
        try:
            chat = await bot.get_chat(group_id)
            chat_name = chat.title
        except:
            pass
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<a href="https://{group_id}.id">🎤</a> <b>Плати говори:</b> {chat_name}\n\nВыберите тариф:', reply_markup=await generate_paydialogueuser_tarifs(group_id))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: 'back_from_paydialuserpay' in call.data, state=MySceneStates.paydialuser_pay)
@dp.callback_query_handler(lambda call: 'paydialchutarif' in call.data)
async def react_to_paydialchutarif(call: CallbackQuery, state: FSMContext):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        chat_name = ''
        try:
            chat = await bot.get_chat(group_id)
            chat_name = chat.title
        except:
            pass

        if call.data == 'back_from_paydialuserpay':
            await state.finish()
            return await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<a href="https://{group_id}.id">🎤</a> <b>Плати Говори:</b> {chat_name}\n\nВыберите способ оплаты:', reply_markup=await generate_paydialogueuser_pmethod(group_id))

        await collection.find_one_and_update({"user_id": call.from_user.id}, {'$set': {"paydial_tarif": int(call.data.split('_')[1]), "paydial_group": group_id}})
        db = await collection.find_one({"chats": group_id})

        if db['user_id'] in [216428203, 1402490508, 5103314362]:
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            await MySceneStates.paydialuser_getemail.set()
            quatback = await bot.send_message(chat_id=call.from_user.id, text=f'<a href="https://{group_id}.id">📝</a> Введите gmail почту, для того чтобы мы смогли отправить вам чек:', reply_markup=await generate_back_paydialemailget())
            return await collection.find_one_and_update({"user_id": call.from_user.id}, {'$set': {"quatback": quatback.message_id}})

        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<a href="https://{group_id}.id">🎤</a> <b>Плати Говори:</b> {chat_name}\n\nВыберите способ оплаты:', reply_markup=await generate_paydialogueuser_pmethod(group_id))
    except Exception as e:
        # traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'eback_paydialemailget', state=MySceneStates.paydialuser_getemail)
async def react_to_eback_paydialemailget(call: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)

        db = await collection.find_one({"chats": group_id})
        index_of_chat = await get_dict_index(db, group_id)
        chat_name = ''
        try:
            chat = await bot.get_chat(group_id)
            chat_name = chat.title
        except:
            pass
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<a href="https://{group_id}.id">🎤</a> <b>Плати говори:</b> {chat_name}\n\nВыберите тариф:', reply_markup=await generate_paydialogueuser_tarifs(group_id))
    except:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'baydyoo_check', state=MySceneStates.paydial_yooauto)
async def react_to_baydyoo_check(call: CallbackQuery, state: FSMContext):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        udb = await collection.find_one({"user_id": call.from_user.id})
        status = paydial_getpaymentstatus(udb['paydial_yoo_pid'])
        if status == True:
            db = await collection.find_one({"chats": group_id})
            index_of_chat = await get_dict_index(db, group_id)
            user_dict_index = await get_chat_user_dict_index(db, int(call.from_user.id), index_of_chat)
            end_data = await calculate_end_date(udb['paydial_tarif'])
            if 'customers' not in db['settings'][index_of_chat]['subscribe_show']['paydialogue']: await collection.find_one_and_update({"user_id": db['user_id']}, {'$set': {f'settings.{index_of_chat}.subscribe_show.paydialogue.customers': []}})
            await collection.find_one_and_update({"user_id": db['user_id']}, {'$set': {f'settings.{index_of_chat}.users.{user_dict_index}.paydialogue_payed': True, f'settings.{index_of_chat}.users.{user_dict_index}.paydialogue_payed_for': end_data[1]}, "$push": {f"settings.{index_of_chat}.subscribe_show.paydialogue.customers": {"id": call.from_user.id, "paydialogue_payed_for": end_data[1]}}})
            chat_name = ''
            try:
                chat = await bot.get_chat(group_id)
                chat_name = chat.title
            except:
                pass
            await state.finish()
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'Доступ к чату <b>"{chat_name}"</b> выдан. Спасибо за то, что Вы с нами!\n\n<b>Тариф длиться до</b>: {end_data[0]}')
        else:
            await call.answer("😥 Пока не вижу оплаты...", show_alert=True)
    except:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'cancbaydyoo', state=MySceneStates.paydial_yooauto)
async def react_to_cancbaydyoo(call: CallbackQuery, state: FSMContext):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        udb = await collection.find_one({"user_id": call.from_user.id})
        cancelpt = cancel_paydial_payment(udb['paydial_yoo_pid'])
        await state.finish()
        db = await collection.find_one({"chats": group_id})
        index_of_chat = await get_dict_index(db, group_id)
        chat_name = ''
        try:
            chat = await bot.get_chat(group_id)
            chat_name = chat.title
        except:
            pass
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<a href="https://{group_id}.id">🎤</a> <b>Плати говори:</b> {chat_name}\n\nВыберите тариф:', reply_markup=await generate_paydialogueuser_tarifs(group_id))
    except:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: 'paydialbuy' in call.data)
async def react_to_paydialbuy(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"chats": group_id})
        udb = await collection.find_one_and_update({"user_id": call.from_user.id}, {"$set": {"paydial_group": group_id, "paydial_pmeth": int(call.data.split("_")[1])}})
        index_of_chat = await get_dict_index(db, group_id)
        tarif_index_id = await get_padialtarifindexid(db, index_of_chat, udb["paydial_tarif"])
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        info = 'Информации нет'
        chat_name = ''
        try:
            chat = await bot.get_chat(group_id)
            chat_name = chat.title
        except:
            pass
        if db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["payment_methods"][int(call.data.split("_")[1])]["info"] != 'None': info = db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["payment_methods"][int(call.data.split("_")[1])]["info"]
        quatback = await bot.send_message(chat_id=call.message.chat.id, text=f'<a href="https://{group_id}.id">🎤</a> <b>Плати Говори</b>: {chat_name}n\n<b>Метод оплаты</b>: {db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["payment_methods"][int(call.data.split("_")[1])]["payment_name"]}\n\n<b>Кол-во дней</b>: {db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["tarif_plans"][tarif_index_id]["days"]}\n<b>Цена</b>: {db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["tarif_plans"][tarif_index_id]["price"]}\n\n<b>Условия</b>: {info}\n\nВыполните условия и отправьте скриншот/видео/pdf оплаты:', reply_markup=await generate_back_paydialuserpay())
        await collection.find_one_and_update({"user_id": call.from_user.id}, {"$set": {"quatback": quatback.message_id}})
        await MySceneStates.paydialuser_pay.set()
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: 'transdial' in call.data)
async def react_to_paydialbuy(call: CallbackQuery):
    try:
        group_id_url = call.message.caption_entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        call_datas = call.data.split('_')
        user_datas = call.message.caption_entities[1].url.replace('https://', '').replace('.com/', '').split('.')
        payment_method_index = user_datas[0]
        tarif_index = await get_padialtarifindexid(db, index_of_chat, int(user_datas[1]))
        chat_name = ''
        try:
            chat = await bot.get_chat(db['settings'][index_of_chat]['chat_id'])
            chat_name = chat.title
        except:
            pass

        if call_datas[2] == 'a':
            user_dict_index = await get_chat_user_dict_index(db, int(call_datas[1]), index_of_chat)
            end_data = await calculate_end_date(db['settings'][index_of_chat]["subscribe_show"]["paydialogue"]["tarif_plans"][tarif_index]["days"])
            if 'customers' not in db['settings'][index_of_chat]['subscribe_show']['paydialogue']: await collection.find_one_and_update({"user_id": call.from_user.id}, {'$set': {f'settings.{index_of_chat}.subscribe_show.paydialogue.customers': []}})
            await collection.find_one_and_update({"user_id": call.from_user.id}, {'$set': {f'settings.{index_of_chat}.users.{user_dict_index}.paydialogue_payed': True, f'settings.{index_of_chat}.users.{user_dict_index}.paydialogue_payed_for': end_data[1]}, "$push": {f"settings.{index_of_chat}.subscribe_show.paydialogue.customers": {"id": int(call_datas[1]), "paydialogue_payed_for": end_data[1]}}})
            await bot.send_message(chat_id=call_datas[1], text=f'Доступ к чату <b>"{chat_name}"</b> выдан. Спасибо за то, что Вы с нами!\n\n<b>Тариф длиться до</b>: {end_data[0]}')
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            await bot.send_message(call.message.chat.id, text='Отчет отправлен ✅')
        else:
            await bot.send_message(chat_id=call_datas[1], text=f'❌ Ваша оплата для доступа в <b>"{chat_name}"</b> не прошла проверку, для большей информации обратитесь к создателю чата: <b><a href="tg://user?id={call.from_user.id}">{call.from_user.first_name}</a></b>(@{call.from_user.username})')
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            await bot.send_message(call.message.chat.id, text='Отчет отправлен ✅')
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'back_from_paydialpaydata')
@dp.callback_query_handler(lambda call: call.data == 'back_from_paydialtarifs')
@dp.callback_query_handler(lambda call: call.data == 'back_from_paydialcustomers')
@dp.callback_query_handler(lambda call: call.data == 'eback_paydialgiveperm', state=MySceneStates.paydial_giveperm)
@dp.callback_query_handler(lambda call: call.data == 'eback_paydialgiveperm', state=MySceneStates.paydial_giveperdays)
@dp.callback_query_handler(lambda call: call.data == 'paydialogue_show')
async def react_to_paydialogue_show(call: CallbackQuery, state: FSMContext):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        if call.data == 'eback_paydialgiveperm':
            await state.finish()
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        text = 'Нету'
        if 'paydialogue' not in db['settings'][index_of_chat]['subscribe_show']:
            await collection.find_one_and_update({"user_id": db['user_id']}, {'$set': {f'settings.{index_of_chat}.subscribe_show.paydialogue': {'active': False, 'payment_methods': [], 'tarif_plans': []}}})
        elif 'warning' in db['settings'][index_of_chat]['subscribe_show']['paydialogue'] and db['settings'][index_of_chat]['subscribe_show']['paydialogue']['warning'] != 'None': text = db['settings'][index_of_chat]['subscribe_show']['paydialogue']['warning']
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b>\n\n<b>Сообщение при нарушении:</b>\n{text}', reply_markup=await generate_paydialogue_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'paydial_giveperms')
async def react_to_paydial_giveperms(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        if 'customers' not in db['settings'][index_of_chat]['subscribe_show']['paydialogue']:
            await collection.find_one_and_update({"user_id": call.from_user.id}, {'$set': {f'settings.{index_of_chat}.subscribe_show.paydialogue.customers': []}})
            db = await collection.find_one({"user_id": call.from_user.id})
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        quatback = await bot.send_message(call.message.chat.id, f'<a href="https://{group_id}.id">👤</a> Введите юзернейм(@username):', reply_markup=await generate_back_paydialgiveperm())
        await MySceneStates.paydial_giveperm.set()
        await collection.find_one_and_update({"user_id": call.from_user.id}, {'$set': {"chat_editing": group_id, "quatback": quatback.message_id}})
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data in ['paydial_customers', 'back_from_backfrompaydicust'])
async def react_to_paydial_customers(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        if 'customers' not in db['settings'][index_of_chat]['subscribe_show']['paydialogue']:
            await collection.find_one_and_update({"user_id": call.from_user.id}, {'$set': {f'settings.{index_of_chat}.subscribe_show.paydialogue.customers': []}})
            db = await collection.find_one({"user_id": call.from_user.id})
        asyncio.create_task(get_paydialcustomers(db['settings'][index_of_chat]['subscribe_show']['paydialogue']['customers'], 1, index_of_chat, group_id, call.message.message_id, call.message.chat.id, update_date=await update_time(db["settings"][index_of_chat]["updated_date"])))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: 'pdcustpaged' in call.data)
async def react_to_pdcustpaged(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        user_id = int(call.data.split('_')[1])
        userchat_dbindx = await get_chat_user_dict_index(db, user_id, index_of_chat)
        await collection.find_one_and_update({"user_id": call.from_user.id}, {'$pull': {f'settings.{index_of_chat}.subscribe_show.paydialogue.customers': {"id": user_id}}, "$set": {f'settings.{index_of_chat}.users.{userchat_dbindx}.paydialogue_payed': False}})
        await react_to_paydial_customers(call)
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: 'paydialc' in call.data)
async def react_to_paydialc(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        user_id = int(call.data.split('_')[1])
        username = 'Нет информации'
        try:
            user = await bot.get_chat(user_id)
            username = user.first_name
        except:
            pass
        user_arr_index = 'None'
        for index, i in enumerate(db['settings'][index_of_chat]['subscribe_show']['paydialogue']['customers']):
            if i['id'] == user_id:
                user_arr_index = index
                break
        else: return

        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b> Клиент\n\n<b>Имя:</b> {username}\n<b>Дата окончания доступа:</b> {await format_unix_to_date(db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["customers"][user_arr_index]["paydialogue_payed_for"])}', reply_markup=await generate_paydcustpage(user_id))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: 'paydialpagesc' in call.data)
async def react_to_paydialpagesc(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        page = db['settings'][index_of_chat]['paydialcuspage']
        if call.data.split('_')[1] == 'next':
            page += 1
        else: page -= 1
        asyncio.create_task(get_paydialcustomers(db['settings'][index_of_chat]['subscribe_show']['paydialogue']['customers'], page, index_of_chat, group_id, call.message.message_id, call.message.chat.id, clb=call.id, update_date=await update_time(db["settings"][index_of_chat]["updated_date"])))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'back_from_paydialtarif')
@dp.callback_query_handler(lambda call: call.data == 'paydialtarifs')
async def react_to_paydialtarifs(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        if len(db['settings'][index_of_chat]['subscribe_show']['paydialogue']['tarif_plans']) == 0:
            return await call.answer('⚠ У вас нет тарифов')
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b> Тарифы', reply_markup=await generate_paydialoguetarifs_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'back_from_paydialpaymeth')
@dp.callback_query_handler(lambda call: call.data == 'paydial_paymethodsshow')
async def react_to_paydial_paymethodsshow(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b> Реквизиты', reply_markup=await generate_paydialoguepaydata_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: 'paydialpm' in call.data)
async def react_to_paydialpm(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)

        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        for i in call.message.reply_markup.inline_keyboard:
            if i[0].callback_data == call.data:
                if i[0].text != db['settings'][index_of_chat]['subscribe_show']['paydialogue']['payment_methods'][int(call.data.split('_')[1])]['payment_name']:
                    return await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b> Реквизиты', reply_markup=await generate_paydialoguepaydata_show(call.from_user.id, index_of_chat))

        info = "Нету"
        pname = db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["payment_methods"][int(call.data.split("_")[1])]["payment_name"]
        if db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["payment_methods"][int(call.data.split("_")[1])]["info"] != 'None': info = db["settings"][index_of_chat]["subscribe_show"]["paydialogue"]["payment_methods"][int(call.data.split("_")[1])]["info"]
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b>\n\n<a href="https://{call.data.split("_")[1]}.com">💳</a> <b>Реквизит</b>: {pname}\n\n<b>Условия</b>:\n{info}', reply_markup=await generate_paydialoguepmethmanage())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: 'paydialtarifd' in call.data)
@dp.callback_query_handler(lambda call: 'backpaydialtarifchoice' in call.data)
async def react_to_paydialpm(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)

        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        call_data = int(call.data.split('_')[1])

        for i in db['settings'][index_of_chat]["subscribe_show"]["paydialogue"]["tarif_plans"]:
            if i['days'] == call_data:
                return await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b>\n\n<a href="https://{i["days"]}.com">📦</a> <b>Тариф на</b>: {i["days"]} дней\n\n<b>Цена</b>:\n{i["price"]}', reply_markup=await generate_paydialoguetarifmanage())
        else:
            if len(db['settings'][index_of_chat]['subscribe_show']['paydialogue']['tarif_plans']) == 0:
                return await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b>', reply_markup=await generate_paydialogue_show(call.from_user.id, index_of_chat))
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b> Тарифы', reply_markup=await generate_paydialoguetarifs_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'paydialrem')
async def react_to_paydialrem(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        pmeth = int(call.message.entities[5].url.replace('https://', '').replace('.com/', ''))
        await collection.find_one_and_update({"user_id": call.from_user.id}, {'$pull': {f'settings.{index_of_chat}.subscribe_show.paydialogue.payment_methods': {"payment_name": db['settings'][index_of_chat]['subscribe_show']['paydialogue']['payment_methods'][pmeth]['payment_name']}}})
        await react_to_paydial_paymethodsshow(call)
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'paydialremtarif')
async def react_to_paydialremtarif(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        tarifid = int(call.message.entities[5].url.replace('https://', '').replace('.com/', ''))
        await collection.find_one_and_update({"user_id": call.from_user.id}, {'$pull': {f'settings.{index_of_chat}.subscribe_show.paydialogue.tarif_plans': {"days": tarifid}}})
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Плати Говори:</b>', reply_markup=await generate_paydialogue_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'subscribe_show')
@dp.callback_query_handler(lambda call: call.data == 'back_from_paydialshow')
@dp.callback_query_handler(lambda call: call.data == 'back_from_subscribe_channels')
@dp.callback_query_handler(lambda call: call.data == 'back_from_subscribe_channelremover')
async def react_to_subscribe_show(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        text = '✋ member_name, чтобы продолжить общение в нашем чате, Вам необходимо:'
        if 'subscribe_show' not in db['settings'][index_of_chat]:
            await collection.find_one_and_update({"user_id": db['user_id']}, {'$set': {f'settings.{index_of_chat}.subscribe_show': {'active': False, 'channels': []}}})
        elif 'warning' in db['settings'][index_of_chat]['subscribe_show'] and db['settings'][index_of_chat]['subscribe_show']['warning'] != 'None':
            text = db['settings'][index_of_chat]['subscribe_show']['warning']

        db = await collection.find_one({"user_id": call.from_user.id})
        channels_len = len(db['settings'][index_of_chat]['subscribe_show']['channels'])
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Подписать:</b>\nЕсли пользователь делает попытку писать в чат что-либо, то он видит сообщение:\n\n{text}\n\n<b>Ваших каналов:</b> {channels_len}', reply_markup=await generate_subscribe_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'subscribecrem')
async def react_to_subscribe_channels(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>🎡 Выберите канал который хотите удалить:</b>', reply_markup=await generate_subscribe_channelremover(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'subscribe_channels')
async def react_to_subscribe_channels(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>🎡 Ваши каналы:</b>', reply_markup=await generate_subscribe_channels(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: 'remchannel' in call.data)
async def react_to_remchannel(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        call_data = call.data.split('_')[1]
        await collection.find_one_and_update({"user_id": call.from_user.id}, {'$pull': {f'settings.{index_of_chat}.subscribe_show.channels': {'id': int(call_data)}}})
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await generate_subscribe_channelremover(db['user_id'], index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'antiflud_show')
async def react_to_forbtoenter_show(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        if 'antiflud_block' not in db['settings'][index_of_chat]: await collection.find_one_and_update({"user_id": db['user_id']}, {'$set': {f'settings.{index_of_chat}.antiflud_block': {'active': False, 'warning': 'None', 'timer': 0}}})
        db = await collection.find_one({"user_id": call.from_user.id})
        timer = 0
        text = '✋ {member_name}, флуд запрещен!'
        if db['settings'][index_of_chat]['antiflud_block']['warning'] != 'None': text = db['settings'][index_of_chat]['antiflud_block']['warning']
        if db['settings'][index_of_chat]['antiflud_block']['timer'] != 0: timer = db['settings'][index_of_chat]['antiflud_block']['timer']
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Стоп флуд:</b>\nОтправка сообщений в чат с задержкой на <b>{timer}</b> сек.\n\n<b>Сообщение при нарушении:</b>\n{text}', reply_markup=await generate_antiflud_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'noname_show')
async def react_to_noname_show(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})
        index_of_chat = await get_dict_index(db, group_id)
        if 'noname' not in db['settings'][index_of_chat]: await collection.find_one_and_update({"user_id": db['user_id']}, {'$set': {f'settings.{index_of_chat}.noname': False}})
        await call.answer()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Без имени:</b>\nБлокировка пользователей скрывающих свой контакт.', reply_markup=await generate_noname_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'back_from_split_mention')
@dp.callback_query_handler(lambda call: call.data == 'back_from_forbtoenter_show')
async def react_to_back_from_split_mention(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        await react_to_noname_show(call)
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: 'activator' in call.data)
async def react_to_activator(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})

        index_of_chat = await get_dict_index(db, group_id)

        call_data_identificator = call.data.split('_')[1]

        if call_data_identificator == 'resources':
            if db['settings'][index_of_chat]['block_resources']['active'] == False:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.block_resources.active": True, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            else:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.block_resources.active": False, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                reply_markup=await generate_block_resources_show(call.from_user.id, index_of_chat))
        elif call_data_identificator == 'repostes':
            if db['settings'][index_of_chat]['block_repostes']['active'] == False:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.block_repostes.active": True, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            else:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.block_repostes.active": False, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                reply_markup=await generate_block_repostes_show(call.from_user.id, index_of_chat))
        elif call_data_identificator == "sysnot":
            if db['settings'][index_of_chat]['system_notice']['active'] == False:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.system_notice.active": True, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            else:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.system_notice.active": False, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                reply_markup=await generate_system_notice_show(call.from_user.id, index_of_chat))
        elif call_data_identificator == "afk":
            if db['settings'][index_of_chat]['afk']['active'] == False:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.afk.active": True, f"settings.{index_of_chat}.updated_date": await get_msk_unix(), f"settings.{index_of_chat}.bot_send_afk": False}})
            else:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.afk.active": False, f"settings.{index_of_chat}.updated_date": await get_msk_unix(), f"settings.{index_of_chat}.bot_send_afk": False}})
            await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                reply_markup=await generate_block_afk_show(call.from_user.id, index_of_chat))
        elif call_data_identificator == "skromniy":
            if db['settings'][index_of_chat]['skromniy']['active'] == False:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.skromniy.active": True, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            else:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.skromniy.active": False, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                reply_markup=await generate_skromniy_show(call.from_user.id, index_of_chat))
        elif call_data_identificator == "tixiychas":
            if db['settings'][index_of_chat]['tixiychas']['active'] == False:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.tixiychas.active": True, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            else:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.tixiychas.active": False, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                reply_markup=await generate_tixiychas_show(call.from_user.id, index_of_chat))
        elif call_data_identificator == "splitmention":
            if db['settings'][index_of_chat]['block_ping']['s_m'] == False:
                if db['settings'][index_of_chat]['block_ping']['active'] == False: return await call.answer('✋ Вы не можете активировать split_mention, без активации блокировки пинга', show_alert=True)
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.block_ping.s_m": True, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            else:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.block_ping.s_m": False, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                reply_markup=await generate_split_mention_show(call.from_user.id, index_of_chat))
        elif call_data_identificator == 'italic':
            if db['settings'][index_of_chat]['msg_filter']['italic'] == False:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.msg_filter.italic": True, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            else:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.msg_filter.italic": False, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            italic = 'Выключено'
            bold = 'Выключено'
            caps = 'Выключено'
            db = await collection.find_one({"user_id": db['user_id']})
            if db['settings'][index_of_chat]['msg_filter']['italic'] == True: italic = 'Включено'
            if db['settings'][index_of_chat]['msg_filter']['bold'] == True: bold = 'Включено'
            if db['settings'][index_of_chat]['msg_filter']['capslock'] == True: caps = 'Включено'
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n<b>Фильтры текстовых сообщений:</b>\n\n<b>Фильтр "Italic" сообщений:</b>\n{italic}\n\n<b>Фильтр "Bold" сообщений:</b>\n{bold}\n\n<b>Фильтр "Caps Lock" сообщений:</b>\n{caps}',
                                        reply_markup=await generate_msg_filters_btns(db['user_id'], index_of_chat))
        elif call_data_identificator == 'bold':
            if db['settings'][index_of_chat]['msg_filter']['bold'] == False:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.msg_filter.bold": True, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            else:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.msg_filter.bold": False, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            italic = 'Выключено'
            bold = 'Выключено'
            caps = 'Выключено'
            db = await collection.find_one({"user_id": db['user_id']})
            if db['settings'][index_of_chat]['msg_filter']['italic'] == True: italic = 'Включено'
            if db['settings'][index_of_chat]['msg_filter']['bold'] == True: bold = 'Включено'
            if db['settings'][index_of_chat]['msg_filter']['capslock'] == True: caps = 'Включено'
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n<b>Фильтры текстовых сообщений:</b>\n\n<b>Фильтр "Italic" сообщений:</b>\n{italic}\n\n<b>Фильтр "Bold" сообщений:</b>\n{bold}\n\n<b>Фильтр "Caps Lock" сообщений:</b>\n{caps}',
                                        reply_markup=await generate_msg_filters_btns(db['user_id'], index_of_chat))
        elif call_data_identificator == 'caps':
            if db['settings'][index_of_chat]['msg_filter']['capslock'] == False:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.msg_filter.capslock": True, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            else:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.msg_filter.capslock": False, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            italic = 'Выключено'
            bold = 'Выключено'
            caps = 'Выключено'
            db = await collection.find_one({"user_id": db['user_id']})
            if db['settings'][index_of_chat]['msg_filter']['italic'] == True: italic = 'Включено'
            if db['settings'][index_of_chat]['msg_filter']['bold'] == True: bold = 'Включено'
            if db['settings'][index_of_chat]['msg_filter']['capslock'] == True: caps = 'Включено'
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n<b>Фильтры текстовых сообщений:</b>\n\n<b>Фильтр "Italic" сообщений:</b>\n{italic}\n\n<b>Фильтр "Bold" сообщений:</b>\n{bold}\n\n<b>Фильтр "Caps Lock" сообщений:</b>\n{caps}',
                                        reply_markup=await generate_msg_filters_btns(db['user_id'], index_of_chat))
        elif call_data_identificator == 'noname':
            if db['settings'][index_of_chat]['noname'] == False:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.noname": True, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            else:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.noname": False, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await generate_noname_show(call.from_user.id, index_of_chat))
        elif call_data_identificator == 'wordsfilter':
            if db['settings'][index_of_chat]['msg_filter']['mfiltersa'] == False:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.msg_filter.mfiltersa": True, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            else:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.msg_filter.mfiltersa": False, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await generate_wordsfilter_show(call.from_user.id, index_of_chat))
        elif call_data_identificator == 'forbtoenter':
            if db['settings'][index_of_chat]['block_ping']['forbtoenter'] == False:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.block_ping.forbtoenter": True, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            else:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.block_ping.forbtoenter": False, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await generate_forbtoenter_show(call.from_user.id, index_of_chat))
        elif call_data_identificator == 'antiflud':
            if db['settings'][index_of_chat]['antiflud_block']['active'] == False:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.antiflud_block.active": True, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            else:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.antiflud_block.active": False, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await generate_antiflud_show(call.from_user.id, index_of_chat))
        elif call_data_identificator == 'nofile':
            if db['settings'][index_of_chat]['nofile_show']['active'] == False:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.nofile_show.active": True, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            else:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.nofile_show.active": False, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await generate_nofile_show(call.from_user.id, index_of_chat))
        elif call_data_identificator == 'subscribe':
            if db['settings'][index_of_chat]['subscribe_show']['active'] == False:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.subscribe_show.active": True, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            else:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.subscribe_show.active": False, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await generate_subscribe_show(call.from_user.id, index_of_chat))
        elif call_data_identificator == 'paydialogue':
            if db['settings'][index_of_chat]['subscribe_show']['paydialogue']['active'] == False:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.subscribe_show.paydialogue.active": True, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            else:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.subscribe_show.paydialogue.active": False, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await generate_paydialogue_show(call.from_user.id, index_of_chat))
        else:
            if db['settings'][index_of_chat]['block_ping']['active'] == False:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.block_ping.active": True, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            else:
                await collection.find_one_and_update({"user_id": call.from_user.id},
                                               {"$set": {f"settings.{index_of_chat}.block_ping.active": False, f"settings.{index_of_chat}.updated_date": await get_msk_unix()}})
            await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                reply_markup=await generate_block_ping_show(call.from_user.id, index_of_chat))

        await call.answer()
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'blocked_resources')
async def show_blocked_resources(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"user_id": call.from_user.id})

        index_of_chat = await get_dict_index(db, group_id)

        await call.answer()
        blocked_reses = ", ".join(db["settings"][index_of_chat]["block_resources"]["r_list"])
        if len(db["settings"][index_of_chat]["block_resources"]["r_list"]) == 0: blocked_reses = 'Нету'
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nЗаблокированные ресурсы:\n<b>{blocked_reses}</b>',
                                    reply_markup=await generate_add_b_resources(), disable_web_page_preview=True)
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'vorchun_show')
async def answer_to_vorchun_show(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"chats": group_id})
        index_of_chat = await get_dict_index(db, group_id)
        text = f'Текст сообщения отсутствует 🤷‍♂'
        timer = '2700'
        media = 'Нету'
        if 'timer' not in db['settings'][index_of_chat]['afk']:
            await collection.find_one_and_update({"chats": group_id}, {"$set": {f'settings.{index_of_chat}.afk.timer': 'None'}})
        elif db['settings'][index_of_chat]['afk']['timer'] != 'None': timer = db['settings'][index_of_chat]['afk']['timer']
        if db['settings'][index_of_chat]['afk']['warning'] != 'None': text = db['settings'][index_of_chat]['afk']['warning']
        if db['settings'][index_of_chat]['afk']['media'] != 'None': media = db['settings'][index_of_chat]['afk']['media']['type']
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Ворчун:</b>\nЕсли в чате никто не пишет <b>{timer}</b> секунд, то выводит сообщение:\n\n{text}\n\n<b>Медия:</b> {media}', reply_markup=await generate_block_afk_show(db['user_id'], index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'add_block_resources')
async def react_to_add_block_resources(call: CallbackQuery):
    if await blocked(call.from_user.id):
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
    group_id_url = call.message.entities[0].url
    group_id = int("-" + re.sub(r"\D", "", group_id_url))
    if await is_chat_in(group_id) == False:
        await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
        return await show_start(call)
    db = await collection.find_one({"user_id": call.from_user.id})
    index_of_chat = await get_dict_index(db, group_id)
    blocks_list = 'Нету'
    if len(db["settings"][index_of_chat]['block_resources']['r_list']) != 0: blocks_list = ', '.join(db["settings"][index_of_chat]['block_resources']['r_list'])
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    quatback = await bot.send_message(call.message.chat.id, f'📋 Введите доменные расширения, которые хотите заблокировать через запятую\n\nПример 1: ru\nПример 2: ru, com, io\n\n<b>Ваш список запретов:</b> {blocks_list}', reply_markup=await generate_back_addblock(), disable_web_page_preview=True)
    await collection.find_one_and_update({"user_id": call.from_user.id}, {"$set": {"chat_editing": group_id, "quatback": quatback.message_id}})
    await MySceneStates.blocked_resources_add.set()

@dp.callback_query_handler(lambda call: call.data == 'remove_block_resources')
async def react_to_add_block_resources(call: CallbackQuery):
    if await blocked(call.from_user.id):
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
    group_id_url = call.message.entities[0].url
    group_id = int("-" + re.sub(r"\D", "", group_id_url))
    if await is_chat_in(group_id) == False:
        await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
        return await show_start(call)
    db = await collection.find_one({"user_id": call.from_user.id})
    index_of_chat = await get_dict_index(db, group_id)
    blocks_list = 'Нету'
    if len(db["settings"][index_of_chat]['block_resources']['r_list']) == 0:
        return await call.answer('✋ У вас нет запретов в вашем списке, которых можно удалить!', show_alert=True)
    else:
        blocks_list = ', '.join(db["settings"][index_of_chat]['block_resources']['r_list'])
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    quatback = await bot.send_message(call.message.chat.id, f'📋 Введите доменные расширения, которые хотите удалить из заблокированных через запятую\n\nПример 1: ru\nПример 2: ru, com, io\n\n<b>Ваш список запретов:</b> {blocks_list}', reply_markup=await generate_back_remblock(), disable_web_page_preview=True)
    await collection.find_one_and_update({"user_id": call.from_user.id}, {"$set": {"chat_editing": group_id, "quatback": quatback.message_id}})
    await MySceneStates.blocked_resources_remove.set()

@dp.callback_query_handler(lambda call: call.data == 'back_to_block_resources')
async def react_to_back_to_block_resources(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"chats": str(group_id)})

        index_of_chat = await get_dict_index(db, group_id)

        await call.answer()
        text = '✋ {member_name}, у нас запрещено использовать ссылки!'
        if db['settings'][index_of_chat]['block_resources']['warning'] != 'None': text = db['settings'][index_of_chat]['block_resources']['warning']
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nСообщение при нарушении:\n{text}', reply_markup=await generate_block_resources_show(call.from_user.id, index_of_chat))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: 'sprav' in call.data)
async def answer_to_sprav(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        call_data = call.data.split('_')[1]
        db = await collection.find_one({'_id': ObjectId('64987b1eeed9918b13b0e8b4')})
        sprav_indx = await get_spravkas_dict_index(call_data)
        if sprav_indx == None: return call.answer()
        text = 'ℹ Информации нет'
        if db['spravka'][sprav_indx]['info'] != 'None': text = db['spravka'][sprav_indx]['info']
        msg_del = await bot.send_message(chat_id=call.message.chat.id, text=text)
        await call.answer()
        asyncio.create_task(delete_message(40, [msg_del.message_id], msg_del.chat.id))
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

# СТАРЫЕ ПУНКТЫ
@dp.callback_query_handler(lambda call: call.data == 'back_to_my_profil')
@dp.callback_query_handler(lambda call: call.data == 'my_profile')
async def show_profile(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        await show_start(call)
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'back_to_main_page')
async def show_start(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        db = await collection.find_one({"user_id": call.from_user.id})
        if len(db['chats']) >= 1:
            lic = 'Лицензии нет'
            if db['lic'] != 'None': lic = db['lic']
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'👤 Ваш профиль:\n\n<b>Пользователь:</b> #{db["inlineid"]} - {db["register_data"]}\n<b>Username:</b> @{call.from_user.username}\n<b>Имя:</b> {call.from_user.first_name}\n<b>Чатов:</b> {len(db["chats"])}\n<b>Лицензий:</b> {db["lic"]}',
                reply_markup=await generate_add_button(), disable_web_page_preview=True)
        else:
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=t_start_text.format(bot_user=t_bot_user),
                reply_markup=await generate_add_button(), disable_web_page_preview=True)
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'chat_users_info')
async def answer_to_chat_users_info(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"chats": group_id})
        index_of_chat = await get_dict_index(db, group_id)
        deleted_acc = 0
        with_sym = 0
        nonactive_7 = 0
        nonactive_14 = 0
        nonactive_30 = 0
        nonactive_60 = 0
        for user in db['settings'][index_of_chat]['users']:
            try:
                user_info = await bot.get_chat(user['id'])
                if await contains_syms(user_info.first_name, db['settings'][index_of_chat]['blocked_syms']) == True or await contains_syms(user_info.last_name, db['settings'][index_of_chat]['blocked_syms']) == True:
                    with_sym += 1
            except ChatNotFound:
                deleted_acc += 1
                continue
            if user['l_msg'] == 'None': continue
            if await days_since_unix_time(user['l_msg']) > 60:
                nonactive_60 += 1
            elif await days_since_unix_time(user['l_msg']) > 30 and await days_since_unix_time(user['l_msg']) < 60:
                nonactive_30 += 1
            elif await days_since_unix_time(user['l_msg']) > 14 and await days_since_unix_time(user['l_msg']) < 30:
                nonactive_14 += 1
            elif await days_since_unix_time(user['l_msg']) > 7 and await days_since_unix_time(user['l_msg']) < 14:
                nonactive_7 += 1

        try:
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n⏰ Последние данные от {await get_msk_time()}\n\n<b>Статистика участников чата:</b>\n<b>Удаленныйх акаунтов:</b> {deleted_acc} участников\n<b>Участники с фильт-символами:</b> {with_sym} участников\n\n<b>Категории не активности:</b>\n<b>Не активны более 7 дней:</b> {nonactive_7} участников\n<b>Не активны более 14 дней:</b> {nonactive_14} участников\n<b>Не активны более 30 дней:</b> {nonactive_30} участников\n<b>Не активны более 60 дней:</b> {nonactive_60} участников\n', reply_markup=await generaate_users_toda_actions())
        except MessageNotModified:
            await call.answer('Актуально')

    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'update_usersgstat')
async def answer_update_usersgstat(call: CallbackQuery):
    try:
        await answer_to_chat_users_info(call)
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'back_from_block_syms')
async def answer_back_from_block_syms(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        await answer_to_chat_users_info(call)
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'filter_show')
async def answer_to_filter_show(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"chats": group_id})
        index_of_chat = await get_dict_index(db, group_id)
        list = 'Нету'
        if len(db['settings'][index_of_chat]['blocked_syms']) != 0: list = ', '.join(db['settings'][index_of_chat]['blocked_syms'])
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Ваш список символов:</b>\n{list}\n\n<b>Выберите действие:</b>',
                                    reply_markup=await generate_add_b_syms())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'add_block_sym')
async def answer_to_add_block_sym(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        quatbakc = await bot.send_message(chat_id=call.message.chat.id, text='📝 Введите символы, текста, эмодзи которых хотите заблокировать через запятую:', reply_markup=await generate_back_addsyms())
        await MySceneStates.blocked_syms_add.set()
        await collection.find_one_and_update({"user_id": call.from_user.id}, {'$set': {"chat_editing": group_id, "quatback": quatbakc.message_id}})
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'remove_block_sym')
async def answer_to_rem_block_sym(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"chats": group_id})
        index_of_chat = await get_dict_index(db, group_id)
        list = 'Нету'
        if len(db['settings'][index_of_chat]['blocked_syms']) != 0: list = ', '.join(
            db['settings'][index_of_chat]['blocked_syms'])
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        quatbakc = await bot.send_message(chat_id=call.message.chat.id, text=f'📝 Введите символы, текста, эмодзи которых хотите удалить из вашего списка через запятую\n\nВаш список: {list}', reply_markup=await generate_back_removesyms())
        await MySceneStates.blocked_syms_remove.set()
        await collection.find_one_and_update({"user_id": call.from_user.id}, {'$set': {"chat_editing": group_id, "quatback": quatbakc.message_id}})
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'back_from_deletion')
async def answer_to_back_from_deletion(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        await answer_to_chat_users_info(call)
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'back_from_cat_chose')
async def answer_to_back_from_cat_chose(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        await answer_to_chat_users_info(call)
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: 'category' in call.data)
async def answer_to_catgory(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"chats": group_id})
        index_of_chat = await get_dict_index(db, group_id)
        data = call.data.split('_')[1]
        if data == 'deleted':
            await collection.find_one_and_update({"chats": group_id}, {"$set": {"category": 'deleted'}})
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nВыберите % удаления:', reply_markup=await generaate_delete_percent())
        elif data == 'symbol':
            await collection.find_one_and_update({"chats": group_id}, {"$set": {"category": 'symbol'}})
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nВыберите % удаления:', reply_markup=await generaate_delete_percent())
        elif data == '7':
            await collection.find_one_and_update({"chats": group_id}, {"$set": {"category": '7'}})
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nВыберите % удаления:', reply_markup=await generaate_delete_percent())
        elif data == '14':
            await collection.find_one_and_update({"chats": group_id}, {"$set": {"category": '14'}})
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nВыберите % удаления:', reply_markup=await generaate_delete_percent())
        elif data == '30':
            await collection.find_one_and_update({"chats": group_id}, {"$set": {"category": '30'}})
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nВыберите % удаления:', reply_markup=await generaate_delete_percent())
        elif data == '60':
            await collection.find_one_and_update({"chats": group_id}, {"$set": {"category": '60'}})
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nВыберите % удаления:', reply_markup=await generaate_delete_percent())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: 'catdelete' in call.data)
async def answer_to_catdelete_percentage(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"chats": group_id})
        index_of_chat = await get_dict_index(db, group_id)
        data = call.data.split('_')[1]
        users_syms = []
        users_deleted = []
        users_7 = []
        users_14 = []
        users_30 = []
        users_60 = []

        msg = await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nИдет удаление...')
        for user in db['settings'][index_of_chat]['users']:
            try:
                user_info = await bot.get_chat(user['id'])
                if await contains_external_links(user_info.first_name, db['settings'][index_of_chat]['blocked_syms']) == True or await contains_external_links(user_info.last_name, db['settings'][index_of_chat]['blocked_syms']) == True:
                    users_syms.append(user['id'])
            except ChatNotFound:
                users_deleted.append(user['id'])
                return
            if await days_since_unix_time(user['l_msg']) > 60:
                users_60.append(user['id'])
            elif await days_since_unix_time(user['l_msg']) > 30 and await days_since_unix_time(user['l_msg']) < 60:
                users_30.append(user['id'])
            elif await days_since_unix_time(user['l_msg']) > 14 and await days_since_unix_time(user['l_msg']) < 30:
                users_14.append(user['id'])
            elif await days_since_unix_time(user['l_msg']) > 7 and await days_since_unix_time(user['l_msg']) < 14:
                users_7.append(user['id'])

        if db['category'] == 'deleted':
            if len(users_deleted) == 0: return await bot.edit_message_text(chat_id=call.message.chat.id,
                                                                     message_id=msg.message_id,
                                                                     text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nУдалены <b>0</b> участников чата ✅', reply_markup=await generaate_back_from_deletion())
            count_to_delete = (int(data) * len(users_deleted)) // 100
            arr_with_users = await trim_array(users_deleted, count_to_delete)
            for i in arr_with_users:
                try:
                    await bot.kick_chat_member(chat_id=group_id, user_id=i)
                    await bot.unban_chat_member(chat_id=group_id, user_id=i)
                    index_of_user = await get_chat_user_dict_index(db, i, index_of_chat)
                    await collection.find_one_and_update({'chats': group_id},
                                                   {"$pull": {f'settings.{index_of_chat}.users.{index_of_user}.id': i}})
                except CantRestrictChatOwner:
                    continue
                except Exception as e:
                    traceback.print_exc()
                    asyncio.create_task(send_error_log(traceback.format_exc()))
            return await bot.edit_message_text(chat_id=call.message.chat.id,
                                         message_id=msg.message_id,
                                         text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nУдалены <b>{len(arr_with_users)}</b> участников чата ✅', reply_markup=await generaate_back_from_deletion())
        elif db['category'] == 'symbol':
            if len(users_syms) == 0: return await bot.edit_message_text(chat_id=call.message.chat.id,
                                                                     message_id=msg.message_id,
                                                                     text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nУдалены <b>0</b> участников чата ✅', reply_markup=await generaate_back_from_deletion())
            count_to_delete = (int(data) * len(users_syms)) // 100
            arr_with_users = await trim_array(users_syms, count_to_delete)
            for i in arr_with_users:
                try:
                    await bot.kick_chat_member(chat_id=group_id, user_id=i)
                    await bot.unban_chat_member(chat_id=group_id, user_id=i)
                    index_of_user = await get_chat_user_dict_index(db, i, index_of_chat)
                    await collection.find_one_and_update({'chats': group_id},
                                                   {"$pull": {f'settings.{index_of_chat}.users.{index_of_user}.id': i}})
                except CantRestrictChatOwner:
                    continue
                except Exception as e:
                    traceback.print_exc()
                    asyncio.create_task(send_error_log(traceback.format_exc()))
            return await bot.edit_message_text(chat_id=call.message.chat.id,
                                         message_id=msg.message_id,
                                         text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nУдалены <b>{len(arr_with_users)}</b> участников чата ✅',
                                         reply_markup=await generaate_back_from_deletion())
        elif db['category'] == '7':
            if len(users_7) == 0: return await bot.edit_message_text(chat_id=call.message.chat.id,
                                                                     message_id=msg.message_id,
                                                                     text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nУдалены <b>0</b> участников чата ✅', reply_markup=await generaate_back_from_deletion())
            count_to_delete = (int(data) * len(users_7)) // 100
            arr_with_users = await trim_array(users_7, count_to_delete)
            for i in arr_with_users:
                try:
                    await bot.kick_chat_member(chat_id=group_id, user_id=i)
                    await bot.unban_chat_member(chat_id=group_id, user_id=i)
                    index_of_user = await get_chat_user_dict_index(db, i, index_of_chat)
                    await collection.find_one_and_update({'chats': group_id},
                                                   {"$pull": {f'settings.{index_of_chat}.users.{index_of_user}.id': i}})
                except CantRestrictChatOwner:
                    continue
                except Exception as e:
                    traceback.print_exc()
                    asyncio.create_task(send_error_log(traceback.format_exc()))
            return await bot.edit_message_text(chat_id=call.message.chat.id,
                                         message_id=msg.message_id,
                                         text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nУдалены <b>{len(arr_with_users)}</b> участников чата ✅',
                                         reply_markup=await generaate_back_from_deletion())
        elif db['category'] == '14':
            if len(users_14) == 0: return await bot.edit_message_text(chat_id=call.message.chat.id,
                                                                     message_id=msg.message_id,
                                                                     text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nУдалены <b>0</b> участников чата ✅', reply_markup=await generaate_back_from_deletion())
            count_to_delete = (int(data) * len(users_14)) // 100
            arr_with_users = await trim_array(users_14, count_to_delete)
            for i in arr_with_users:
                try:
                    await bot.kick_chat_member(chat_id=group_id, user_id=i)
                    await bot.unban_chat_member(chat_id=group_id, user_id=i)
                    index_of_user = await get_chat_user_dict_index(db, i, index_of_chat)
                    await collection.find_one_and_update({'chats': group_id},
                                                   {"$pull": {f'settings.{index_of_chat}.users.{index_of_user}.id': i}})
                except CantRestrictChatOwner:
                    continue
                except Exception as e:
                    traceback.print_exc()
                    asyncio.create_task(send_error_log(traceback.format_exc()))
            return await bot.edit_message_text(chat_id=call.message.chat.id,
                                         message_id=msg.message_id,
                                         text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nУдалены <b>{len(arr_with_users)}</b> участников чата ✅',
                                         reply_markup=await generaate_back_from_deletion())
        elif db['category'] == '30':
            if len(users_30) == 0: return await bot.edit_message_text(chat_id=call.message.chat.id,
                                                                     message_id=msg.message_id,
                                                                     text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nУдалены <b>0</b> участников чата ✅', reply_markup=await generaate_back_from_deletion())
            count_to_delete = (int(data) * len(users_30)) // 100
            arr_with_users = await trim_array(users_30, count_to_delete)
            for i in arr_with_users:
                try:
                    await bot.kick_chat_member(chat_id=group_id, user_id=i)
                    await bot.unban_chat_member(chat_id=group_id, user_id=i)
                    index_of_user = await get_chat_user_dict_index(db, i, index_of_chat)
                    await collection.find_one_and_update({'chats': group_id},
                                                   {"$pull": {f'settings.{index_of_chat}.users.{index_of_user}.id': i}})
                except CantRestrictChatOwner:
                    continue
                except Exception as e:
                    traceback.print_exc()
                    asyncio.create_task(send_error_log(traceback.format_exc()))
            return await bot.edit_message_text(chat_id=call.message.chat.id,
                                         message_id=msg.message_id,
                                         text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nУдалены <b>{len(arr_with_users)}</b> участников чата ✅',
                                         reply_markup=await generaate_back_from_deletion())
        elif db['category'] == '60':
            if len(users_60) == 0: return await bot.edit_message_text(chat_id=call.message.chat.id,
                                                                     message_id=msg.message_id,
                                                                     text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nУдалены <b>0</b> участников чата ✅', reply_markup=await generaate_back_from_deletion())
            count_to_delete = (int(data) * len(users_60)) // 100
            arr_with_users = await trim_array(users_60, count_to_delete)
            for i in arr_with_users:
                try:
                    await bot.kick_chat_member(chat_id=group_id, user_id=i)
                    await bot.unban_chat_member(chat_id=group_id, user_id=i)
                    index_of_user = await get_chat_user_dict_index(db, i, index_of_chat)
                    await collection.find_one_and_update({'chats': group_id}, {"$pull": {f'settings.{index_of_chat}.users.{index_of_user}.id': i}})
                except CantRestrictChatOwner:
                    continue
                except Exception as e:
                    traceback.print_exc()
                    asyncio.create_task(send_error_log(traceback.format_exc()))

            return await bot.edit_message_text(chat_id=call.message.chat.id,
                                         message_id=msg.message_id,
                                         text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\nУдалены <b>{len(arr_with_users)}</b> участников чата ✅',
                                         reply_markup=await generaate_back_from_deletion())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'back_from_percent')
async def answer_to_back_from_percent(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        await answer_to_delete_users_from_cat(call)
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'delete_users_from_cat')
async def answer_to_delete_users_from_cat(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        db = await collection.find_one({"chats": group_id})
        index_of_chat = await get_dict_index(db, group_id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id))}\n\n<b>Выберите категорию с которой хотите удалить участников:</b>', reply_markup=await generaate_users_toda_categories())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'next_page')
async def react_to_next_page(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        db = await collection.find_one({"user_id": call.from_user.id})
        current_page = db['current_pg'] + 1
        await collection.find_one_and_update({"user_id": call.from_user.id}, {'$set': {'current_pg': current_page}})

        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='🛢️ Выберите чат для настройки:', reply_markup=await generate_my_chats(current_page=current_page, user_id=db["user_id"]))
        await call.answer()
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'prev_page')
async def react_to_prev_page(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        db = await collection.find_one({"user_id": call.from_user.id})
        current_page = db['current_pg'] - 1
        await collection.find_one_and_update({"user_id": call.from_user.id}, {'$set': {'current_pg': current_page}})

        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='🛢️ Выберите чат для настройки:', reply_markup=await generate_my_chats(current_page=current_page, user_id=db["user_id"]))
        await call.answer()
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: 'schat' in call.data)
async def react_to_settings_chats(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        chat_id = call.data.split('_')[1]
        db = await collection.find_one({'chats': chat_id})
        index_of_chat = await get_dict_index(db, chat_id)
        if db['settings'][index_of_chat]['lic'] == True: return await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=t_settings.format(group_id=chat_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(chat_id)),
                         reply_markup=await generate_settings(True))
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=t_settings.format(group_id=chat_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(chat_id)),
                         reply_markup=await generate_settings())
        await call.answer()
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'donate')
async def answer_to_donate(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        quatback = await bot.send_message(chat_id=call.message.chat.id, text='🪙 Введите сумму доната:', reply_markup=await generate_back_donatemoney())
        await collection.find_one_and_update({"user_id": call.from_user.id}, {"$set": {"quatback": quatback.message_id}})
        await MySceneStates.donate_money_scene.set()
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'back_from_donate_method')
async def answer_to_back_from_donate_method(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        await show_start(call)
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: 'donpay' in call.data)
async def react_to_donpay(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        db = await collection.find_one({"user_id": call.from_user.id})
        float_amount =float(db['donate_money']) / 100
        if call.data.split('_')[1] == 'yoomoney':
            amount = db['donate_money']
            product = LabeledPrice(label='Product', amount=amount)
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            await bot.send_invoice(
                chat_id=call.message.chat.id,
                title=f'Помощь в развитии',
                description=f'Оказывая финансовую поддержку нашему проекту, Вы вносите непосредственный вклад в их развитие. Спасибо!',
                payload=f"d_{float_amount}",
                provider_token=config['PROVIDER'],
                currency='RUB',
                prices=[product],
                start_parameter=call.from_user.id,
                is_flexible=False,
                protect_content=True,
                reply_markup=await generate_donate_payment_button()
            )
            await call.answer()
        else:
            amount = float_amount
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            await bot.send_message(call.message.chat.id, text=f'💳 Ручная оплата:\n\nОплатите <b>{amount}₽</b> по реквизитам 👇\n\n<b>{config["TYPE"]}</b>\n<code>{config["CARD_NUMBER"]}</code>\n<b>{config["CARD_OWNER"]}</b>', reply_markup=await generate_dmanual_payment())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: 'dmanul' in call.data)
async def answer_to_dmanul(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        if call.data.split('_')[1] == 'back':
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                   text=f'💸 <b>Выберите способ оплаты:</b>',
                                   reply_markup=await generate_dpayment_method())
        else:
            await call.answer('Спасибо за оплату 😊')
            await show_start(call)
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'back_to_settings')
async def react_to_back_to_settings(call: CallbackQuery):
    if await blocked(call.from_user.id):
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
    group_id_url = call.message.entities[0].url
    group_id = "-" + re.sub(r"\D", "", group_id_url)
    if await is_chat_in(group_id) == False:
        await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
        return await show_start(call)
    db = await collection.find_one({"chats": group_id})
    index_of_chat = await get_dict_index(db, group_id)
    if db['settings'][index_of_chat]['lic'] == True: return await bot.edit_message_text(text=t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id)), message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=await generate_settings(lic=True))
    await bot.edit_message_text(text=t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id)), message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=await generate_settings())


# MANUAL ACCEPTION:
@dp.callback_query_handler(lambda call: 'mmpay' in call.data)
async def answer_to_mpayq(call: CallbackQuery):
    try:
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        call_data = call.data.split('_')[1]
        db = await collection.find_one({"settings": {"$elemMatch": {'chat_id': group_id}}})
        index_of_chat = await get_dict_index(db, group_id)
        if call_data == 'acadmin':
            adb = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
            liccount = db['lic'] + 1
            liccountgeneral = adb['lics_buyed'] + 1
            alics = adb['active_lic'] + 1
            price_indx = get_price_index(db['priceq'])
            price = adb['price'][price_indx]['price']
            earned = adb['earned'] + price
            enddate = await calculate_end_date(int(db['priceq']))
            current_datetime = datetime.now(pytz.utc)
            moscow_tz = pytz.timezone('Europe/Moscow')
            current_datetime_moscow = current_datetime.astimezone(moscow_tz)
            formatted_datetime = current_datetime_moscow.strftime("%H:%M %d.%m.%Y")
            await collection.find_one_and_update({"user_id": db['user_id']}, {
                "$set": {"lic": liccount, f"settings.{index_of_chat}.lic": True,
                         f"settings.{index_of_chat}.lic_end": [enddate[0], enddate[1], db['priceq']],
                         f"settings.{index_of_chat}.lic_buyed_date": formatted_datetime, "manual_msg": False, "manual_s": False}})
            await collection.find_one_and_update({"_id": ObjectId('64987b1eeed9918b13b0e8b4')}, {
                "$set": {"lics_buyed": liccountgeneral, "earned": earned, "active_lic": alics},
                "$push": {"chat_with_lics": group_id}})
            await bot.send_message(chat_id=db['user_id'], text=f'🟢 Лицензии продлена до: {enddate[0]}\n\nОстались вопросы? - пишите 👉🏻 {t_admin_user}')
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

            user = 'Пользователь заблокировал бота'
            username = '@NONE'
            fist_name = 'Неизвестно'
            try:
                user = await bot.get_chat(db['user_id'])
                if user.username: username = f"@{user.username}"
                fist_name = user.first_name
            except Exception as e:
                traceback.print_exc()
                asyncio.create_task(send_error_log(traceback.format_exc()))

            return await collection.find_one_and_update({"_id": ObjectId('64987b1eeed9918b13b0e8b4')}, {"$push": {'licsbuyedinfos': {'info': f'[{await get_msk_time()}](#{db["inlineid"]} | {username}) {fist_name}  -  купил лицензию {db["priceq"]} дней за {price}₽ ({config["TYPE"]})', 'indx': len(adb['licsbuyedinfos'])}}})
        else:
            await collection.find_one_and_update({'user_id': db['user_id']}, {"$set": {"manual_msg": False, "manual_s": False}})
            await call.answer('Уведомляю...')
            await bot.send_message(chat_id=db['user_id'], text=f'🔴 Ваш перевод не получен...\n\nК сожалению ваша оплата не прошла проверку...\n\n❗ Если вы считаете это ошибкой, напишите: {t_admin_user}')
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.callback_query_handler(lambda call: call.data == 'money_top_up')
async def react_to_money_top_up(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        db = await collection.find_one({"user_id": call.from_user.id})
        if db['manual_msg'] == True or db['manual_s'] == True:
            if db['manual_s'] == True:
                return await call.answer('✋ Ваша заявка на проверке', show_alert=True)
            return await call.answer('❗ Вы не можете оплачивать лицензию одновременно с другой', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        index_of_chat = await get_dict_index(db, group_id)
        if db['settings'][index_of_chat]['lic'] == True: return await bot.edit_message_text(text=t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id)), chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await generate_settings(lic=True))
        db = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
        prices = ''
        unsortedp = db['price']
        positions = sorted(unsortedp, key=lambda x: int(x['period']))
        for i in positions:
            prices += f'💎 {i["period"]} дней – {i["price"]}₽\n'
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<a href="https://{group_id}.id">🛒</a> <b>Прайс-лист лицензий:</b>\n{prices}', reply_markup=await generate_payment_page())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: 'buy' in call.data)
async def react_to_buy(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        db = await collection.find_one({"user_id": call.from_user.id})
        if db['manual_msg'] == True or db['manual_s'] == True:
            if db['manual_s'] == True:
                await call.answer('✋ Ваша заявка на проверке', show_alert=True)
                return await react_to_back_to_settings(call)
            await call.answer('❗ Вы не можете оплачивать лицензию одновременно с другой',
                show_alert=True)
            return await react_to_back_to_settings(call)

        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        index_of_chat = await get_dict_index(db, group_id)
        if db['settings'][index_of_chat]['lic'] == True: return await bot.edit_message_text(
            text=t_settings.format(group_id=group_id, bot_user=t_bot_user,
                                   upd_time=await update_time(db["settings"][index_of_chat]["updated_date"])),
            chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await generate_settings(lic=True))
        await collection.find_one_and_update({"user_id": call.from_user.id}, {"$set": {"priceq": call.data.split('_')[1]}})
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<a href="https://{group_id}.id">💸</a> <b>Выберите способ оплаты:</b>', reply_markup=await generate_payment_method())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: call.data == 'lic_info')
async def answer_to_lic_info(call: CallbackQuery):
    if await blocked(call.from_user.id):
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
    group_id_url = call.message.entities[0].url
    group_id = "-" + re.sub(r"\D", "", group_id_url)
    if await is_chat_in(group_id) == False:
        await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
        return await show_start(call)
    db = await collection.find_one({"chats": group_id})
    index_of_chat = await get_dict_index(db, group_id)
    if db['settings'][index_of_chat]['lic'] == False:
        await call.answer('ℹ У вас нет лицензии на данный чат или срок действия лицензии истек', show_alert=True)
        return await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=await generate_settings())
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<a href="https://{group_id}.id">💎</a> <b>Информация о лицензии:</b>\n\n<b>Дата приобретения</b>: {db["settings"][index_of_chat]["lic_buyed_date"]}\n<b>Срок действия лицензии</b>: до {db["settings"][index_of_chat]["lic_end"][0]}\n<b>Приобретенный срок:</b> {db["settings"][index_of_chat]["lic_end"][2]} дней', reply_markup=await generate_back_to_settings())

# ОПЛАТА
@dp.callback_query_handler(lambda call: 'pay' in call.data)
async def react_to_pay(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        db = await collection.find_one({"user_id": call.from_user.id})
        if db['manual_msg'] == True or db['manual_s'] == True:
            if db['manual_s'] == True:
                await call.answer('✋ Ваша заявка на проверке', show_alert=True)
                await react_to_back_to_settings(call)
            await call.answer('❗ Вы не можете оплачивать лицензию одновременно с другой', show_alert=True)
            return await react_to_back_to_settings(call)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if await is_chat_in(group_id) == False:
            await call.answer('✋ Извините, я потерял доступ к данному чату', show_alert=True)
            return await show_start(call)
        index_of_chat = await get_dict_index(db, group_id)
        if db['settings'][index_of_chat]['lic'] == True: return await bot.edit_message_text(
            text=t_settings.format(group_id=group_id, bot_user=t_bot_user,
                                   upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id)),
            chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await generate_settings(lic=True))
        chat = await bot.get_chat(group_id)
        if call.data.split('_')[1] == 'yoomoney':
            # return await call.answer('Тут будет оплата invoke')
            db = await collection.find_one({"user_id": call.from_user.id})
            admindb = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
            priceindex = get_price_index(db['priceq'])
            amount = int(Decimal(str(admindb['price'][priceindex]['price'])) * 100)
            product = LabeledPrice(label='Product', amount=amount)
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            await bot.send_invoice(
                chat_id=call.message.chat.id,
                title=f'Лицензия на {db["priceq"]} дней | Л̶и̶м̶и̶т̶ы̶ ̶н̶а̶ ̶ч̶а̶т̶ - {chat.title}',
                description='Купив лицензию, вы сможете избавиться от лимитов на чат',
                payload=f"{db['priceq']}_{group_id}",
                provider_token=config['PROVIDER'],
                currency='RUB',
                prices=[product],
                start_parameter=call.from_user.id,
                is_flexible=False,
                protect_content=True
            )
            await call.answer()
        else:
            # return await call.answer('Пока не доступно 😶')
            db = await collection.find_one({"user_id": call.from_user.id})
            admindb = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
            priceindex = get_price_index(db['priceq'])
            amount = admindb['price'][priceindex]['price']
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            manual_comentidc = admindb['manual_comentid'] + 1
            await bot.send_message(call.message.chat.id, text=f'<a href="https://{group_id}.id">💳</a> Ручная оплата:\n\nОплатите <b>{amount}₽</b> по реквизитам 👇\n\n<b>{config["TYPE"]}</b>\n<code>{config["CARD_NUMBER"]}</code>\n<b>{config["CARD_OWNER"]}</b>\n\n❗ В КОМЕНТАРИЯХ УКАЖИТЕ НОМЕР: #{manual_comentidc}\n\nПосле перевода нажмите на кнопку "Я перевел"', reply_markup=await generate_manual_payment())
            await collection.find_one_and_update({"_id": ObjectId('64987b1eeed9918b13b0e8b4')}, {"$set": {"manual_comentid": manual_comentidc}})
            await collection.find_one_and_update({"user_id": call.from_user.id}, {"$set": {"manual_codeid": manual_comentidc, "manual_msg": True}})
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

@dp.callback_query_handler(lambda call: 'manualp' in call.data)
async def answer_to_manualp(call: CallbackQuery):
    try:
        if await blocked(call.from_user.id):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            return await call.answer('🔒 Извините, вы заблокированы', show_alert=True)
        group_id_url = call.message.entities[0].url
        group_id = "-" + re.sub(r"\D", "", group_id_url)
        if call.data.split('_')[1] == 'back':
            db = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
            prices = ''
            unsortedp = db['price']
            positions = sorted(unsortedp, key=lambda x: int(x['period']))
            for i in positions:
                prices += f'💎 {i["period"]} дней – {i["price"]}₽\n'
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=f'(<a href="https://{group_id}.id">🛒</a>) <b>Прайс-лист лицензий:</b>\n{prices}',
                                        reply_markup=await generate_payment_page())
            await collection.find_one_and_update({"user_id": call.from_user.id}, {"$set": {"manual_msg": False}})
        else:
            db = await collection.find_one_and_update({"user_id": call.from_user.id}, {"$set": {"manual_s": True}})
            adb = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
            priceindx = get_price_index(db['priceq'])
            group = await bot.get_chat(group_id)
            await bot.send_message(chat_id=config['MAIN_ADMIN_ID'], text=f'<a href="https://{group_id}.id">💳</a> <b>Новый запрос на проверку ручной оплаты:</b>\n\n<b>Лицензия для чата:</b> <a href="https://{group_id}.id">{group.title}</a>\n<b>Срок лицензии:</b> {db["priceq"]} дней\n<b>Цена лицензии:</b> {adb["price"][priceindx]["price"]}₽\n\n<b>Код который должен быть в коментариях:</b> <code>#{db["manual_codeid"]}</code>\n\n<b>Пользователь:</b> <a href="https://t.me/{call.from_user.username}">{call.from_user.first_name}</a>', disable_web_page_preview=True, disable_notification=False, reply_markup=await generate_manual_payment_admin_actions())
            await call.answer('Ваша заявка отправлена на проверку ✅')
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            index_of_chat = await get_dict_index(db, group_id)
            if db['settings'][index_of_chat]['lic'] == True: return await bot.edit_message_text(
                text=t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id)),
                message_id=call.message.message_id, chat_id=call.message.chat.id,
                reply_markup=await generate_settings(lic=True))
            await bot.send_message(text=t_settings.format(group_id=group_id, bot_user=t_bot_user, upd_time=await update_time(db["settings"][index_of_chat]["updated_date"]), chat_name=await get_chat_name(group_id)),
                                        chat_id=call.message.chat.id,
                                        reply_markup=await generate_settings())
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))


@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    trash = await bot.send_message(pre_checkout_query.from_user.id, '🔄️ Транскрипция...')
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True, error_message='Произошла ошибка при подтверждении транскрипции ⚠')
    await bot.delete_message(pre_checkout_query.from_user.id, trash.message_id)

@dp.message_handler(content_types=ContentTypes.SUCCESSFUL_PAYMENT)
async def process_successful_payment(ctx: Message):
    db = await collection.find_one({"user_id": ctx.from_user.id})
    if ctx.successful_payment.invoice_payload.split('_')[0] == 'd':
        adb = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
        earnup = float(ctx.successful_payment.total_amount) / 100
        earned = adb['earned'] + earnup
        await collection.find_one_and_update({"_id": ObjectId('64987b1eeed9918b13b0e8b4')},
                                       {"$set": {"earned": earned}})
        await ctx.answer(text=f"Успешная оплата ✅\n\nСпасибо вам огромное что остаетесь с нами! Мы благодарны вам и будем продвигать производительность и качество бота на большие высоты 😊", reply_markup=await generate_back_to_main())
        username = '@NONE'
        if ctx.from_user.username: username = f'@{ctx.from_user.username}'
        return await collection.find_one_and_update({"_id": ObjectId('64987b1eeed9918b13b0e8b4')}, {"$push": {'licsbuyedinfos': {'info': f'[{await get_msk_time()}](#{db["inlineid"]} | {username}) {ctx.from_user.first_name}  -  задонатил {earnup}₽ (ЮКасса)', 'indx': len(adb['licsbuyedinfos'])}}})
    index_of_chat = await get_dict_index(db, ctx.successful_payment.invoice_payload.split('_')[1])
    adb = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
    liccount = db['lic'] + 1
    liccountgeneral = adb['lics_buyed'] + 1
    alics = adb['active_lic'] + 1
    earnup = float(ctx.successful_payment.total_amount) / 100
    earned = adb['earned'] + earnup
    enddate = await calculate_end_date(int(ctx.successful_payment.invoice_payload.split('_')[0]))
    current_datetime = datetime.now(pytz.utc)
    moscow_tz = pytz.timezone('Europe/Moscow')
    current_datetime_moscow = current_datetime.astimezone(moscow_tz)
    formatted_datetime = current_datetime_moscow.strftime("%H:%M %d.%m.%Y")
    await collection.find_one_and_update({"user_id": ctx.from_user.id}, {"$set": {"lic": liccount, f"settings.{index_of_chat}.lic": True, f"settings.{index_of_chat}.lic_end": [enddate[0], enddate[1], ctx.successful_payment.invoice_payload.split('_')[0]], f"settings.{index_of_chat}.lic_buyed_date": formatted_datetime}})
    await collection.find_one_and_update({"_id": ObjectId('64987b1eeed9918b13b0e8b4')}, {"$set": {"lics_buyed": liccountgeneral, "earned": earned, "active_lic": alics}, "$push": {"chat_with_lics": ctx.successful_payment.invoice_payload.split('_')[1]}})
    await ctx.answer(f'😇 Свяжитесь с {t_admin_user}, если возникнут проблемы')
    chat = 'Ошибка при получении имени'
    try:
        chat = await bot.get_chat(chat_id=db['settings'][index_of_chat]['chat_id'])
    except Exception as e:
        traceback.print_exc()
        asyncio.create_task(send_error_log(traceback.format_exc()))

    await ctx.answer(text=f"Успешная оплата ✅\n\nИнформация о лицензии в настройках чата(<a href='https://{ctx.successful_payment.invoice_payload.split('_')[1]}.id'>{chat.title}</a>)", reply_markup=await generate_back_to_settings())
    username = '@NONE'
    if ctx.from_user.username: username = f'@{ctx.from_user.username}'
    await collection.find_one_and_update({"_id": ObjectId('64987b1eeed9918b13b0e8b4')}, {"$push": {'licsbuyedinfos': {'info': f'[{await get_msk_time()}](#{db["inlineid"]} | {username}) {ctx.from_user.first_name}  -  купил лицензию {ctx.successful_payment.invoice_payload.split("_")[0]} дней за {earnup}₽ (ЮКасса)', 'indx': len(adb['licsbuyedinfos'])}}})

