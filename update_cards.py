import requests
import mysql.connector
import logging
import threading
from queue import Queue
from config_logging import setup_logging

setup_logging()

# Configurar el número de hilos
NUM_THREADS = 10

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

def process_batch(cards, rarity_dict):
    connection = None
    try:
        connection = connect_db()
        cursor = connection.cursor()
        
        add_card = (
            "INSERT INTO cards (name, archetype, type, description) "
            "VALUES (%s, %s, %s, %s) "
            "ON DUPLICATE KEY UPDATE archetype = VALUES(archetype), type = VALUES(type), "
            "description = VALUES(description)"
        )

        add_card_set = (
            "INSERT INTO card_sets (card_id, set_name, set_code, rarity_id, set_price) "
            "VALUES (%s, %s, %s, %s, %s)"
        )

        add_card_prices = (
            "INSERT INTO card_prices (card_id, cardmarket_price, tcgplayer_price, ebay_price, amazon_price, coolstuffinc_price) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )

        for card in cards:
            card_data = (
                card.get('name', ''),
                card.get('archetype', ''),
                card.get('type', ''),
                card.get('desc', '')
            )
            cursor.execute(add_card, card_data)
            card_id = cursor.lastrowid

            for card_set in card.get('card_sets', []):
                rarity_name = card_set.get('set_rarity', '')
                set_data = (
                    card_id,
                    card_set.get('set_name', ''),
                    card_set.get('set_code', ''),
                    rarity_dict.get(rarity_name, None),
                    float(card_set.get('set_price', 0.0))
                )
                cursor.execute(add_card_set, set_data)

            price_data = (
                card_id,
                card.get('card_prices', [{}])[0].get('cardmarket_price', 0.0),
                card.get('card_prices', [{}])[0].get('tcgplayer_price', 0.0),
                card.get('card_prices', [{}])[0].get('ebay_price', 0.0),
                card.get('card_prices', [{}])[0].get('amazon_price', 0.0),
                card.get('card_prices', [{}])[0].get('coolstuffinc_price', 0.0)
            )
            cursor.execute(add_card_prices, price_data)

        connection.commit()
        logging.info(f"Batch de {len(cards)} cartas procesado exitosamente.")
    except mysql.connector.Error as err:
        logging.error(f"Error al procesar batch: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def worker_thread(queue, rarity_dict):
    while True:
        cards = queue.get()
        if cards is None:
            break
        process_batch(cards, rarity_dict)
        queue.task_done()

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

    rarities = {card_set.get('set_rarity', '') for card in cards for card_set in card.get('card_sets', []) if card_set.get('set_rarity', '')}
    logging.debug(f"Rarezas encontradas: {rarities}")

    try:
        connection = connect_db()
        cursor = connection.cursor()

        rarity_dict = update_rarities(cursor, rarities)
        logging.debug(f"Diccionario de rarezas: {rarity_dict}")

        # Prepare for multithreading
        queue = Queue()
        threads = []

        # Launch worker threads
        for _ in range(NUM_THREADS):
            thread = threading.Thread(target=worker_thread, args=(queue, rarity_dict))
            thread.start()
            threads.append(thread)

        # Split cards into batches and put them in the queue
        batch_size = len(cards) // NUM_THREADS
        for i in range(0, len(cards), batch_size):
            queue.put(cards[i:i + batch_size])

        # Wait for all tasks to be done
        queue.join()

        # Stop worker threads
        for _ in range(NUM_THREADS):
            queue.put(None)
        for thread in threads:
            thread.join()

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