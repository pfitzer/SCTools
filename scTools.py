import configparser
import os.path
import shutil
import subprocess
import sys
import tempfile
import tkinter
from tkinter import filedialog as fd
from tkinter import Text

import customtkinter


def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller
    see https://stackoverflow.com/a/44352931
    """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class App(customtkinter.CTk):
    copy_dirs = ['Controls', 'Profiles']
    launcher_dir = 'RSI Launcher'
    launcher = "RSI Launcher.exe"
    tmp_dir = os.path.join(tempfile.gettempdir(), 'sc_settings')
    config_path = os.path.expandvars(r'%APPDATA%\SCTools')
    conf_file = os.path.join(config_path, 'config.ini')
    config = configparser.ConfigParser()

    def __init__(self):
        super().__init__()

        self.iconbitmap(resource_path('logo_256x256.ico'))

        self.conf_data = None
        self.directory = None
        self.app_dir()

        self.title('StarCitizen Tools')
        self.geometry("700x500")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.dir_frame = customtkinter.CTkFrame(self)
        self.dir_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nswe")
        self.opt_frame = customtkinter.CTkFrame(self)
        self.opt_frame.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="nswe")
        self.out_grid = customtkinter.CTkFrame(self, fg_color="transparent")
        self.out_grid.grid(row=1, column=0, padx=10, pady=10, sticky='we', columnspan=2)

        self.label_settings = customtkinter.CTkLabel(self.dir_frame, text="Settings", fg_color="transparent",
                                                     font=('arial', 16))
        self.label_settings.grid(row=0, column=0, padx=10, pady=10, sticky="nswe")

        self.button = customtkinter.CTkButton(self.dir_frame, text="select install directory", command=self.ask_dir)
        self.button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.label = customtkinter.CTkLabel(self.dir_frame, text=self.directory, fg_color="transparent")
        self.label.grid(row=2, column=0, padx=10, pady=(10, 10), sticky="nsew")

        self.option_label = customtkinter.CTkLabel(self.dir_frame, text='Mode', width=50, fg_color="transparent")
        self.option_label.grid(row=3, column=0, padx=0, pady=10, sticky="nsw")

        self.optionmenu = customtkinter.CTkOptionMenu(self.dir_frame, values=["light", "dark"],
                                                      command=self.optionmenu_callback)
        self.optionmenu.grid(row=4, column=0, padx=10, pady=10, sticky="nsw")

        self.console = Text(self.out_grid, height=6)
        self.console.grid(row=1, column=10, padx=10, pady=10, sticky="ew")

        self.func_label = customtkinter.CTkLabel(self.opt_frame, text="Actions", fg_color="transparent",
                                                 font=('arial', 16))
        self.func_label.grid(row=0, column=0, padx=10, pady=10, sticky="nswe")

        self.copy_button = customtkinter.CTkButton(self.opt_frame, text="save settings", command=self.copy_settings)
        self.copy_button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.restore_button = customtkinter.CTkButton(self.opt_frame, text="load settings",
                                                      command=self.restore_settings)
        self.restore_button.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        self.user_button = customtkinter.CTkButton(self.opt_frame, text="delete user folder", command=self.delete_user,
                                                   fg_color="#cc0000")
        self.user_button.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        self.shader_button = customtkinter.CTkButton(self.opt_frame, text="delete shaders", command=self.delete_shaders,
                                                     fg_color="#cc0000")
        self.shader_button.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")

        self.logs_button = customtkinter.CTkButton(self.opt_frame, text="clear log files", command=self.clear_logs,
                                                   fg_color="#cc0000")
        self.logs_button.grid(row=5, column=0, padx=10, pady=10, sticky="nsew")

        self.launcher_button = customtkinter.CTkButton(self.opt_frame, text="start launcher",
                                                       command=self.start_launcher, fg_color="#009933")
        self.launcher_button.grid(row=6, column=0, padx=10, pady=10, sticky="nsew")

        self.read_config()
        self.check_save_state()

    def ask_dir(self):
        self.read_config()
        self.directory = fd.askdirectory()
        self.label.configure(text=self.directory)
        if not 'PATH' in self.config:
            self.config.add_section('PATH')
        self.config.set('PATH', 'inst_dir', self.directory)
        self.console_write("directory set")
        with open(self.conf_file, 'w') as config:
            self.config.write(config)

    def copy_settings(self):
        if not self.directory:
            self.ask_dir()
        d = os.path.join(self.directory, 'USER', 'Client', '0')
        try:
            for to_copy in self.copy_dirs:
                shutil.copytree(os.path.join(d, to_copy), os.path.join(self.tmp_dir, to_copy), dirs_exist_ok=True)
                self.console_write(f"{os.path.join(d, to_copy)} copied")
            self.restore_button.configure(state='normal')
        except Exception as e:
            self.console_write(e)

    def restore_settings(self):
        if not self.directory:
            self.ask_dir()
        d = os.path.join(self.directory, 'USER', 'Client', '0')

        try:
            for to_copy in self.copy_dirs:
                shutil.copytree(os.path.join(self.tmp_dir, to_copy), os.path.join(d, to_copy), dirs_exist_ok=True)
                self.console_write(f"{os.path.join(self.tmp_dir, to_copy)} copied")
        except Exception as e:
            self.console_write(e)

    def delete_shaders(self):
        path = os.path.expandvars(r'C:\Users\%username%\AppData\Local\Star Citizen')
        shutil.rmtree(path, ignore_errors=True)
        self.console_write('shader directories deleted')

    def delete_user(self):
        self.copy_settings()
        shutil.rmtree(os.path.join(self.directory, 'USER'), ignore_errors=True)
        self.console_write('USER directory deleted')

    def clear_logs(self):
        log_dir = os.path.join(self.directory, 'logbackups')
        size = sum(entry.stat().st_size for entry in os.scandir(log_dir)) / 1024**2
        for filename in os.listdir(log_dir):
            file_path = os.path.join(log_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                self.console_write(e)
        self.console_write(f'{round(size, 2)} MB log backups cleared')

    def start_launcher(self):
        if not self.directory:
            self.ask_dir()
        subprocess.call([os.path.join(self.directory, '..', '..', self.launcher_dir, self.launcher)])

    def app_dir(self):
        if not os.path.isdir(self.config_path):
            os.mkdir(self.config_path)

    def read_config(self):
        self.config.read(self.conf_file)
        if 'PATH' in self.config:
            self.directory = self.config['PATH']['inst_dir']
            self.label.configure(text=self.config['PATH']['inst_dir'])
        if 'LAYOUT' in self.config:
            customtkinter.set_appearance_mode(self.config['LAYOUT']['mode'])
            self.optionmenu.set(self.config['LAYOUT']['mode'])
        else:
            customtkinter.set_appearance_mode("dark")
            self.optionmenu.set("dark")

    def console_write(self, text):
        self.console.insert(tkinter.END, f"- {text}\n")

    def optionmenu_callback(self, choice):
        customtkinter.set_appearance_mode(choice)
        if not 'LAYOUT' in self.config:
            self.config.add_section('LAYOUT')
        self.config.set('LAYOUT', 'mode', choice)
        with open(self.conf_file, 'w') as config:
            self.config.write(config)

    def check_save_state(self):
        for d in self.copy_dirs:
            if not os.path.isdir(os.path.join(self.tmp_dir, d)):
                self.restore_button.configure(state='disabled')


app = App()
app.mainloop()
