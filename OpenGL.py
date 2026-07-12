import customtkinter as ctk
import os
import psutil
import subprocess
import shutil
import string
import threading
import requests
import zipfile
import io

# Настройка темы
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class InjectorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SpikeWare SO2")
        self.geometry("700x400")

        # Боковая панель
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=10)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.sidebar, text="SETTINGS", font=("Arial", 18, "bold")).pack(pady=20)

        self.bs_version = ctk.CTkOptionMenu(self.sidebar, values=["BlueStacks 5", "BlueStacks 4 (64bit)", "BlueStacks 4 (32bit)"], height=40, font=("Arial", 14))
        self.bs_version.pack(pady=10, padx=20, fill="x")

        self.cheat_select = ctk.CTkOptionMenu(self.sidebar, values=["Internal"], height=40, font=("Arial", 14))
        self.cheat_select.pack(pady=10, padx=20, fill="x")

        # Основная часть
        self.log_box = ctk.CTkTextbox(self, height=250, font=("Consolas", 12))
        self.log_box.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.btn = ctk.CTkButton(self, text="LOAD", command=self.start_process, height=50, font=("Arial", 16, "bold"))
        self.btn.pack(pady=10, padx=10, fill="x")

    def log(self, msg):
        self.log_box.insert("end", f"{msg}\n")
        self.log_box.see("end")

    def download_and_extract(self):
        self.log("[*] Скачивание чита...")
        url = "https://github.com/demidsiamka/opengl/raw/refs/heads/main/OpenGL-Stable.zip"
        
        # Получаем путь к папке %temp%
        temp_dir = os.environ.get('TEMP')
        # Создаем специфичную подпапку, чтобы не засорять корень temp
        extract_to = os.path.join(temp_dir, "163FH-VY8AS-V7ZC1-48KBZ")
        
        try:
            response = requests.get(url)
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                # Создаем директорию, если она не существует
                os.makedirs(extract_to, exist_ok=True)
                zip_ref.extractall(extract_to)
            
           # self.log(f"[+] Распаковано в: {extract_to}")
            # Сохраняем путь к распакованному файлу для дальнейшего использования
            self.extracted_dll_path = os.path.join(extract_to, "opengl32.dll")
            return True
        except Exception as e:
            self.log(f"[-] Ошибка загрузки: {e}")
            return False

    def find_bs_path(self):
        target_folder = {
            "BlueStacks 5": "BlueStacks_nxt",
            "BlueStacks 4 (64bit)": "BlueStacks_bgp64",
            "BlueStacks 4 (32bit)": "BlueStacks"
        }.get(self.bs_version.get())

        for drive in [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]:
            for root, dirs, files in os.walk(drive):
                if target_folder in dirs:
                    return os.path.join(root, target_folder)
        return None

    def monitor_process(self, dst_dll):
        self.log("[*] Игра запущена. Не закрывайте лаунчер...")
        while any(p.info['name'] == "HD-Player.exe" for p in psutil.process_iter(['name'])):
            threading.Event().wait(3)
        
        if os.path.exists(dst_dll):
            os.remove(dst_dll)
        self.log("[+] Игра завершена. Лаунчер можно закрывать")
        self.btn.configure(state="normal")

    def run_logic(self):
        self.btn.configure(state="disabled")
        
        if not self.download_and_extract():
            self.btn.configure(state="normal")
            return

        bs_path = self.find_bs_path()
        if not bs_path:
            self.log("[-] Код ошибки: PNF-32")
            self.btn.configure(state="normal")
            return

        dst_dll = os.path.join(bs_path, "opengl32.dll")
        shutil.copy2(self.extracted_dll_path, dst_dll)

        self.log("[+] Чит внедрен успешно.")
        
        subprocess.Popen([os.path.join(bs_path, "HD-Player.exe"), "--cmd", "launchApp", 
                          "--package", "com.axlebolt.standoff2", "--source", "desktop_shortcut"])
        
        threading.Thread(target=self.monitor_process, args=(dst_dll,), daemon=True).start()

    def start_process(self):
        threading.Thread(target=self.run_logic, daemon=True).start()

if __name__ == "__main__":
    app = InjectorApp()
    app.mainloop()