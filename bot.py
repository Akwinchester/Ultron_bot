import telebot
from config import BOT_TOKEN, MESSAGE_TEXT, BUTTON_TEXT
from formation_text_message import select_activity, setting_notification, tg_entry_text, list_activity_True
from models.user import create_user, get_user_id, add_friend, check_user_name_bd, update_user,get_user_name
from models.activity import *

from keyboards import *

from models.entry import add_row
from data_structares import Row, RowFactory

from datetime import date
from keyboa import Keyboa
import re
from werkzeug.security import check_password_hash

message_id_for_edit = {}
user_row = {}


bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')


# Приветственное сообщение с клавиатурой: "Зарегистрирован" or "Не зарегистрирован"
@bot.message_handler(commands=['start'])
def send_welcome_message(message):
    keyboard = make_keyboard_check_registration()
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!!!\n' + MESSAGE_TEXT['start'],
                     reply_markup=keyboard())
    # create_user(call.message.from_user.first_name, call.message.chat.id, call.message.from_user.username)


# Функция удаление сообщений бота и пользователя по идентификаторам
def remove_messages(message, list_key:list):
    for key in list_key:
        if key in message_id_for_edit:
            try:
                bot.delete_message(chat_id=message.chat.id, message_id=message_id_for_edit[key])
                del message_id_for_edit[key]
            except:
                print('Ошибка удаления сообщения с id:', message_id_for_edit[key], 'в чате с id:', message.chat.id)


# Обработка ответа пользователя с клавиатуры: "Зарегистрирован" or "Не зарегистрирован"
@bot.callback_query_handler(func=lambda call: re.match(r'check_registration=[0-1]',call.data))
def processing_registration_selection(call):
    status = call.data.split('=')[1]
    if status == '1':
        answer = bot.send_message(call.message.chat.id, MESSAGE_TEXT['authorized'])
        print(MESSAGE_TEXT['authorized'], ': ' , call.message.id)
        message_id_for_edit['check_authorization'] = answer.id
        bot.register_next_step_handler(call.message, get_and_check_username)

    elif status == '0':
        answer = bot.send_message(call.message.chat.id, MESSAGE_TEXT['no_authorized'])
        print(MESSAGE_TEXT['authorized'] , ': ' ,call.message.id)
        message_id_for_edit['check_authorization'] = answer.id


# Забираем из сообщения username и проверяем есть ли имя пользователя в БД
def get_and_check_username(message):
    remove_messages(message, ['check_authorization_True', 'check_authorization_False', 'user_name'])
    message_id_for_edit['user_name'] = message.id
    user = check_user_name_bd(message.text)
    if user:
        answer = bot.send_message(message.chat.id, f'Отлично пользователь с именем {message.text} найден в системе. Отправь следующим сообщением пароль')
        print(f'Отлично пользователь с именем {message.text} найден в системе. Отправь следующим сообщением пароль', answer.id)
        message_id_for_edit['check_authorization_True'] = answer.id
        remove_messages(message, ['check_authorization'])
        bot.register_next_step_handler(message, get_and_check_password, user)

    else:
        answer = bot.send_message(message.chat.id, 'Сожалею, но пользователь не найден. Проверь написание и отправь сообщение с именем еще раз.')
        print('Сожалею, но пользователь не найден. Проверь написание и отправь сообщение с именем еще раз.', answer.id)
        message_id_for_edit['check_authorization_False'] = answer.id
        bot.register_next_step_handler(message, get_and_check_username)


# Забираем из сообщения пароль и сравниваем с хешем пароля из БД
def get_and_check_password(message, user):
    remove_messages(message, ['user_name', 'password_False', 'check_authorization_True'])

    if check_password_hash(user.password, message.text):
        update_user(user_name=user.username, real_name=message.from_user.first_name,
                    chat_id=message.chat.id, nick=message.from_user.username)
        bot.send_message(message.chat.id, 'Поздравляю, вы вошли в систему. Ваши аккаунты на сайте и в боте синхронизированы.')
        bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    else:
        bot.delete_message(chat_id=message.chat.id, message_id=message.id)
        answer = bot.send_message(message.chat.id, "Увы, пароль неверный. Отправь сообщением верный пароль")
        message_id_for_edit['password_False'] = answer.id
        bot.register_next_step_handler(message, get_and_check_password, user)


# Открытие главного меню
@bot.message_handler(content_types=['text'], regexp=BUTTON_TEXT['start'])
def open_main_menu(message):
    bot.send_message(message.chat.id, MESSAGE_TEXT['main_menu'], reply_markup=make_keyboard_main_menu())


# Возвращение в главное меню через кнопку отмены
@bot.message_handler(content_types=['text'], regexp=BUTTON_TEXT['cancel'])
def handle_cancel_button(message):
    bot.send_message(message.chat.id, MESSAGE_TEXT['main_menu'], reply_markup=make_keyboard_main_menu())


# Обработка нажатия кнопки "Добавить запись"
# Переход к выбору активности для новой записи
@bot.message_handler(content_types=['text'], regexp=BUTTON_TEXT['add_row'])
def open_activity_selection_for_entry(message):
    bot.delete_message(message.chat.id, message.id)
    user_id = get_user_id(message.chat.id)
    keyboard = make_keyboard_list_activity(user_id, status=1)
    answer = bot.send_message(message.chat.id, 'Выбери или создай активность', reply_markup=keyboard())
    message_id_for_edit['add_activity'] = answer.message_id


# Обработка нажатия кнопки добавлене активности "добавить запись"->"+"
# Открытие меню выбора создания или подключения активности
@bot.callback_query_handler(func=lambda call: call.data == 'activity=add_activity')
def open_settings_activities(call):
    user_id = get_user_id(call.message.chat.id)
    keyboard = make_keyboard_add_new_or_friend_activity(user_id)

    if 'add_activity' in message_id_for_edit:
        bot.edit_message_text(list_activity_True(user_id), call.message.chat.id, message_id_for_edit['add_activity'],
                              reply_markup=keyboard())
    else:
        answer = bot.send_message(call.message.chat.id, list_activity_True(user_id), reply_markup=keyboard())
        message_id_for_edit['add_activity'] = answer.message_id

    message_id_for_edit['list_activity'] = call.message.id


# Обработка нажатия кнопки добавлене активности "добавить запись"->"+"->"имя пользователя".
# Отображение списка активностей выбранного пользователя
@bot.callback_query_handler(func=lambda call: re.match(r'activity=show_list_activity_friend=[0-9]+',call.data))
def display_friend_activities(call):
    print('re')
    friend_id = call.data.split('=')[2]
    friend_name = get_user_name(friend_id)
    keyboard = make_keyboard_list_activity_friend(friend_id)
    bot.edit_message_text(f'Активности пользователя {friend_name}',  call.message.chat.id, message_id_for_edit['add_activity'], reply_markup=keyboard())


# Обработка нажатия кнопки добавлене активности "добавить запись"->"+"->"имя пользователя"->"название активности".
# Создание дубликата активности по шаблону активности друга, для возможности участвовать в соревновании по данной активности.
@bot.callback_query_handler(func=lambda call: re.match(r'activity=add_friend=[0-9]+_activity=[0-9]+',call.data))
def clone_activity_friend(call):
    user_id = get_user_id(call.message.chat.id)
    activity_id = call.data.split('=')[3]
    create_activity_for_template(user_id=user_id, activity_id=activity_id)


# Обработка нажатия кнопки добавлене активности "добавить запись"->"+"->"новая активность"
# Запрос на ввод названия и старт создания новой активности
@bot.callback_query_handler(func=lambda call: call.data == 'activity=create_activity')
def start_activity_creation(call):
    answer = bot.send_message(call.message.chat.id, 'отправь название новой активности следующим сообщением')
    message_id_for_edit['name_activity'] = answer.message_id
    bot.register_next_step_handler(call.message, get_name_new_activity)


#Получение имени новой активности от пользователя из сообщения
#Создание активности из полученного имени активности
def get_name_new_activity(message):
    chat_id = message.chat.id
    add_activity(chat_id, name_activity=message.text)
    user_id = get_user_id(message.chat.id)
    keyboard = make_keyboard_list_activity(user_id, status=1)
    #Todo заменить на remove_messages
    bot.delete_message(chat_id, message.id)
    bot.delete_message(chat_id, message_id_for_edit['name_activity'])
    bot.edit_message_text(text='Выбери или создай активность', message_id=message_id_for_edit['list_activity'],
                          chat_id=message.chat.id,
                          reply_markup=keyboard())


# Обработка нажатия кнопки добавлене активности "добавить запись"->"+"->"мои активности"
# Отображение неактивных активностей пользователя
@bot.callback_query_handler(func=lambda call: call.data == 'activity=my_activity')
def display_archived_activities(call):
    user_id = get_user_id(call.message.chat.id)
    keyboard = make_keyboard_list_activity_for_change_status(user_id=user_id, status=0)
    answer = bot.send_message(call.message.chat.id, 'Неактивные активности', reply_markup=keyboard())


# Смена статуса активности "добавить запись"->"+"->"мои активности"->"название активности"
# Смена статуса выбранной активности c "архивная" на "актуальная"
@bot.callback_query_handler(func=lambda call: re.match(r'activity=change_status=[0-9]',call.data))
def add_activity_from_archive(call):
    activity_id = call.data.split('=')[2]
    change_status_activity(activity_id)


# Обработка нажатия на кнопку: "Добавить запись"->"имя_активности"
# Отображение меню настроек выбранной активности
@bot.callback_query_handler(func=lambda call: re.match(r'activity=[0-9]+\b',call.data))
def open_activity_menu(call):
    chat_id = call.message.chat.id
    activity_id = call.data.split('=')[1]
    message_id_for_edit['list_activity'] = call.message.id
    keyboard = make_keyboard_setting_activity(activity_id)
    bot.edit_message_text(select_activity(activity_id), chat_id, call.message.id, reply_markup=keyboard())


# Обработка нажатия на кнопку: "Добавить запись"->"имя_активности"->"Удалить активность"
# Удаление выбранной активности
@bot.callback_query_handler(func=lambda call: re.match(r'activity_[0-9]+=delete',call.data))
def delete_selected_activity(call):
    activity_id = call.data.split('=')[0].split('_')[1]
    delete_activity(activity_id)
    user_id = get_user_id(call.message.chat.id)
    keyboard = make_keyboard_list_activity(user_id, status=1)
    bot.edit_message_text('Выбери или создай активность',call.message.chat.id, call.message.id, reply_markup=keyboard())



#Обраотка нажатия на кнопку: "уведомления" из (удалить активность, уведомления, продолжить)
# Переход к настройке уведомлений выбранной активности
@bot.callback_query_handler(func=lambda call: re.match(r'activity_[0-9]+=push',call.data))
def open_notifications_settings(call):
    activity_name = get_name_activity(call.data.split('=')[0].split('_')[1])
    activity_id = call.data.split('=')[0].split('_')[1]
    keyboard = make_keyboard_setting_push(activity_id)
    message_id_for_edit['activity_settings_menu'] = call.message.id
    # TODO: сделать формирование текстового сообщения
    bot.edit_message_text(setting_notification(activity_id),
                          call.message.chat.id, call.message.id, reply_markup=keyboard())


# Обработка: "уведомления"->"список активностей"
# Обработка: "имя_активности"->"список активностей"
# Обработка: "добавить запись"->"+"->"имя пользователя"->"<<<<".
# Возврат к списку актуальных активностей из позиций: список активностей друга, настройка уведомления, меню выбранной активности
@bot.callback_query_handler(func=lambda call: re.match(r'[0-9]+_push=save|activity_[0-9]+=list_activity|activity=[0-9]+_friend=list_activity|activity=change_status=list_activity|activity=add_friend=[0-9]+_activity=back',call.data))
def back_to_current_activities(call):
    user_id = get_user_id(call.message.chat.id)
    keyboard = make_keyboard_list_activity(user_id, status=1)
    bot.edit_message_text('Выбери или создай активность', call.message.chat.id, call.message.id, reply_markup=keyboard())


# Обработка: "уведомления"->"текст уведомления"
# Запрос на ввод кастомного текста-шаблона уведомления для выбранной активности
@bot.callback_query_handler(func=lambda call: re.match(r'[0-9]+_push=text',call.data))
def start_setting_notification_text(call):
    answer = bot.send_message(call.message.chat.id, MESSAGE_TEXT['example_push'])
    message_id_for_edit['push_setting_text'] = answer.id
    activity_id = call.data.split('=')[0].split('_')[0]
    bot.register_next_step_handler(call.message, get_text_push, activity_id)


#Забираю текст уведомления от пользователя из сообщения
def get_text_push(message, activity_id):
    update_notification_text(activity_id=activity_id, notification_text=message.text)
    keyboard = make_keyboard_setting_push(activity_id)
    bot.edit_message_text(f'Настройка текста уведомления и получателей уведомления для активности: <b>{get_name_activity(activity_id)}</b>.  Текст: <b>{message.text}</b>',
                          message.chat.id, message_id_for_edit['activity_settings_menu'], reply_markup=keyboard())
    #Todo заменить на remove_messages
    bot.delete_message(message.chat.id, message_id_for_edit['push_setting_text'])
    bot.delete_message(message.chat.id, message.id)


# Обработка "уведомления"->"получатели"
# Показ и настройка списка текущих получателей уведомлений
@bot.callback_query_handler(func=lambda call: re.match(r'[0-9]+_push=addresses',call.data))
def setting_recipient_list(call):
    user_id = get_user_id(call.message.chat.id)
    activity_id = call.data.split('_')[0]
    keyboard = make_keyboard_list_friend(user_id, activity_id=activity_id)
    #TODO нужно сделать кнопки навигации, чтобы иметь возможность вернуться к списку активностей
    bot.edit_message_text(formation_message_list_adresses(formation_list_adresses(activity_id)), call.message.chat.id, call.message.id, reply_markup=keyboard())


# Обработка "уведомления"->"получатели"-> "+"
# Запрос на ввод ника нового получателя, для добавления нового друга
@bot.callback_query_handler(func=lambda call: re.match(r'activity=[0-9]+_friend=add_friend',call.data))
def start_add_new_friend(call):
    message_id_for_edit['list_friend'] = call.message.id
    user_id = get_user_id(call.message.chat.id)
    activity_id = call.data.split('_')[0].split('=')[1]
    answer = bot.send_message(call.message.chat.id, 'Отправь следующим сообщением ник пользователя, которого хочешь добавить в друзья, @ печатать не надо')
    message_id_for_edit['info_add_friend'] = answer.id
    bot.register_next_step_handler(call.message, add_friend_by_nick, user_id, activity_id)


# Обработка: "уведомления"->"получатели"-> "+"
# Забираю ник из сообщения от пользователя
# Добавление нового получателя по нику
#Todo вынести текстовые сообщения в config.py
def add_friend_by_nick(message, user_id, activity_id):
    flug = add_friend(user_id, nick=message.text)
    bot.delete_message(message.chat.id, message.id)
    bot.delete_message(message.chat.id, message_id_for_edit['info_add_friend'])

    if flug:
        keyboard = make_keyboard_list_friend(user_id, activity_id)
        bot.edit_message_text(formation_message_list_adresses(formation_list_adresses(activity_id)), message.chat.id, message_id_for_edit['list_friend'], reply_markup=keyboard())

        if 'error_add_new_friend' in message_id_for_edit:
            bot.delete_message(message.chat.id, message_id_for_edit['error_add_new_friend'])

    else:
        error_add_friend = bot.send_message(message.chat.id, 'Не получилось добавить друга. Возможные причины: контакт уже у вас в друзьях, ошибка в нике,'
                                          ' пользователь с этим ником не зарегистрирован в боте')
        message_id_for_edit['error_add_new_friend'] = error_add_friend.id

        answer = bot.send_message(message.chat.id,
                                  'Отправь следующим сообщением ник пользователя, которого хочешь добавить в друзья, @ печатать не надо')

        message_id_for_edit['info_add_friend'] = answer.id
        bot.register_next_step_handler(message, add_friend_by_nick, user_id, activity_id)


# Обработка: "уведомления"->"получатели"-> "имя_получателя"
# Добавление выбранного друга в список получателей уведомлений по выбранной активности
#TODO нужно делать проверку на то, что сообщение нуждается в обновлении. Чтобы не падала ошибка, что старое и новое содержимое идентично
#TODO реализовать удаление адресата из списка
@bot.callback_query_handler(func=lambda call: re.match(r'activity=[0-9]+_friend=[0-9]+',call.data))
def add_friend_in_recipient(call):
    friend_id = call.data.split('_')[1].split('=')[1]
    activity_id = call.data.split('_')[0].split('=')[1]
    user_id = get_user_id(call.message.chat.id)
    add_address(friend_id=friend_id, activity_id=activity_id)
    keyboard = make_keyboard_list_friend(user_id, activity_id)
    bot.edit_message_text(text=formation_message_list_adresses(formation_list_adresses(activity_id)),
                          chat_id=call.message.chat.id, message_id=call.message.id,
                          reply_markup=keyboard())



# Обработка: "Добавить запись"->"название активности"
# Выбор: клавиатура "указывать количественную характеристику or пропустить"
@bot.callback_query_handler(func=lambda call: re.match(r'activity_[0-9]+=continue',call.data))
def start_add_entry(call):
    chat_id = call.message.chat.id
    activity_id = call.data.split('=')[0].split('_')[1]
    bot.delete_message(chat_id, message_id_for_edit['list_activity'])
    user_row[chat_id] = RowFactory()
    user_row[chat_id].set_activity_id(activity_id)
    keyboard = make_keyboard_skip_amount()
    bot.send_message(chat_id, 'Можешь указать количественную характеристику', reply_markup=keyboard())


# Запрос на ввод количественного значения
@bot.callback_query_handler(func=lambda call: re.match(r'amount=continue',call.data))
def request_amount_input(call):
    bot.delete_message(call.message.chat.id, call.message.id)
    answer = bot.send_message(call.message.chat.id, 'Отправь количество следующим сообщением')
    message_id_for_edit['amount_continue'] = answer.id
    bot.register_next_step_handler(call.message, get_amount)


#Получение количественной характеристики от пользователя из сообщения
def get_amount(message):
    user_row[message.chat.id].set_amount(int(message.text))
    bot.delete_message(chat_id=message.chat.id, message_id=message_id_for_edit['amount_continue'])
    bot.delete_message(message.chat.id, message.id)

    keyboard = make_keyboard_skip_description()
    answer = bot.send_message(message.chat.id, 'Можешь добавить описание', reply_markup=keyboard())
    message_id_for_edit['description_cskip'] = answer.id


# Пропускаем ввод количественной характеристики
# Переход к вводу описания с пропуском значения
@bot.callback_query_handler(func=lambda call: re.match(r'amount=skip',call.data))
def skip_amount_input(call):
    bot.delete_message(call.message.chat.id, call.message.id)
    user_row[call.message.chat.id].set_amount(0)
    keyboard = make_keyboard_skip_description()
    bot.send_message(call.message.chat.id, 'Можешь добавить описание', reply_markup=keyboard())



# Запрос на ввод описания записи
@bot.callback_query_handler(func=lambda call: re.match(r'description=continue',call.data))
def request_description_input(call):
    answer = bot.send_message(call.message.chat.id, 'Отправь описание следующим сообщением')
    message_id_for_edit['description_cskip'] = answer.id

    bot.delete_message(call.message.chat.id, call.message.id)
    bot.register_next_step_handler(call.message, get_description)


#Получение описания от пользователя из сообщения
def get_description(message):
    user_row[message.chat.id].set_description(message.text)
    user_row[message.chat.id].set_date_added(date.today())
    bot.delete_message(message.chat.id, message.id)
    bot.delete_message(message.chat.id, message_id_for_edit['description_cskip'])
    create_and_save_entry(user_row[message.chat.id], message)


#Обрабатываем пропускание описания
@bot.callback_query_handler(func=lambda call: re.match(r'description=skip',call.data))
def skip_description(call):
    bot.delete_message(call.message.chat.id, call.message.id)
    user_row[call.message.chat.id].set_description('-')
    user_row[call.message.chat.id].set_date_added(date.today())
    create_and_save_entry(user_row[call.message.chat.id], call.message)


#Этап создания объекта Row и записи данных в БД
def create_and_save_entry(row_maker, message):
    row = row_maker.create_row()
    add_row(row)
    send_notifications(row, message)

# Отправка уведомлений и сообщения пользователю о добавленной записи
def send_notifications(data_row:Row, message):
    notification_text = get_notification_text(data_row.activity_id)
    if notification_text == '-':
        notification_text = tg_entry_text(data_row)

    if '[количество]' in notification_text:
        notification_text = notification_text.replace('[количество]', str(data_row.amount))
    if notification_text:
        list_chat_id = formation_list_chat_id(data_row.activity_id)
        for chat_id in list_chat_id:
            bot.send_message(int(chat_id), notification_text)
    bot.send_message(message.chat.id, tg_entry_text(data_row) )


# Обработчик коллбэков без явного соответствия
@bot.callback_query_handler(func=lambda call: True)
def process_callback(call):
    bot.send_message(call.message.chat.id, call.data)


if __name__ == '__main__':
    bot.infinity_polling(none_stop=True)


#Что нужно сделать:
#TODO Выделить из этого файла логическую часть в отдельный модуль

#TODO реализовать удаление адресата из списка

#TODO реализовать удаление из друзей

#TODO Вынести все текстовые сообщения и именя кнопок в файлы config.py и formation_text_message.py в свловарь с осмысленными и читабельными ключами

#TODO сделать аннотации ко всем функциям(кроме обработчиков, которые принимают call или message без доп аргументов) типы получаемых данных, типы возвращаемых данных

#TODO сделать ревью кода с помощью GPT: добавить блоки try: except: где это необходимо, ренейминг, привести к единому стилю, привести в должный вид import-ы

#TODO сделать логирование ошибок и основных событий в боте: (добавление пользователя, создание активности, добавление друзей)

#TODO подуать нужны ли тесты и если нужны, сделать