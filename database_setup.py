import mysql.connector
from mysql.connector import errorcode

# Conexión a la base de datos
def connect_db():
    return mysql.connector.connect(
        host='localhost',
        user='yUg1C0ll3ct10n',
        password='%2If3jH$4HvotW&GlD',
        database='yugicollectionapp'
    )

# Crear la base de datos y la tabla de cartas si no existen
def setup_database():
    connection = connect_db()
    cursor = connection.cursor()

    # Crear base de datos si no existe
    cursor.execute("CREATE DATABASE IF NOT EXISTS yugicollectionapp")

    # Seleccionar la base de datos
    cursor.execute("USE yugicollectionapp")

    # Crear tabla de cartas
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
    cursor.close()
    connection.close()

# Ejecutar configuración
setup_database()