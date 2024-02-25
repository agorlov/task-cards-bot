ALTER TABLE users
ADD COLUMN hello_failure_count integer DEFAULT 0,
ADD COLUMN hello_failure_date timestamp without time zone;
COMMENT ON COLUMN users.hello_failure_count IS 'Счетчик неудачных отправок последнего сообщения';
COMMENT ON COLUMN users.hello_failure_date IS 'Дата последней неудачной попытки отправки сообщения';