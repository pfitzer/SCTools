import configparser
import os.path
import shutil
import subprocess
import tempfile
from tkinter import filedialog as fd

import customtkinter

customtkinter.set_appearance_mode("dark")


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

        self.iconbitmap(os.path.join(os.getcwd(), 'logo_256x256.ico'))

        self.conf_data = None
        self.directory = None
        self.app_dir()
        self.read_config()

        self.title('StarCitizen Tools')
        self.geometry("600x400")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.dir_frame = customtkinter.CTkFrame(self)
        self.dir_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nswe")
        self.opt_frame = customtkinter.CTkFrame(self)
        self.opt_frame.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="nswe")
        self.out_grid = customtkinter.CTkFrame(self)
        self.out_grid.grid(row=1, column=0, padx=10, pady=10, sticky='we', columnspan=2)

        self.button = customtkinter.CTkButton(self.dir_frame, text="select install directory", command=self.ask_dir)
        self.button.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.label = customtkinter.CTkLabel(self.dir_frame, text=self.directory, fg_color="transparent")
        self.label.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="nsew")
        self.console = customtkinter.CTkLabel(self.out_grid, text='', height=100, fg_color="transparent")
        self.console.grid(row=1, column=10, padx=10, pady=0, sticky="ew")

        self.copy_button = customtkinter.CTkButton(self.opt_frame, text="save settings", command=self.copy_settings)
        self.copy_button.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.restore_button = customtkinter.CTkButton(self.opt_frame, text="load settings",
                                                      command=self.restore_settings)
        self.restore_button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.shader_button = customtkinter.CTkButton(self.opt_frame, text="delete shaders", command=self.delete_shaders,
                                                     fg_color="#cc0000")
        self.shader_button.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        self.launcher_button = customtkinter.CTkButton(self.opt_frame, text="start launcher",
                                                       command=self.start_launcher, fg_color="#009933")
        self.launcher_button.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

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
        t = ''
        try:
            for to_copy in self.copy_dirs:
                shutil.copytree(os.path.join(d, to_copy), os.path.join(self.tmp_dir, to_copy), dirs_exist_ok=True)
                t = t + f"{os.path.join(d, to_copy)} copied\n"
            self.console_write(t)
        except Exception as e:
            self.console_write(e)

    def restore_settings(self):
        if not self.directory:
            self.ask_dir()
        d = os.path.join(self.directory, 'USER', 'Client', '0')
        t = ''
        try:
            for to_copy in self.copy_dirs:
                shutil.copytree(os.path.join(self.tmp_dir, to_copy), os.path.join(d, to_copy), dirs_exist_ok=True)
                t = t + f"{os.path.join(self.tmp_dir, to_copy)} copied\n"
            self.console_write(t)
        except Exception as e:
            self.console_write(e)

    def delete_shaders(self):
        path = os.path.expandvars(r'C:\Users\%username%\AppData\Local\Star Citizen')
        shutil.rmtree(path, ignore_errors=True)
        self.console_write('shader directories deleted')

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

    def console_write(self, text):
        self.console.configure(text=text)


app = App()
app.mainloop()
