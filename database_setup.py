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

# Crear la base de datos y la tabla de cartas si no existen
def setup_database():
    try:
        connection = connect_db()
        cursor = connection.cursor()

        logging.info("Creando base de datos si no existe.")
        cursor.execute("CREATE DATABASE IF NOT EXISTS yugicollectionapp")

        logging.info("Seleccionando la base de datos.")
        cursor.execute("USE yugicollectionapp")

        logging.info("Creando tabla de cartas si no existe.")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cards (
                id INT PRIMARY KEY,
                name VARCHAR(255),
                archetype VARCHAR(255),
                type VARCHAR(255),
                `desc` TEXT,
                rarity VARCHAR(255),
                price DECIMAL(10, 2),
                quantity INT DEFAULT 0
            )
        ''')

        connection.commit()
        logging.info("Base de datos y tabla configuradas correctamente.")
    except mysql.connector.Error as err:
        logging.error(f"Error al configurar la base de datos: {err}")
    finally:
        cursor.close()
        connection.close()
        logging.info("Conexión a la base de datos cerrada.")

# Ejecutar configuración
setup_database()