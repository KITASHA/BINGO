CREATE_QUIZZES_TABLE = """
CREATE TABLE IF NOT EXISTS quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number INTEGER,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    explanation TEXT,
    image_q TEXT,
    image_a TEXT,
    fever INTEGER DEFAULT 0,
    exclude INTEGER DEFAULT 0
);
"""