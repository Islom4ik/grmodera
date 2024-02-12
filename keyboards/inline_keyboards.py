# Встроенные кнопки под сообщения:
import time

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.exceptions import BotKicked, BotBlocked, ChatNotFound

import data.configs
from database.database import collection, ObjectId
from data.loader import bot, config
from data.configs import get_dict_index, shorten_text
from data.texts import t_bot_user, t_admin_user
import traceback

async def support():
    markup = InlineKeyboardMarkup()
    sup = InlineKeyboardButton('👤 Поддержка', url=f'https://t.me/{t_admin_user.replace("@", "")}')
    markup.add(sup)
    return markup

async def generate_add_button():
    markup = InlineKeyboardMarkup()
    add_bottogroup_btn = InlineKeyboardButton('➕ Добавить группу', url=f'https://t.me/{t_bot_user}?startgroup=true')
    my_groups_btn = InlineKeyboardButton('🗃️ Мои чаты', callback_data='show_my_chats')
    donate_btn = InlineKeyboardButton('💰 Поддержать донатом', callback_data='donate')
    markup.add(add_bottogroup_btn)
    markup.add(my_groups_btn)
    markup.add(donate_btn)
    return markup

async def generate_mychats_button():
    markup = InlineKeyboardMarkup()
    my_groups_btn = InlineKeyboardButton('🗃️ Мои чаты', callback_data='show_my_chats')
    markup.add(my_groups_btn)
    return markup


async def generate_settings_button(chat_id):
    markup = InlineKeyboardMarkup()
    settings_btn = InlineKeyboardButton('⚙ Настроить бота', url=f'https://t.me/{t_bot_user}?start=settings_{chat_id}')
    markup.add(settings_btn)
    return markup

async def generate_check_admin_rights():
    markup = InlineKeyboardMarkup()
    check_btn = InlineKeyboardButton('📃 Проверить права', callback_data='check_admingr')
    markup.add(check_btn)
    return markup

async def generate_rules_keyboard():
    markup = InlineKeyboardMarkup()
    rules_btn = InlineKeyboardButton('🪧 Правила чата', callback_data='rules')
    markup.add(rules_btn)
    return markup

async def generate_settings(lic=False):
    markup = InlineKeyboardMarkup()
    edit_texts_btn = InlineKeyboardButton('✍ Изменение текста', callback_data='settings_texts')
    edit_admin_btn = InlineKeyboardButton('🧑‍⚖ Настройки администрирования', callback_data='settings_admins')
    users_info_btn = InlineKeyboardButton('📊 Статистика участников', callback_data='chat_users_info')
    buy_lic_btn = InlineKeyboardButton('💎 Купить лицензию', callback_data='money_top_up')
    lic_info_btn = InlineKeyboardButton('ℹ Информация о лицензии', callback_data='lic_info')
    delete_bot_btn = InlineKeyboardButton('⛔ Удалить чат', callback_data='delete_chat_b')
    done_btn = InlineKeyboardButton('✅ Готово', callback_data='done_btn')
    markup.add(edit_admin_btn)
    markup.add(edit_texts_btn)
    markup.add(users_info_btn)
    if lic == False: markup.add(buy_lic_btn)
    else: markup.add(lic_info_btn)
    markup.add(delete_bot_btn)
    markup.add(done_btn)
    return markup

async def generate_edit_text_settings():
    markup = InlineKeyboardMarkup()
    texts_greeting_btn = InlineKeyboardButton('👋 Приветствие нового участника', callback_data='texts_greeting')
    show_rules = InlineKeyboardButton('🪧 Правила чата', callback_data='show_rules')
    warning_btn = InlineKeyboardButton('👮 Патруль', callback_data='show_warning')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_to_chose')
    markup.add(texts_greeting_btn)
    markup.add(show_rules)
    markup.add(warning_btn)
    markup.add(back_btn)
    return markup

async def generate_text_editing_page():
    markup = InlineKeyboardMarkup()
    edit_greeting_btn = InlineKeyboardButton('✍ Изменить текст приветствия', callback_data='edit_greeting')
    format_btn = InlineKeyboardButton('💬 Тэги', callback_data='formating')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_to_show_page')
    markup.add(edit_greeting_btn)
    markup.add(format_btn)
    markup.add(back_btn)
    return markup

async def generate_rules_editing_page():
    markup = InlineKeyboardMarkup()
    edit_rules_btn = InlineKeyboardButton('✍ Изменить правила', callback_data='edit_rules')
    format_btn = InlineKeyboardButton('💬 Тэги', callback_data='formating')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_to_show_page')
    markup.add(edit_rules_btn)
    markup.add(format_btn)
    markup.add(back_btn)
    return markup

async def generate_warning_editing_page():
    markup = InlineKeyboardMarkup()
    edit_banwarning_btn = InlineKeyboardButton('📝 Команда: /ban', callback_data='edit_banwarning')
    edit_kickwarning_btn = InlineKeyboardButton('📝 Команда: /kick', callback_data='edit_kickwarning')
    edit_unbantext_btn = InlineKeyboardButton('📝 Команда: /unban', callback_data='edit_unbantext')
    format_btn = InlineKeyboardButton('💬 Тэги', callback_data='formating')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_to_show_page')
    markup.add(edit_banwarning_btn)
    markup.add(edit_kickwarning_btn)
    markup.add(edit_unbantext_btn)
    markup.add(format_btn)
    markup.add(back_btn)
    return markup

async def generate_admins_settings():
    markup = InlineKeyboardMarkup()
    block_resources_show_btn = InlineKeyboardButton('🌐 Блок внешних ссылок', callback_data='block_resources_show')
    system_notice_show_btn = InlineKeyboardButton('📢 Удаление оповещений',
                                                  callback_data='system_notice_show')
    block_repostes_show_btn = InlineKeyboardButton('📩 Запрет репостов', callback_data='block_repostes_show')
    block_ping_show_btn = InlineKeyboardButton('🔕 Запрет пинга', callback_data='block_ping_show')
    format_btn = InlineKeyboardButton('💬 Тэги', callback_data='formating')
    vorchun_btn = InlineKeyboardButton('🗣️ Ворчун', callback_data='vorchun_show')
    msgfilter_btn = InlineKeyboardButton('💬 Фильтр сообщений', callback_data='msgfilter_show')
    nouser_btn = InlineKeyboardButton('🙈 Без имени', callback_data='noname_show')
    words_filter_btn = InlineKeyboardButton('🤬 Антимат', callback_data='words_filters_show')
    skromniy_btn = InlineKeyboardButton('😶 Гость', callback_data='skromniy_show')
    tixiychas_btn = InlineKeyboardButton('😴 Тихий час', callback_data='tixiychas_show')
    antiflud_btn = InlineKeyboardButton('🤫 Стоп флуд', callback_data='antiflud_show')
    nofile_btn = InlineKeyboardButton('📂 Нет файлам', callback_data='nofile_show')
    subscribe_btn = InlineKeyboardButton('❤ Подписать', callback_data='subscribe_show')
    remmessages_btn = InlineKeyboardButton('🚮 Удалить сообщения', callback_data='remmessages_show')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_to_chose')
    markup.add(block_resources_show_btn, system_notice_show_btn)
    markup.add(block_repostes_show_btn, format_btn)
    markup.add(block_ping_show_btn, vorchun_btn)
    markup.add(msgfilter_btn, nouser_btn)
    markup.add(words_filter_btn, skromniy_btn)
    markup.add(tixiychas_btn, antiflud_btn)
    markup.add(nofile_btn, subscribe_btn)
    markup.add(remmessages_btn)
    markup.add(back_btn)
    return markup

async def generaate_users_toda_actions():
    markup = InlineKeyboardMarkup()
    update = InlineKeyboardButton('🔄️ Обновить данные', callback_data='update_usersgstat')
    remove_btn = InlineKeyboardButton('🗑️ Удаление из категорий', callback_data='delete_users_from_cat')
    filter_show_btn = InlineKeyboardButton('🔣 Фильтр символов', callback_data='filter_show')
    info_btn = InlineKeyboardButton('ℹ Справка', callback_data='sprav_usersstat')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_to_chose')
    markup.add(update)
    markup.add(remove_btn, filter_show_btn)
    markup.add(info_btn)
    markup.add(back_btn)
    return markup

async def generate_remmessages_show(user_id):
    markup = InlineKeyboardMarkup()
    db = await collection.find_one({"user_id": user_id})
    daysint_btn = InlineKeyboardButton('За сутки', callback_data='rmmsgs_days')
    weekint_btn = InlineKeyboardButton('За неделю', callback_data='rmmsgs_week')
    monthint_btn = InlineKeyboardButton('За месяц', callback_data='rmmsgs_month')
    setint_btn = InlineKeyboardButton('Указать интервал', callback_data='rmmsgs_set')
    info_btn = InlineKeyboardButton('ℹ Справка', callback_data='sprav_remmessages')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_to_admin_page')
    markup.add(daysint_btn)
    markup.add(weekint_btn)
    markup.add(monthint_btn)
    markup.add(setint_btn)
    markup.add(info_btn)
    markup.add(back_btn)
    return markup

async def generate_remmessages_agreement():
    markup = InlineKeyboardMarkup()
    agree_btn = InlineKeyboardButton('Удалить 🚀', callback_data='remmessages_agreement')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_from_remagreement')
    markup.add(agree_btn)
    markup.add(back_btn)
    return markup

async def generate_skromniy_show(user_id, indxofchat):
    markup = InlineKeyboardMarkup()
    db = await collection.find_one({"user_id": user_id})
    status = '🔴 | Выключено'
    if db['settings'][indxofchat]['skromniy']['active'] == True: status = '🟢 | Включено'
    status_btn = InlineKeyboardButton(f'{status}', callback_data='activator_skromniy')
    time_btn = InlineKeyboardButton('⏳ Изменить таймер', callback_data='edit_skromniytimer')
    edittext_btn = InlineKeyboardButton('📝 Изменить текст', callback_data='edit_skromniyw')
    format_btn = InlineKeyboardButton('💬 Тэги', callback_data='formating')
    info_btn = InlineKeyboardButton('ℹ Справка', callback_data='sprav_skromniy')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_to_admin_page')
    markup.add(status_btn)
    markup.add(time_btn, edittext_btn)
    markup.add(format_btn)
    markup.add(info_btn)
    markup.add(back_btn)
    return markup

async def generate_nofile_show(user_id, indxofchat):
    markup = InlineKeyboardMarkup()
    db = await collection.find_one({"user_id": user_id})
    status = '🔴 | Выключено'
    if db['settings'][indxofchat]['nofile_show']['active'] == True: status = '🟢 | Включено'
    status_btn = InlineKeyboardButton(f'{status}', callback_data='activator_nofile')
    edit_btn = InlineKeyboardButton('📝 Изменить лимит', callback_data='edit_nofilelimit')
    info_btn = InlineKeyboardButton('ℹ Справка', callback_data='sprav_nofile')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_to_admin_page')
    markup.add(status_btn)
    markup.add(edit_btn)
    markup.add(info_btn)
    markup.add(back_btn)
    return markup

async def generate_subscribe_show(user_id, indxofchat):
    markup = InlineKeyboardMarkup()
    db = await collection.find_one({"user_id": user_id})
    status = '🔴 | Выключено'
    if db['settings'][indxofchat]['subscribe_show']['active'] == True: status = '🟢 | Включено'
    status_btn = InlineKeyboardButton(f'{status}', callback_data='activator_subscribe')
    add_btn = InlineKeyboardButton(f'➕ Добавить', callback_data='edit_subscribecadd')
    rem_btn = InlineKeyboardButton(f'➖ Удалить', callback_data='subscribecrem')
    edit_text = InlineKeyboardButton(text='📝 Изменить текст нарушения', callback_data=f'edit_subscrwarnedit')
    channels_btn = InlineKeyboardButton(f'🎡 Мои каналы', callback_data='subscribe_channels')
    paydialogue_btn = InlineKeyboardButton(f'🎤 Плати Говори', callback_data='paydialogue_show')
    info_btn = InlineKeyboardButton('ℹ Справка', callback_data='sprav_subscribe')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_to_admin_page')
    markup.add(status_btn)
    markup.add(channels_btn)
    markup.add(edit_text)
    markup.add(add_btn, rem_btn)
    markup.add(paydialogue_btn)
    markup.add(info_btn)
    markup.add(back_btn)
    return markup

async def generate_subscribe_channels(user_id, indxofchat):
    markup = InlineKeyboardMarkup()
    db = await collection.find_one({"user_id": user_id})
    channels_btns = []
    if len(db['settings'][indxofchat]['subscribe_show']['channels']) != 0:
        for i in db['settings'][indxofchat]['subscribe_show']['channels']:
            channel = ''
            try:
                channel = await bot.get_chat(i['id'])
            except:
                continue
            channels_btns.append(InlineKeyboardButton(f'🚀 {channel.title} - {await channel.get_members_count()} участников', callback_data=f'subchannel_{i["id"]}'))
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_from_subscribe_channels')
    markup.add(*channels_btns)
    markup.add(back_btn)
    return markup

async def generate_paydialogueuser_tarifs(chat_id):
    markup = InlineKeyboardMarkup(row_width=1)
    db = await collection.find_one({"chats": chat_id})
    index_of_chat = await get_dict_index(db, chat_id)
    tarif_btns = []
    for i in db['settings'][index_of_chat]['subscribe_show']['paydialogue']['tarif_plans']:
        tarif_btns.append(InlineKeyboardButton(text=f'{i["days"]} дней - {i["price"]} ₽', callback_data=f'paydialchutarif_{i["days"]}'))
    markup.add(*tarif_btns)
    return markup

async def generate_paydialogueuser_pmethod(chat_id):
    markup = InlineKeyboardMarkup(row_width=1)
    db = await collection.find_one({"chats": chat_id})
    index_of_chat = await get_dict_index(db, chat_id)
    tarif_btns = []
    for index, method in enumerate(db['settings'][index_of_chat]['subscribe_show']['paydialogue']['payment_methods']):
        tarif_btns.append(InlineKeyboardButton(text=method['payment_name'], callback_data=f'paydialbuy_{index}'))
    back_btn = InlineKeyboardButton(text=f'⏪ Назад', callback_data=f'back_from_paydialuser_pmethod')
    markup.add(*tarif_btns)
    markup.add(back_btn)
    return markup

async def generate_paydialogueuser_yoopay(url, amount):
    markup = InlineKeyboardMarkup(row_width=1)
    pay = InlineKeyboardButton(text=f'Оплатить {amount} ₽', web_app=WebAppInfo(url=url))
    check = InlineKeyboardButton(text=f'Проверить оплату', callback_data="baydyoo_check")
    back_btn = InlineKeyboardButton(text=f'⏪ Отмена', callback_data=f'cancbaydyoo')
    markup.add(pay)
    markup.add(check)
    markup.add(back_btn)
    return markup

async def generate_paydialogue_show(user_id, indxofchat):
    markup = InlineKeyboardMarkup()
    db = await collection.find_one({"user_id": user_id})
    status = '🔴 | Выключено'
    if db['settings'][indxofchat]['subscribe_show']['paydialogue']['active'] == True: status = '🟢 | Включено'
    activator = InlineKeyboardButton(text=status, callback_data=f'activator_paydialogue')
    add_tarifadd = InlineKeyboardButton(text='➕ Добавить тариф', callback_data=f'edit_paydialtarifadd')
    edit_text = InlineKeyboardButton(text='📝 Изменить текст нарушения', callback_data=f'edit_paydialtarifwarning')
    tarifs = InlineKeyboardButton(text='📦 Мои тарифы', callback_data=f'paydialtarifs')
    pay_methods = InlineKeyboardButton(text='💳 Реквизиты', callback_data=f'paydial_paymethodsshow')
    paydial_customers = InlineKeyboardButton(text='👤 Купили', callback_data=f'paydial_customers')
    paydial_give = InlineKeyboardButton(text='⚡ Ручная выдача', callback_data=f'paydial_giveperms')
    info_btn = InlineKeyboardButton('ℹ Справка', callback_data='sprav_paydialogue')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_from_paydialshow')
    markup.add(activator)
    markup.add(add_tarifadd)
    markup.add(edit_text)
    markup.add(tarifs, pay_methods)
    markup.add(paydial_customers)
    markup.add(paydial_give)
    markup.add(info_btn)
    markup.add(back_btn)
    return markup

async def generate_paydialogue_customers(requesting:bool, users=None, pagesc=None, page=None):
    try:
        markup = InlineKeyboardMarkup(row_width=1)
        back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_from_paydialcustomers')
        if requesting == True:
            markup.add(back_btn)
            return markup
        btns = []

        for i in users:
            status = '🟢'
            if await data.configs.get_msk_unix() >= i["end"][0]:
                status = '🔴'
            btns.append(InlineKeyboardButton(f'{status} / {i["un"]} / {i["end"][1]}', callback_data=f'paydialc_{i["ui"]}'))
        markup.add(*btns)
        prev_btn = InlineKeyboardButton('⬅', callback_data='paydialpagesc_prev')
        next_btn = InlineKeyboardButton('➡', callback_data='paydialpagesc_next')
        markup = InlineKeyboardMarkup(row_width=2, inline_keyboard=markup.inline_keyboard)
        markup.add(prev_btn, next_btn)
        markup.add(back_btn)
        return markup
    except Exception as e:
        traceback.print_exc()

async def generate_paydialoguepaydata_show(user_id, indxofchat):
    db = await collection.find_one({"user_id": user_id})
    markup = InlineKeyboardMarkup(row_width=1)
    payments_btns = []
    ind = 0
    for i in db['settings'][indxofchat]['subscribe_show']['paydialogue']['payment_methods']:
        payments_btns.append(InlineKeyboardButton(text=i['payment_name'], callback_data=f'paydialpm_{ind}'))
        ind += 1
    if len(payments_btns) > 7:
        markup = InlineKeyboardMarkup(row_width=2)

    add_paymethods = InlineKeyboardButton(text='➕ Добавить', callback_data=f'edit_paydialadd')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_from_paydialpaydata')
    markup.add(add_paymethods)
    markup.add(*payments_btns)
    markup.add(back_btn)
    return markup

async def generate_paydcustpage(user_id):
    markup = InlineKeyboardMarkup(row_width=1)
    delete_btn = InlineKeyboardButton('🗑️ Удалить', callback_data=f'pdcustpaged_{user_id}')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_from_backfrompaydicust')
    markup.add(delete_btn)
    markup.add(back_btn)
    return markup

async def generate_paydialoguetarifs_show(user_id, indxofchat):
    markup = InlineKeyboardMarkup(row_width=1)
    db = await collection.find_one({"user_id": user_id})
    tarifs_btns = []
    for i in db['settings'][indxofchat]['subscribe_show']['paydialogue']['tarif_plans']:
        tarifs_btns.append(InlineKeyboardButton(text=f'{i["days"]} дней - {i["price"]} ₽', callback_data=f'paydialtarifd_{i["days"]}'))
    if len(tarifs_btns) > 7:
        markup = InlineKeyboardMarkup(row_width=2)
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_from_paydialtarifs')
    markup.add(*tarifs_btns)
    markup.add(back_btn)
    return markup

async def generate_paydialoguepmethmanage():
    markup = InlineKeyboardMarkup()
    paymethods_addinf = InlineKeyboardButton(text='ℹ Добавить условия', callback_data=f'edit_paydialpayinfo')
    rem_paymethods = InlineKeyboardButton(text='🚮 Удалить метод', callback_data=f'paydialrem')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_from_paydialpaymeth')
    markup.add(paymethods_addinf)
    markup.add(rem_paymethods)
    markup.add(back_btn)
    return markup

async def generate_paydialoguetarifmanage():
    markup = InlineKeyboardMarkup()
    tarif_editdata = InlineKeyboardButton(text='📝 Изменить', callback_data=f'edit_paydialtarifdatas')
    rem_tarif = InlineKeyboardButton(text='🚮 Удалить тариф', callback_data=f'paydialremtarif')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_from_paydialtarif')
    markup.add(tarif_editdata)
    markup.add(rem_tarif)
    markup.add(back_btn)
    return markup

async def generate_subscribe_channelremover(user_id, indxofchat):
    markup = InlineKeyboardMarkup(row_width=2)
    db = await collection.find_one({"user_id": user_id})
    channels_btns = []
    if len(db['settings'][indxofchat]['subscribe_show']['channels']) != 0:
        for i in db['settings'][indxofchat]['subscribe_show']['channels']:
            channels_btns.append(InlineKeyboardButton(f'{i["title"]}', callback_data=f'remchannel_{i["id"]}'))
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_from_subscribe_channelremover')
    markup.add(*channels_btns)
    markup.add(back_btn)
    return markup

async def generate_back_paydialuserpay():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(text='⏪ Назад', callback_data='back_from_paydialuserpay'))
    return markup

async def generate_paydialuserpay_acchoice(user_id):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(text='✅ Потвердить', callback_data=f'transdial_{user_id}_a'), InlineKeyboardButton(text='❌ Отказ', callback_data=f'transdial_{user_id}_d'))
    return markup

async def generate_channels_tosbleft(channels: list, chat_id):
    markup = InlineKeyboardMarkup(row_width=1)
    channels_btns = []
    for i in channels:
        if i == 'bot':
            channels_btns.append(InlineKeyboardButton(f'GrModera - Бот администратор', url=f'https://t.me/{t_bot_user}'))
        elif i == 'paydialogue':
            channels_btns.append(InlineKeyboardButton(f'Оплатить доступ 💰', url=f'https://t.me/{t_bot_user}?start=paydial_{chat_id}'))
        else:
            channels_btns.append(InlineKeyboardButton(f'{i["title"]}', url=f'https://t.me/{i["user_name"]}'))
    markup.add(*channels_btns)
    return markup

async def generate_tixiychas_show(user_id, indxofchat):
    markup = InlineKeyboardMarkup()
    db = await collection.find_one({"user_id": user_id})
    status = '🔴 | Выключено'
    if db['settings'][indxofchat]['tixiychas']['active'] == True: status = '🟢 | Включено'
    status_btn = InlineKeyboardButton(f'{status}', callback_data='activator_tixiychas')
    time_btn = InlineKeyboardButton('➕ Добавить промежуток', callback_data='edit_tixiychast')
    time_del_btn = InlineKeyboardButton('🗑️ Удалить', callback_data='edit_deltixiychast')
    info_btn = InlineKeyboardButton('ℹ Справка', callback_data='sprav_tixiychas')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_to_admin_page')
    markup.add(status_btn)
    markup.add(time_btn, time_del_btn)
    markup.add(info_btn)
    markup.add(back_btn)
    return markup

async def generate_tixiychas_chose_days():
    markup = InlineKeyboardMarkup()
    ed = InlineKeyboardButton(f'Каждый день', callback_data='tixday_ed')
    wd = InlineKeyboardButton('В выходные', callback_data='tixday_wd')
    id = InlineKeyboardButton('В указанную дату', callback_data='tixday_id')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_from_tixiychas_chose_days')
    markup.add(ed)
    markup.add(wd)
    markup.add(id)
    markup.add(back_btn)
    return markup

async def generate_tixiychas_del_times(user_id, chat_id):
    markup = InlineKeyboardMarkup(row_width=1)
    user = await collection.find_one({"user_id": int(user_id)})
    index_of_chat = await get_dict_index(user, chat_id)
    btns = []
    if len(user['settings'][index_of_chat]['tixiychas']['timers']) != 0:
       for i in user['settings'][index_of_chat]['tixiychas']['timers']:
           btns.append(InlineKeyboardButton(f'{i["time"]}', callback_data=f'deltix_{i["time"]}'))
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_from_tixiychas_chose_days')
    markup.add(*btns)
    markup.add(back_btn)
    return markup

async def generate_msg_filters_btns(user_id, indxofchat):
    markup = InlineKeyboardMarkup()
    db = await collection.find_one({"user_id": user_id})
    italic = '🔴'
    bold = '🔴'
    caps = '🔴'
    if db['settings'][indxofchat]['msg_filter']['italic'] == True: italic = '🟢'
    if db['settings'][indxofchat]['msg_filter']['bold'] == True: bold = '🟢'
    if db['settings'][indxofchat]['msg_filter']['capslock'] == True: caps = '🟢'

    italic_btn = InlineKeyboardButton(f'{italic} | Italic', callback_data='activator_italic')
    bold_btn = InlineKeyboardButton(f'{bold} | Bold', callback_data='activator_bold')
    caps_btn = InlineKeyboardButton(f'{caps} | Caps Lock', callback_data='activator_caps')
    format_btn = InlineKeyboardButton('💬 Тэги', callback_data='formating')
    info_btn = InlineKeyboardButton('ℹ Справка', callback_data='sprav_msgfilters')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_from_msg_filters')
    markup.add(italic_btn, bold_btn)
    markup.add(caps_btn)
    markup.add(format_btn)
    markup.add(info_btn)
    markup.add(back_btn)
    return markup

async def generate_wordsfilter_show(user_id, indxofchat):
    markup = InlineKeyboardMarkup()
    db = await collection.find_one({"user_id": user_id})
    status = '🔴 | Выключено'
    if db['settings'][indxofchat]['msg_filter']['mfiltersa'] == True: status = '🟢 | Включено'

    status_btn = InlineKeyboardButton(f'{status} ', callback_data='activator_wordsfilter')
    add_btn = InlineKeyboardButton('➕ Добавить запрет', callback_data='wordsfilter_add')
    rem_btn = InlineKeyboardButton('🗑️ Удалить запрет', callback_data='wordsfilter_rem')
    wtext = InlineKeyboardButton('📝 Изменить текст нарушения', callback_data='edit_antimatw')
    format_btn = InlineKeyboardButton('💬 Тэги', callback_data='formating')
    info_btn = InlineKeyboardButton('ℹ Справка', callback_data='sprav_wordsfilter')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_from_wordsfilter_show')
    markup.add(status_btn)
    markup.add(add_btn, rem_btn)
    markup.add(wtext)
    markup.add(format_btn)
    markup.add(info_btn)
    markup.add(back_btn)
    return markup

async def generaate_back_from_deletion():
    markup = InlineKeyboardMarkup()
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_from_deletion')
    markup.add(back_btn)
    return markup

async def generaate_users_toda_categories():
    markup = InlineKeyboardMarkup()
    deleteds_btn = InlineKeyboardButton('👻 Удаленные аккаунты', callback_data='category_deleted')
    symbol_btn = InlineKeyboardButton('🔣 Участники попадающие под фильтр', callback_data='category_symbol')
    nonactive_7_btn = InlineKeyboardButton('🟠 Не активны более 7  д', callback_data='category_7')
    nonactive_14_btn = InlineKeyboardButton('🟠 Не активны более 14 д', callback_data='category_14')
    nonactive_30_btn = InlineKeyboardButton('🟠 Не активны более 30 д', callback_data='category_30')
    nonactive_60_btn = InlineKeyboardButton('🟠 Не активны более 60 д', callback_data='category_60')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_from_cat_chose')
    markup.add(deleteds_btn)
    markup.add(symbol_btn)
    markup.add(nonactive_7_btn)
    markup.add(nonactive_14_btn)
    markup.add(nonactive_30_btn)
    markup.add(nonactive_60_btn)
    markup.add(back_btn)
    return markup

async def generaate_delete_percent():
    markup = InlineKeyboardMarkup()
    delete_10_btn = InlineKeyboardButton('🔹 Удалить 10%', callback_data='catdelete_10')
    delete_20_btn = InlineKeyboardButton('🔹 Удалить 20%', callback_data='catdelete_20')
    delete_30_btn = InlineKeyboardButton('🔹 Удалить 30%', callback_data='catdelete_30')
    delete_40_btn = InlineKeyboardButton('🔹 Удалить 40%', callback_data='catdelete_40')
    delete_50_btn = InlineKeyboardButton('🔹 Удалить 50%', callback_data='catdelete_50')
    delete_100_btn = InlineKeyboardButton('💯 Удалить 100%', callback_data='catdelete_100')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_from_percent')
    markup.add(delete_10_btn)
    markup.add(delete_20_btn)
    markup.add(delete_30_btn)
    markup.add(delete_40_btn)
    markup.add(delete_50_btn)
    markup.add(delete_100_btn)
    markup.add(back_btn)
    return markup

async def generate_block_resources_show(user_id, chat_index):
    markup = InlineKeyboardMarkup()
    db = await collection.find_one({"user_id": user_id})
    status = '🔴 | Выключено'
    if db['settings'][chat_index]['block_resources']['active'] == True:
        status = '🟢 | Включено '

    activate_btn = InlineKeyboardButton(status, callback_data='activator_resources')
    blocked_resources_btn = InlineKeyboardButton('📋 Список ресурсов', callback_data='blocked_resources')
    edit_resourcesw_btn = InlineKeyboardButton('📝 Изменить текст', callback_data='edit_resourcesw')
    format_btn = InlineKeyboardButton('💬 Тэги', callback_data='formating')
    info_btn = InlineKeyboardButton('ℹ Справка', callback_data='sprav_bresources')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_to_admin_page')
    markup.add(activate_btn)
    markup.add(blocked_resources_btn)
    markup.add(edit_resourcesw_btn)
    markup.add(format_btn)
    markup.add(info_btn)
    markup.add(back_btn)
    return markup



async def generate_block_repostes_show(user_id, chat_index):
    markup = InlineKeyboardMarkup()
    db = await collection.find_one({"user_id": user_id})
    status = '🔴 | Выключено'
    if db['settings'][chat_index]['block_repostes']['active'] == True:
        status = '🟢 | Включено '

    activate_btn = InlineKeyboardButton(status, callback_data='activator_repostes')
    edit_repostesw_btn = InlineKeyboardButton('📝 Изменить текст', callback_data='edit_repostesw')
    format_btn = InlineKeyboardButton('💬 Тэги', callback_data='formating')
    info_btn = InlineKeyboardButton('ℹ Справка', callback_data='sprav_brepostes')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_to_admin_page')
    markup.add(activate_btn)
    markup.add(edit_repostesw_btn)
    markup.add(format_btn)
    markup.add(info_btn)
    markup.add(back_btn)
    return markup

async def generate_system_notice_show(user_id, chat_index):
    markup = InlineKeyboardMarkup()
    db = await collection.find_one({"user_id": user_id})
    status = '🔴 | Выключено'
    if db['settings'][chat_index]['system_notice']['active'] == True:
        status = '🟢 | Включено '

    activate_btn = InlineKeyboardButton(status, callback_data='activator_sysnot')
    format_btn = InlineKeyboardButton('💬 Тэги', callback_data='formating')
    info_btn = InlineKeyboardButton('ℹ Справка', callback_data='sprav_sysnot')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_to_admin_page')
    markup.add(activate_btn)
    markup.add(format_btn)
    markup.add(info_btn)
    markup.add(back_btn)
    return markup


async def generate_block_ping_show(user_id, chat_index):
    markup = InlineKeyboardMarkup()
    db = await collection.find_one({"user_id": user_id})
    status = '🔴 | Выключено'
    if db['settings'][chat_index]['block_ping']['active'] == True:
        status = '🟢 | Включено '

    activate_btn = InlineKeyboardButton(status, callback_data='activator_ping')
    edit_pingw_btn = InlineKeyboardButton('📝 Изменить текст нарушения', callback_data='edit_pingw')
    format_btn = InlineKeyboardButton('💬 Тэги', callback_data='formating')
    info_btn = InlineKeyboardButton('ℹ Справка', callback_data='sprav_bping')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_to_admin_page')
    markup.add(activate_btn)
    markup.add(edit_pingw_btn)
    markup.add(format_btn)
    markup.add(info_btn)
    markup.add(back_btn)
    return markup

async def generate_split_mention_show(user_id, chat_index):
    markup = InlineKeyboardMarkup()
    db = await collection.find_one({"user_id": user_id})
    status = '🔴 | Выключено'
    if db['settings'][chat_index]['block_ping']['s_m'] == True:
        status = '🟢 | Включено '

    activate_btn = InlineKeyboardButton(status, callback_data='activator_splitmention')
    info_btn = InlineKeyboardButton('ℹ Справка', callback_data='sprav_sm')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_from_split_mention')
    markup.add(activate_btn)
    markup.add(info_btn)
    markup.add(back_btn)
    return markup

async def generate_forbtoenter_show(user_id, chat_index):
    markup = InlineKeyboardMarkup()
    db = await collection.find_one({"user_id": user_id})
    status = '🔴 | Выключено'
    if db['settings'][chat_index]['block_ping']['forbtoenter'] == True:
        status = '🟢 | Включено '

    activate_btn = InlineKeyboardButton(status, callback_data='activator_forbtoenter')
    info_btn = InlineKeyboardButton('ℹ Справка', callback_data='sprav_forbtoenter')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_from_forbtoenter_show')
    markup.add(activate_btn)
    markup.add(info_btn)
    markup.add(back_btn)
    return markup

async def generate_antiflud_show(user_id, chat_index):
    markup = InlineKeyboardMarkup()
    db = await collection.find_one({"user_id": user_id})
    status = '🔴 | Выключено'
    if db['settings'][chat_index]['antiflud_block']['active'] == True:
        status = '🟢 | Включено '

    activate_btn = InlineKeyboardButton(status, callback_data='activator_antiflud')
    antifludw_btn = InlineKeyboardButton('📝 Изменить текст нарушения', callback_data='edit_antifludw')
    timer_btn = InlineKeyboardButton('⌚ Изменить задержку', callback_data='edit_antifludtimer')
    format_btn = InlineKeyboardButton('💬 Тэги', callback_data='formating')
    info_btn = InlineKeyboardButton('ℹ Справка', callback_data='sprav_antiflud')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_to_admin_page')
    markup.add(activate_btn)
    markup.add(antifludw_btn, timer_btn)
    markup.add(format_btn)
    markup.add(info_btn)
    markup.add(back_btn)
    return markup

async def generate_block_afk_show(user_id, chat_index):
    markup = InlineKeyboardMarkup()
    db = await collection.find_one({"user_id": user_id})
    status = '🔴 | Выключено'
    if db['settings'][chat_index]['afk']['active'] == True:
        status = '🟢 | Включено '

    activate_btn = InlineKeyboardButton(status, callback_data='activator_afk')
    edit_pingw_btn = InlineKeyboardButton('📝 Изменить текст', callback_data='edit_afkw')
    edit_media_btn = InlineKeyboardButton('📝 Изменить фото/видео', callback_data='edit_afkmedia')
    edit_time_btn = InlineKeyboardButton('⏳ Изменить таймер', callback_data='edit_afktimer')
    info_btn = InlineKeyboardButton('ℹ Справка', callback_data='sprav_vorchun')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_to_admin_page')
    markup.add(activate_btn)
    markup.add(edit_pingw_btn)
    markup.add(edit_media_btn)
    markup.add(edit_time_btn)
    markup.add(info_btn)
    markup.add(back_btn)
    return markup

async def generate_noname_show(user_id, chat_index):
    markup = InlineKeyboardMarkup()
    db = await collection.find_one({"user_id": user_id})
    status = '🔴 | Выключено'
    if db['settings'][chat_index]['noname'] == True:
        status = '🟢 | Включено '

    activate_btn = InlineKeyboardButton(status, callback_data='activator_noname')
    splitmention_show_btn = InlineKeyboardButton('🥷 @ username', callback_data='splitmention_show')
    # forbtoenter_show_btn = InlineKeyboardButton('✋ Вход запрещен', callback_data='forbtoenter_show')
    info_btn = InlineKeyboardButton('ℹ Справка', callback_data='sprav_noname')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_to_admin_page')
    markup.add(activate_btn)
    markup.add(splitmention_show_btn)
    markup.add(info_btn)
    markup.add(back_btn)
    return markup

async def generate_back_to_main():
    markup = InlineKeyboardMarkup()
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_to_main_page')
    markup.add(back_btn)
    return markup

async def generate_add_b_resources():
    markup = InlineKeyboardMarkup()
    add_btn = InlineKeyboardButton('➕ Добавить запрет', callback_data='add_block_resources')
    delete_btn = InlineKeyboardButton('🗑️ Удалить', callback_data='remove_block_resources')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_to_block_resources')
    markup.add(add_btn)
    markup.add(delete_btn)
    markup.add(back_btn)
    return markup

async def generate_add_b_syms():
    markup = InlineKeyboardMarkup()
    add_btn = InlineKeyboardButton('➕ Добавить фильтр', callback_data='add_block_sym')
    delete_btn = InlineKeyboardButton('🗑️ Удалить', callback_data='remove_block_sym')
    info_btn = InlineKeyboardButton('ℹ Справка', callback_data='sprav_filternames')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_from_block_syms')
    markup.add(add_btn, delete_btn)
    markup.add(info_btn)
    markup.add(back_btn)
    return markup

async def generate_my_chats(user_id, current_page=0, buttons_per_page=6):
    try:
        db = await collection.find_one({"user_id": user_id})
        inline_buttons = []
        for i in db['chats']:
            try:
                chat = await bot.get_chat(i)
                inline_buttons.append(InlineKeyboardButton(text=f'{chat.title}', callback_data=f'schat_{chat.id}'))
            except BotKicked:
                continue
            except:
                continue

        markup = ''
        if len(inline_buttons) != 0:
            pages = [inline_buttons[i:i + buttons_per_page] for i in range(0, len(inline_buttons), buttons_per_page)]
            current_page = current_page % len(pages)
            markup = InlineKeyboardMarkup().add(*pages[current_page])

            prev_btn = 'N'
            next_btn = 'N'
            if len(pages) > 1:
                if current_page > 0:
                    prev_btn = InlineKeyboardButton('◀ Назад', callback_data='prev_page')
                if current_page < len(pages) - 1:
                    next_btn = (InlineKeyboardButton('Вперед ▶', callback_data='next_page'))

            if next_btn != 'N' and prev_btn != 'N':
                markup.add(prev_btn, next_btn)
            elif next_btn != 'N':
                markup.add(next_btn)
            elif prev_btn != 'N':
                markup.add(prev_btn)

            markup.add(InlineKeyboardButton('⏪ Назад в меню', callback_data='back_to_main_page'))
        else:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('⏪ Назад в меню', callback_data='back_to_main_page'))

        return markup
    except Exception as e:
        traceback.print_exc()

async def generate_userstats_chats(user_id, current_page=0, buttons_per_page=6):
    try:
        db = await collection.find_one({"user_id": int(user_id)})
        inline_buttons = []
        for i in db['chats']:
            try:
                chat = await bot.get_chat(i)
                index_of_chat = await get_dict_index(db, chat.id)
                if db['settings'][index_of_chat]['lic'] == True:
                    inline_buttons.append(InlineKeyboardButton(text=f'💎 {chat.title}', callback_data=f'userstatschat_{chat.id}'))
                    continue
                inline_buttons.append(InlineKeyboardButton(text=f'{chat.title}', callback_data=f'userstatschat_{chat.id}'))
            except BotKicked:
                continue
            except:
                continue

        markup = ''
        if len(inline_buttons) != 0:
            pages = [inline_buttons[i:i + buttons_per_page] for i in range(0, len(inline_buttons), buttons_per_page)]
            current_page = current_page % len(pages)
            markup = InlineKeyboardMarkup().add(*pages[current_page])

            prev_btn = 'N'
            next_btn = 'N'
            if len(pages) > 1:
                if current_page > 0:
                    prev_btn = InlineKeyboardButton('◀ Назад', callback_data='usersstats_groups_prev')
                if current_page < len(pages) - 1:
                    next_btn = (InlineKeyboardButton('Вперед ▶', callback_data='usersstats_groups_next'))

            if next_btn != 'N' and prev_btn != 'N':
                markup.add(prev_btn, next_btn)
            elif next_btn != 'N':
                markup.add(next_btn)
            elif prev_btn != 'N':
                markup.add(prev_btn)

            markup.add(InlineKeyboardButton('⏪ Назад', callback_data='back_from_userstats_groups_chose'))
        else:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('⏪ Назад', callback_data='back_from_userstats_groups_chose'))

        return markup
    except Exception as e:
        traceback.print_exc()

async def generate_userschat_actions():
    markup = InlineKeyboardMarkup()
    licadd = InlineKeyboardButton('💎 Выдать лицензию', callback_data='lic_addparent')
    licren = InlineKeyboardButton('💎 Забрать лицензию', callback_data='lic_remparent')
    back = InlineKeyboardButton('⏪ Назад', callback_data='back_from_userschat_actions')
    markup.add(licadd)
    markup.add(licren)
    markup.add(back)
    return markup

async def generate_userschat_cancel_addparent():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='back_from_userschat_addparent')
    markup.add(back)
    return markup

async def generate_admin_main_page(id=0):
    markup = InlineKeyboardMarkup()
    stats_btn = InlineKeyboardButton('📊 Статистика бота 📊', callback_data='admin_bot_stats')
    edit_money_btn = InlineKeyboardButton('🪙 Изменить цены', callback_data='admin_edit_money')
    edit_limits_btn = InlineKeyboardButton('✋ Изменить лимиты', callback_data='admin_edit_limits')
    post_btn = InlineKeyboardButton('📢 Отправить сообщения всем', callback_data='admin_post')
    admins_manager = InlineKeyboardButton('👤 Управление доступом', callback_data='admins_manager')
    admins_spravkas = InlineKeyboardButton('ℹ Справки', callback_data='admins_spravkas')
    leave_admin_btn = InlineKeyboardButton('↩ Выйти с админки', callback_data='admin_exit')
    markup.add(stats_btn)
    markup.add(edit_money_btn, edit_limits_btn)
    markup.add(post_btn)
    if id == int(config['MAIN_ADMIN_ID']): markup.add(admins_manager)
    markup.add(admins_spravkas)
    markup.add(leave_admin_btn)
    return markup

async def generate_admins_spravkas():
    markup = InlineKeyboardMarkup(row_width=3)
    db = await collection.find_one({'_id': ObjectId('64987b1eeed9918b13b0e8b4')})
    btns = []
    for i in db['spravka']:
        btns.append(InlineKeyboardButton(i['n'], callback_data=f'sprvd_{i["func"]}'))
    back = InlineKeyboardButton('⏪ Назад', callback_data='back_from_admins_spravkas')
    markup.add(*btns)
    markup.add(back)
    return markup

async def generate_admin_spravka_show():
    markup = InlineKeyboardMarkup(row_width=3)
    edit = InlineKeyboardButton('📝 Изменить текст', callback_data='sprvedit')
    back = InlineKeyboardButton('⏪ Назад', callback_data='back_from_admins_spravka_show')
    markup.add(edit)
    markup.add(back)
    return markup

async def generate_admins_manager():
    markup = InlineKeyboardMarkup()
    add_admin_btn = InlineKeyboardButton('🔓 Дать доступ к админке', callback_data='admin_add')
    rem_admin_btn = InlineKeyboardButton('🔒 Забрать доступ к админке', callback_data='admin_rem')
    back = InlineKeyboardButton('⏪ Назад', callback_data='back_from_admins_manager')
    markup.add(add_admin_btn)
    markup.add(rem_admin_btn)
    markup.add(back)
    return markup

async def generate_admin_return():
    markup = InlineKeyboardMarkup()
    admin_statsusers_btn = InlineKeyboardButton('👥 Пользователи', callback_data='admin_statsusers')
    admin_statsfinancs_btn = InlineKeyboardButton('💰 Финансы', callback_data='admin_statsfinancs')
    admin_stats_back_btn = InlineKeyboardButton('⏪ Назад', callback_data='admin_stats_back')
    markup.add(admin_statsusers_btn, admin_statsfinancs_btn)
    markup.add(admin_stats_back_btn)
    return markup

async def generate_admin_statsfinancs(page_info):
    markup = InlineKeyboardMarkup()
    prev_financian_page = InlineKeyboardButton('◀', callback_data='prev_financian_page')
    info_btn = InlineKeyboardButton(f'{page_info}', callback_data='pageinfofinan')
    next_financian_page = InlineKeyboardButton('▶', callback_data='next_financian_page')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_from_admin_statsfinancs')
    markup.add(prev_financian_page, info_btn, next_financian_page)
    markup.add(back_btn)
    return markup

async def generate_admusers_select(current_page=0, buttons_per_page=10):
    try:
        db = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
        inline_buttons = []
        sorted_users = []
        for user in db['users']:
            try:
                chat = await bot.get_chat(user)
                udb = await collection.find_one({'user_id': user})
                sorted_users.append({"chats": len(udb["chats"]), "text": f'{chat.first_name} - {len(udb["chats"])} | 💎 {udb["lic"]}', "user": user})
            except ChatNotFound:
                continue
            except BotBlocked:
                continue
        sorted_users = sorted(sorted_users, key=lambda x: x["chats"], reverse=True)
        for sorted_user in sorted_users:
            inline_buttons.append(InlineKeyboardButton(text=sorted_user["text"], callback_data=f'stuser_{sorted_user["user"]}'))

        markup = ''
        if len(inline_buttons) != 0:
            pages = [inline_buttons[i:i + buttons_per_page] for i in range(0, len(inline_buttons), buttons_per_page)]
            current_page = current_page % len(pages)
            markup = InlineKeyboardMarkup(row_width=3)
            for page in pages[current_page]:
                markup.add(page)


            pagescount_btn = InlineKeyboardButton(f'{current_page + 1} из {len(pages)}', callback_data='pagescounter')
            next_btn = InlineKeyboardButton('Вперед ▶', callback_data='admusers_next')
            prev_btn = InlineKeyboardButton('◀ Назад', callback_data='admusers_prev')
            markup.add(prev_btn, pagescount_btn, next_btn)

            markup.add(InlineKeyboardButton('🔍 Поиск по ID', callback_data='admusersstats_idsearch'))
            markup.add(InlineKeyboardButton('⏪ Назад', callback_data='back_from_admusers_stats'))
        else:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('⏪ Назад', callback_data='back_from_admusers_stats'))

        return markup
    except Exception as e:
        traceback.print_exc()

async def generate_back_from_search_id():
    markup = InlineKeyboardMarkup()
    back= InlineKeyboardButton('⏪ Назад', callback_data='back_from_search_id')
    markup.add(back)
    return markup


async def generate_admin_return_main():
    markup = InlineKeyboardMarkup()
    admin_stats_back_btn = InlineKeyboardButton('⏪ Назад в админку', callback_data='back_from_added_position')
    markup.add(admin_stats_back_btn)
    return markup

async def generate_user_info_show(user_id):
    markup = InlineKeyboardMarkup()
    db = await collection.find_one({'user_id': user_id})
    bl = '🔒 Заблокировать'
    if db['blocked'] == True: bl = '🔓 Разблокировать'

    block = InlineKeyboardButton(bl, callback_data='blockunblock')
    groups = InlineKeyboardButton('🗃️ Группы', callback_data='userstat_groups')
    back = InlineKeyboardButton('⏪ Назад', callback_data='back_from_user_info')
    markup.add(block)
    markup.add(groups)
    markup.add(back)
    return markup

async def generate_payment_page():
    markup = InlineKeyboardMarkup(row_width=1)
    db = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
    unsortedp = db['price']
    positions = sorted(unsortedp, key=lambda x: int(x['period']))
    btns = []
    for i in positions:
        btns.append(InlineKeyboardButton(f'🛒 Купить - {i["period"]} дней', callback_data=f'buy_{i["period"]}'))
    back_btn = InlineKeyboardButton('⏪ Назад в настройки', callback_data='back_to_settings')
    markup.add(*btns)
    markup.add(back_btn)
    return markup

async def generate_delete_positions():
    markup = InlineKeyboardMarkup(row_width=1)
    db = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
    unsortedp = db['price']
    positions = sorted(unsortedp, key=lambda x: int(x['period']))
    btns = []
    for i in positions:
        btns.append(InlineKeyboardButton(f'{i["period"]} дней - {i["price"]}₽', callback_data=f'positdelete_{i["period"]}'))
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_to_edit_price')
    markup.add(*btns)
    markup.add(back_btn)
    return markup

async def generate_eidit_positions():
    markup = InlineKeyboardMarkup(row_width=1)
    db = await collection.find_one({"_id": ObjectId('64987b1eeed9918b13b0e8b4')})
    unsortedp = db['price']
    positions = sorted(unsortedp, key=lambda x: int(x['period']))
    btns = []
    for i in positions:
        btns.append(InlineKeyboardButton(f'📝 {i["period"]} дней - {i["price"]}₽', callback_data=f'positedite_{i["period"]}'))
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_to_edit_price')
    markup.add(*btns)
    markup.add(back_btn)
    return markup

async def generate_payment_method():
    markup = InlineKeyboardMarkup()
    manual_btn = InlineKeyboardButton('💳 Ручной перевод', callback_data='pay_manual')
    yoomoney_btn = InlineKeyboardButton('💳 ЮMoney', callback_data='pay_yoomoney')
    back_btn = InlineKeyboardButton('⏪ Назад в настройки', callback_data='back_to_settings')
    markup.add(manual_btn)
    markup.add(yoomoney_btn)
    markup.add(back_btn)
    return markup

async def generate_dpayment_method():
    markup = InlineKeyboardMarkup()
    manual_btn = InlineKeyboardButton('💳 Ручной перевод', callback_data='donpay_manual')
    yoomoney_btn = InlineKeyboardButton('💳 ЮMoney', callback_data='donpay_yoomoney')
    back_btn = InlineKeyboardButton('⏪ Отменить', callback_data='back_from_donate_method')
    markup.add(manual_btn)
    markup.add(yoomoney_btn)
    markup.add(back_btn)
    return markup

async def generate_back_to_settings():
    markup = InlineKeyboardMarkup()
    back_btn = InlineKeyboardButton('⏪ Назад в настройки', callback_data='back_to_settings')
    markup.add(back_btn)
    return markup

async def generate_back_to_profil():
    markup = InlineKeyboardMarkup()
    back_btn = InlineKeyboardButton('⏪ Открыть профиль', callback_data='back_to_my_profil')
    markup.add(back_btn)
    return markup

async def generate_admin_limit_edit_choice():
    markup = InlineKeyboardMarkup()
    limit_to_users_edit_btn = InlineKeyboardButton('📝 Изменить ограничение', callback_data='aedit_limittousers')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_from_edit_limits')
    markup.add(limit_to_users_edit_btn)
    markup.add(back_btn)
    return markup

async def generate_admin_price_edit_choice():
    markup = InlineKeyboardMarkup()
    admin_addposition_btn = InlineKeyboardButton('➕ Добавить новую позицию', callback_data='admin_addposition')
    admin_editposition_btn = InlineKeyboardButton('✍ Изменить существующую позицию', callback_data='admin_editposition')
    admin_deleteposition_btn = InlineKeyboardButton('🗑️ Удалить позицию', callback_data='admin_deleteposition')
    back_btn = InlineKeyboardButton('⏪ Назад', callback_data='back_from_edit_limits')
    markup.add(admin_addposition_btn)
    markup.add(admin_editposition_btn)
    markup.add(admin_deleteposition_btn)
    markup.add(back_btn)
    return markup

async def generate_positedit():
    markup = InlineKeyboardMarkup()
    edit_days = InlineKeyboardButton('🔹 Изменить срок', callback_data='posited_days')
    edit_price = InlineKeyboardButton('🔹 Изменить цену', callback_data='posited_price')
    cancel_editing = InlineKeyboardButton('🔴 Отменить изменение', callback_data='posited_cancel')
    accept_editing = InlineKeyboardButton('🟢 Применить изменения', callback_data='posited_accept')
    markup.add(edit_days)
    markup.add(edit_price)
    markup.add(cancel_editing)
    markup.add(accept_editing)
    return markup

async def generate_manual_payment():
    markup = InlineKeyboardMarkup()
    manualp_sendtoacc = InlineKeyboardButton('✅ Я перевел', callback_data='manualp_sendtoacc')
    manualp_back = InlineKeyboardButton('⏪ Назад', callback_data='manualp_back')
    markup.add(manualp_sendtoacc)
    markup.add(manualp_back)
    return markup

async def generate_dmanual_payment():
    markup = InlineKeyboardMarkup()
    manualp_sendtoacc = InlineKeyboardButton('✅ Готово', callback_data='dmanul_done')
    manualp_back = InlineKeyboardButton('⏪ Назад', callback_data='dmanul_back')
    markup.add(manualp_sendtoacc)
    markup.add(manualp_back)
    return markup

async def generate_back_resedittext():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_resedittext')
    markup.add(back)
    return markup

async def generate_back_paydialemailget():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_paydialemailget')
    markup.add(back)
    return markup

async def generate_back_paydialgiveperm():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_paydialgiveperm')
    markup.add(back)
    return markup

async def generate_back_repedittext():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_repedittext')
    markup.add(back)
    return markup

async def generate_back_pingedittext():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_pingedittext')
    markup.add(back)
    return markup

async def generate_back_addblock():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_addblock')
    markup.add(back)
    return markup

async def generate_back_remblock():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_remblock')
    markup.add(back)
    return markup

async def generate_back_ruledittext():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_ruledittext')
    markup.add(back)
    return markup

async def generate_back_gretedittext():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_gretedittext')
    markup.add(back)
    return markup

async def generate_back_banedittext():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_banedittext')
    markup.add(back)
    return markup

async def generate_back_kickedittext():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_kickedittext')
    markup.add(back)
    return markup

async def generate_back_unbanedittext():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_unbanedittext')
    markup.add(back)
    return markup

async def generate_back_afkedittext():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_afkedittext')
    markup.add(back)
    return markup

async def generate_back_afkeditmedia():
    markup = InlineKeyboardMarkup()
    delete = InlineKeyboardButton('🚮 Удалить фото/видео', callback_data='eback_afkeditmedia_delete')
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_afkeditmedia')
    markup.add(delete)
    markup.add(back)
    return markup

async def generate_back_donatemoney():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_donatemoney')
    markup.add(back)
    return markup

async def generate_back_addsyms():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_addsyms')
    markup.add(back)
    return markup

async def generate_back_removesyms():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_removesyms')
    markup.add(back)
    return markup

async def generate_back_antimat():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_antimat')
    markup.add(back)
    return markup

async def generate_back_skromniytimer():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_skromniytimer')
    markup.add(back)
    return markup


async def generate_back_msgfiltersadd():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_msgfiltersadd')
    markup.add(back)
    return markup

async def generate_back_msgfiltersrem():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_msgfiltersrem')
    markup.add(back)
    return markup

async def generate_back_vtimer():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_vtimer')
    markup.add(back)
    return markup


async def generate_back_skromniywed():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_skromniywed')
    markup.add(back)
    return markup

async def generate_back_tixtimers():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_tixtimers')
    markup.add(back)
    return markup

async def generate_back_rmsginterval():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_rmsginterval')
    markup.add(back)
    return markup

async def generate_back_antifludscenes():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_antifludscenes')
    markup.add(back)
    return markup

async def generate_back_nofilescenes():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_nofilescenes')
    markup.add(back)
    return markup

async def generate_back_subchaneladd():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_subchaneladd')
    markup.add(back)
    return markup

async def generate_back_paydialpmethadd():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_paydialadd')
    markup.add(back)
    return markup

async def generate_back_paydialtarifdataedit():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_paydialtarifdataedit')
    markup.add(back)
    return markup

async def generate_back_paydialwarninged():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_paydialwarninged')
    markup.add(back)
    return markup

async def generate_back_subscrwarned():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_subscrwarned')
    markup.add(back)
    return markup

async def generate_back_paydialpminfoadd():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_paydialpminfoadd')
    markup.add(back)
    return markup

async def generate_paydialtarifd_editchoice(tarif_id):
    markup = InlineKeyboardMarkup()
    days = InlineKeyboardButton('📝 Дни', callback_data='edit_paydialtarifdays')
    price = InlineKeyboardButton('📝 Цену', callback_data='edit_paydialtarifprice')
    back = InlineKeyboardButton('⏪ Назад', callback_data=f'backpaydialtarifchoice_{tarif_id}')
    markup.add(days)
    markup.add(price)
    markup.add(back)
    return markup

async def generate_back_paydialtarif():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='eback_paydialtarif')
    markup.add(back)
    return markup

async def generate_manual_payment_admin_actions():
    markup = InlineKeyboardMarkup()
    accept = InlineKeyboardButton('Проверил ✅', callback_data='mmpay_acadmin')
    decline = InlineKeyboardButton('Не пришло 🤷‍♂', callback_data='mmpay_decadmin')
    markup.add(accept)
    markup.add(decline)
    return markup


async def generate_back_to_main():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='back_to_main_page')
    markup.add(back)
    return markup

async def generate_donate_payment_button():
    markup = InlineKeyboardMarkup()
    pay = InlineKeyboardButton('Помочь', pay=True)
    markup.add(pay)
    return markup

async def admin_back_from_add_admin():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='admcanc_addaddmin')
    markup.add(back)
    return markup

async def admin_back_from_admin_post():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='admcanc_adminpost')
    markup.add(back)
    return markup

async def admin_back_from_add_admin_position():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='admcanc_addaddminposition')
    markup.add(back)
    return markup

async def admin_back_from_add_admin_positedday():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='admcanc_addaddminpositedday')
    markup.add(back)
    return markup

async def admin_back_from_add_admin_positedprice():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='admcanc_addaddminpositedprice')
    markup.add(back)
    return markup

async def admin_back_from_admin_edlimits():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='admcanc_adminedlimits')
    markup.add(back)
    return markup

async def admin_back_from_sprav_scene():
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⏪ Назад', callback_data='admcanc_adminspravscene')
    markup.add(back)
    return markup

async def generete_bot_delete_chat_question():
    markup = InlineKeyboardMarkup()
    delete = InlineKeyboardButton('⛔ Уверен на 100%', callback_data='deletechatbots_d')
    no = InlineKeyboardButton('⏪ Передумал', callback_data='deletechatbots_canc')
    markup.add(delete)
    markup.add(no)
    return markup

async def generate_admins_rem():
    markup = InlineKeyboardMarkup(row_width=3)
    db = await collection.find_one({'_id': ObjectId('64987b1eeed9918b13b0e8b4')})
    adminsarr = db['admins']
    users = []
    for i in adminsarr:
        try:
            user = await bot.get_chat(i)
            users.append(InlineKeyboardButton(text=await shorten_text(user.first_name, 10), callback_data=f'remadm_{i}'))
        except ChatNotFound:
            await collection.find_one_and_update({'_id': ObjectId('64987b1eeed9918b13b0e8b4')}, {"$pull": {'admins': i}})
            continue
    markup.add(*users)
    back = InlineKeyboardButton('⏪ Назад', callback_data='back_from_adminrem')
    markup.add(back)
    return markup