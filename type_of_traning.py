# импортируем библиотеку для работы со статусами
from aiogram.dispatcher.filters.state import State, StatesGroup


class get_message(StatesGroup):
    """
    Класс статусов получения сообщений
    """
    type_traning = State()
    Faculty = State()
    Direction = State()
    last_state = State()