-- message.message_id сообщения из телеги будем сохранять

ALTER TABLE tasks ADD COLUMN telegram_message_id bigint;  
COMMENT ON COLUMN tasks.telegram_message_id IS 'Telegram message id (for editing)';