import logging
import os
import subprocess
import ctypes
import sys
import tkinter as tk
from tkinter import messagebox
import winshell
from win32com.client import Dispatch

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print("Este script necesita privilegios de administrador para ejecutarse.")
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    sys.exit(0)

class MySQLInstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MySQL Installer")

        self.label = tk.Label(root, text="¿Tienes MySQL Workbench instalado?")
        self.label.pack(pady=10)

        self.workbench_var = tk.StringVar(value="no")
        self.radio_yes = tk.Radiobutton(root, text="Sí", variable=self.workbench_var, value="yes")
        self.radio_yes.pack()
        self.radio_no = tk.Radiobutton(root, text="No", variable=self.workbench_var, value="no")
        self.radio_no.pack()

        self.button = tk.Button(root, text="Continuar", command=self.proceed)
        self.button.pack(pady=20)

    def proceed(self):
        self.workbench_installed = self.workbench_var.get() == "yes"
        self.root.destroy()

def run_gui():
    root = tk.Tk()
    app = MySQLInstallerGUI(root)
    root.mainloop()
    return app.workbench_installed

workbench_installed = run_gui()

def setup_logging():
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    info_log_file = os.path.join(log_dir, 'info.log')
    error_log_file = os.path.join(log_dir, 'error.log')

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    info_handler = logging.FileHandler(info_log_file)
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))

    error_handler = logging.FileHandler(error_log_file)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))

    logger.addHandler(info_handler)
    logger.addHandler(error_handler)

setup_logging()

def install_mysql():
    mysql_installer_url = "https://dev.mysql.com/get/Downloads/MySQLInstaller/mysql-installer-web-community-8.0.26.0.msi"
    installer_path = os.path.join(os.getcwd(), "mysql-installer.msi")

    subprocess.run(["curl", "-L", "-o", installer_path, mysql_installer_url])
    subprocess.run(["msiexec", "/i", installer_path, "/quiet", "/norestart", "ADDLOCAL=ALL", "REMOVE=ConnectorODBC,ConnectorJ"])
    subprocess.run(["mysqladmin", "-u", "root", "password", "toor"])

if not workbench_installed:
    install_mysql()

def run_db_script():
    db_script_path = os.path.join(os.getcwd(), "db.sql")
    subprocess.run(["mysql", "-u", "root", "-ptoor", "-e", f"source {db_script_path}"])

run_db_script()

def create_shortcut():
    desktop = winshell.desktop()
    path = os.path.join(desktop, "YugiCollectionApp.lnk")
    target = os.path.join(os.getcwd(), "gui.py")
    wDir = os.getcwd()
    icon = target

    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = wDir
    shortcut.IconLocation = icon
    shortcut.save()

create_shortcut()