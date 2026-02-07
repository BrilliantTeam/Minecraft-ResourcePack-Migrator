"""
Minecraft Resource Pack Converter - Runner Script

This script serves as the command-line interface for the resource pack converter.
It handles:
- Environment validation
- Package dependency management
- File discovery and validation
- User interaction and language selection
- Conversion process execution
- Progress reporting and error handling

The script supports multiple languages (Chinese, English, and Spanish), with full 
multilingual support for all user interactions and messages.

Author: RiceChen_
Version: 1.4.6
"""

import subprocess
import sys
import os
import time
import json
import shutil
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
import converter

# Initialize rich console for formatted output
console = Console()

# Translation dictionary mapping keys to language-specific text
TRANSLATIONS = {
    "checking_python": {
        "zh": "檢查 Python 環境...",
        "en": "Checking Python environment...",
        "es": "Verificando el entorno de Python...",
        "de": "Python-Umgebung wird überprüft..."
    },
    "python_version_error": {
        "zh": "錯誤：需要 Python 3.6 或更新版本",
        "en": "Error: Python 3.6 or newer is required",
        "es": "Error: Se requiere Python 3.6 o una versión más reciente",
        "de": "Fehler: Python Version 3.6 ist erforderlich"
    },
    "installing_package": {
        "zh": "正在安裝必要套件 {}...",
        "en": "Installing required package {}...",
        "es": "Instalando paquete requerido {}...",
        "de": "Nötige Pakete werden installiert..."
    },
    "package_install_error": {
        "zh": "錯誤：無法安裝 {}",
        "en": "Error: Unable to install {}",
        "es": "Error: No se puede instalar {}",
        "de": "Fehler: {} konnte nicht installiert werden"
    },
    "input_dir_error": {
        "zh": "錯誤：找不到輸入資料夾 '{}'",
        "en": "Error: Input directory '{}' not found",
        "es": "Error: No se encontró el directorio de entrada '{}'",
        "de": "Fehler: Der Ordner '{}' wurde nicht gefunden"
    },
    "create_input_dir": {
        "zh": "請建立 '{}' 資料夾並放入要轉換的檔案",
        "en": "Please create '{}' directory and place files to convert",
        "es": "Por favor, cree el directorio '{}' y coloque los archivos a convertir",
        "de": "Bitte erstelle den Ordner '{}' und lege die umzuwandelnden Dateien dort ab."
    },
    "searching_files": {
        "zh": "搜尋可轉換的檔案...",
        "en": "Searching for convertible files...",
        "es": "Buscando archivos convertibles...",
        "de": "Es wird nach umwandelbaren Dateien gesucht..."
    },
    "no_files_found": {
        "zh": "找不到需要轉換的檔案！",
        "en": "No files found for conversion!",
        "es": "¡No se encontraron archivos para convertir!",
        "de": "Keine Dateien für die Umwandlung gefunden!"
    },
    "check_list_title": {
        "zh": "檢查清單",
        "en": "Checklist",
        "es": "Lista de verificación",
        "de": "Checkliste"
    },
    "check_json_exists": {
        "zh": "輸入資料夾中有 JSON 檔案",
        "en": "JSON files exist in input folder",
        "es": "Existen archivos JSON en la carpeta de entrada",
        "de": "JSON-Dateien gefunden"
    },
    "check_json_format": {
        "zh": "JSON 檔案包含 'overrides' 和 'custom_model_data' 欄位",
        "en": "JSON files contain 'overrides' and 'custom_model_data' fields",
        "es": "Los archivos JSON contienen campos 'overrides' y 'custom_model_data'",
        "de": "JSON-Dateien enthalten 'overrides' und 'custom_model_data'-Felder"
    },
    "check_file_location": {
        "zh": "檔案放在正確的位置（{}/ 資料夾中）",
        "en": "Files are in correct location (in {} folder)",
        "es": "Los archivos están en la ubicación correcta (en la carpeta {})",
        "de": "Die Dateien sind am richtigen Ort (im Ordner {})"
    },
    "found_files_title": {
        "zh": "可轉換的檔案",
        "en": "Convertible Files",
        "es": "Archivos Convertibles",
        "de": "Umwandelbare Dateien"
    },
    "continue_prompt": {
        "zh": "是否繼續轉換？[Y/n]",
        "en": "Continue conversion? [Y/n]",
        "es": "¿Continuar con la conversión? [S/n]",
        "de": "Umwandlung fortsetzen? [J/N]"
    },
    "conversion_cancelled": {
        "zh": "已取消轉換",
        "en": "Conversion cancelled",
        "es": "Conversión cancelada",
        "de": "Umwandlung gestoppt"
    },
    "env_check_complete": {
        "zh": "環境檢查完成，開始執行轉換程式...",
        "en": "Environment check complete, starting conversion...",
        "es": "Verificación del entorno completada, iniciando conversión...",
        "de": "Umgebungsprüfung abgeschlossen, starte Umwandlung..."
    },
    "converter_not_found": {
        "zh": "錯誤：找不到轉換程式 (converter.py)",
        "en": "Error: Converter program (converter.py) not found",
        "es": "Error: No se encontró el programa convertidor (converter.py)",
        "de": "Fehler: Umwandlungsprogramm (converter.py) wurde nicht gefunden"
    },
    "check_converter_location": {
        "zh": "請確認 converter.py 檔案在正確的位置",
        "en": "Please ensure converter.py is in the correct location",
        "es": "Por favor, asegúrese de que converter.py esté en la ubicación correcta",
        "de": "Bitte prüfe, ob converter.py am richtigen Ort ist"
    },
    "execution_error": {
        "zh": "執行過程中發生錯誤：{}",
        "en": "Error during execution: {}",
        "es": "Error durante la ejecución: {}",
        "de": "Fehler im Prozess: {}"
    },
    "press_enter": {
        "zh": "按 Enter 鍵結束程式...",
        "en": "Press Enter to exit...",
        "es": "Presione Enter para salir...",
        "de": "Drücke Enter, um zu beenden..."
    },
    "title": {
        "zh": "Minecraft 資源包更新工具 (1.14 ~ 1.21.4+)",
        "en": "Minecraft Resource Pack Migrator (1.14 ~ 1.21.4+)",
        "es": "Migrador de Paquetes de Recursos de Minecraft (1.14 ~ 1.21.4+)",
        "de": "Minecraft Resourcenpaket-Umwandler (1.14 zu 1.21.4+)"
    },
    "enter_mode_choice": {
        "zh": "請輸入 1、2 或 3",
        "en": "Please enter 1, 2 or 3",
        "es": "Por favor ingrese 1, 2 o 3",
        "de": "Gib 1, 2 oder 3 ein"
    },
    "enter_language_choice": {
        "zh": "請輸入 1、2、3 或 4",
        "en": "Please enter 1, 2, 3 or 4",
        "es": "Por favor ingrese 1, 2, 3 o 4",
        "de": "Bitte gib 1, 2, 3 oder 4 ein"
    },
    "language_selection_prompt": {
        "zh": "語言選擇 | Language Selection | Selección de idioma | Sprachauswahl",
        "en": "語言選擇 | Language Selection | Selección de idioma | Sprachauswahl",
        "es": "語言選擇 | Language Selection | Selección de idioma | Sprachauswahl",
        "de": "語言選擇 | Language Selection | Selección de idioma | Sprachauswahl",
    },
    "language_chinese": {
        "zh": "中文",
        "en": "Chinese",
        "es": "Chino",
        "de": "Chinesisch"
    },
    "language_english": {
        "zh": "英文",
        "en": "English",
        "es": "Inglés",
        "de": "Englisch"
    },
    "language_spanish": {
        "zh": "西班牙文",
        "en": "Spanish",
        "es": "Español",
        "de": "Spanisch"
    },
    "language_german": {
        "zh": "德语",
        "en": "German",
        "es": "Alemán",
        "de": "Deutsch"
    },
    "choose_language": {
        "zh": "選擇語言",
        "en": "Choose Language",
        "es": "Seleccionar Idioma",
        "de": "Sprache auswählen"
    },
    "column_number": {
        "zh": "序號",
        "en": "No.",
        "es": "Núm.",
        "de": "Nr."
    },
    "column_file_path": {
        "zh": "檔案路徑",
        "en": "File Path",
        "es": "Ruta del Archivo",
        "de": "Dateipfad"
    },
    "choose_mode": {
        "zh": "選擇轉換模式",
        "en": "Choose Conversion Mode",
        "es": "Seleccionar Modo de Conversión",
        "de": "Umwandlungsmodus wählen"
    },
    "mode_cmd": {
        "zh": "Custom Model Data 轉換",
        "en": "Custom Model Data Conversion",
        "es": "Conversión de Custom Model Data",
        "de": "Custom Model Data Umwandlung"
    },
    "mode_item": {
        "zh": "Item Model 轉換",
        "en": "Item Model Conversion",
        "es": "Conversión de Item Model",
        "de": "Itemmodell-Unwandlung"
    },
    "mode_damage": {
        "zh": "Damage 轉換",
        "en": "Damage Conversion",
        "es": "Conversión de Daño",
        "de": "Damage-basierte Umwandlung"
    }
}

def get_text(key, lang="zh", *args):
    """
    Retrieve translated text for the specified key and language
    
    Args:
        key (str): Translation key to look up
        lang (str, optional): Language code ('zh' or 'en'). Defaults to 'zh'
        *args: Optional format arguments for the text
        
    Returns:
        str: Translated text, formatted with args if provided
    """
    text = TRANSLATIONS.get(key, {}).get(lang, f"Missing translation: {key}")
    if args:
        return text.format(*args)
    return text

def check_and_install_package(package_name, lang="zh"):
    """
    Check if a Python package is installed and install it if missing
    
    Args:
        package_name (str): Name of the package to check/install
        lang (str, optional): Language code for messages. Defaults to 'zh'
        
    Returns:
        bool: True if package is available (installed or already present),
              False if installation failed
    """
    try:
        __import__(package_name)
        return True
    except ImportError:
        console.print(f"[yellow]{get_text('installing_package', lang, package_name)}[/yellow]")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            return True
        except subprocess.CalledProcessError:
            console.print(f"[red]{get_text('package_install_error', lang, package_name)}[/red]")
            return False

def find_convertible_files(directory):
    """
    Search for JSON files that can be converted in the given directory
    
    Looks for JSON files containing custom model data overrides
    or damage predicates, checking the file structure to ensure 
    they are valid for conversion.
    
    Args:
        directory (str): Directory path to search in
        
    Returns:
        list: List of relative paths to convertible JSON files
    """
    convertible_files = []
    
    if not os.path.exists(directory):
        return convertible_files
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                    
                    # Check if file has overrides
                    if "overrides" in json_data:
                        for override in json_data.get("overrides", []):
                            if "predicate" in override:
                                predicate = override["predicate"]
                                # Check for either custom_model_data or damage predicates
                                if ("custom_model_data" in predicate or 
                                    ("damaged" in predicate and "damage" in predicate)):
                                    convertible_files.append(os.path.relpath(file_path, directory))
                                    break
                                    
                except (json.JSONDecodeError, UnicodeDecodeError, Exception):
                    continue
    
    return convertible_files

def display_convertible_files(files, lang):
    """
    Display a formatted table of convertible files
    
    Args:
        files (list): List of file paths to display
        lang (str): Language code for column headers
    """
    if not files:
        return
    
    table = Table(
        title=get_text("found_files_title", lang),
        show_header=True,
        border_style="blue",
        expand=True
    )
    
    # Add translated column headers
    table.add_column(get_text("column_number", lang), style="cyan", justify="center")
    table.add_column(get_text("column_file_path", lang), style="green")
    
    # Add files to table
    for i, file in enumerate(files, 1):
        table.add_row(str(i), file)
    
    console.print("\n", table)

def display_checklist(input_dir, lang):
    """
    Display a checklist of requirements for conversion
    
    Shows a table of items that users should verify before proceeding
    with the conversion process.
    
    Args:
        input_dir (str): Input directory path to reference in checks
        lang (str): Language code for messages
    """
    table = Table(
        title=get_text("check_list_title", lang),
        show_header=False,
        border_style="yellow",
        expand=True
    )
    
    table.add_column(style="yellow")
    
    # Add checklist items
    table.add_row(f"1. {get_text('check_json_exists', lang)}")
    table.add_row(f"2. {get_text('check_json_format', lang)}")
    table.add_row(f"3. {get_text('check_file_location', lang, input_dir)}")
    
    console.print("\n", table)

def main(lang="zh"):
    """
    Main program execution flow
    
    Handles the complete conversion process including:
    - Environment validation
    - Directory setup
    - File discovery
    - User confirmation
    - Conversion execution
    - Result reporting
    
    Args:
        lang (str, optional): Language code. Defaults to "zh"
        
    Returns:
        bool: True if conversion successful, False otherwise
    """
    # Check Python version
    console.print(f"[cyan]{get_text('checking_python', lang)}[/cyan]")
    if sys.version_info < (3, 6):
        console.print(Panel(
            get_text("python_version_error", lang),
            style="red",
            expand=False
        ))
        return False

    # Set up directories
    input_dir = "input"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Verify input directory exists
    if not os.path.exists(input_dir):
        console.print(Panel(
            f"{get_text('input_dir_error', lang, input_dir)}\n{get_text('create_input_dir', lang, input_dir)}",
            style="red",
            expand=False
        ))
        return False

    # Search for convertible files
    console.print(f"[cyan]{get_text('searching_files', lang)}[/cyan]")
    convertible_files = find_convertible_files(input_dir)
    
    if not convertible_files:
        console.print(f"\n[yellow]{get_text('no_files_found', lang)}[/yellow]")
        display_checklist(input_dir, lang)
        return False
    
    # Display found files and get user confirmation
    display_convertible_files(convertible_files, lang)

    # Prompt for conversion mode
    console.print(Panel(
        get_text("choose_mode", lang),
        style="cyan",
        expand=False
    ))
    console.print("1. [green]" + get_text("mode_cmd", lang) + "[/green]")
    console.print("2. [blue]" + get_text("mode_item", lang) + "[/blue]")
    console.print("3. [yellow]" + get_text("mode_damage", lang) + "[/yellow]")
    
    mode_choice = Prompt.ask(
        f"\n{get_text('enter_mode_choice', lang)}",
        default="1"
    ).strip()
    
    # Map mode choice to mode type
    mode_mapping = {
        "1": "cmd",
        "2": "item",
        "3": "damage"
    }
    selected_mode = mode_mapping.get(mode_choice, "cmd")

    # Get user confirmation
    if not Prompt.ask(
        f"\n[cyan]{get_text('continue_prompt', lang)}[/cyan]",
        default="y"
    ).lower() == "y":
        console.print(f"[yellow]{get_text('conversion_cancelled', lang)}[/yellow]")
        return False

    # Check and install required packages
    required_packages = ['rich']
    for package in required_packages:
        if not check_and_install_package(package, lang):
            return False

    # Start conversion process
    console.print(Panel(
        get_text("env_check_complete", lang),
        style="green",
        expand=False
    ))
    time.sleep(1)

    try:
        # Configure converter
        converter.CURRENT_LANG = lang
        converter.console = console

        # Prepare output paths
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_zip = f"converted_{timestamp}.zip"
        output_path = os.path.join(output_dir, output_zip)

        # Create temporary directory
        temp_output_dir = f"temp_output_{timestamp}"
        os.makedirs(temp_output_dir, exist_ok=True)

        try:
            # Execute conversion based on selected mode
            if selected_mode == "item":
                processed_files = converter.process_directory_item_model(input_dir, temp_output_dir)
            else:  # cmd or damage mode
                processed_files = converter.process_directory(input_dir, temp_output_dir, selected_mode)
                converter.adjust_folder_structure(temp_output_dir)
            
            # Create output ZIP file
            converter.create_zip(temp_output_dir, output_path)

            # Display completion report
            console.print(f"\n[green]{get_text('process_complete', lang)}[/green]")
            table = converter.create_file_table(processed_files)
            console.print("\n", table)

            # Show output file information
            console.print(f"\n[cyan]{get_text('converted_files_count', lang, len(processed_files))}[/cyan]")
            console.print(f"[cyan]{get_text('output_file', lang)}: {output_zip}[/cyan]")

            return True

        finally:
            # Clean up temporary directory
            if os.path.exists(temp_output_dir):
                try:
                    shutil.rmtree(temp_output_dir)
                except Exception:
                    pass

    except ImportError:
        # Handle missing converter module
        console.print(Panel(
            f"{get_text('converter_not_found', lang)}\n{get_text('check_converter_location', lang)}",
            style="red",
            expand=False
        ))
        return False
    except Exception as e:
        # Handle other errors
        console.print(Panel(
            get_text("execution_error", lang, str(e)),
            style="red",
            expand=False
        ))
        return False

if __name__ == "__main__":
    """
    Script entry point - Handles initialization and main program execution
    
    Flow:
    1. Sets up console encoding for Windows
    2. Displays language selection prompt
    3. Executes main conversion process
    4. Handles program exit
    """
    # Set UTF-8 console encoding for Windows systems
    if sys.platform.startswith('win'):
        os.system('chcp 65001')
    
    # Display language selection prompt with bilingual options
    console.print(Panel(
        get_text("language_selection_prompt", "zh"),
        style="cyan",
        expand=False
    ))
    console.print(f"1. [green]{get_text('language_chinese', 'zh')}[/green]")
    console.print(f"2. [blue]{get_text('language_english', 'en')}[/blue]")
    console.print(f"3. [yellow]{get_text('language_spanish', 'es')}[/yellow]")
    console.print(f"4. [magenta]{get_text('language_german', 'de')}[/magenta]")

    lang_choice = Prompt.ask(
        f"{get_text('enter_language_choice', 'zh')} / "
        f"{get_text('enter_language_choice', 'en')} / "
        f"{get_text('enter_language_choice', 'es')} / "
        f"{get_text('enter_language_choice', 'de')}",
        default="1"
    ).strip()

    lang = {
        "1": "zh",
        "2": "en",
        "3": "es",
        "4": "de"
    }.get(lang_choice, "zh")
    
    # Display program title in selected language
    console.print(Panel(
        get_text("title", lang),
        style="bold cyan",
        expand=False
    ))
    
    # Execute main program and capture success status
    success = main(lang)
    
    # On Windows, wait for user input before closing
    if sys.platform.startswith('win'):
        input(f"\n{get_text('press_enter', lang)}")
    
    # Exit with status code (0 for success, 1 for failure)
    sys.exit(0 if success else 1)
