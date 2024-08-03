import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from concurrent.futures import ThreadPoolExecutor
import requests
import mysql.connector
import logging
from config_logging import setup_logging

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
    try:
        connection = connect_db()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT cards.*, rarities.name AS rarity_name
            FROM cards
            LEFT JOIN rarities ON cards.rarity = rarities.id
            WHERE cards.name = %s
        """, (card_name,))
        card_info = cursor.fetchone()
        cursor.close()
        connection.close()
        return card_info
    except mysql.connector.Error as err:
        logging.error(f"Error al obtener la información de la carta: {err}")
        return None

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

def add_card_quantity():
    """Añade una cantidad especificada a la carta seleccionada."""
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Advertencia", "Por favor, seleccione una carta.")
        return

    item = tree.item(selected_item)
    card_name = item['values'][0]

    quantity = simpledialog.askinteger("Añadir Cantidad", f"Cantidad para añadir a '{card_name}':")
    if quantity is None:
        return

    def task():
        update_card_quantity(card_name, quantity)
        filter_cards()  # Refresh the list

    executor.submit(task)

def show_card_info():
    """Muestra la información de la carta seleccionada."""
    selected_item = tree.selection()
    if not selected_item:
        return

    item = tree.item(selected_item)
    card_name = item['values'][0]

    card_info = get_card_info(card_name)
    if card_info:
        info = f"Nombre: {card_info['name']}\nArquetipo: {card_info['archetype']}\nTipo: {card_info['type']}\nDescripción: {card_info['description']}\nRareza: {card_info['rarity_name']}\nPrecio: {card_info['price']}\nCantidad: {card_info['quantity']}"
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, info)
    else:
        messagebox.showerror("Error", "No se pudo obtener la información de la carta.")

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

# Crear la interfaz gráfica
root = tk.Tk()
root.title("YugiCollectionApp")

# Configurar el marco de búsqueda
search_frame = tk.Frame(root)
search_frame.pack(fill=tk.X, pady=10)

search_var = tk.StringVar()
filter_var = tk.StringVar(value="name")

search_label = tk.Label(search_frame, text="Buscar carta:")
search_label.pack(side=tk.LEFT, padx=5)
search_entry = tk.Entry(search_frame, textvariable=search_var, width=30)
search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
search_button = tk.Button(search_frame, text="Buscar", command=filter_cards)
search_button.pack(side=tk.LEFT, padx=5)

# Crear el menú de filtros
filter_label = tk.Label(search_frame, text="Filtrar por:")
filter_label.pack(side=tk.LEFT, padx=5)
filter_options = ["name", "archetype", "type", "description", "rarity", "price"]
filter_menu = tk.OptionMenu(search_frame, filter_var, *filter_options)
filter_menu.pack(side=tk.LEFT, padx=5)

# Crear el marco de resultados
result_frame = tk.Frame(root)
result_frame.pack(fill=tk.BOTH, expand=True, pady=10)

# Crear el Treeview
columns = ("name", "archetype", "type", "description", "rarity", "price", "quantity")
tree = ttk.Treeview(result_frame, columns=columns, show='headings')
tree.pack(fill=tk.BOTH, expand=True)

for col in columns:
    tree.heading(col, text=col.capitalize())
    tree.column(col, width=100)

# Configurar el marco de botones adicionales
button_frame = tk.Frame(root)
button_frame.pack(fill=tk.X, pady=10)

# Crear botones
add_quantity_button = tk.Button(button_frame, text="Añadir Cantidad", command=add_card_quantity)
add_quantity_button.pack(side=tk.LEFT, padx=5)

show_info_button = tk.Button(button_frame, text="Mostrar Info", command=show_card_info)
show_info_button.pack(side=tk.LEFT, padx=5)

high_quantity_button = tk.Button(button_frame, text="Mostrar Alta Cantidad", command=alert_high_quantity_cards)
high_quantity_button.pack(side=tk.LEFT, padx=5)

update_db_button = tk.Button(button_frame, text="Actualizar DB", command=update_cards)
update_db_button.pack(side=tk.LEFT, padx=5)

# Crear el marco de información de la carta
info_frame = tk.Frame(root)
info_frame.pack(fill=tk.X, pady=10)

# Crear el widget de texto para resultados
result_text = tk.Text(info_frame, height=5, width=60)
result_text.pack(fill=tk.BOTH, expand=True, pady=10)

# Agregar un binding para el Treeview
tree.bind("<<TreeviewSelect>>", lambda event: show_card_info())

# Ejecutar la aplicación
root.mainloop()