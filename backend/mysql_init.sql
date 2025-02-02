CREATE DATABASE IF NOT EXISTS chatbot;

USE chatbot;

CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100),
    password VARCHAR(100)
);

INSERT INTO users (username, password)
VALUES ('test_user', '$2b$12$rAmQ/AWbhQZdaWrkA22KiuZnmPw1j8glx7ORGeA/Wm7i9Tjo59HlO');

-- UPDATE users
-- SET username = 'test_user', password = '$2b$12$rAmQ/AWbhQZdaWrkA22KiuZnmPw1j8glx7ORGeA/Wm7i9Tjo59HlO'
-- WHERE id = 1;

