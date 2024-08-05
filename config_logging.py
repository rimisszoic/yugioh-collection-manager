import logging
import os

def setup_logging():
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)  # Crea la carpeta logs si no existe

    info_log_file = os.path.join(log_dir, 'info.log')
    error_log_file = os.path.join(log_dir, 'error.log')

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Crear manejador para información
    info_handler = logging.FileHandler(info_log_file)
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))

    # Crear manejador para errores
    error_handler = logging.FileHandler(error_log_file)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))

    # Agregar los manejadores al logger
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)

# Llamar a la función de configuración de logging al inicio del script principal
setup_logging()