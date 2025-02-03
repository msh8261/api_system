CREATE DATABASE IF NOT EXISTS chatbot;

USE chatbot;

CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) UNIQUE NOT NULL,  -- Increase the length to 255 and add NOT NULL for better consistency
    password VARCHAR(255) NOT NULL  -- Add NOT NULL to ensure password is required
);

CREATE TABLE IF NOT EXISTS chat_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    question TEXT NOT NULL,  -- Make sure question is not nullable
    answer TEXT NOT NULL,  -- Make sure answer is not nullable
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE  -- Add foreign key constraint and set ON DELETE CASCADE for referential integrity
);

INSERT INTO users (username, password)
VALUES ('test_user', '$2b$12$rAmQ/AWbhQZdaWrkA22KiuZnmPw1j8glx7ORGeA/Wm7i9Tjo59HlO');



