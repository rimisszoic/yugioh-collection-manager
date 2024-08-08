import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageTk
import mysql.connector
import logging
import requests
from io import BytesIO
from config_logging import setup_logging
from update_cards import update_card_database

# Configurar logging
setup_logging()

# Configurar el ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=4)

def connect_db():
    """Conectar a la base de datos MySQL."""
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

def update_card_quantity(card_name, quantity):
    """Actualiza la cantidad de una carta en la base de datos en un hilo separado."""
    def task():
        try:
            connection = connect_db()
            cursor = connection.cursor()
            cursor.execute("UPDATE cards SET quantity = %s WHERE name = %s", (quantity, card_name))
            connection.commit()
            logging.info(f"Cantidad de la carta '{card_name}' actualizada a {quantity}.")
        except mysql.connector.Error as err:
            logging.error(f"Error al actualizar la cantidad de la carta: {err}")
        finally:
            cursor.close()
            connection.close()
    
    future = executor.submit(task)
    return future

def get_card_info(card_name):
    """Obtiene la información de una carta de la base de datos."""
    connection = None
    cursor = None
    card_info = None
    
    try:
        connection = connect_db()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM cards WHERE name = %s"
        cursor.execute(query, (card_name,))
        card_info = cursor.fetchone()
        while cursor.nextset():
            pass
        
    except mysql.connector.Error as err:
        logging.error(f"Error al obtener información de la carta: {err}")
        card_info = None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    
    return card_info

def fetch_image(card_name, callback):
    """Descarga la imagen de una carta y la pasa a través del callback."""
    try:
        # URL de ejemplo, reemplázala con la URL real de la API o la fuente de imágenes
        url = f"https://api.example.com/cards/{card_name}/image"
        response = requests.get(url)
        image_data = response.content
        image = Image.open(BytesIO(image_data))
        callback(image)
    except Exception as e:
        logging.error(f"Error al descargar la imagen: {e}")

def update_cards():
    """Actualiza la base de datos de cartas en un hilo separado."""
    def task():
        try:
            update_card_database()
            messagebox.showinfo("Éxito", "Base de datos de cartas actualizada.")
        except Exception as err:
            logging.error(f"Error al actualizar la base de datos de cartas: {err}")
            messagebox.showerror("Error", f"Error al actualizar la base de datos de cartas: {err}")
    
    future = executor.submit(task)
    return future

def filter_cards():
    """Filtra las cartas según el criterio seleccionado."""
    filter_by = filter_var.get()
    search_term = search_var.get().strip()

    query = f"SELECT * FROM cards WHERE {filter_by.lower()} LIKE %s"
    search_pattern = f"%{search_term}%"

    try:
        connection = connect_db()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, (search_pattern,))
        results = cursor.fetchall()
        cursor.close()
        connection.close()

        for item in tree.get_children():
            tree.delete(item)

        for card in results:
            tree.insert("", "end", values=(card["name"], card["archetype"], card["type"], card["description"], card["rarity"], card["price"], card["quantity"]))
    except mysql.connector.Error as err:
        logging.error(f"Error al filtrar cartas: {err}")
        messagebox.showerror("Error", f"Error al filtrar cartas: {err}")

def show_card_info():
    """Muestra la información de la carta seleccionada en una nueva ventana."""
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Advertencia", "No se ha seleccionado ninguna carta.")
        return

    item = tree.item(selected_item[0])
    card_name = item['values'][0]

    card_info = get_card_info(card_name)
    
    def on_image_fetched(image):
        # Convertir la imagen a un formato que pueda mostrar Tkinter
        photo = ImageTk.PhotoImage(image)
        img_label.config(image=photo)
        img_label.image = photo
    
    # Crear la ventana de información de la carta
    info_window = tk.Toplevel(root)
    info_window.title(f"Información de {card_name}")
    info_window.geometry("400x600")

    # Mostrar la imagen
    img_label = tk.Label(info_window)
    img_label.pack(pady=10)

    # Obtener y mostrar la información de la carta
    if card_info:
        info_text = (f"Nombre: {card_info.get('name', 'Desconocido')}\n"
                     f"Arquetipo: {card_info.get('archetype', 'Desconocido')}\n"
                     f"Tipo: {card_info.get('type', 'Desconocido')}\n"
                     f"Descripción: {card_info.get('description', 'Desconocida')}\n"
                     f"Rareza: {card_info.get('rarity', 'Desconocida')}\n"
                     f"Precio: {card_info.get('price', 'Desconocido')}\n"
                     f"Cantidad: {card_info.get('quantity', 'Desconocida')}")
        
        info_label = tk.Label(info_window, text=info_text, justify=tk.LEFT)
        info_label.pack(pady=10)

        # Campo para añadir cantidad
        def add_quantity():
            try:
                quantity = int(quantity_entry.get())
                update_card_quantity(card_name, quantity)
                filter_cards()  # Refresh the list
                info_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Cantidad inválida. Debe ser un número entero.")

        tk.Label(info_window, text=f"Añadir cantidad a '{card_name}':").pack(pady=10)
        quantity_entry = tk.Entry(info_window)
        quantity_entry.pack(pady=5)
        tk.Button(info_window, text="Añadir", command=add_quantity).pack(pady=10)
        tk.Button(info_window, text="Cancelar", command=info_window.destroy).pack(pady=5)

    # Descargar la imagen en un hilo separado
    executor.submit(fetch_image, card_name, on_image_fetched)

def alert_high_quantity_cards():
    """Muestra una alerta con las cartas que tienen alta cantidad."""
    try:
        connection = connect_db()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cards WHERE quantity >= 100")
        results = cursor.fetchall()
        cursor.close()
        connection.close()

        if results:
            high_qty_info = "\n".join([f"{card['name']}: {card['quantity']}" for card in results])
            messagebox.showinfo("Cartas con Alta Cantidad", high_qty_info)
        else:
            messagebox.showinfo("Cartas con Alta Cantidad", "No hay cartas con alta cantidad.")
    except mysql.connector.Error as err:
        logging.error(f"Error al obtener cartas con alta cantidad: {err}")
        messagebox.showerror("Error", f"Error al obtener cartas con alta cantidad: {err}")

def get_archetypes():
    """Obtiene la lista de arquetipos únicos de la base de datos."""
    connection = None
    cursor = None
    archetypes = []

    try:
        connection = connect_db()
        cursor = connection.cursor()
        query = "SELECT DISTINCT archetype FROM cards"
        cursor.execute(query)
        archetypes = [row[0] for row in cursor.fetchall()]

    except mysql.connector.Error as err:
        logging.error(f"Error en la base de datos: {err}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return archetypes

def filter_by_archetype():
    """Filtra la lista de cartas por el arquetipo seleccionado en el dropdown."""
    selected_archetype = archetype_var.get()
    if not selected_archetype:
        messagebox.showwarning("Advertencia", "Por favor, selecciona un arquetipo.")
        return

    for row in tree.get_children():
        tree.delete(row)

    connection = None
    cursor = None
    try:
        connection = connect_db()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM cards WHERE archetype = %s"
        cursor.execute(query, (selected_archetype,))
        cards = cursor.fetchall()

        for card in cards:
            tree.insert('', tk.END, values=(card['name'], card['archetype'], card['type'], card['description'], card['rarity'], card['price'], card['quantity']))

    except mysql.connector.Error as err:
        logging.error(f"Error en la base de datos: {err}")
        messagebox.showerror("Error", "No se pudo filtrar las cartas.")
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Crear la interfaz gráfica
root = tk.Tk()
root.title("YugiCollectionApp")

search_frame = tk.Frame(root)
search_frame.pack(fill=tk.X, pady=10)

search_var = tk.StringVar()
filter_var = tk.StringVar(value="name")

search_label = tk.Label(search_frame, text="Buscar carta:")
search_label.pack(side=tk.LEFT, padx=5)
search_entry = tk.Entry(search_frame, textvariable=search_var, width=30)
search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

def on_enter(event):
    filter_cards()

search_entry.bind("<Return>", on_enter)

search_button = tk.Button(search_frame, text="Buscar", command=filter_cards)
search_button.pack(side=tk.LEFT, padx=5)

filter_label = tk.Label(search_frame, text="Filtrar por:")
filter_label.pack(side=tk.LEFT, padx=5)
filter_options = ["name", "archetype", "type", "description", "rarity", "price"]
filter_menu = tk.OptionMenu(search_frame, filter_var, *filter_options)
filter_menu.pack(side=tk.LEFT, padx=5)

archetypes = get_archetypes()
archetype_var = tk.StringVar(value="")
archetype_menu = ttk.Combobox(search_frame, textvariable=archetype_var, values=archetypes)
archetype_menu.pack(side=tk.LEFT, padx=5)

result_frame = tk.Frame(root)
result_frame.pack(fill=tk.BOTH, expand=True, pady=10)

columns = ("name", "archetype", "type", "description", "rarity", "price", "quantity")
tree = ttk.Treeview(result_frame, columns=columns, show='headings')
tree.pack(fill=tk.BOTH, expand=True)

for col in columns:
    tree.heading(col, text=col.capitalize())
    tree.column(col, width=100)

button_frame = tk.Frame(root)
button_frame.pack(fill=tk.X, pady=10)

add_quantity_button = tk.Button(button_frame, text="Añadir Cantidad", command=lambda: show_card_info())
add_quantity_button.pack(side=tk.LEFT, padx=5)

show_info_button = tk.Button(button_frame, text="Mostrar Info", command=show_card_info)
show_info_button.pack(side=tk.LEFT, padx=5)

high_quantity_button = tk.Button(button_frame, text="Mostrar Alta Cantidad", command=alert_high_quantity_cards)
high_quantity_button.pack(side=tk.LEFT, padx=5)

update_db_button = tk.Button(button_frame, text="Actualizar DB", command=update_cards)
update_db_button.pack(side=tk.LEFT, padx=5)

filter_archetype_button = tk.Button(button_frame, text="Filtrar por Arquetipo", command=filter_by_archetype)
filter_archetype_button.pack(side=tk.LEFT, padx=5)

info_frame = tk.Frame(root)
info_frame.pack(fill=tk.X, pady=10)

result_text = tk.Text(info_frame, height=5, width=60)
result_text.pack(fill=tk.BOTH, expand=True, pady=10)

tree.bind("<<TreeviewSelect>>", lambda event: show_card_info())

# Ejecutar la aplicación
root.mainloop()