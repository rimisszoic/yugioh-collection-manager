deimport requests
import mysql.connector
from mysql.connector import errorcode

# Conectar a la base de datos
def connect_db():
    return mysql.connector.connect(
            host='localhost',
                    user='yugioh_user',
                            password='TuContraseñaSeguraAqui',
                                    database='yugioh'
                                        )

                                        # Actualizar la base de datos con los datos de las cartas
                                        def update_card_database():
                                            response = requests.get('https://db.ygoprodeck.com/api/v7/cardinfo.php')
                                                
                                                    if response.status_code != 200:
                                                            print(f"Error al descargar datos de la API. Código de estado: {response.status_code}")
                                                                    return

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
                                                                                                                                                                                        desc = card.get('desc', 'Sin descripción')
                                                                                                                                                                                                rarity = card.get('card_prices', [{}])[0].get('cardmarket_price', '0.00')

                                                                                                                                                                                                        # Extraer el precio más alto de las diferentes fuentes
                                                                                                                                                                                                                prices = card.get('card_prices', [{}])
                                                                                                                                                                                                                        price = max(float(p.get('cardmarket_price', 0)) for p in prices)

                                                                                                                                                                                                                                cursor.execute('''
                                                                                                                                                                                                                                            INSERT INTO cards (id, name, archetype, type, desc, rarity, price)
                                                                                                                                                                                                                                                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                                                                                                                                                                                                                                                                    ON DUPLICATE KEY UPDATE
                                                                                                                                                                                                                                                                                name=VALUES(name), archetype=VALUES(archetype), type=VALUES(type),
                                                                                                                                                                                                                                                                                            desc=VALUES(desc), rarity=VALUES(rarity), price=VALUES(price)
                                                                                                                                                                                                                                                                                                    ''', (card_id, name, archetype, type, desc, rarity, price))

                                                                                                                                                                                                                                                                                                        connection.commit()
                                                                                                                                                                                                                                                                                                            cursor.close()
                                                                                                                                                                                                                                                                                                                connection.close()

                                                                                                                                                                                                                                                                                                                if __name__ == "__main__":
                                                                                                                                                                                                                                                                                                                    update_card_database()
