# импортируем конфиг с именем бота и API токеном телеграмм
from config import API_TOKEN, name_bot
# Импортируем классы которые хранят статусы
from reg import Registration  # регистрация пользователя
from act import Activations  # активация учетной записи администратором
from type_of_traning import get_message  # текущий статус получения итогового сообщения

# класс для работы с БД MS SQL
from sqlazure import SQLazure
# Импоритуем библиотеку для логирования
import logging
# импортируем библиотеку для работы с датой и временем
from datetime import datetime
# импортируем библиотеку для работы с api телеграмм
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

# задаем уровень логов
logging.basicConfig(level=logging.INFO)

# инициализируем бота
bot = Bot(token=API_TOKEN)
# инициализируем хранилище для стутусов
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# инициализируем соединение с БД
db = SQLazure()
# список для создания кнопкок
main_list_button = ['/Факультеты']
# список для создания кнопок администратора
admin_list_button = ['/Активировать', '/Деактивировать']
mobile_block = ['Назад', 'Главное меню', 'Закончить']


# Команда активации бота /Start
@dp.message_handler(commands=['start'])
async def subscribe(message: types.Message):
    # далем проверку существует ли пользователь в БД если пользователя нет, то предлагаем ему пройти регистрацию
    try:
        if not db.client_exists(message.from_user.id):
            # если пользователя нет в базе
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add('/Зарегистрироваться')
            await message.answer("Вы не зарегистированы, необходимо выполнить регистрацию",
                                 reply_markup=markup)
        # если пользователь есть то проверяем статус is active, если False подписка не активная
        elif db.client_exists(message.from_user.id) == True and db.check_is_active(message.from_user.id) == False:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add('/start')
            await message.answer("Ваша учетная запись ожидает активации, "
                                 "Ваш ID {}, сообщите БТ.".format(message.from_user.id),
                                 reply_markup=markup)
        # проверка записи пользователя на курс
        # все проверки пройдены, значит пользователь зарегистрирован и активирован.
        # создаим клавиатуру в цикле ( перенести клавиатуры в отдельный файл py и импортировать как класс)
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)  # создаем обьект клавиатуры
            for i in main_list_button:
                markup.add(i)
            await message.answer(f"Добро пожаловать в информативный бот {name_bot}", reply_markup=markup)
    except Exception as exc:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add('/start')
        await bot.send_message(272893637, 'Ошибка функция subscribe ' + str(exc))
        await bot.send_message(message.from_user.id, 'Произошла ошибка попробуйте позже, для повторного ввода нажмите '
                                                     'кнопку  start', reply_markup=markup)


# БЛОК КОДА РЕГИСТРАЦИИ ПОЛЬЗОВАТЕЛЯ В БОТЕ ( ЗАПОЛНЯЕМ ТАБЛИЦУ clients и устанавливем статус is_active = 0 )
# Добавляем возможность отмены, если пользователь передумал заполнять
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='Отмена регистрации', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    # проверяем текущиий статус
    current_state = await state.get_state()
    # если статус пустой то возвращаем None
    if current_state is None:
        return None
    # если статус не пустой, то завершаем статус
    await state.finish()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('/Зарегистрироваться')
    await message.reply('Вы отменили регистрацию, для повторного запуска регистрации нажмите на кнопку',
                        reply_markup=markup)


@dp.message_handler(commands=['Зарегистрироваться'])
async def reg_start(message: types.Message):
    # проверяем существует ли пользователь в бд
    # если пользователя нет, то запускаем наш статус регистрации и запрашиваем имя
    try:
        if not db.client_exists(message.from_user.id):  # проверка пользователья существует ли БД
            await Registration.f_name.set()  # устанавливаем статус регистрации на запрос имени
            markup = types.ReplyKeyboardRemove()  # удалем клавиатуру
            await message.answer("На любом этапе регистрации вы можете от нее отказаться, написал мне отмена "
                                 "регистрации, либо нажав на кубик рядом с кнопкой отправки сообщения")
            await message.answer("Введите имя, например Александр", reply_markup=markup)  # запрашиваем имя
        # иначе пользователь существует в бд и предлагаем ему нажать start
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add('/start')
            await message.answer("Вы уже зарегистрированы, нажмите на кнопку start для перехода в главное меню",
                                 reply_markup=markup)
    except Exception as exc:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add('/start')
        await bot.send_message(272893637, 'Ошибка функция reg_start ' + str(exc))
        await bot.send_message(message.from_user.id, 'Произошла ошибка попробуйте позже, для повторного ввода нажмите '
                                                     'кнопку  start', reply_markup=markup)


# Сюда приходит ответ с именем
@dp.message_handler(state=Registration.f_name)  # проверяем статус у сообщения
async def name_request(message: types.Message, state: FSMContext):
    # открываем state
    async with state.proxy() as data:
        # заносим наше имя
        data['f_name'] = message.text
    # команда для установки слудующего статуса
    await Registration.next()
    # запрашиваем фамилию
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('отмена регистрации')
    await message.answer("Введите фамилию, например Смирнов", reply_markup=markup)


# Сюда приходит ответ с Фамилией
@dp.message_handler(state=Registration.l_name)  # проверяем статус
async def last_name_request(message: types.Message, state: FSMContext):
    # открываем статусы
    async with state.proxy() as data:
        # заносим фамилию
        data['l_name'] = message.text
    # устанавливаем следующий статус
    await Registration.next()
    # запрашиваем возраст,  обязательно целое число
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('отмена регистрации')
    await message.answer("Введите возраст числом, например 25", reply_markup=markup)


# проверяем возраст,  проверяем что статус запроса возраста установлен Registration.age, проверяем что пришло
# действительно число, функция isdigit() возращает True если там число, иначе false, если пришло не число, запрашиваем
# повторно или можем отменить регистрацию /cancel
@dp.message_handler(lambda message: not message.text.isdigit(), state=Registration.age)
async def process_age_invalid(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('отмена регистрации')
    return await message.answer("Вы ввели не число,введите повторно например 25", reply_markup=markup)


# проверяем  возраст, пришло действительно число и статус установлен  Registration.age
@dp.message_handler(lambda message: message.text.isdigit(), state=Registration.age)
async def process_age(message: types.Message, state: FSMContext):
    await Registration.next()  # устанавливаем следующий статус
    await state.update_data(age=int(message.text))  # делаем update списка и конвертируем возраст в число
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)  # создам клавиатуру для запроса пола
    markup.add("М", "Ж")  # добавляем 2 кнопки
    await message.answer("Укажите пол (кнопкой)", reply_markup=markup)  # запрашиваем ввод пола


# проверяем какое пришло сообщение со статусом Registration.gender, если пришло не "М" или "Ж" то запрашиваем
# повторно пол
@dp.message_handler(lambda message: message.text not in ["М", "Ж"], state=Registration.gender)
async def process_gender_invalid(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)  # создам клавиатуру для запроса пола
    markup.add("М", "Ж")  # добавляем 2 кнопки
    return await message.answer("Неизвестный пол. Укажите пол кнопкой на клавиатуре", reply_markup=markup)


# хендлеры работают сверху вниз, то есть выполняется сначала верхний и потом уже нижний, здесь достаточно проверить
# статус сообщение, он должен быть Registration.gender
@dp.message_handler(state=Registration.gender)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:  # открываем статусы
        data['gender'] = message.text  # записываем пол
        markup = types.ReplyKeyboardRemove()  # создаем обьект который удаляет клавиатуру
        await Registration.next()  # устанавливаем следующий сатус
        await message.answer("Укажите ваш город:", reply_markup=markup)  # запрашиваем город и удаляем клавиатуру


# принимаем название города, со статусом Registration.city, можно конечно сделать проверку через справочник городов,
# но пока не будем этого делать
@dp.message_handler(state=Registration.city)
async def process_phone(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:  # открываем статусы
            data['city'] = message.text  # записываем город
            await message.reply("Регистрируемся, ожидайте")  # отправляем сообщение пользователю
            # вызываем функцию регистраци пользователя и передаем полученные параметры
            reg = db.client_reg(user_id=message.from_user.id, date_reg=datetime.now().strftime("%d-%m-%Y %H:%M"),
                                f_name=data['f_name'], l_name=data['l_name'],
                                age=data['age'], gender=data['gender'], city=data['city'])
            #  отправляем сообщение об успешной регистрации.
            await message.answer("Ваша учетная запись ожидает активации, "
                                 "Ваш ID {}, сообщите его БТ".format(
                message.from_user.id))
            await state.finish()  # устанавливем что все статусы мы завершили и выходим из данного статуса
    except Exception as exc:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add('/start')
        await bot.send_message(272893637, 'Ошибка функция process_phone ' + str(exc))
        await bot.send_message(message.from_user.id, 'Произошла ошибка попробуйте позже, для повторного ввода нажмите '
                                                     'кнопку  start', reply_markup=markup)


# КОНЕЦ БЛОКА КОДА РЕГИСТРАЦИИ ПОЛЬЗОВАТЕЛЯ БЛОК

# БЛОК КОДА АДМИНИСТРАТИВНОГО МЕНЮ И ФУНКЦИЙ
# команда /admin при вызове команды пользователем, проверяем что у пользователя статус admin True  иначе падаем в else
@dp.message_handler(commands=['admin'])
async def adm(message: types.Message):
    try:
        if db.check_is_admin(message.from_user.id):  # проверяем статус Admin 1 или 0
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)  # создаем обьект клавиатуру
            for i in admin_list_button:  # в цикле бежим по списку и добавляем кнопки
                markup.add(i)  # добавляем кнопки
            await message.answer("Вы в административном меню, выберите действие на клавиатуре", reply_markup=markup)
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add('/help')
            await message.answer("Неизвестная команда, для вызова справки нажмите кнопку help",
                                 reply_markup=markup)
    except Exception as exc:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add('/start')
        await bot.send_message(272893637, 'Ошибка функция adm ' + str(exc))
        await bot.send_message(message.from_user.id, 'Произошла ошибка попробуйте позже, для повторного ввода нажмите '
                                                     'кнопку  start', reply_markup=markup)


# команда для активация учетной записи администратором ( меняем статус записи,  поле is_active = 1)
@dp.message_handler(commands=['Активировать'])
async def user_activation(message: types.Message):
    try:
        if db.check_is_admin(message.from_user.id):  # проверяем что пользователь который вызывал команду администратор
            await Activations.user_id.set()  # устанавл иваем статус на запрос имени курса
            markup = types.ReplyKeyboardRemove()
            await message.answer("Укажите id пользователя",
                                 reply_markup=markup)
        else:
            pass
    except Exception as exc:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add('/start')
        await bot.send_message(272893637, 'Ошибка функция user_activation ' + str(exc))
        await bot.send_message(message.from_user.id, f'Произошла ошибка попробуйте позже, для повторного ввода нажмите '
                                                     'кнопку  start', reply_markup=markup)


# Добавляем возможность отмены, если пользователь передумал заполнять
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('/Активировать')
    await message.reply('Вы отменили активацию, для повторного запуска активации нажмите на кнопку',
                        reply_markup=markup)


# Сюда приходит ответ с id пользователя
@dp.message_handler(state=Activations.user_id)  # ловим статус сообщения в нашем случае это users_id
async def user_activation_get_dep(message: types.Message, state: FSMContext):
    # открываем state
    async with state.proxy() as data:
        data['user_id'] = message.text  # записываем user_id
        await Activations.next()  # устанавливаем следующий статус по порядку
        markup = types.ReplyKeyboardRemove()  # создаем обьект удаления клавиатуры
        await bot.send_message(message.from_user.id,
                               "Для активации учетной записи, отправьте номер отдела",
                               reply_markup=markup)


# Сюда приходит ответ с department
@dp.message_handler(state=Activations.department)
async def process_activate_id(message: types.Message, state: FSMContext):
    try:
        # открываем state
        async with state.proxy() as data:
            # заносим department
            data['department'] = message.text
            if db.client_exists(data['user_id']):
                print(1)
                db.active_client(data['user_id'],
                                 data['department'])  # активируем пользователя, меняем статус в таблице clients
                # is_active = 1
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
                markup.add('/start')
                await bot.send_message(data['user_id'], 'Ваша учетная запись активирована, нажмите на кнопку /start',
                                       reply_markup=markup)
                await message.answer(
                    'Учетная запись {} активирована, сообщение отправлено пользователю'.format(data['user_id']))
                await state.finish()
            else:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
                markup.add('/Активировать')
                markup.add('/start')
                await bot.send_message(message.from_user.id, 'Учетная запись с данным id не существует, проверьте id',
                                       reply_markup=markup)
                await state.finish()
    except Exception as exc:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add('/start')
        await bot.send_message(272893637, 'Ошибка функция process_activate_id ' + str(exc))
        await bot.send_message(message.from_user.id, 'Произошла ошибка попробуйте позже, для повторного ввода нажмите '
                                                     'кнопку  start', reply_markup=markup)
        await state.finish()


@dp.message_handler(commands=['Факультеты'])
async def faculties(message: types.Message):
    # проверяем существует ли пользователь в бд
    # если пользователя нет, то запускаем наш статус запроса типа обучения
    try:
        if (db.check_is_active(message.from_user.id)):  # проверка пользователя, активирована ли учетная запись
            await get_message.type_traning.set()  # устанавливаем статус выбора запроса типа обучения
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)  # создаем обьект клавиатуры
            type_traning = db.get_type_of_traning()  # получаем список направлений
            for i in type_traning.keys():
                markup.add(i)
            await message.answer("Выберите тип образования используя клавиатуру",
                                 reply_markup=markup)  # запрашиваем факультет
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            await message.answer("Ваша учетная запись ожидает активации,Ваш ID {}, сообщите БТ.".format(
                message.from_user.id), reply_markup=markup)
    except Exception as exc:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add('/start')
        await bot.send_message(272893637, 'Ошибка функция faculties ' + str(exc))
        await bot.send_message(message.from_user.id, 'Произошла ошибка попробуйте позже, для повторного ввода нажмите '
                                                     'кнопку  start', reply_markup=markup)


# обрабатываем кнопку назад в статусе типа обучения
@dp.message_handler(Text(equals='Назад', ignore_case=True), state=get_message.Faculty)
async def back_action_faculty(message: types.Message, state: FSMContext):
    try:
        current_state = await state.get_state()  # получаем текущий статус
        if current_state == 'get_message:Faculty':  # проверяем что статус Faculty
            await get_message.type_traning.set()  # устаналиваем предыдущий статус
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)  # создаем обьект клавиатуры
            type_traning = db.get_type_of_traning()  # получаем список направлений
            for i in type_traning.keys():
                markup.add(i)
            await message.answer("Выберите тип образования используя клавиатуру",
                                 reply_markup=markup)  # запрашиваем факультет
    except Exception as exc:
        await state.finish()  # завершаем статусы
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add('/start')
        await bot.send_message(272893637, 'Ошибка функция back_action_faculty ' + str(exc))
        await bot.send_message(message.from_user.id,
                               'Произошла ошибка попробуйте позже, для повторного ввода нажмите '
                               'кнопку  start', reply_markup=markup)


# обрабатываем кнопку назад в статусе выбора факультета
@dp.message_handler(Text(equals='Назад', ignore_case=True), state=get_message.Direction)
async def back_action_direction(message: types.Message, state: FSMContext):
    try:
        current_state = await state.get_state()  # получаем текущий статус
        if current_state == 'get_message:Direction':  # проверяем что статус Direction
            await get_message.Faculty.set()  # устаналиваем предыдущий статус Faculty
            async with state.proxy() as data:
                faculty_list = db.get_faculty(data['type_traning'])  # получаем  список факультетов
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            for i in faculty_list:
                markup.add(i)
            markup.add('Назад')
            await message.answer("Выберите  факультет, используя клавиатуру", reply_markup=markup)
    except Exception as exc:
        await state.finish()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add('/start')
        await bot.send_message(272893637, 'Ошибка функция back_action_direction ' + str(exc))
        await bot.send_message(message.from_user.id,
                               'Произошла ошибка попробуйте позже, для повторного ввода нажмите '
                               'кнопку  start', reply_markup=markup)


# обрабатываем кнопку назад и главное меню на финальном статусе
@dp.message_handler(Text(equals='Назад', ignore_case=True), state=get_message.last_state)
@dp.message_handler(Text(equals='Главное меню', ignore_case=True), state=get_message.last_state)
async def back_action_last(message: types.Message, state: FSMContext):
    current_state = await state.get_state()  # получаем текущий статус
    try:
        if current_state == 'get_message:last_state' and message.text == 'Назад':
            await get_message.Faculty.set()  # устаналиваем предыдущий статус
            async with state.proxy() as data:
                # получаем список направлений
                directions_list = db.get_directions(int(data['type_traning']), int(data['Faculty']))
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            for i in directions_list:
                markup.add(i)
            markup.add('Назад')
            await message.answer("Выбирите направление, используя клавиатуру", reply_markup=markup)
            await get_message.next()
        elif current_state == 'get_message:last_state' and message.text == 'Главное меню':
            await get_message.type_traning.set()  # устанавливаем статус выбора типа обучения
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)  # создаем обьект клавиатуры
            type_traning = db.get_type_of_traning()  # получаем список направлений
            for i in type_traning.keys():
                markup.add(i)
            await message.answer("Выберите тип образования используя клавиатуру",
                                 reply_markup=markup)  # запрашиваем факультет

    except Exception as exc:
        await state.finish()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add('/start')
        await bot.send_message(272893637, 'Ошибка функция back_action_last ' + str(exc))
        await bot.send_message(message.from_user.id,
                               'Произошла ошибка попробуйте позже, для повторного ввода нажмите '
                               'кнопку  start', reply_markup=markup)


# Сюда приходит ответ с выбором типа образования
@dp.message_handler(state=get_message.type_traning)  # проверяем статус у сообщения
async def get_type_traning(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            # получаем id направления и записываем
            id = db.get_id_type_of_traning(message.text)
            # получаем список факультетов по типу образования
            faculty_list = db.get_faculty(id[0])
            data['type_traning'] = id[0]
        # команда для установки слудующего статуса
        await get_message.next()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        for i in faculty_list:
            markup.add(i)
        markup.add('Назад')
        await message.answer("Выберите  факультет, используя клавиатуру", reply_markup=markup)

    except Exception as exc:
        await state.finish()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add('/start')
        await bot.send_message(272893637, 'Ошибка функция get_type_traning ' + str(exc))
        await bot.send_message(message.from_user.id, 'Произошла ошибка попробуйте позже, для повторного ввода нажмите '
                                                     'кнопку  start', reply_markup=markup)


# Сюда приходит ответ с факультетом
@dp.message_handler(state=get_message.Faculty)  # проверяем статус
async def get_faculty(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            # получаем id факультета и записываем
            id = db.get_faculty_id(data['type_traning'], message.text)
            data['Faculty'] = id
            # получаем список направлений для нашего типа обучения и факультета
            directions_list = db.get_directions(int(data['type_traning']), int(data['Faculty']))
        # устанавливаем следующий статус
        await get_message.next()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        for i in directions_list:
            markup.add(i)
        markup.add('Назад')
        # запрашиваем выбор направления
        await message.answer("Выбирите направление, используя клавиатуру", reply_markup=markup)
    except Exception as exc:
        await state.finish()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add('/start')
        await bot.send_message(272893637, 'Ошибка функция get_faculty ' + str(exc))
        await bot.send_message(message.from_user.id, 'Произошла ошибка попробуйте позже, для повторного ввода нажмите '
                                                     'кнопку  start', reply_markup=markup)


# Сюда приходит ответ с направлением
@dp.message_handler(state=get_message.Direction)  # проверяем статус
async def get_direction(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            # получаем id направления и записываем
            id = db.get_direction_id(data['type_traning'], data['Faculty'], message.text)
            data['Direction'] = id
            # получаем текст по нашему типу обучения,факультету и направления
            message_list = db.get_message(int(data['type_traning']), int(data['Faculty']), int(data['Direction']))
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            for i in message_list:
                await  bot.send_message(message.from_user.id, i, reply_markup=markup)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            for i in mobile_block:
                markup.add(i)
            await bot.send_message(message.from_user.id, 'Выберите действие', reply_markup=markup)
            # устанавливаем следующий статус
            await get_message.next()
            # записываем лог
            db.mobile_units_log_insert(user_id=message.from_user.id,
                                       date=datetime.now().strftime("%d-%m-%Y %H:%M"),
                                       department=db.get_department_user(message.from_user.id),
                                       type_traning_id=int(data['type_traning']),
                                       faculties_id=int(data['Faculty']),
                                       directions_id=int(data['Direction']))


    except Exception as exc:
        await state.finish()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add('/start')
        await bot.send_message(272893637, 'Ошибка функция get_direction ' + str(exc))
        await bot.send_message(message.from_user.id, 'Произошла ошибка попробуйте позже, для повторного ввода нажмите '
                                                     'кнопку  start', reply_markup=markup)


# заканчиваем статус мобильного блока
@dp.message_handler(state=get_message.last_state)  # проверяем статус
async def get_last(message: types.Message, state: FSMContext):
    try:
        await state.finish()  # завершаем статус
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        for i in main_list_button:
            markup.add(i)
        await bot.send_message(message.from_user.id, f'Добро пожаловать в информативный бот {name_bot}',
                               reply_markup=markup)
    except Exception as exc:
        await state.finish()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add('/start')
        await bot.send_message(272893637, 'Ошибка функция get_last ' + str(exc))
        await bot.send_message(message.from_user.id, 'Произошла ошибка попробуйте позже, для повторного ввода нажмите '
                                                     'кнопку  start', reply_markup=markup)


# обработаем весь остальной текст
@dp.message_handler(content_types=['text'])
async def send_auth_text(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('/start')
    await bot.send_message(message.from_user.id, 'Я этого не понимаю, для перехода в гланое меню нажмите на кнопку '
                                                 '/start', reply_markup=markup)


# запускаем бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
