"""
Minecraft Resource Pack Converter GUI Application

This application provides a graphical interface for converting Minecraft resource packs
between different formats. It supports both Custom Model Data and Item Model conversions,
with a bilingual interface (English/Chinese).

Features:
- Bilingual support (English/Chinese)
- Two conversion modes: Custom Model Data and Item Model
- Support for both folder and ZIP file inputs
- Progress tracking and status display
- Configurable output location
- Cross-platform compatibility

Author: RiceChen_
Version: 1.2.5
"""

import sys
import os
import shutil
import zipfile
import tempfile
import errno
import stat
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import converter
import json
import threading
from rich.console import Console
import subprocess

# Language translation mapping dictionary
# Keys are UI element identifiers, values are language-specific translations
TRANSLATIONS = {
    "title": {
        "zh": "Minecraft 資源包更新工具 (1.14 ~ 1.21.4+)",
        "en": "Minecraft Resource Pack Migrator (1.14 ~ 1.21.4+)"
    },
    "language_selection": {
        "zh": "語言選擇 | Language Selection",
        "en": "語言選擇 | Language Selection"
    },
    "conversion_mode": {
        "zh": "轉換模式",
        "en": "Conversion Mode"
    },
    "mode_cmd": {
        "zh": "Custom Model Data 轉換",
        "en": "Custom Model Data Conversion"
    },
    "mode_item": {
        "zh": "Item Model 轉換",
        "en": "Item Model Conversion"
    },
    "file_list": {
        "zh": "檔案列表",
        "en": "File List"
    },
    "choose_folder": {
        "zh": "選擇資料夾",
        "en": "Choose Folder"
    },
    "choose_zip": {
        "zh": "選擇ZIP",
        "en": "Choose ZIP"
    },
    "start_convert": {
        "zh": "開始轉換",
        "en": "Start Convert"
    },
    "author": {
        "zh": "作者：RiceChen_",
        "en": "Author: RiceChen_"
    },
    "clear_files": {
        "zh": "清除檔案",
        "en": "Clear Files"
    },
    "confirm_exit": {
        "zh": "確認離開",
        "en": "Confirm Exit"
    },
    "confirm_exit_processing": {
        "zh": "正在處理檔案中，確定要離開嗎？\n檔案處理將會中斷。",
        "en": "Processing files, are you sure to exit?\nFile processing will be interrupted."
    },
    "confirm_exit_normal": {
        "zh": "確定要離開程式嗎？",
        "en": "Are you sure to exit?"
    },
    "warning": {
        "zh": "警告",
        "en": "Warning"
    },
    "select_files_first": {
        "zh": "請先選擇檔案",
        "en": "Please select files first"
    },
    "complete": {
        "zh": "完成",
        "en": "Complete"
    },
    "conversion_complete": {
        "zh": "轉換完成！輸出檔案：{}",
        "en": "Conversion complete! Output file: {}"
    },
    "select_folder": {
        "zh": "選擇資料夾",
        "en": "Select Folder"
    },
    "select_zip": {
        "zh": "選擇ZIP檔案",
        "en": "Select ZIP File"
    },
    "extracting": {
        "zh": "正在解壓縮...",
        "en": "Extracting..."
    },
    "copying_files": {
        "zh": "正在複製檔案...",
        "en": "Copying files..."
    },
    "error": {
        "zh": "錯誤",
        "en": "Error"
    },
    "processing": {
        "zh": "處理中...",
        "en": "Processing..."
    },
    "conversion_failed": {
        "zh": "轉換失敗：{}",
        "en": "Conversion failed: {}"
    },
    "output_folder": {
        "zh": "輸出資料夾",
        "en": "Output Folder"
    },
    "open_output_folder": {
        "zh": "開啟輸出資料夾",
        "en": "Open Output Folder"
    },
    "change_output_folder": {
        "zh": "變更輸出位置",
        "en": "Change Output Location"
    },
    "select_output_folder": {
        "zh": "選擇輸出資料夾",
        "en": "Select Output Folder"
    }
}

def get_text(key, lang):
    """
    Retrieve text in the specified language for a given key
    
    Args:
        key (str): Translation key to look up
        lang (str): Language code ('zh' or 'en')
    
    Returns:
        str: Translated text or error message if translation not found
    """
    return TRANSLATIONS.get(key, {}).get(lang, f"Missing translation: {key}")

class GuiConsole(Console):
    """
    Custom console class for GUI integration
    
    Extends rich.console.Console to provide GUI-specific functionality including
    progress tracking and status updates through the GUI interface.
    """
    
    def __init__(self, status_label, progress_bar, progress_var):
        """
        Initialize GUI console with Tkinter widgets
        
        Args:
            status_label: Label widget for status messages
            progress_bar: Progressbar widget for progress display
            progress_var: Variable for progress tracking
        """
        super().__init__()
        self.status_label = status_label
        self.progress_bar = progress_bar
        self.progress_var = progress_var
        self.current_task = None
        self.total = 0
        self.completed = 0

    def print(self, *args, **kwargs):
        """
        Handle output messages and update status label
        
        Converts rich console formatted text to plain text and updates the GUI status.
        
        Args:
            *args: Variable length argument list for message components
            **kwargs: Arbitrary keyword arguments
        """
        message = " ".join(str(arg) for arg in args)
        # Remove rich format tags
        for tag in ['cyan', 'green', 'yellow', 'red', 'bold']:
            message = message.replace(f'[{tag}]', '').replace(f'[/{tag}]', '')
        
        self.status_label.after(0, self.status_label.config, {"text": message})
        
        # Reset progress for specific operations
        if any(x in message.lower() for x in ["processing files", "moving files", "compressing files"]):
            self.reset_progress()

    def reset_progress(self):
        """Reset progress tracking variables and progress bar display"""
        self.completed = 0
        self.total = 0
        self.progress_var.set(0)

    def update(self, completed=None, total=None, advance=1):
        """
        Update progress bar status
        
        Args:
            completed (int, optional): Number of completed items
            total (int, optional): Total number of items
            advance (int): Number of steps to advance
        """
        if total is not None:
            self.total = total
        if completed is not None:
            self.completed = completed
        else:
            self.completed += advance

        if self.total > 0:
            progress = (self.completed / self.total) * 100
            self.progress_var.set(progress)

class CustomProgress:
    """
    Custom progress tracking class for GUI integration
    
    Provides a progress tracking interface compatible with rich.progress
    while updating GUI elements. Used as a bridge between the converter
    module and the GUI.
    """
    
    def __init__(self, console):
        """
        Initialize progress tracker
        
        Args:
            console: GuiConsole instance for progress updates
        """
        self.console = console

    def __enter__(self):
        """Context manager entry point"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point"""
        pass

    def add_task(self, description, total=None):
        """
        Add a new progress tracking task
        
        Args:
            description (str): Task description
            total (int, optional): Total number of steps
            
        Returns:
            int: Task ID (always 0 in this implementation)
        """
        if total is not None:
            self.console.reset_progress()
            self.console.total = total
        return 0

    def update(self, task_id, advance=1, completed=None, total=None):
        """
        Update progress for a task
        
        Args:
            task_id (int): Task identifier (ignored)
            advance (int): Steps to advance
            completed (int, optional): Completed steps
            total (int, optional): Total steps
        """
        if total is not None:
            self.console.total = total
        self.console.update(completed=completed, advance=advance)

class ResourcePackConverter(tk.Tk):
    """
    Main application class for the Minecraft Resource Pack Converter
    
    Provides a graphical interface for converting Minecraft resource packs
    between different formats. Handles file selection, conversion process,
    progress display, and user interaction.
    """
    
    def __init__(self):
        """Initialize the application window and setup required components"""
        super().__init__()
        
        # Basic window setup
        self.title(get_text("title", "zh"))
        self.geometry("800x600")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initialize variables
        self.current_lang = tk.StringVar(value="zh")
        self.current_lang.trace_add("write", self.update_language)
        self.conversion_mode = tk.StringVar(value="cmd")
        self.processing = False
        
        # Setup program directories
        self.program_dir = os.path.join(os.environ['ProgramFiles'], 'MCPackConverter')
        self.setup_directories()
        
        # Create temporary working directory
        self.temp_dir = tempfile.mkdtemp(prefix="mcpack_")
        os.chmod(self.temp_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        os.makedirs(os.path.join(self.temp_dir, "input"), exist_ok=True)
        
        # Set output directory
        self.output_dir = os.path.join(self.program_dir, "output")
        
        # Create main frame and GUI elements
        self.setup_gui()
        
        # Initialize console and converter
        self.setup_console()

    def setup_directories(self):
        """
        Set up necessary program directories with appropriate permissions
        
        Creates program directories and sets appropriate access permissions.
        Handles any permission-related errors during setup.
        """
        try:
            # Create main program directory
            if not os.path.exists(self.program_dir):
                os.makedirs(self.program_dir)
            
            # Create input and output directories
            for dir_name in ['input', 'output']:
                dir_path = os.path.join(self.program_dir, dir_name)
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
            
            # Set directory permissions
            for root, dirs, files in os.walk(self.program_dir):
                for d in dirs:
                    dir_path = os.path.join(root, d)
                    os.chmod(dir_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                for f in files:
                    file_path = os.path.join(root, f)
                    os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
                    
        except PermissionError:
            messagebox.showerror(
                "Error",
                "Unable to create necessary directories. Please run as administrator."
            )
            sys.exit(1)
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error while setting up directories: {str(e)}"
            )
            sys.exit(1)

    def setup_gui(self):
        """
        Set up the main GUI components
        
        Creates and configures all GUI elements including frames, buttons,
        and other widgets.
        """
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_title()
        self.create_language_selection()
        self.create_conversion_mode()
        self.create_output_selection()
        self.create_file_list()
        self.create_buttons()
        self.create_progress()
        self.create_status()

    def create_title(self):
        """
        Create and configure the application title section
        
        Creates a frame with the application title and author information
        """
        title_frame = ttk.Frame(self.main_frame)
        title_frame.pack(pady=10)
        
        self.title_label = ttk.Label(
            title_frame,
            text=get_text("title", self.current_lang.get()),
            font=('TkDefaultFont', 12, 'bold'),
            justify='center'
        )
        self.title_label.pack()
        
        self.author_label = ttk.Label(
            title_frame,
            text=get_text("author", self.current_lang.get()),
            font=('TkDefaultFont', 9, 'bold'),
            justify='center'
        )
        self.author_label.pack()

    def create_conversion_mode(self):
        """
        Create the conversion mode selection section
        
        Creates radio buttons for selecting between Custom Model Data
        and Item Model conversion modes
        """
        self.mode_frame = ttk.LabelFrame(
            self.main_frame,
            text=get_text("conversion_mode", self.current_lang.get())
        )
        self.mode_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Radiobutton(
            self.mode_frame,
            text=get_text("mode_cmd", self.current_lang.get()),
            variable=self.conversion_mode,
            value="cmd"
        ).pack(side=tk.LEFT, padx=20, pady=5)
        
        ttk.Radiobutton(
            self.mode_frame,
            text=get_text("mode_item", self.current_lang.get()),
            value="item",
            variable=self.conversion_mode
        ).pack(side=tk.LEFT, padx=20, pady=5)

    def create_output_selection(self):
        """
        Create the output directory selection section
        
        Creates a frame showing the current output path and a button
        to change the output location. Includes a label displaying the
        current path and a button to modify it.
        """
        self.output_frame = ttk.LabelFrame(
            self.main_frame,
            text=get_text("output_folder", self.current_lang.get())
        )
        self.output_frame.pack(fill=tk.X, padx=5, pady=5)

        # Display current output path with word wrap
        self.output_path_var = tk.StringVar(value=self.output_dir)
        path_label = ttk.Label(
            self.output_frame,
            textvariable=self.output_path_var,
            wraplength=600
        )
        path_label.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        # Change location button
        self.change_output_btn = ttk.Button(
            self.output_frame,
            text=get_text("change_output_folder", self.current_lang.get()),
            command=self.change_output_location
        )
        self.change_output_btn.pack(side=tk.RIGHT, padx=5, pady=5)

    def create_language_selection(self):
        """
        Create the language selection section
        
        Creates a frame with radio buttons for language selection (Chinese/English).
        Changes take effect immediately upon selection.
        """
        self.lang_frame = ttk.LabelFrame(
            self.main_frame,
            text=get_text("language_selection", self.current_lang.get())
        )
        self.lang_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Chinese option
        ttk.Radiobutton(
            self.lang_frame,
            text="中文",
            variable=self.current_lang,
            value="zh"
        ).pack(side=tk.LEFT, padx=20, pady=5)
        
        # English option
        ttk.Radiobutton(
            self.lang_frame,
            text="English",
            variable=self.current_lang,
            value="en"
        ).pack(side=tk.LEFT, padx=20, pady=5)

    def create_file_list(self):
        """
        Create the file list display section
        
        Creates a scrollable listbox showing all JSON files that will be
        processed during conversion. Includes a scrollbar for navigation.
        """
        self.list_frame = ttk.LabelFrame(
            self.main_frame,
            text=get_text("file_list", self.current_lang.get())
        )
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create and configure scrollbar
        scrollbar = ttk.Scrollbar(self.list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create and configure listbox
        self.file_list = tk.Listbox(
            self.list_frame,
            yscrollcommand=scrollbar.set
        )
        self.file_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.file_list.yview)

    def create_buttons(self):
        """
        Create the control buttons section
        
        Creates two groups of buttons:
        1. Left side: folder selection, ZIP selection, conversion start, and clear
        2. Right side: output folder access
        """
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create left-side button frame
        left_frame = ttk.Frame(btn_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Define and create main action buttons
        buttons = [
            ("folder_btn", "choose_folder", self.choose_folder),
            ("zip_btn", "choose_zip", self.choose_zip),
            ("convert_btn", "start_convert", self.start_conversion),
            ("clear_btn", "clear_files", self.clear_files)
        ]
        
        # Create each button with proper text and command
        for attr, text_key, command in buttons:
            btn = ttk.Button(
                left_frame,
                text=get_text(text_key, self.current_lang.get()),
                command=command
            )
            btn.pack(side=tk.LEFT, padx=5)
            setattr(self, attr, btn)
        
        # Create output folder open button on right side
        self.open_output_btn = ttk.Button(
            btn_frame,
            text=get_text("open_output_folder", self.current_lang.get()),
            command=self.open_output_folder
        )
        self.open_output_btn.pack(side=tk.RIGHT, padx=5)

    def change_output_location(self):
        """
        Handle output location change request
        
        Opens a directory selection dialog and updates the output location
        if a new directory is selected.
        """
        new_dir = filedialog.askdirectory(
            title=get_text("select_output_folder", self.current_lang.get()),
            initialdir=self.output_dir
        )
        if new_dir:
            self.output_dir = new_dir
            self.output_path_var.set(new_dir)

    def open_output_folder(self):
        """
        Open the output folder in the system's file explorer
        
        Uses platform-specific commands to open the folder:
        - Windows: explorer.exe
        - macOS: open command
        - Linux: xdg-open
        """
        if sys.platform == "win32":
            os.startfile(self.output_dir)
        elif sys.platform == "darwin":  # macOS
            subprocess.Popen(["open", self.output_dir])
        else:  # Linux
            subprocess.Popen(["xdg-open", self.output_dir])

    def create_progress(self):
        """
        Create the progress bar
        
        Creates a progress bar for showing conversion progress
        and file processing status.
        """
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.main_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)

    def create_status(self):
        """
        Create the status display
        
        Creates a label for showing status messages and progress information.
        Text wraps automatically to fit the window width.
        """
        self.status_label = ttk.Label(
            self.main_frame,
            text="",
            wraplength=780
        )
        self.status_label.pack(pady=5, fill=tk.X)

    def setup_console(self):
        """
        Initialize the console and converter components
        
        Creates a GUI console instance and configures the converter
        module to use it for output and progress tracking.
        """
        self.gui_console = GuiConsole(
            self.status_label,
            self.progress_bar,
            self.progress_var
        )
        converter.console = self.gui_console
        converter.CustomProgress = CustomProgress

    def update_language(self, *args):
        """
        Update all interface text when language is changed
        
        Updates text in:
        - Window title
        - All labels and frame titles
        - All buttons
        - Conversion mode radio buttons
        Also updates the converter module's language setting.
        
        Args:
            *args: Variable arguments (unused, required for trace_add callback)
        """
        lang = self.current_lang.get()
        
        # Update window and main labels
        self.title(get_text("title", lang))
        self.title_label.config(text=get_text("title", lang))
        self.author_label.config(text=get_text("author", lang))
        
        # Update frame titles
        self.lang_frame.config(text=get_text("language_selection", lang))
        self.mode_frame.config(text=get_text("conversion_mode", lang))
        self.list_frame.config(text=get_text("file_list", lang))
        self.output_frame.config(text=get_text("output_folder", lang))
        
        # Update button text
        self.folder_btn.config(text=get_text("choose_folder", lang))
        self.zip_btn.config(text=get_text("choose_zip", lang))
        self.convert_btn.config(text=get_text("start_convert", lang))
        self.clear_btn.config(text=get_text("clear_files", lang))
        self.change_output_btn.config(text=get_text("change_output_folder", lang))
        self.open_output_btn.config(text=get_text("open_output_folder", lang))
        
        # Update conversion mode radio buttons
        for radio_button in self.mode_frame.winfo_children():
            if isinstance(radio_button, ttk.Radiobutton):
                value = radio_button.cget("value")
                if value == "cmd":
                    radio_button.config(text=get_text("mode_cmd", lang))
                elif value == "item":
                    radio_button.config(text=get_text("mode_item", lang))
        
        # Update converter module language
        converter.CURRENT_LANG = lang

    def set_buttons_state(self, state):
        """
        Enable or disable all control buttons
        
        Args:
            state (str): Button state ('disabled' or '!disabled')
        """
        # Update main buttons
        for btn in [self.folder_btn, self.zip_btn, self.convert_btn, self.clear_btn]:
            btn.state([state])
        
        # Update conversion mode radio buttons
        for radio_button in self.mode_frame.winfo_children():
            if isinstance(radio_button, ttk.Radiobutton):
                if state == 'disabled':
                    radio_button.state(['disabled'])
                else:
                    radio_button.state(['!disabled'])

    def handle_remove_readonly(self, func, path, exc):
        """
        Handle removal of read-only files
        
        Special handler for shutil.rmtree to handle read-only files on Windows.
        
        Args:
            func: Original function that failed
            path: Path to the file/directory
            exc: Exception information tuple
        
        Raises:
            Original exception if not a permission error
        """
        excvalue = exc[1]
        if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
            os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            func(path)
        else:
            raise excvalue

    def process_files_async(self, input_path, is_zip=False):
        """
        Process input files asynchronously
        
        Handles both ZIP files and folders as input. Extracts/copies files
        to a temporary directory while updating progress.
        
        Args:
            input_path (str): Path to input ZIP file or folder
            is_zip (bool): Whether the input is a ZIP file
        """
        try:
            # Prepare input directory
            input_dir = os.path.join(self.temp_dir, "input")
            if os.path.exists(input_dir):
                shutil.rmtree(input_dir, onerror=self.handle_remove_readonly)
            os.makedirs(input_dir)

            lang = self.current_lang.get()
            
            # Handle ZIP file input
            if is_zip:
                self.status_label.config(text=get_text("extracting", lang))
                with zipfile.ZipFile(input_path, 'r') as zip_ref:
                    file_list = [f for f in zip_ref.namelist() 
                                if not f.startswith('.git/')]
                    total_files = len(file_list)
                    for i, file in enumerate(file_list, 1):
                        zip_ref.extract(file, input_dir)
                        self.progress_var.set((i / total_files) * 100)
                        
            # Handle folder input
            else:
                self.status_label.config(text=get_text("copying_files", lang))
                total_items = sum([len(files) for root, _, files in os.walk(input_path) 
                                if '.git' not in root])
                processed = 0
                
                for root, _, files in os.walk(input_path):
                    if '.git' in root:
                        continue
                        
                    for file in files:
                        src_path = os.path.join(root, file)
                        rel_path = os.path.relpath(src_path, input_path)
                        dst_path = os.path.join(input_dir, rel_path)
                        
                        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                        shutil.copy2(src_path, dst_path)
                        
                        processed += 1
                        self.progress_var.set((processed / total_items) * 100)

            # Update UI after processing
            self.update_file_list()
            self.status_label.config(text="")
            self.progress_var.set(0)

        except Exception as e:
            self.after(0, messagebox.showerror, 
                        get_text("error", self.current_lang.get()), 
                        str(e))
        finally:
            self.processing = False
            self.after(0, self.set_buttons_state, '!disabled')

    def update_file_list(self):
        """
        Update the file list display
        
        Scans the input directory for JSON files and updates the listbox
        with their relative paths.
        """
        self.file_list.delete(0, tk.END)
        input_dir = os.path.join(self.temp_dir, "input")
        for root, _, files in os.walk(input_dir):
            for file in files:
                if file.lower().endswith('.json'):
                    rel_path = os.path.relpath(os.path.join(root, file), input_dir)
                    self.file_list.insert(tk.END, rel_path)

    def choose_folder(self):
        """
        Handle folder selection
        
        Opens a folder selection dialog and starts processing the selected
        folder if one is chosen. Processing is done in a separate thread.
        """
        if self.processing:
            return
        
        folder = filedialog.askdirectory(
            title=get_text("select_folder", self.current_lang.get())
        )
        if folder:
            self.processing = True
            self.set_buttons_state('disabled')
            threading.Thread(
                target=self.process_files_async,
                args=(folder, False)
            ).start()

    def choose_zip(self):
        """
        Handle ZIP file selection
        
        Opens a file selection dialog for ZIP files and starts processing
        the selected file if one is chosen. Processing is done in a
        separate thread.
        """
        if self.processing:
            return
            
        zip_file = filedialog.askopenfilename(
            title=get_text("select_zip", self.current_lang.get()),
            filetypes=[("ZIP files", "*.zip")]
        )
        if zip_file:
            self.processing = True
            self.set_buttons_state('disabled')
            threading.Thread(
                target=self.process_files_async,
                args=(zip_file, True)
            ).start()

    def clear_files(self):
        """
        Clear the input file list and temporary directory
        
        Removes all files from the input directory, clears the file list display,
        resets the progress bar, and clears the status message.
        """
        self.file_list.delete(0, tk.END)
        input_dir = os.path.join(self.temp_dir, "input")
        if os.path.exists(input_dir):
            shutil.rmtree(input_dir, onerror=self.handle_remove_readonly)
        os.makedirs(input_dir)
        self.progress_var.set(0)
        self.status_label.config(text="")

    def start_conversion(self):
        """
        Start the conversion process
        
        Validates that files are selected before starting conversion.
        Conversion is performed in a separate thread to prevent GUI freezing.
        Shows warning if no files are selected.
        """
        lang = self.current_lang.get()
        if self.file_list.size() == 0:
            messagebox.showwarning(
                get_text("warning", lang),
                get_text("select_files_first", lang)
            )
            return
        
        if self.processing:
            return
            
        self.processing = True
        self.set_buttons_state('disabled')
        threading.Thread(target=self.convert_files).start()

    def convert_files(self):
        """
        Execute the file conversion process
        
        Main conversion process handling both Custom Model Data and Item Model
        conversions. Creates a ZIP file with the converted files.
        
        Process:
        1. Prepares directories and paths
        2. Performs conversion based on selected mode
        3. Creates output ZIP file
        4. Shows completion message or error
        5. Cleans up temporary files
        """
        try:
            lang = self.current_lang.get()
            original_cwd = os.getcwd()
            temp_output_dir = None

            # Set converter language
            converter.CURRENT_LANG = self.current_lang.get()
            
            # Create timestamp and output paths
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_zip = f"converted_{timestamp}.zip"
            output_path = os.path.join(self.output_dir, output_zip)
            
            # Setup directories
            temp_input_dir = os.path.join(self.temp_dir, "input")
            temp_output_dir = os.path.join(self.temp_dir, "temp_output")
            
            # Change to temp directory
            os.chdir(self.temp_dir)
            
            # Ensure output directory exists
            if not os.path.exists(temp_output_dir):
                os.makedirs(temp_output_dir)
            
            try:
                # Convert files based on selected mode
                if self.conversion_mode.get() == "cmd":
                    processed_files = converter.process_directory(temp_input_dir, temp_output_dir)
                    # Adjust folder structure (CMD mode only)
                    converter.adjust_folder_structure(temp_output_dir)
                else:
                    processed_files = converter.process_directory_item_model(temp_input_dir, temp_output_dir)
                
                # Ensure output directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Create ZIP file
                converter.create_zip(temp_output_dir, output_path)
                
                # Show completion message
                if os.path.exists(output_path):
                    self.after(0, messagebox.showinfo,
                        get_text("complete", lang),
                        get_text("conversion_complete", lang).format(output_zip)
                    )
                else:
                    raise Exception(get_text("conversion_failed", lang).format(
                        "未能生成輸出檔案" if lang == "zh" else "Failed to generate output file"
                    ))
                
            finally:
                # Restore original working directory
                os.chdir(original_cwd)
            
        except Exception as e:
            self.after(0, messagebox.showerror, 
                        get_text("error", lang), 
                        str(e))
            
        finally:
            # Cleanup and reset UI
            self.processing = False
            self.progress_var.set(0)
            self.status_label.config(text="")
            self.after(0, self.set_buttons_state, '!disabled')
            
            # Remove temporary output directory
            if temp_output_dir and os.path.exists(temp_output_dir):
                try:
                    shutil.rmtree(temp_output_dir, onerror=self.handle_remove_readonly)
                except Exception:
                    pass

    def on_closing(self):
        """
        Handle application closing
        
        Shows confirmation dialog before closing, with different messages
        depending on whether processing is in progress. Cleans up temporary
        files before exit.
        """
        lang = self.current_lang.get()
        if self.processing:
            response = messagebox.askokcancel(
                get_text("confirm_exit", lang),
                get_text("confirm_exit_processing", lang),
                icon="warning"
            )
        else:
            response = messagebox.askokcancel(
                get_text("confirm_exit", lang),
                get_text("confirm_exit_normal", lang),
                icon="question"
            )
        
        if response:
            if os.path.exists(self.temp_dir):
                try:
                    shutil.rmtree(self.temp_dir, onerror=self.handle_remove_readonly)
                except Exception:
                    pass
            self.quit()

def main():
    """
    Main program entry point
    
    Initializes the application with proper character encoding and
    handles any unexpected errors during startup.
    
    Sets up:
    - Character encoding for Windows systems
    - Main application window
    - Error handling and reporting
    """
    try:
        # Set UTF-8 encoding for Windows systems
        if sys.platform.startswith('win'):
            os.system('chcp 65001')
        
        # Create and run main application
        app = ResourcePackConverter()
        app.mainloop()
    except Exception as e:
        # Handle unexpected errors
        import traceback
        error_message = f"An error occurred:\n{str(e)}\n\nDetails:\n{traceback.format_exc()}"
        if 'app' in locals() and hasattr(app, 'destroy'):
            messagebox.showerror("Error", error_message)
            app.destroy()
        else:
            # Fallback to console output if GUI hasn't been created
            print(error_message)
            input("Press Enter to close...")
        sys.exit(1)

if __name__ == "__main__":
    main()