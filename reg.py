# импортируем библиотеку для работы со статусами
from aiogram.dispatcher.filters.state import State, StatesGroup

class Registration(StatesGroup):
    """
    Класс статусов регистрации пользователя
    """
    f_name = State()
    l_name = State()
    age = State()
    gender = State()
    city = State()

