import tkinter as tk
from tkinter import messagebox
import webbrowser
import requests
import time
import os

# --- DESIGN KONSTANTEN ---
BG_DARK = "#1e1e2e"      # Dunkler Hintergrund (Mocha-Style)
BG_LIGHT = "#313244"     # Etwas helleres Grau für Karten/Eingaben
ACCENT = "#89b4fa"       # Sanftes Blau
SUCCESS = "#a6e3a1"      # Sanftes Grün
TEXT_COLOR = "#cdd6f4"   # Off-white Text
FONT_MAIN = ("Segoe UI", 12)
FONT_BOLD = ("Segoe UI", 14, "bold")

SKIP_FILE = "update_done.dat"

class HTMLFormatterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HTML Text Formatter Pro")
        self.geometry("400x450")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)

        self.container = tk.Frame(self, bg=BG_DARK)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (MainMenu, InputMenu):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.current_mode = ""
        self.show_frame("MainMenu")
        self.check_for_update()

    def check_for_update(self):
        timestamp = int(time.time())
        url = f"https://raw.githubusercontent.com/Energiemaster/mein-app-projekt/main/Html%20Update.txt?t={timestamp}"
        try:
            headers = {'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                content = response.text.strip()
                if content == "1":
                    if not os.path.exists(SKIP_FILE):
                        self.show_update_overlay()
                elif content == "0":
                    if os.path.exists(SKIP_FILE):
                        os.remove(SKIP_FILE)
        except Exception as e:
            print(f"Update-Check übersprungen: {e}")

    def show_update_overlay(self):
        self.overlay = tk.Toplevel(self)
        self.overlay.title("Update")
        self.overlay.geometry("350x300")
        self.overlay.configure(bg=BG_LIGHT)
        self.overlay.grab_set()
        self.overlay.protocol("WM_DELETE_WINDOW", lambda: None)
        
        tk.Label(self.overlay, text="UPDATE VERFÜGBAR", font=FONT_BOLD, fg=ACCENT, bg=BG_LIGHT).pack(pady=(30, 10))
        tk.Label(self.overlay, text="Eine neue Version steht bereit.\nMöchtest du sie jetzt laden?", 
                 fg=TEXT_COLOR, bg=BG_LIGHT, justify="center").pack(pady=10)

        tk.Button(self.overlay, text="Jetzt laden", font=FONT_BOLD, bg=SUCCESS, fg=BG_DARK, 
                  activebackground="#94e2d5", relief="flat", cursor="hand2", width=18,
                  command=self.open_update_url).pack(pady=15)
        
        tk.Button(self.overlay, text="Später", font=FONT_MAIN, bg=BG_DARK, fg=TEXT_COLOR, 
                  relief="flat", cursor="hand2", width=18,
                  command=self.close_overlay_only).pack()

    def close_overlay_only(self):
        self.overlay.destroy()

    def open_update_url(self):
        with open(SKIP_FILE, "w") as f:
            f.write("User hat auf Download geklickt")
        update_url = "https://github.com/Energiemaster/mein-app-projekt/raw/refs/heads/main/main.exe"
        webbrowser.open(update_url)
        self.overlay.destroy()

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        if page_name == "InputMenu":
            frame.prepare_ui(self.current_mode)

    def set_mode_and_switch(self, mode):
        self.current_mode = mode
        self.show_frame("InputMenu")

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        
        tk.Label(self, text="HTML Formatter", font=("Segoe UI", 20, "bold"), fg=ACCENT, bg=BG_DARK).pack(pady=(50, 40))
        
        btn_style = {"font": FONT_MAIN, "bg": BG_LIGHT, "fg": TEXT_COLOR, "activebackground": ACCENT, 
                     "relief": "flat", "cursor": "hand2", "width": 25, "height": 2}

        tk.Button(self, text="Hochgestellt ( <sup> )", **btn_style,
                  command=lambda: controller.set_mode_and_switch("hoch")).pack(pady=10)
        
        tk.Button(self, text="Tiefgestellt ( <sub> )", **btn_style,
                  command=lambda: controller.set_mode_and_switch("tief")).pack(pady=10)

class InputMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        
        self.lbl_title = tk.Label(self, text="", font=FONT_BOLD, fg=ACCENT, bg=BG_DARK)
        self.lbl_title.pack(pady=(30, 20))
        
        # Container für Input
        self.entry = tk.Entry(self, width=25, font=FONT_MAIN, bg=BG_LIGHT, fg=TEXT_COLOR, 
                             insertbackground="white", relief="flat", justify="center")
        self.entry.pack(pady=10, ipady=8)
        self.entry.bind("<Return>", self.format_text)

        self.result_var = tk.StringVar()
        self.result_entry = tk.Entry(self, textvariable=self.result_var, width=25,
                                     font=FONT_BOLD, state='readonly', relief="flat",
                                     readonlybackground=BG_DARK, fg=SUCCESS, justify="center")
        self.result_entry.pack(pady=20)

        # Buttons
        tk.Button(self, text="Kopieren", font=FONT_BOLD, bg=ACCENT, fg=BG_DARK, 
                  relief="flat", cursor="hand2", width=15, command=self.copy_to_clipboard).pack(pady=5)
        
        tk.Button(self, text="Zurück", font=FONT_MAIN, bg=BG_DARK, fg=TEXT_COLOR, 
                  relief="flat", cursor="hand2", command=lambda: controller.show_frame("MainMenu")).pack(pady=10)

    def prepare_ui(self, mode):
        self.mode = mode
        self.entry.delete(0, tk.END)
        self.result_var.set("")
        self.lbl_title.config(text="Text eingeben (" + ("Hoch" if mode == "hoch" else "Tief") + ")")
        self.entry.focus_set()

    def format_text(self, event=None):
        text = self.entry.get()
        tag = "sup" if self.mode == "hoch" else "sub"
        self.result_var.set(f"<{tag}>{text}</{tag}>")

    def copy_to_clipboard(self):
        res = self.result_var.get()
        if res:
            self.clipboard_clear()
            self.clipboard_append(res)
            messagebox.showinfo("Erfolg", "Kopiert!")

if __name__ == "__main__":
    app = HTMLFormatterApp()
    app.mainloop()