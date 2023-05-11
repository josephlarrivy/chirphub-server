DROP TABLE users;

CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY NOT NULL,
    username VARCHAR(20) NOT NULL,
    displayname VARCHAR(50) NOT NULL,
    avatar VARCHAR(200) NOT NULL,
    password_hash VARCHAR(100) NOT NULL,
    UNIQUE (id, username)
);