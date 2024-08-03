import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import requests
import mysql.connector
from concurrent.futures import ThreadPoolExecutor

# Configurar el ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=4)

def connect_db():
    """Conectar a la base de datos MySQL."""
    return mysql.connector.connect(
        host='localhost',
        user='yUg1C0ll3ct10n',
        password='%2If3jH$4HvotW&GlD',
        database='yugicollectionapp'
    )

def update_card_quantity(card_name, quantity):
    """Actualiza la cantidad de una carta en la base de datos en un hilo separado."""
    def task():
        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE cards SET quantity = %s WHERE name = %s",
            (quantity, card_name)
        )
        connection.commit()
        cursor.close()
        connection.close()
    future = executor.submit(task)
    return future

def get_card_info(card_name):
    """Obtiene la información de una carta de la base de datos."""
    connection = connect_db()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT cards.*, rarities.name AS rarity_name
        FROM cards
        LEFT JOIN rarities ON cards.rarity = rarities.score
        WHERE cards.name = %s
    """, (card_name,))
    card_info = cursor.fetchone()
    cursor.close()
    connection.close()
    return card_info

def search_cards_advanced(**kwargs):
    """
    Busca cartas en la API de YGOPRODeck utilizando diferentes parámetros.

    Parámetros:
    **kwargs: Parámetros de búsqueda como nombre, arquetipo, nivel, atributo, etc.

    Retorna:
    Una lista de cartas que coinciden con los criterios de búsqueda.
    """
    base_url = 'https://db.ygoprodeck.com/api/v7/cardinfo.php'
    try:
        if 'name' in kwargs:
            kwargs['fname'] = kwargs.pop('name')
        
        response = requests.get(base_url, params=kwargs)
        response.raise_for_status()
        return response.json()['data']
    except Exception as e:
        messagebox.showerror("Error", f"Error al buscar cartas: {e}")
        return []

def filter_cards():
    """Filtra las cartas y actualiza el Treeview con los resultados."""
    field = filter_var.get()
    query = search_var.get()

    if not query:
        query = '%'

    # Mapear los filtros a parámetros de la API
    params = {}
    if field == "Nombre":
        params['name'] = query
    elif field == "Arquetipo":
        params['archetype'] = query
    elif field == "Tipo":
        params['type'] = query
    elif field == "Descripción":
        params['desc'] = query
    elif field == "Rareza":
        params['rarity'] = query
    elif field == "Precio":
        params['price'] = query
    else:
        params['name'] = query

    # Buscar cartas en la API
    cards = search_cards_advanced(**params)

    # Clear the existing rows
    for row in tree.get_children():
        tree.delete(row)

    # Insert new rows
    for card in cards:
        # Obtener la cantidad de la carta en la base de datos
        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute("SELECT quantity FROM cards WHERE name = %s", (card.get('name', 'N/A'),))
        quantity = cursor.fetchone()
        cursor.close()
        connection.close()

        quantity = quantity[0] if quantity else 'N/A'

        tree.insert('', tk.END, values=(
            card.get('name', 'N/A'),
            card.get('archetype', 'N/A'),
            card.get('type', 'N/A'),
            card.get('desc', 'N/A'),
            card.get('rarity', 'N/A'),
            card.get('price', 'N/A'),
            quantity
        ))

def add_card_quantity():
    """Añade o actualiza la cantidad de una carta en la base de datos."""
    selected_item = tree.selection()
    if selected_item:
        card_name = tree.item(selected_item[0], 'values')[0]
        quantity = simpledialog.askinteger("Cantidad", "Ingrese la cantidad:")
        if quantity is not None:
            future = update_card_quantity(card_name, quantity)
            future.result()
            messagebox.showinfo("Éxito", f"Se ha actualizado la cantidad de la carta '{card_name}'.")
            filter_cards()  # Actualizar el Treeview después de actualizar la cantidad

def show_card_info():
    """Muestra la información detallada de una carta."""
    selected_item = tree.selection()
    if selected_item:
        card_name = tree.item(selected_item[0], 'values')[0]
        card_info = get_card_info(card_name)
        if card_info:
            # Clear the current info
            for widget in info_frame.winfo_children():
                widget.grid_forget()
            
            # Display new card info
            tk.Label(info_frame, text=f"Nombre: {card_info['name']}", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5, pady=2, sticky='w')
            tk.Label(info_frame, text=f"Arquetipo: {card_info['archetype']}", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=2, sticky='w')
            tk.Label(info_frame, text=f"Tipo: {card_info['type']}", font=("Arial", 12)).grid(row=2, column=0, padx=5, pady=2, sticky='w')
            tk.Label(info_frame, text=f"Descripción: {card_info['description']}", font=("Arial", 12)).grid(row=3, column=0, padx=5, pady=2, sticky='w')
            tk.Label(info_frame, text=f"Rareza: {card_info['rarity_name']}", font=("Arial", 12)).grid(row=4, column=0, padx=5, pady=2, sticky='w')
            tk.Label(info_frame, text=f"Precio: {card_info['price']}", font=("Arial", 12)).grid(row=5, column=0, padx=5, pady=2, sticky='w')
            tk.Label(info_frame, text=f"Cantidad: {card_info['quantity']}", font=("Arial", 12)).grid(row=6, column=0, padx=5, pady=2, sticky='w')
        else:
            result_text.delete(1.0, tk.END)  # Clear the result_text if no card is found
            result_text.insert(tk.END, f"No se encontró la carta '{card_name}'.")

def alert_high_quantity_cards():
    """Muestra las cartas con una cantidad mayor a un umbral especificado."""
    threshold = simpledialog.askinteger("Umbral de Cantidad", "Ingrese el umbral para la cantidad:", initialvalue=3)
    if threshold is None:
        return

    connection = connect_db()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT name, quantity FROM cards WHERE quantity > %s", (threshold,))
    cards = cursor.fetchall()
    cursor.close()
    connection.close()

    display_text = "Las siguientes cartas tienen más de {} unidades:\n".format(threshold)
    if cards:
        for card in cards:
            display_text += f"{card['name']}: {card['quantity']}\n"
    else:
        display_text = f"No hay cartas con más de {threshold} unidades."

    result_text.delete(1.0, tk.END)  # Borra el contenido anterior
    result_text.insert(tk.END, display_text)

def update_cards():
    """Actualiza la base de datos de cartas usando un script externo."""
    def task():
        import update_cards  # Asegúrate de que el script `update_cards.py` esté en el mismo directorio
        try:
            update_cards.update_card_database()
            messagebox.showinfo("Éxito", "La base de datos se ha actualizado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Hubo un error al actualizar la base de datos: {e}")
    
    future = executor.submit(task)
    future.result()

# Crear la ventana principal
root = tk.Tk()
root.title("Aplicación de Colección de Cartas")

# Variables globales
search_var = tk.StringVar()
filter_var = tk.StringVar(value="Nombre")

# Crear el marco de búsqueda
search_frame = tk.Frame(root)
search_frame.pack(pady=10)

# Crear el campo de búsqueda
search_label = tk.Label(search_frame, text="Buscar:")
search_label.pack(side=tk.LEFT, padx=5)
search_entry = tk.Entry(search_frame, textvariable=search_var, width=30)
search_entry.pack(side=tk.LEFT, padx=5)
search_button = tk.Button(search_frame, text="Buscar", command=filter_cards)
search_button.pack(side=tk.LEFT, padx=5)

# Crear el menú de filtros
filter_label = tk.Label(search_frame, text="Filtrar por:")
filter_label.pack(side=tk.LEFT, padx=5)
filter_options = ["Nombre", "Arquetipo", "Tipo", "Descripción", "Rareza", "Precio"]
filter_menu = tk.OptionMenu(search_frame, filter_var, *filter_options)
filter_menu.pack(side=tk.LEFT, padx=5)

# Crear el marco de resultados
result_frame = tk.Frame(root)
result_frame.pack(pady=10)

# Crear el Treeview
columns = ("name", "archetype", "type", "description", "rarity", "price", "quantity")
tree = ttk.Treeview(result_frame, columns=columns, show='headings')
tree.pack()

for col in columns:
    tree.heading(col, text=col.capitalize())

# Crear el marco de botones adicionales
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

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
info_frame.pack(pady=10)

# Crear el widget de texto para resultados
result_text = tk.Text(root, height=5, width=60)
result_text.pack(pady=10)

# Agregar un binding para el Treeview
tree.bind("<<TreeviewSelect>>", lambda event: show_card_info())

# Ejecutar la aplicación
root.mainloop()