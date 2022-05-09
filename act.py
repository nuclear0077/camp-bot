# импортируем библиотеку для работы со статусами
from aiogram.dispatcher.filters.state import State, StatesGroup


class Activations(StatesGroup):
    """
    Класс статусов для активации пользователя
    """
    user_id = State()
    department = State()