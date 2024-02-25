-- Создание таблицы пользователей
CREATE TABLE users (
    telegram_id BIGINT PRIMARY KEY,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    lastname VARCHAR(55),
    firstname VARCHAR(55),
    username VARCHAR(255) UNIQUE,
    email VARCHAR(255) UNIQUE,
    phone_number VARCHAR(20) UNIQUE,
    lastmessage TIMESTAMP
);

-- Комментарий к таблице пользователей
COMMENT ON TABLE users IS 'Пользователи приложения';

-- Комментарии к столбцам пользователей
COMMENT ON COLUMN users.telegram_id IS 'ID пользователя из Telegram';
COMMENT ON COLUMN users.registration_date IS 'Дата и время регистрации';
COMMENT ON COLUMN users.firstname IS 'Имя';
COMMENT ON COLUMN users.lastname IS 'Фамилия';
COMMENT ON COLUMN users.username IS 'Имя пользователя (логин)';
COMMENT ON COLUMN users.email IS 'Адрес электронной почты';
COMMENT ON COLUMN users.phone_number IS 'Номер телефона';
COMMENT ON COLUMN users.lastmessage IS 'Дата последнего отправленного сообщения';

-- Создание ENUM для статусов задачи
CREATE TYPE task_status AS ENUM ('ожидает выполнения', 'в работе', 'завершена', 'отменена');

-- Создание таблицы задач
CREATE TABLE tasks (
    task_id SERIAL PRIMARY KEY,
    owner_id BIGINT NOT NULL,
    status task_status,
    parent_task_id INT,
    task_text TEXT NOT NULL,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    postponement_count INT DEFAULT 0,
    completion_comment TEXT,
    FOREIGN KEY (owner_id) REFERENCES users(telegram_id),
    FOREIGN KEY (parent_task_id) REFERENCES tasks(task_id)
);

-- Комментарий к таблице задач
COMMENT ON TABLE tasks IS 'Задачи для выполнения';

-- Комментарии к столбцам задач
COMMENT ON COLUMN tasks.task_id IS 'Уникальный идентификатор задачи';
COMMENT ON COLUMN tasks.owner_id IS 'ID владельца задачи (ссылка на пользователя)';
COMMENT ON COLUMN tasks.status IS 'Статус задачи';
COMMENT ON COLUMN tasks.parent_task_id IS 'ID родительской задачи (ссылка на другую задачу)';
COMMENT ON COLUMN tasks.task_text IS 'Текст задачи';
COMMENT ON COLUMN tasks.start_time IS 'Дата и время начала выполнения';
COMMENT ON COLUMN tasks.end_time IS 'Дата и время окончания выполнения';
COMMENT ON COLUMN tasks.postponement_count IS 'Счетчик откладываний';
COMMENT ON COLUMN tasks.completion_comment IS 'Комментарий по итогу выполнения';


ALTER TABLE tasks
ADD COLUMN creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP;