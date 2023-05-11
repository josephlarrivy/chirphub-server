DROP TABLE chirps CASCADE;
DROP TABLE users CASCADE;

CREATE TABLE users (
    id VARCHAR(50) PRIMARY KEY NOT NULL,
    username VARCHAR(30) NOT NULL,
    displayname VARCHAR(50) NOT NULL,
    avatar VARCHAR(300) NOT NULL,
    password_hash VARCHAR(100) NOT NULL,
    UNIQUE (id, username)
);

CREATE TABLE chirps (
  id VARCHAR(36) PRIMARY KEY NOT NULL,
  user_id VARCHAR(36) NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  text VARCHAR(290) NOT NULL,
  image VARCHAR(290) NOT NULL,
  likes INT DEFAULT 0,
  rechirps INT DEFAULT 0,
  comments INT DEFAULT 0,
  FOREIGN KEY (user_id) REFERENCES users (id)
);