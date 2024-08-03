DROP DATABASE IF EXISTS yugicollectionapp;

CREATE DATABASE yugicollectionapp;

USE yugicollectionapp;

CREATE TABLE cards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    archetype VARCHAR(255),
    type VARCHAR(255),
    `desc` TEXT,  -- Usar comillas invertidas para evitar conflicto con la palabra reservada
    quantity INT DEFAULT 0,
    rarity VARCHAR(255),
    price DECIMAL(10, 2)
);

DROP USER IF EXISTS 'yUg1C0ll3ct10n'@'localhost';

CREATE USER 'yUg1C0ll3ct10n'@'localhost' IDENTIFIED BY '%2If3jH$4HvotW&GlD';

GRANT SELECT, INSERT, UPDATE, DELETE ON yugicollectionapp.* TO 'yUg1C0ll3ct10n'@'localhost';

GRANT CREATE ROUTINE, ALTER ROUTINE, EXECUTE ON yugiohcollectionapp.* TO 'yUg1C0ll3ct10n'@'localhost';

-- Otorga los permisos necesarios al usuario 'yUg1C0ll3ct10n'
GRANT ALL PRIVILEGES ON *.* TO 'yUg1C0ll3ct10n'@'localhost' WITH GRANT OPTION;

-- Aplica los cambios
FLUSH PRIVILEGES;

ALTER TABLE cards CHANGE `desc` description TEXT;

CREATE TABLE rarities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    score INT NOT NULL,
    name VARCHAR(255) NOT NULL
);
