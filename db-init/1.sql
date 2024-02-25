-- Индивидуальная нумерация тикетов для каждого пользователя
--
-- task_id удаляем, вместо добавляем составной ключ onwer_id + ticket_number
-- 11.02.2024

ALTER TABLE tasks ADD COLUMN task_number SERIAL;
COMMENT ON COLUMN tasks.task_number IS 'Номер задачи для каждого пользователя';

UPDATE tasks
SET task_number = sub.rn
FROM (
    SELECT task_id, ROW_NUMBER() OVER (PARTITION BY owner_id ORDER BY task_id) AS rn
    FROM tasks
) AS sub
WHERE tasks.task_id = sub.task_id;

CREATE TABLE tasks_new (
    owner_id BIGINT NOT NULL,
    task_number SERIAL,
    status task_status,
    task_text TEXT NOT NULL,
    creation_time TIMESTAMP DEFAULT current_timestamp,    
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    postponement_count INT DEFAULT 0,
    completion_comment TEXT,
    PRIMARY KEY (owner_id, task_number),
    FOREIGN KEY (owner_id) REFERENCES users(telegram_id)
);

INSERT INTO tasks_new (owner_id, task_number, status, task_text, start_time, end_time, postponement_count, completion_comment)
SELECT owner_id, task_number, status, task_text, start_time, end_time, postponement_count, completion_comment
FROM tasks;

DROP TABLE tasks;

ALTER TABLE tasks_new RENAME TO tasks;

SELECT column_name, data_type, column_default, is_nullable, pgd.description
FROM information_schema.columns col
LEFT JOIN pg_description pgd ON col.table_name::regclass = pgd.objoid
AND col.ordinal_position = pgd.objsubid
WHERE table_name = 'tasks';

COMMENT ON TABLE tasks IS 'Задачи для выполнения';

-- Комментарии к столбцам задач
COMMENT ON COLUMN tasks.task_number IS 'Номер задачи для каждого пользователя';
COMMENT ON COLUMN tasks.owner_id IS 'ID владельца задачи (ссылка на пользователя)';
COMMENT ON COLUMN tasks.status IS 'Статус задачи';
COMMENT ON COLUMN tasks.task_text IS 'Текст задачи';
COMMENT ON COLUMN tasks.start_time IS 'Дата и время начала выполнения';
COMMENT ON COLUMN tasks.end_time IS 'Дата и время окончания выполнения';
COMMENT ON COLUMN tasks.postponement_count IS 'Счетчик откладываний';
COMMENT ON COLUMN tasks.completion_comment IS 'Комментарий по итогу выполнения';

CREATE OR REPLACE FUNCTION increment_task_number()
RETURNS TRIGGER AS $$
DECLARE
    last_task_number INT;
BEGIN
    SELECT COALESCE(MAX(task_number), 0) INTO last_task_number FROM tasks WHERE owner_id = NEW.owner_id;
    NEW.task_number = last_task_number + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_increment_task_number
BEFORE INSERT ON tasks
FOR EACH ROW
EXECUTE FUNCTION increment_task_number();