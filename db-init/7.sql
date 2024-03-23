-- Сохранение текста как embedding, для того чтобы не добавлять похожие дела
ALTER TABLE tasks ADD COLUMN embedding DOUBLE PRECISION[];
COMMENT ON COLUMN tasks.embedding IS 'Embedding for the task text';
