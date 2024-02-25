-- Очки кармы пользователя

ALTER TABLE users
ADD COLUMN karma_score INT DEFAULT 0;

COMMENT ON COLUMN users.karma_score IS 'Очки кармы пользователя';