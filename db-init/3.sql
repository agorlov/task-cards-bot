ALTER TABLE tasks
ADD COLUMN planned_date TIMESTAMP;

COMMENT ON COLUMN tasks.planned_date IS 'Дата, начиная с которой задача считается актуальной';

UPDATE tasks
SET planned_date = creation_time;