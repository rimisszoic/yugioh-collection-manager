import requests
import mysql.connector
from mysql.connector import errorcode

def connect_db():
    """Establece una conexión a la base de datos MySQL."""
    return mysql.connector.connect(
        host='localhost',
        user='yUg1C0ll3ct10n',
        password='%2If3jH$4HvotW&GlD',
        database='yugicollectionapp'
    )

def update_card_database():
    """Actualiza la base de datos con los datos de las cartas desde la API."""
    try:
        response = requests.get('https://db.ygoprodeck.com/api/v7/cardinfo.php')
        response.raise_for_status()  # Lanza una excepción si el código de estado no es 200

        data = response.json()
        print("Datos recibidos de la API:")
        print(data)  # Imprime la respuesta completa para depuración

        cards = data.get('data', [])
        
        if not isinstance(cards, list):
            print("La estructura de datos no es la esperada.")
            return
        
        if not cards:
            print("No se encontraron cartas.")
            return

        connection = connect_db()
        cursor = connection.cursor()

        for card in cards:
            card_id = card.get('id')
            name = card.get('name', 'Desconocido')
            archetype = card.get('archetype', 'Sin Arquetipo')
            type = card.get('type', 'Desconocido')
            description = card.get('desc', 'Sin descripción')  # Usar 'desc' en lugar de 'description'
            
            # Extraer el precio más alto de las diferentes fuentes
            prices = card.get('card_prices', [{}])
            price = max(
                (float(p.get('cardmarket_price', 0)) for p in prices),
                default=0
            )

            # Obtener la rareza (esto depende de la estructura de tu base de datos, usa 'rarity' si es necesario)
            rarity = card.get('card_prices', [{}])[0].get('cardmarket_price', '0.00')

            cursor.execute('''
                INSERT INTO cards (id, name, archetype, type, description, rarity, price)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                name=VALUES(name), archetype=VALUES(archetype), type=VALUES(type),
                description=VALUES(description), rarity=VALUES(rarity), price=VALUES(price)
            ''', (card_id, name, archetype, type, description, rarity, price))

        connection.commit()
        cursor.close()
        connection.close()
        print("La base de datos se ha actualizado correctamente.")
    
    except requests.RequestException as e:
        print(f"Error en la solicitud de la API: {e}")
    
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error de autenticación con la base de datos.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("La base de datos no existe.")
        else:
            print(f"Error de MySQL: {err}")
    
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    update_card_database()