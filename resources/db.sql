CREATE TABLE rarities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE,
    score INT DEFAULT 0
);

CREATE TABLE cards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    archetype VARCHAR(255),
    type VARCHAR(255),
    description TEXT
);

CREATE TABLE card_sets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    card_id INT,
    set_name VARCHAR(255),
    set_code VARCHAR(255),
    rarity_id INT,
    set_price DECIMAL(10, 2),
    FOREIGN KEY (card_id) REFERENCES cards(id),
    FOREIGN KEY (rarity_id) REFERENCES rarities(id)
);

CREATE TABLE card_prices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    card_id INT,
    cardmarket_price DECIMAL(10, 2),
    tcgplayer_price DECIMAL(10, 2),
    ebay_price DECIMAL(10, 2),
    amazon_price DECIMAL(10, 2),
    coolstuffinc_price DECIMAL(10, 2),
    FOREIGN KEY (card_id) REFERENCES cards(id)
);
