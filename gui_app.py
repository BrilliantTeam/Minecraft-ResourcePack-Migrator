import sys
import os
import shutil
import zipfile
import tempfile
import errno
import stat
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog
import converter
import json
import threading
import subprocess
from rich.console import Console

TRANSLATIONS = {
    "title": {
        "zh": "Minecraft 資源包更新工具",
        "en": "Minecraft Resource Pack Migrator",
        "es": "Minecraft Migrador de Resource Packs",
        "de": "Minecraft Resourcenpaket-Umwandler"
    },
    "subtitle": {
        "zh": "1.14 ~ 1.21.4+",
        "en": "1.14 ~ 1.21.4+",
        "es": "1.14 ~ 1.21.4+",
        "de": "1.14 ~ 1.21.4+"
    },
    "conversion_mode": {
        "zh": "轉換模式",
        "en": "Conversion Mode",
        "es": "Modo de Conversion",
        "de": "Umwandlungsmodus"
    },
    "mode_cmd": {
        "zh": "Custom Model Data",
        "en": "Custom Model Data",
        "es": "Custom Model Data",
        "de": "Custom Model Data"
    },
    "mode_item": {
        "zh": "Item Model",
        "en": "Item Model",
        "es": "Item Model",
        "de": "Item Model"
    },
    "mode_damage": {
        "zh": "Damage",
        "en": "Damage",
        "es": "Damage",
        "de": "Damage"
    },
    "file_list": {
        "zh": "檔案列表",
        "en": "File List",
        "es": "Lista de Archivos",
        "de": "Dateiliste"
    },
    "choose_folder": {
        "zh": "+ 資料夾",
        "en": "+ Folder",
        "es": "+ Carpeta",
        "de": "+ Ordner"
    },
    "choose_zip": {
        "zh": "+ ZIP",
        "en": "+ ZIP",
        "es": "+ ZIP",
        "de": "+ ZIP"
    },
    "start_convert": {
        "zh": "▶  開始轉換",
        "en": "▶  Convert",
        "es": "▶  Convertir",
        "de": "▶  Umwandeln"
    },
    "author": {
        "zh": "RiceChen_  ·  v1.5",
        "en": "RiceChen_  ·  v1.5",
        "es": "RiceChen_  ·  v1.5",
        "de": "RiceChen_  ·  v1.5"
    },
    "clear_files": {
        "zh": "清除",
        "en": "Clear",
        "es": "Limpiar",
        "de": "Leeren"
    },
    "confirm_exit": {
        "zh": "確認離開",
        "en": "Confirm Exit",
        "es": "Confirma Salir",
        "de": "Beenden"
    },
    "confirm_exit_processing": {
        "zh": "正在處理檔案中，確定要離開嗎？\n檔案處理將會中斷。",
        "en": "Processing files, are you sure to exit?\nFile processing will be interrupted.",
        "es": "Aun procesando archivos, estas seguro que deseas salir?\nInterrumpira la conversion de archivos",
        "de": "Es werden derzeit noch Dateien verarbeitet, möchtest du trotzdem beenden?\nDer Prozess wird dabei unterbrochen."
    },
    "confirm_exit_normal": {
        "zh": "確定要離開程式嗎？",
        "en": "Are you sure to exit?",
        "es": "Estas seguro que quieres salir?",
        "de": "Bist du sicher, dass du beenden möchtest?"
    },
    "warning": {
        "zh": "警告",
        "en": "Warning",
        "es": "Advertencia",
        "de": "Warnung"
    },
    "select_files_first": {
        "zh": "請先選擇檔案",
        "en": "Please select files first",
        "es": "Porfavor seleccione primero los archivos",
        "de": "Bitte wähle zuerst die Dateien aus"
    },
    "complete": {
        "zh": "完成",
        "en": "Complete",
        "es": "Completado",
        "de": "Abgeschlossen"
    },
    "conversion_complete": {
        "zh": "轉換完成！輸出檔案：{}",
        "en": "Conversion complete! Output: {}",
        "es": "Completada! Archivo: {}",
        "de": "Abgeschlossen! Datei: {}"
    },
    "select_folder": {
        "zh": "選擇資料夾",
        "en": "Select Folder",
        "es": "Seleccionar Carpeta",
        "de": "Ordner auswählen"
    },
    "select_zip": {
        "zh": "選擇ZIP檔案",
        "en": "Select ZIP File",
        "es": "Seleccionar ZIP",
        "de": "ZIP auswählen"
    },
    "extracting": {
        "zh": "正在解壓縮...",
        "en": "Extracting...",
        "es": "Extrayendo...",
        "de": "Entpacke..."
    },
    "copying_files": {
        "zh": "正在複製檔案...",
        "en": "Copying files...",
        "es": "Copiando archivos...",
        "de": "Kopiere Dateien..."
    },
    "error": {
        "zh": "錯誤",
        "en": "Error",
        "es": "Error",
        "de": "Fehler"
    },
    "conversion_failed": {
        "zh": "轉換失敗：{}",
        "en": "Conversion failed: {}",
        "es": "Fallo: {}",
        "de": "Fehler: {}"
    },
    "output_folder": {
        "zh": "輸出資料夾",
        "en": "Output Folder",
        "es": "Carpeta de Salida",
        "de": "Ausgabeordner"
    },
    "open_output_folder": {
        "zh": "開啟輸出資料夾",
        "en": "Open Output Folder",
        "es": "Abrir Carpeta",
        "de": "Ausgabe öffnen"
    },
    "change_output_folder": {
        "zh": "變更...",
        "en": "Change...",
        "es": "Cambiar...",
        "de": "Ändern..."
    },
    "select_output_folder": {
        "zh": "選擇輸出資料夾",
        "en": "Select Output Folder",
        "es": "Seleccionar Carpeta de Salida",
        "de": "Ausgabeort auswählen"
    },
    "conversion_mode_description": {
        "zh": "模式說明",
        "en": "Description",
        "es": "Descripcion",
        "de": "Beschreibung"
    },
    "mode_cmd_description": {
        "zh": "適用於依然想要在 1.21.4 以上版本使用 Custom Model Data 定義模型的狀況",
        "en": "Suitable for scenarios where you want to continue using Custom Model Data to define models in versions 1.21.4 and above",
        "es": "Para escenarios donde se prefiere continuar usando Custom Model Data en la versión 1.21.4+",
        "de": "Geeignet für Szenarien, in denen weiterhin Custom Model Data in Version 1.21.4+ verwendet werden soll."
    },
    "mode_item_description": {
        "zh": "直接將定義模型的方式變更為 Item Model，採用定義模型的最新方式",
        "en": "Directly changes the model definition method to Item Model, adopting the latest approach",
        "es": "Cambia directamente la definición del modelo a Item Model, usando la implementación más reciente",
        "de": "Ändert die Modell-Definitionsmethode direkt auf Item Model und übernimmt den neuesten Ansatz."
    },
    "mode_damage_description": {
        "zh": "僅針對透過耐久值來定義模型的情況。如果原先是 Custom Model Data + Damage，請改用其他模式",
        "en": "Only for cases where models are defined by durability. If the original uses Custom Model Data + Damage, use a different mode",
        "es": "Solo para casos donde los modelos están definidos por durabilidad. Si usa CMD+Damage, use otro modo",
        "de": "Nur für Fälle, in denen Modelle durch Haltbarkeit definiert sind. Bei CMD+Damage bitte anderen Modus verwenden."
    },
    "report_issue": {
        "zh": "回報問題",
        "en": "Report Issue",
        "es": "Reportar Error",
        "de": "Fehler melden"
    },
    "file_generation_failed": {
        "zh": "未能生成輸出檔案",
        "en": "Failed to generate output file",
        "es": "Error al generar archivo de salida",
        "de": "Ausgabedatei konnte nicht erstellt werden"
    },
    "ok":     {"zh": "確定",  "en": "OK",     "es": "Aceptar",  "de": "OK"},
    "cancel": {"zh": "取消",  "en": "Cancel", "es": "Cancelar", "de": "Abbrechen"},
    "theme_light": {"zh": "淺色", "en": "Light", "es": "Claro",  "de": "Hell"},
    "theme_dark":  {"zh": "深色", "en": "Dark",  "es": "Oscuro", "de": "Dunkel"},
}

DARK_THEME = {
    'bg':               '#0f0f0f',
    'bg_panel':         '#181818',
    'bg_input':         '#222222',
    'bg_row_hover':     '#1e1e1e',
    'bg_mode_active':   '#1a2a1a',
    'border':           '#2a2a2a',
    'border_accent':    '#3a5a3a',
    'accent':           '#4ec94e',
    'accent_dim':       '#2d5e2d',
    'text':             '#d8d8d8',
    'text_dim':         '#555555',
    'text_bright':      '#ffffff',
    'text_muted':       '#888888',
    'sel_bg':           '#0d3a5c',
    'sel_fg':           '#ffffff',
    'btn_bg':           '#252525',
    'btn_fg':           '#aaaaaa',
    'btn_hover':        '#303030',
    'btn_primary_bg':   '#1e6b1e',
    'btn_primary_fg':   '#ffffff',
    'btn_primary_hover':'#28882d',
    'header_bg':        '#111111',
    'progress_bg':      '#1a1a1a',
    'progress_fg':      '#4ec94e',
    'pill_bg':          '#222222',
    'pill_fg':          '#666666',
    'pill_hover':       '#333333',
}

LIGHT_THEME = {
    'bg':               '#f2f2f2',
    'bg_panel':         '#e8e8e8',
    'bg_input':         '#ffffff',
    'bg_row_hover':     '#ebebeb',
    'bg_mode_active':   '#dff0df',
    'border':           '#d8d8d8',
    'border_accent':    '#8ec88e',
    'accent':           '#2a7a2a',
    'accent_dim':       '#c0dcc0',
    'text':             '#1c1c1c',
    'text_dim':         '#999999',
    'text_bright':      '#000000',
    'text_muted':       '#777777',
    'sel_bg':           '#0070cc',
    'sel_fg':           '#ffffff',
    'btn_bg':           '#dcdcdc',
    'btn_fg':           '#444444',
    'btn_hover':        '#cccccc',
    'btn_primary_bg':   '#2a7a2a',
    'btn_primary_fg':   '#ffffff',
    'btn_primary_hover':'#338833',
    'header_bg':        '#e0e0e0',
    'progress_bg':      '#dcdcdc',
    'progress_fg':      '#2a7a2a',
    'pill_bg':          '#d4d4d4',
    'pill_fg':          '#666666',
    'pill_hover':       '#c8c8c8',
}

C = dict(DARK_THEME)

def _font(size=10, style=''):
    if sys.platform == 'win32':
        family = 'Segoe UI'
    elif sys.platform == 'darwin':
        family = 'Helvetica Neue'
    else:
        family = 'DejaVu Sans'
    return (family, size, style) if style else (family, size)

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_text(key, lang):
    return TRANSLATIONS.get(key, {}).get(lang, f"[{key}]")

class ThemedDialog(tk.Toplevel):
    _ICON = {
        'info':     ('●', '#4ec94e'),
        'warning':  ('▲', '#e8c040'),
        'error':    ('✖', '#e05050'),
        'question': ('◆', '#5080e0'),
    }

    def __init__(self, parent, title, message, kind='info', buttons=('OK',)):
        super().__init__(parent)
        self.result = None
        self.title(title)
        self.configure(bg=C['bg'])
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        try:
            self.iconbitmap(get_resource_path("assets/icon.ico"))
        except Exception:
            pass
        self._build(title, message, kind, buttons)
        self.update_idletasks()
        pw = parent.winfo_rootx() + parent.winfo_width() // 2
        ph = parent.winfo_rooty() + parent.winfo_height() // 2
        self.geometry(f"+{pw - self.winfo_width()//2}+{ph - self.winfo_height()//2}")
        self.lift()
        self.focus_force()
        self.wait_window()

    def _build(self, title, message, kind, buttons):
        hdr = tk.Frame(self, bg=C['header_bg'], height=48)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text=title, bg=C['header_bg'], fg=C['text_bright'],
                 font=_font(12, 'bold'), padx=20, anchor='w'
                 ).pack(fill=tk.BOTH, expand=True)
        tk.Frame(self, bg=C['border'], height=1).pack(fill=tk.X)

        body = tk.Frame(self, bg=C['bg'])
        body.pack(fill=tk.BOTH, padx=28, pady=26)

        icon_char, icon_color = self._ICON.get(kind, ('●', C['accent']))
        tk.Label(body, text=icon_char, bg=C['bg'], fg=icon_color,
                 font=_font(28)).grid(row=0, column=0, sticky='n', padx=(0, 22))
        tk.Label(body, text=message, bg=C['bg'], fg=C['text'],
                 font=_font(11), wraplength=400, justify=tk.LEFT, anchor='nw'
                 ).grid(row=0, column=1, sticky='w')

        tk.Frame(self, bg=C['border'], height=1).pack(fill=tk.X)
        btn_row = tk.Frame(self, bg=C['bg_panel'])
        btn_row.pack(fill=tk.X, padx=20, pady=16)

        for i, label in enumerate(reversed(buttons)):
            primary = (i == 0)
            bg  = C['btn_primary_bg']    if primary else C['btn_bg']
            fg  = C['btn_primary_fg']    if primary else C['btn_fg']
            hbg = C['btn_primary_hover'] if primary else C['btn_hover']

            def _click(lbl=label):
                self.result = lbl
                self.destroy()

            b = tk.Button(btn_row, text=label, command=_click,
                          bg=bg, fg=fg, activebackground=hbg, activeforeground=fg,
                          relief='flat', bd=0, cursor='hand2',
                          font=_font(11), padx=22, pady=8)
            b.pack(side=tk.RIGHT, padx=(10, 0))
            b.bind('<Enter>', lambda e, btn=b, c=hbg: btn.config(bg=c))
            b.bind('<Leave>', lambda e, btn=b, c=bg:  btn.config(bg=c))

class GuiConsole(Console):
    def __init__(self, status_label, progress_bar, progress_var):
        super().__init__()
        self.status_label = status_label
        self.progress_bar = progress_bar
        self.progress_var = progress_var
        self.total = 0
        self.completed = 0
        self._current_key = None
        self._reverse = {
            text.strip(): key
            for key, langs in converter.TRANSLATIONS.items()
            for text in langs.values()
            if text.strip() and '{' not in text
        }

    def print(self, *args, **kwargs):
        message = " ".join(str(a) for a in args)
        for tag in ['cyan', 'green', 'yellow', 'red', 'bold']:
            message = message.replace(f'[{tag}]', '').replace(f'[/{tag}]', '')
        message = message.strip()
        self._current_key = self._reverse.get(message)
        self.status_label.after(0, self.status_label.config, {"text": message})
        if any(x in message.lower() for x in ["processing files", "moving files", "compressing files"]):
            self.reset_progress()

    def reapply_lang(self, lang):
        if self._current_key:
            text = converter.TRANSLATIONS.get(self._current_key, {}).get(lang)
            if text:
                self.status_label.config(text=text)

    def reset_progress(self):
        self.completed = 0
        self.total = 0
        self.progress_var.set(0)

    def update(self, completed=None, total=None, advance=1):
        if total is not None:
            self.total = total
        if completed is not None:
            self.completed = completed
        else:
            self.completed += advance
        if self.total > 0:
            self.progress_var.set((self.completed / self.total) * 100)

class CustomProgress:
    def __init__(self, console):
        self.console = console

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    def add_task(self, description, total=None):
        if total is not None:
            self.console.reset_progress()
            self.console.total = total
        return 0

    def update(self, task_id, advance=1, completed=None, total=None):
        if total is not None:
            self.console.total = total
        self.console.update(completed=completed, advance=advance)

class ResourcePackConverter(tk.Tk):

    LANGS = [("zh", "中文"), ("en", "EN"), ("es", "ES"), ("de", "DE")]

    def __init__(self):
        super().__init__()
        self.title(get_text("title", "zh"))
        self.geometry("1040x680")
        self.minsize(840, 560)
        self.configure(bg=C['bg'])
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        try:
            self.iconbitmap(get_resource_path("assets/icon.ico"))
        except Exception:
            pass

        if sys.platform == "win32":
            self.program_dir = os.path.join(os.environ['APPDATA'], 'MCPackConverter')
        else:
            self.program_dir = os.path.join(os.path.expanduser('~'), '.mcpackconverter')

        self.settings_file = os.path.join(self.program_dir, 'settings.json')
        self.load_settings()

        self._is_dark = (self.settings.get('theme', 'dark') == 'dark')
        if not self._is_dark:
            C.update(LIGHT_THEME)

        self.current_lang    = tk.StringVar(value=self.settings.get('language', 'zh'))
        self.conversion_mode = tk.StringVar(value="cmd")
        self.processing      = False
        self._status_key     = None

        self.temp_dir = tempfile.mkdtemp(prefix="mcpack_")
        os.chmod(self.temp_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        os.makedirs(os.path.join(self.temp_dir, "input"), exist_ok=True)

        self.output_dir = self.settings.get('output_dir', os.path.join(self.program_dir, "output"))

        self._section_labels = []
        self._mode_options   = []
        self._setup_style()
        self.setup_gui()
        self.setup_console()
        self._setup_traces()

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            else:
                self.settings = {'language': 'zh', 'theme': 'dark',
                                 'output_dir': os.path.join(self.program_dir, "output")}
        except Exception:
            self.settings = {'language': 'zh', 'theme': 'dark',
                             'output_dir': os.path.join(self.program_dir, "output")}

    def save_settings(self):
        try:
            os.makedirs(self.program_dir, exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'language':   self.current_lang.get(),
                    'theme':      'dark' if self._is_dark else 'light',
                    'output_dir': self.output_dir,
                }, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def _setup_traces(self):
        for var in (self.current_lang, self.conversion_mode):
            for mode, cbname in var.trace_info():
                try:
                    var.trace_remove(mode, cbname)
                except Exception:
                    pass
        self.current_lang.trace_add("write", self.update_language)
        self.conversion_mode.trace_add("write", self._on_mode_change)

    def _switch_theme(self):
        if self.processing:
            return
        self._is_dark = not self._is_dark
        C.update(DARK_THEME if self._is_dark else LIGHT_THEME)

        saved_files = list(self.file_list.get(0, tk.END))
        saved_mode  = self.conversion_mode.get()
        saved_lang  = self.current_lang.get()

        for w in self.winfo_children():
            w.destroy()

        self._section_labels = []
        self._mode_options   = []
        self.configure(bg=C['bg'])
        self._setup_style()
        self.setup_gui()
        self.setup_console()
        self._setup_traces()

        self.current_lang.set(saved_lang)
        self.conversion_mode.set(saved_mode)

        for f in saved_files:
            self.file_list.insert(tk.END, f)
        if saved_files:
            self._file_count_var.set(str(len(saved_files)))

        self.save_settings()

    def _setup_style(self):
        s = ttk.Style(self)
        s.theme_use('clam')
        s.configure('.', background=C['bg'], foreground=C['text'],
                    borderwidth=0, relief='flat')
        s.configure('TScrollbar',
                    background=C['btn_bg'], troughcolor=C['bg_input'],
                    borderwidth=0, arrowcolor=C['text_dim'], relief='flat', arrowsize=12)
        s.map('TScrollbar',
              background=[('active', C['btn_hover']), ('pressed', C['btn_hover'])])
        s.configure('TProgressbar',
                    background=C['progress_fg'], troughcolor=C['progress_bg'],
                    borderwidth=0, thickness=3, relief='flat')

    def setup_gui(self):
        self._build_status_bar()
        self._build_action_bar()
        self._build_header()
        self._build_content()

    def _build_header(self):
        header = tk.Frame(self, bg=C['header_bg'], height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        tk.Frame(self, bg=C['border'], height=1).pack(fill=tk.X, side=tk.TOP)

        lang = self.current_lang.get()

        left = tk.Frame(header, bg=C['header_bg'])
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(24, 0))

        self.title_label = tk.Label(
            left, text=get_text("title", lang),
            bg=C['header_bg'], fg=C['text_bright'],
            font=_font(12, 'bold'), anchor='w'
        )
        self.title_label.pack(anchor='w', pady=(12, 1))

        self.subtitle_label = tk.Label(
            left, text=get_text("subtitle", lang),
            bg=C['header_bg'], fg=C['text_dim'],
            font=_font(8), anchor='w'
        )
        self.subtitle_label.pack(anchor='w')

        right = tk.Frame(header, bg=C['header_bg'])
        right.pack(side=tk.RIGHT, padx=(0, 24), fill=tk.Y)

        self._theme_lbl = tk.Label(
            right,
            text=get_text("theme_light" if self._is_dark else "theme_dark", lang),
            bg=C['pill_bg'], fg=C['pill_fg'],
            font=_font(9), padx=12, pady=4, cursor='hand2'
        )
        self._theme_lbl.pack(side=tk.LEFT, padx=(0, 16), pady=20)
        self._theme_lbl.bind('<Button-1>', lambda e: self._switch_theme())
        self._theme_lbl.bind('<Enter>',
            lambda e: self._theme_lbl.config(bg=C['pill_hover'], fg=C['text']))
        self._theme_lbl.bind('<Leave>',
            lambda e: self._theme_lbl.config(bg=C['pill_bg'], fg=C['pill_fg']))

        self._lang_btns = {}
        for code, display in self.LANGS:
            lbl = tk.Label(
                right, text=display, cursor='hand2',
                bg=C['header_bg'], font=_font(10), padx=7, pady=4
            )
            lbl.pack(side=tk.LEFT, padx=1, pady=20)
            lbl.bind('<Button-1>', lambda e, c=code: self.current_lang.set(c))
            lbl.bind('<Enter>', lambda e, l=lbl, c=code:
                     l.config(fg=C['text']) if c != self.current_lang.get() else None)
            lbl.bind('<Leave>', lambda e, l=lbl, c=code:
                     l.config(fg=C['text_dim']) if c != self.current_lang.get() else None)
            self._lang_btns[code] = lbl

        self._refresh_lang_btns()

    def _refresh_lang_btns(self):
        active = self.current_lang.get()
        for code, lbl in self._lang_btns.items():
            lbl.config(fg=C['accent'] if code == active else C['text_dim'])

    def _build_content(self):
        content = tk.Frame(self, bg=C['bg'])
        content.pack(fill=tk.BOTH, expand=True)
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, minsize=300, weight=0)
        content.grid_columnconfigure(1, minsize=1,   weight=0)
        content.grid_columnconfigure(2, weight=1)

        left = tk.Frame(content, bg=C['bg_panel'])
        left.grid(row=0, column=0, sticky='nsew')
        self._build_left_panel(left)

        tk.Frame(content, bg=C['border'], width=1).grid(row=0, column=1, sticky='ns')

        right = tk.Frame(content, bg=C['bg'])
        right.grid(row=0, column=2, sticky='nsew')
        self._build_right_panel(right)

    def _build_left_panel(self, panel):
        lang = self.current_lang.get()

        self._sec(panel, "conversion_mode")

        mode_container = tk.Frame(panel, bg=C['bg_panel'])
        mode_container.pack(fill=tk.X, padx=0, pady=(0, 4))

        self._mode_options = []
        for value, key in [("cmd", "mode_cmd"), ("item", "mode_item"), ("damage", "mode_damage")]:
            self._mode_options.append(self._mode_row(mode_container, value, key))

        self._refresh_mode_options()

        tk.Frame(panel, bg=C['border'], height=1).pack(fill=tk.X, pady=(8, 0))

        self._sec(panel, "conversion_mode_description")

        self.mode_description_label = tk.Label(
            panel, text="",
            bg=C['bg_panel'], fg=C['text_muted'],
            font=_font(9), wraplength=268,
            justify=tk.LEFT, padx=20, anchor='nw'
        )
        self.mode_description_label.pack(fill=tk.X, pady=(0, 4))
        self.update_mode_description()

        tk.Frame(panel, bg=C['border'], height=1).pack(fill=tk.X, pady=(8, 0))

        self._sec(panel, "output_folder")

        out_inner = tk.Frame(panel, bg=C['bg_panel'])
        out_inner.pack(fill=tk.X, padx=20, pady=(0, 10))

        self.output_path_var = tk.StringVar(value=self.output_dir)
        tk.Label(
            out_inner, textvariable=self.output_path_var,
            bg=C['bg_input'], fg=C['text_muted'],
            font=_font(9), anchor='w', padx=8, pady=6, wraplength=252
        ).pack(fill=tk.X, pady=(0, 7))

        self.change_output_btn = self._btn(
            out_inner, "change_output_folder", self.change_output_location
        )
        self.change_output_btn.pack(anchor='w')

        tk.Frame(panel, bg=C['bg_panel']).pack(fill=tk.BOTH, expand=True)
        tk.Frame(panel, bg=C['border'], height=1).pack(fill=tk.X)

        self.author_label = tk.Label(
            panel, text=get_text("author", lang),
            bg=C['bg_panel'], fg=C['text_dim'],
            font=_font(9), padx=20, pady=10, anchor='w'
        )
        self.author_label.pack(fill=tk.X)

    def _mode_row(self, parent, value, text_key):
        lang   = self.current_lang.get()
        active = (self.conversion_mode.get() == value)

        frame = tk.Frame(
            parent,
            bg=C['bg_mode_active'] if active else C['bg_panel'],
            cursor='hand2'
        )
        frame.pack(fill=tk.X)

        accent_bar = tk.Frame(frame, width=3,
                              bg=C['accent'] if active else C['bg_panel'])
        accent_bar.pack(side=tk.LEFT, fill=tk.Y)

        dot = tk.Label(
            frame,
            text="●" if active else "○",
            bg=C['bg_mode_active'] if active else C['bg_panel'],
            fg=C['accent'] if active else C['text_dim'],
            font=_font(9), padx=10
        )
        dot.pack(side=tk.LEFT, pady=10)

        label = tk.Label(
            frame,
            text=get_text(text_key, lang),
            bg=C['bg_mode_active'] if active else C['bg_panel'],
            fg=C['text_bright'] if active else C['text'],
            font=_font(11) if active else _font(10),
            anchor='w', pady=10
        )
        label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        def select():
            self.conversion_mode.set(value)

        def on_enter(e):
            if self.conversion_mode.get() != value:
                for w in [frame, dot, label]:
                    w.config(bg=C['bg_row_hover'])

        def on_leave(e):
            if self.conversion_mode.get() != value:
                for w in [frame, dot, label]:
                    w.config(bg=C['bg_panel'])
                accent_bar.config(bg=C['bg_panel'])

        for w in [frame, accent_bar, dot, label]:
            w.bind('<Button-1>', lambda e: select())
        frame.bind('<Enter>', on_enter)
        label.bind('<Enter>', on_enter)
        dot.bind('<Enter>', on_enter)
        frame.bind('<Leave>', on_leave)
        label.bind('<Leave>', on_leave)
        dot.bind('<Leave>', on_leave)

        return (frame, accent_bar, dot, label, value, text_key)

    def _refresh_mode_options(self):
        active_val = self.conversion_mode.get()
        for (frame, accent_bar, dot, label, value, text_key) in self._mode_options:
            is_active = (value == active_val)
            bg = C['bg_mode_active'] if is_active else C['bg_panel']
            frame.config(bg=bg)
            accent_bar.config(bg=C['accent'] if is_active else C['bg_panel'], width=3)
            dot.config(bg=bg, fg=C['accent'] if is_active else C['text_dim'],
                       text="●" if is_active else "○")
            label.config(bg=bg,
                         fg=C['text_bright'] if is_active else C['text'],
                         font=_font(11) if is_active else _font(10))

    def _on_mode_change(self, *args):
        self._refresh_mode_options()
        self.update_mode_description()

    def _sec(self, parent, key):
        lbl = tk.Label(
            parent,
            text=get_text(key, self.current_lang.get()).upper(),
            bg=C['bg_panel'], fg=C['text_dim'],
            font=_font(8, 'bold'), padx=20, anchor='w'
        )
        lbl.pack(fill=tk.X, pady=(14, 4))
        self._section_labels.append((lbl, key))
        return lbl

    def _build_right_panel(self, panel):
        hdr = tk.Frame(panel, bg=C['bg'])
        hdr.pack(fill=tk.X)

        self._file_list_hdr = tk.Label(
            hdr, text=get_text("file_list", self.current_lang.get()).upper(),
            bg=C['bg'], fg=C['text_dim'],
            font=_font(8, 'bold'), padx=16, anchor='w'
        )
        self._file_list_hdr.pack(side=tk.LEFT, pady=(14, 4))

        self._file_count_var = tk.StringVar(value="")
        tk.Label(
            hdr, textvariable=self._file_count_var,
            bg=C['bg'], fg=C['text_dim'],
            font=_font(9), padx=16, anchor='e'
        ).pack(side=tk.RIGHT, pady=(14, 4))

        tk.Frame(panel, bg=C['border'], height=1).pack(fill=tk.X)

        list_frame = tk.Frame(panel, bg=C['bg'])
        list_frame.pack(fill=tk.BOTH, expand=True)

        sb = ttk.Scrollbar(list_frame)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_list = tk.Listbox(
            list_frame,
            bg=C['bg'], fg=C['text'],
            selectbackground=C['sel_bg'], selectforeground=C['sel_fg'],
            activestyle='none',
            borderwidth=0, highlightthickness=0,
            font=('Consolas', 10),
            yscrollcommand=sb.set
        )
        self.file_list.pack(fill=tk.BOTH, expand=True, padx=(12, 0), pady=6)
        sb.config(command=self.file_list.yview)
        self.file_list.bind('<Double-1>', self.open_selected_file)

    def _build_action_bar(self):
        tk.Frame(self, bg=C['border'], height=1).pack(fill=tk.X, side=tk.BOTTOM)

        bar = tk.Frame(self, bg=C['header_bg'], height=56)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)

        left = tk.Frame(bar, bg=C['header_bg'])
        left.pack(side=tk.LEFT, padx=12, pady=10)

        self.folder_btn = self._btn(left, "choose_folder", self.choose_folder)
        self.folder_btn.pack(side=tk.LEFT, padx=(0, 4))

        self.zip_btn = self._btn(left, "choose_zip", self.choose_zip)
        self.zip_btn.pack(side=tk.LEFT, padx=(0, 4))

        self.clear_btn = self._btn(left, "clear_files", self.clear_files)
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 4))

        self.report_btn = self._btn(left, "report_issue", self.report_issue)
        self.report_btn.pack(side=tk.LEFT)

        right = tk.Frame(bar, bg=C['header_bg'])
        right.pack(side=tk.RIGHT, padx=12, pady=10)

        self.open_output_btn = self._btn(right, "open_output_folder", self.open_output_folder)
        self.open_output_btn.pack(side=tk.LEFT, padx=(0, 10))

        lang = self.current_lang.get()
        self.convert_btn = tk.Button(
            right,
            text=get_text("start_convert", lang),
            command=self.start_conversion,
            bg=C['btn_primary_bg'], fg=C['btn_primary_fg'],
            activebackground=C['btn_primary_hover'],
            activeforeground=C['btn_primary_fg'],
            relief='flat', bd=0, cursor='hand2',
            font=_font(12, 'bold'), padx=22, pady=6
        )
        self.convert_btn.pack(side=tk.LEFT)
        self.convert_btn.bind('<Enter>',
            lambda e: self.convert_btn.config(bg=C['btn_primary_hover']))
        self.convert_btn.bind('<Leave>',
            lambda e: self.convert_btn.config(bg=C['btn_primary_bg']))

    def _build_status_bar(self):
        bar = tk.Frame(self, bg=C['bg_panel'])
        bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            bar, variable=self.progress_var, maximum=100, style='TProgressbar'
        )
        self.progress_bar.pack(fill=tk.X)

        self.status_label = tk.Label(
            bar, text="",
            bg=C['bg_panel'], fg=C['text_muted'],
            font=_font(9), padx=14, pady=4, anchor='w'
        )
        self.status_label.pack(fill=tk.X)

    def _btn(self, parent, text_key, command, primary=False):
        bg  = C['btn_primary_bg']    if primary else C['btn_bg']
        fg  = C['btn_primary_fg']    if primary else C['btn_fg']
        hbg = C['btn_primary_hover'] if primary else C['btn_hover']
        btn = tk.Button(
            parent,
            text=get_text(text_key, self.current_lang.get()),
            command=command,
            bg=bg, fg=fg, activebackground=hbg, activeforeground=fg,
            relief='flat', bd=0, cursor='hand2',
            font=_font(10), padx=12, pady=6
        )
        btn.bind('<Enter>', lambda e: btn.config(bg=hbg))
        btn.bind('<Leave>', lambda e: btn.config(bg=bg))
        return btn

    def setup_console(self):
        self.gui_console = GuiConsole(
            self.status_label, self.progress_bar, self.progress_var
        )
        converter.console = self.gui_console
        converter.CustomProgress = CustomProgress

    def update_language(self, *args):
        lang = self.current_lang.get()

        self.title(get_text("title", lang))
        self.title_label.config(text=get_text("title", lang))
        self.subtitle_label.config(text=get_text("subtitle", lang))
        self._refresh_lang_btns()
        self.author_label.config(text=get_text("author", lang))
        self._theme_lbl.config(
            text=get_text("theme_light" if self._is_dark else "theme_dark", lang)
        )

        for lbl, key in self._section_labels:
            lbl.config(text=get_text(key, lang).upper())

        for (_, _, _, label, value, text_key) in self._mode_options:
            label.config(text=get_text(text_key, lang))

        self.update_mode_description()
        self._file_list_hdr.config(text=get_text("file_list", lang).upper())

        self.change_output_btn.config(text=get_text("change_output_folder", lang))
        self.folder_btn.config(text=get_text("choose_folder", lang))
        self.zip_btn.config(text=get_text("choose_zip", lang))
        self.clear_btn.config(text=get_text("clear_files", lang))
        self.report_btn.config(text=get_text("report_issue", lang))
        self.open_output_btn.config(text=get_text("open_output_folder", lang))
        self.convert_btn.config(text=get_text("start_convert", lang))

        if self._status_key:
            self.status_label.config(text=get_text(self._status_key, lang))
        elif hasattr(self, 'gui_console'):
            self.gui_console.reapply_lang(lang)

        converter.CURRENT_LANG = lang
        self.save_settings()

    def update_mode_description(self, *args):
        mode = self.conversion_mode.get()
        lang = self.current_lang.get()
        key  = {"cmd": "mode_cmd_description",
                "item": "mode_item_description",
                "damage": "mode_damage_description"}.get(mode, "")
        if hasattr(self, 'mode_description_label') and self.mode_description_label:
            self.mode_description_label.config(text=get_text(key, lang) if key else "")

    def _info(self, title, message):
        ThemedDialog(self, title, message, 'info',
                     (get_text('ok', self.current_lang.get()),))

    def _error(self, title, message):
        ThemedDialog(self, title, message, 'error',
                     (get_text('ok', self.current_lang.get()),))

    def _warning(self, title, message):
        ThemedDialog(self, title, message, 'warning',
                     (get_text('ok', self.current_lang.get()),))

    def _ask(self, title, message, kind='question'):
        lang   = self.current_lang.get()
        ok_txt = get_text('ok', lang)
        ca_txt = get_text('cancel', lang)
        d = ThemedDialog(self, title, message, kind, buttons=(ca_txt, ok_txt))
        return d.result == ok_txt

    def change_output_location(self):
        new_dir = filedialog.askdirectory(
            title=get_text("select_output_folder", self.current_lang.get()),
            initialdir=self.output_dir
        )
        if new_dir:
            self.output_dir = new_dir
            self.output_path_var.set(new_dir)
            self.save_settings()

    def open_output_folder(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        if sys.platform == "win32":
            os.startfile(self.output_dir)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", self.output_dir])
        else:
            subprocess.Popen(["xdg-open", self.output_dir])

    def set_buttons_state(self, state):
        tk_state = tk.DISABLED if state == 'disabled' else tk.NORMAL
        for btn in [self.folder_btn, self.zip_btn, self.convert_btn, self.clear_btn]:
            btn.config(state=tk_state)
        for (frame, _, _, _, value, _) in self._mode_options:
            frame.config(cursor='' if state == 'disabled' else 'hand2')

    def handle_remove_readonly(self, func, path, exc):
        excvalue = exc[1]
        if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
            os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            func(path)
        else:
            raise excvalue

    def update_file_list(self):
        self.file_list.delete(0, tk.END)
        input_dir = os.path.join(self.temp_dir, "input")
        count = 0
        for root, _, files in os.walk(input_dir):
            for file in files:
                if file.lower().endswith('.json'):
                    rel = os.path.relpath(os.path.join(root, file), input_dir)
                    self.file_list.insert(tk.END, rel)
                    count += 1
        self._file_count_var.set(str(count) if count else "")

    def open_selected_file(self, event):
        sel = self.file_list.curselection()
        if sel:
            path = os.path.join(self.temp_dir, "input", self.file_list.get(sel))
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])

    def process_files_async(self, input_path, is_zip=False):
        try:
            input_dir = os.path.join(self.temp_dir, "input")
            if os.path.exists(input_dir):
                shutil.rmtree(input_dir, onerror=self.handle_remove_readonly)
            os.makedirs(input_dir)

            if is_zip:
                self._status_key = "extracting"
                self.after(0, self.status_label.config,
                           {"text": get_text("extracting", self.current_lang.get())})
                with zipfile.ZipFile(input_path, 'r') as zf:
                    files = [f for f in zf.namelist() if not f.startswith('.git/')]
                    total = len(files)
                    for i, f in enumerate(files, 1):
                        zf.extract(f, input_dir)
                        self.progress_var.set((i / total) * 100)
            else:
                self._status_key = "copying_files"
                self.after(0, self.status_label.config,
                           {"text": get_text("copying_files", self.current_lang.get())})
                total = sum(len(fs) for r, _, fs in os.walk(input_path) if '.git' not in r)
                done  = 0
                for root, _, flist in os.walk(input_path):
                    if '.git' in root:
                        continue
                    for file in flist:
                        src = os.path.join(root, file)
                        dst = os.path.join(input_dir, os.path.relpath(src, input_path))
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        shutil.copy2(src, dst)
                        done += 1
                        self.progress_var.set((done / total) * 100)

            self._status_key = None
            self.after(0, self.update_file_list)
            self.after(0, self.status_label.config, {"text": ""})
            self.after(0, self.progress_var.set, 0)

        except Exception as e:
            err = str(e)
            self.after(0, lambda: self._error(get_text("error", self.current_lang.get()), err))
        finally:
            self._status_key = None
            self.processing = False
            self.after(0, self.set_buttons_state, '!disabled')

    def choose_folder(self):
        if self.processing:
            return
        folder = filedialog.askdirectory(
            title=get_text("select_folder", self.current_lang.get())
        )
        if folder:
            self.processing = True
            self.set_buttons_state('disabled')
            threading.Thread(target=self.process_files_async, args=(folder, False)).start()

    def choose_zip(self):
        if self.processing:
            return
        zip_file = filedialog.askopenfilename(
            title=get_text("select_zip", self.current_lang.get()),
            filetypes=[("ZIP files", "*.zip")]
        )
        if zip_file:
            self.processing = True
            self.set_buttons_state('disabled')
            threading.Thread(target=self.process_files_async, args=(zip_file, True)).start()

    def clear_files(self):
        self.file_list.delete(0, tk.END)
        self._file_count_var.set("")
        input_dir = os.path.join(self.temp_dir, "input")
        if os.path.exists(input_dir):
            shutil.rmtree(input_dir, onerror=self.handle_remove_readonly)
        os.makedirs(input_dir)
        self.progress_var.set(0)
        self.status_label.config(text="")

    def report_issue(self):
        import webbrowser
        webbrowser.open("https://github.com/BrilliantTeam/Minecraft-ResourcePack-Migrator/issues")

    def start_conversion(self):
        lang = self.current_lang.get()
        if self.file_list.size() == 0:
            self._warning(get_text("warning", lang), get_text("select_files_first", lang))
            return
        if self.processing:
            return
        self.processing = True
        self.set_buttons_state('disabled')
        threading.Thread(target=self.convert_files).start()

    def convert_files(self):
        lang = self.current_lang.get()
        temp_output_dir = None
        try:
            original_cwd = os.getcwd()
            converter.CURRENT_LANG = lang

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_zip  = f"converted_{timestamp}.zip"
            output_path = os.path.join(self.output_dir, output_zip)

            temp_input_dir  = os.path.join(self.temp_dir, "input")
            temp_output_dir = os.path.join(self.temp_dir, "temp_output")
            os.chdir(self.temp_dir)
            os.makedirs(temp_output_dir, exist_ok=True)

            try:
                mode = self.conversion_mode.get()
                if mode == "item":
                    converter.process_directory_item_model(temp_input_dir, temp_output_dir)
                else:
                    converter.process_directory(temp_input_dir, temp_output_dir, mode)
                    converter.adjust_folder_structure(temp_output_dir)

                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                converter.create_zip(temp_output_dir, output_path)

                if os.path.exists(output_path):
                    msg = get_text("conversion_complete", lang).format(output_zip)
                    self.after(0, lambda: self._info(get_text("complete", lang), msg))
                else:
                    raise Exception(get_text("conversion_failed", lang).format(
                        get_text("file_generation_failed", lang)
                    ))
            finally:
                os.chdir(original_cwd)

        except Exception as e:
            err = str(e)
            self.after(0, lambda: self._error(get_text("error", lang), err))
        finally:
            self.gui_console._current_key = None
            self.processing = False
            self.progress_var.set(0)
            self.status_label.config(text="")
            self.after(0, self.set_buttons_state, '!disabled')
            if temp_output_dir and os.path.exists(temp_output_dir):
                try:
                    shutil.rmtree(temp_output_dir, onerror=self.handle_remove_readonly)
                except Exception:
                    pass

    def on_closing(self):
        lang = self.current_lang.get()
        if self.processing:
            ok = self._ask(get_text("confirm_exit", lang),
                           get_text("confirm_exit_processing", lang), kind='warning')
        else:
            ok = self._ask(get_text("confirm_exit", lang),
                           get_text("confirm_exit_normal", lang), kind='question')
        if ok:
            self.save_settings()
            if os.path.exists(self.temp_dir):
                try:
                    shutil.rmtree(self.temp_dir, onerror=self.handle_remove_readonly)
                except Exception:
                    pass
            self.quit()

def main():
    try:
        if sys.platform.startswith('win'):
            os.system('chcp 65001')
        app = ResourcePackConverter()
        app.mainloop()
    except Exception as e:
        import traceback
        msg = f"An error occurred:\n{e}\n\nDetails:\n{traceback.format_exc()}"
        try:
            from tkinter import messagebox as _mb
            _mb.showerror("Error", msg)
        except Exception:
            print(msg)
            input("Press Enter to close...")
        sys.exit(1)

if __name__ == "__main__":
    main()
