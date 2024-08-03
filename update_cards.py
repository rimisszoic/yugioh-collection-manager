import requests
import mysql.connector
from mysql.connector import errorcode
import logging
from config_logging import setup_logging

# Configurar logging
setup_logging()

# Conexión a la base de datos
def connect_db():
    try:
        logging.info("Intentando conectar a la base de datos.")
        connection = mysql.connector.connect(
            host='localhost',
            user='yUg1C0ll3ct10n',
            password='%2If3jH$4HvotW&GlD',
            database='yugicollectionapp'
        )
        logging.info("Conexión a la base de datos exitosa.")
        return connection
    except mysql.connector.Error as err:
        logging.error(f"Error al conectar a la base de datos: {err}")
        raise

# Insertar o actualizar rarezas
def update_rarities(cursor, rarities):
    try:
        rarity_dict = {}
        cursor.execute("SELECT id, name FROM rarities")
        existing_rarities = cursor.fetchall()

        for rarity_id, rarity_name in existing_rarities:
            rarity_dict[rarity_name] = rarity_id

        for rarity in rarities:
            if rarity not in rarity_dict:
                cursor.execute("INSERT INTO rarities (name, score) VALUES (%s, %s)", (rarity, 0))
                cursor.connection.commit()
                cursor.execute("SELECT id FROM rarities WHERE name = %s", (rarity,))
                rarity_dict[rarity] = cursor.fetchone()[0]

        return rarity_dict
    except mysql.connector.Error as err:
        logging.error(f"Error al actualizar rarezas: {err}")
        raise

# Actualizar o insertar cartas
def upsert_cards(cursor, cards, rarity_dict):
    add_card = (
        "INSERT INTO cards (name, archetype, type, description, quantity, rarity_id, price) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s) "
        "ON DUPLICATE KEY UPDATE archetype = VALUES(archetype), type = VALUES(type), "
        "description = VALUES(description), quantity = VALUES(quantity), rarity_id = VALUES(rarity_id), "
        "price = VALUES(price)"
    )

    for card in cards:
        card_data = (
            card.get('name', ''),
            card.get('archetype', ''),
            card.get('type', ''),
            card.get('desc', ''),
            0,  # Cantidad por defecto
            rarity_dict.get(card.get('rarity', ''), None),
            card.get('card_prices', [{}])[0].get('cardmarket_price', 0.0)
        )
        cursor.execute(add_card, card_data)

def update_card_database():
    logging.info("Iniciando actualización de la base de datos de cartas.")
    try:
        response = requests.get('https://db.ygoprodeck.com/api/v7/cardinfo.php')
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error al descargar datos de la API: {e}")
        return

    try:
        data = response.json()
        logging.debug("Datos recibidos de la API.")
    except ValueError as e:
        logging.error(f"Error al parsear JSON: {e}")
        return
    
    cards = data.get('data', [])
    
    if not isinstance(cards, list):
        logging.error("La estructura de datos no es la esperada.")
        return

    try:
        connection = connect_db()
        cursor = connection.cursor()

        rarities = {card.get('rarity', '') for card in cards if card.get('rarity', '')}
        rarity_dict = update_rarities(cursor, rarities)

        upsert_cards(cursor, cards, rarity_dict)
        connection.commit()

        logging.info("Actualización de la base de datos de cartas completada.")
    except mysql.connector.Error as err:
        logging.error(f"Error al actualizar la base de datos: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        logging.info("Conexión a la base de datos cerrada.")

if __name__ == "__main__":
    update_card_database()