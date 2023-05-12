DROP TABLE IF EXISTS chirps_tags;
DROP TABLE IF EXISTS chirp_likes;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS chirps;
DROP TABLE IF EXISTS users;

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
  rechirps INT DEFAULT 0,
  comments INT DEFAULT 0,
  FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE tags (
  id VARCHAR(36) PRIMARY KEY NOT NULL,
  name VARCHAR(100) NOT NULL,
  UNIQUE (id, name)
);

CREATE TABLE chirps_tags (
  chirp_id VARCHAR(36) NOT NULL,
  tag_id VARCHAR(36) NOT NULL,
  FOREIGN KEY (chirp_id) REFERENCES chirps (id),
  FOREIGN KEY (tag_id) REFERENCES tags (id)
);

CREATE TABLE comments (
  id VARCHAR(50) PRIMARY KEY NOT NULL,
  user_id VARCHAR(36) NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  text VARCHAR(290) NOT NULL,
  chirp_id VARCHAR(36) NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users (id),
  FOREIGN KEY (chirp_id) REFERENCES chirps (id)
);

CREATE TABLE chirp_likes (
  id SERIAL PRIMARY KEY,
  chirp_id VARCHAR(36) NOT NULL,
  user_id VARCHAR(50) NOT NULL,
  FOREIGN KEY (chirp_id) REFERENCES chirps (id),
  FOREIGN KEY (user_id) REFERENCES users (id)
);
