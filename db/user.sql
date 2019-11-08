CREATE TABLE User (
  id INTEGER PRIMARY KEY,
  sex VARCHAR(255),
  name VARCHAR(255),
  nickname VARCHAR(255),
  age VARCHAR(255),
  job VARCHAR(255),
  email VARCHAR(255) UNIQUE,
  telephone_number VARCHAR(255),
  password VARCHAR(255)
  comment VARCHAR (255)
);
