# импортируем библиотеку для работы с sql
import pyodbc
# импортируем параметры для подключения к ms sql
from config import param_sql, prefix_table


# создадим класс для работы с sql
class SQLazure:
    def __init__(self, ):
        """Подключаемся к БД и сохраняем курсор соединения"""
        pass

    def get_connection(self, ):
        self.connection = pyodbc.connect(
            server=param_sql['server'],
            database=param_sql['database'],
            user=param_sql['user'],
            password=param_sql['password'],
            tds_version=param_sql['tds_version'],
            port=param_sql['port'],
            driver=param_sql['driver'],
            timeout=param_sql['timeout']
        )
        self.cursor = self.connection.cursor()
        return self.connection, self.cursor

    def close_connection(self):
        """Закрываем соединение с БД"""
        self.connection.close()

# БЛОК КОДА ФУНКЦИЙ ДЛЯ РАБОТЫ С ТАБЛИЦЕЙ clients
    def client_exists(self, user_id):
        """Проверяем, есть ли уже пользователь в базе
        :param user_id: id пользователя
        :return: True or False
        """
        self.connection, self.cursor = self.get_connection()
        with self.connection:
            result = self.cursor.execute(f'SELECT * FROM {prefix_table}_clients_bot WHERE User_id = ?',
                                         (user_id,)).fetchall()
            return bool(len(result))

    def client_reg(self, user_id, date_reg, f_name, l_name, age, gender, city, is_active=0, admin=0):
        """Функция для регистрации нового пользователя
        :param user_id: id пользователя
        :param date_reg: Datetime.now()
        :param f_name: Имя пользвателя
        :param l_name:  Фамилия
        :param age: Возвраст
        :param gender: Пол
        :param city: Город
        :param is_active: Статус активации учетной записи
        :param admin:  Административная учетная записи
        :return:
        """
        self.connection, self.cursor = self.get_connection()
        with self.connection:
            return self.cursor.execute(f"INSERT INTO {prefix_table}_clients_bot VALUES(?,?,?,?,?,?,?,?,NULL,?)",
                                       (user_id, date_reg, f_name, l_name, age, gender, city,
                                        is_active, admin))

    def check_is_active(self, user_id):
        """Функция для проверки активации учетной записи
        :param user_id: id пользователя
        :return: 1 - если активирована 0 - не активирована
        """
        self.connection, self.cursor = self.get_connection()
        with self.connection:
            status = []
            for i in self.cursor.execute(
                    f'SELECT Is_active FROM {prefix_table}_clients_bot WHERE User_id = ?', (user_id,)).fetchall():
                status.append(i.Is_active)
            status = int(status[0])
            return status

    def check_is_admin(self, user_id):
        """Функция для проверки прав администратора учетной записи
        :param user_id: id пользователя
        :return: 1 - если администратор 0 - не администратор
        """
        self.connection, self.cursor = self.get_connection()
        with self.connection:
            status = []
            for i in self.cursor.execute(
                    f'SELECT Admin FROM {prefix_table}_clients_bot WHERE User_id = ?', (user_id,)).fetchall():
                status.append(i.Admin)
            status = int(status[0])
            return status

    def active_client(self, user_id, department, is_active=1):
        """Функция для активация учетной записи
        :param user_id: id пользователя
        :param department: номер отдела
        :param is_active: признак что запись активирована
        :return: Bool
        """
        self.connection, self.cursor = self.get_connection()
        with self.connection:
            self.cursor.execute(f"UPDATE {prefix_table}_clients_bot SET Is_active = ?, Department =? WHERE user_id = ?",
                                (is_active, department, user_id))
        return True

    def get_type_of_traning(self):
        """
        Функция для получения список всех типов образования
        :return: словарь типов образования в формате Name:ID
        """
        self.connection, self.cursor = self.get_connection()
        dict_type_of_traning = {}
        with self.connection:
            for i in self.cursor.execute(f'select ID, Name from {prefix_table}_type_of_traning_bot').fetchall():
                dict_type_of_traning.update({i.Name: i.ID})
        return dict_type_of_traning

    def get_id_type_of_traning(self, name):
        """
        Функция для получения id типа образования по имени
        :param name: имя типа образования
        :return: id типа образования
        """
        self.connection, self.cursor = self.get_connection()
        id = []
        with self.connection:
            for i in self.cursor.execute(f'select ID from {prefix_table}_type_of_traning_bot where Name =?',
                                         name).fetchall():
                id.append(i.ID)
        return id

# БЛОК КОДА ПОЛУЧЕНИЯ ФАКУЛЬТЕТОВ
    def get_faculty(self, type_of_traning):
        """
        Функция для получения списка факультетов
        :param type_of_traning: ID типа образования
        :return: список факультетов по данному типу образования
        """
        self.connection, self.cursor = self.get_connection()
        faculty_list = []
        with self.connection:
            for i in self.cursor.execute(f'select Name from {prefix_table}_Faculties_bot where Type_traning_id = ?',
                                         (type_of_traning)).fetchall():
                faculty_list.append(i.Name)
        return faculty_list

    def get_faculty_id(self, type_of_traning, faculty_name):
        """
        Функция для получения id факультета
        :param type_of_traning: ID типа образования
        :param faculty_name: имя факультета
        :return: id факультета
        """
        self.connection, self.cursor = self.get_connection()
        id = None
        with self.connection:
            for i in self.cursor.execute(
                    f'select ID from {prefix_table}_Faculties_bot where Type_traning_id = ? and Name = ?',
                    (type_of_traning, faculty_name)).fetchall():
                id = i.ID
        return id

    def get_directions(self, id_type_of_traning, id_faculty):
        """
        Функция для получения списка направлений
        :param id_type_of_traning: ID типа образования
        :param id_faculty: ID факультета
        :return: имя направления
        """
        self.connection, self.cursor = self.get_connection()
        directions_list = []
        with self.connection:
            for i in self.cursor.execute(
                    f'select Name from {prefix_table}_Directions_bot where Type_traning_id = ? and '
                    'Faculties_id = ?', (id_type_of_traning, id_faculty)).fetchall():
                directions_list.append(i.Name)
        return directions_list

    def get_direction_id(self, type_of_traning_id, faculty_id, direction_name):
        """
        Функция для получения списка направлений
        :param type_of_traning_id: ID типа образования
        :param faculty_id: ID факультета
        :param direction_name: имя направления
        :return: id направления
        """
        self.connection, self.cursor = self.get_connection()
        id = None
        with self.connection:
            for i in self.cursor.execute(f'select ID from {prefix_table}_Directions_bot where Type_traning_id = ? and '
                                         'Faculties_id = ? and Name = ?', (type_of_traning_id, faculty_id,
                                                                           direction_name)).fetchall():
                id = i.ID
        return id

    def get_message(self, type_of_traning_id, faculty_id, direction_id):
        """
        Функция для получения сообщения исходя из предыдущего выбора пользователя
        :param type_of_traning_id: ID типа образования
        :param faculty_id: ID факультета
        :param direction_id: ID направления
        :return: сообщение
        """
        self.connection, self.cursor = self.get_connection()
        message_list = []
        with self.connection:
            for i in self.cursor.execute(
                    f'select Description from {prefix_table}_data_bot where Type_traning_id = ? and '
                    'Faculties_id = ? and Directions_id = ?', (type_of_traning_id, faculty_id,
                                                               direction_id)).fetchall():
                message_list.append(i.Description)
        return message_list

    # Блок кода для записи в лог мобильные блоки
    def mobile_units_log_insert(self, user_id, date, department, type_traning_id, faculties_id, directions_id):
        """
        Функция для добавления логов в таблицу
        :param user_id: id пользователя который делал запрос
        :param date: дата и время запроса
        :param department: номер отдела
        :param type_traning_id: ID типа образования
        :param faculties_id: ID факультета
        :param directions_id: ID направления
        :return:
        """
        self.connection, self.cursor = self.get_connection()
        with self.connection:
            return self.cursor.execute(f"INSERT INTO {prefix_table}_mobile_units_log_bot VALUES(?,?,?,?,?,?)",
                                       (user_id, date, department, type_traning_id, faculties_id, directions_id))

    def get_department_user(self, user_id):
        """
        Функция для получения номера отдела
        :param user_id: id пользователя который делал запрос
        :return: номер отдела пользователя
        """
        self.connection, self.cursor = self.get_connection()
        with self.connection:
            for i in self.cursor.execute(f"select Department from {prefix_table}_clients_bot where user_id = ?",
                                         (user_id)):
                return i.Department
