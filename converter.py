"""
Minecraft Resource Pack Converter Module

This module handles the conversion of Minecraft resource pack files between different formats.
It supports both Custom Model Data and Item Model conversion modes with comprehensive features:
Features:
- Bilingual support (English/Chinese)
- Both GUI and console interfaces
- Progress tracking and reporting
- ZIP file handling
- Directory structure management
- Detailed processing reports
- Error handling and recovery

The module can be used both as a standalone command-line tool and as part of a GUI application.
Author: RiceChen_

Version: 1.4.6
"""

import json
import os
import shutil
import zipfile
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

# Global variables
CURRENT_LANG = "zh"
console = Console()
CustomProgress = None

# Language translations
TRANSLATIONS = {
    "processing_start": {
        "zh": "開始處理檔案...",
        "en": "Starting file processing...",
        "es": "Iniciando procesamiento de archivos...",
        "de": "Starte Dateiverarbeitung..."
    },
    "adjusting_structure": {
        "zh": "調整資料夾結構...",
        "en": "Adjusting folder structure...",
        "es": "Ajustando estructura de carpetas...",
        "de": "Verändere Ordnerstruktur..."
    },
    "moving_files": {
        "zh": "移動檔案中",
        "en": "Moving files",
        "es": "Moviendo archivos",
        "de": "Verschiebe Dateien"
    },
    "processing_files": {
        "zh": "處理檔案中",
        "en": "Processing files",
        "es": "Procesando archivos",
        "de": "Verarbeite Dateien"
    },
    "creating_zip": {
        "zh": "建立ZIP檔案...",
        "en": "Creating ZIP file...",
        "es": "Creando archivo ZIP...",
        "de": "Erstelle ZIP-Archiv..."
    },
    "compressing_files": {
        "zh": "壓縮檔案中",
        "en": "Compressing files",
        "es": "Comprimiendo archivos",
        "de": "Komprimiere Dateien"
    },
    "moved_models": {
        "zh": "已將物品模型從 {} 移動到 {}",
        "en": "Moved item models from {} to {}",
        "es": "Modelos de objetos movidos de {} a {}",
        "de": "Itemmodelle wurde von {} nach {} verschoben"
    },
    "process_complete": {
        "zh": "處理完成！",
        "en": "Processing complete!",
        "es": "¡Procesamiento completado!",
        "de": "Vorgang beendet!"
    },
    "converted_files_count": {
        "zh": "已轉換 {} 個檔案",
        "en": "Converted {} files",
        "es": "Se convirtieron {} archivos",
        "de": "{} Dateien wurden umgewandelt"
    },
    "output_file": {
        "zh": "輸出檔案",
        "en": "Output file",
        "es": "Archivo de salida",
        "de": "Ausgabedatei"
    },
    "current_file": {
        "zh": "當前檔案：{}",
        "en": "Current file: {}",
        "es": "Archivo actual: {}",
        "de": "Aktuelle Datei: {}"
    },
    "input_dir_error": {
        "zh": "錯誤：找不到輸入資料夾 '{}'",
        "en": "Error: Input directory '{}' not found",
        "es": "Error: No se encontró el directorio de entrada '{}'",
        "de": "Fehler: Ordner {} nicht gefunden"
    },
    "error_occurred": {
        "zh": "發生錯誤：{}",
        "en": "Error occurred: {}",
        "es": "Ocurrió un error: {}",
        "de": "Es ist ein Fehler aufgetreten: {}"
    },
    "file_table_title": {
        "zh": "檔案處理報告",
        "en": "File Processing Report",
        "es": "Reporte de Procesamiento de Archivos",
        "de": "Dateiverarbeitungsjournal"
    },
    "file_name": {
        "zh": "檔案名稱",
        "en": "File Name",
        "es": "Nombre del Archivo",
        "de": "Dateiname"
    },
    "file_type": {
        "zh": "類型",
        "en": "Type",
        "es": "Tipo",
        "de": "Typ"
    },
    "file_status": {
        "zh": "狀態",
        "en": "Status",
        "es": "Estado",
        "de": "Status"
    },
    "status_converted": {
        "zh": "已轉換",
        "en": "Converted",
        "es": "Convertido",
        "de": "Umgewandelt"
    },
    "status_copied": {
        "zh": "已複製",
        "en": "Copied",
        "es": "Copiado",
        "de": "Kopiert"
    },
}

def get_text(key, *args):
    """Get translated text"""
    text = TRANSLATIONS.get(key, {}).get(CURRENT_LANG, f"Missing translation: {key}")
    return text.format(*args) if args else text

def get_progress_bar():
    """Create appropriate progress bar based on console type"""
    if hasattr(console, 'status_label') and hasattr(console, 'progress_bar') and CustomProgress:
        return CustomProgress(console)
    return Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(complete_style="green", finished_style="green"),
        TaskProgressColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        TextColumn("•"),
        TimeRemainingColumn(),
        TransferSpeedColumn(),
        refresh_per_second=10,
        expand=True
    )

def is_fishing_rod_model(json_data, file_path=""):
    """
    Check if the JSON data represents a fishing rod model based on file path and content
    
    Args:
        json_data (dict): Input JSON data
        file_path (str): Path to the JSON file
        
    Returns:
        bool: True if it's a fishing rod model, False otherwise
    """
    normalized_path = os.path.basename(file_path).lower()
    
    # Check filename
    if normalized_path == "fishing_rod.json":
        return True
        
    # Check parent and predicates
    if (json_data.get("parent") == "item/handheld_rod" and 
        "overrides" in json_data and
        any("cast" in o.get("predicate", {}) for o in json_data.get("overrides", []))):
        return True
        
    return False

def get_fishing_rod_model(cmd_value, base_model, cast_model, json_data):
    """
    Generate fishing rod model structure for a specific custom model data value
    
    Args:
        cmd_value (int): Custom model data value
        base_model (str): Base model path
        cast_model (str): Model path for cast state
        json_data (dict): Original JSON data
        
    Returns:
        dict: Fishing rod model structure
    """
    # Find models for this CMD value
    normal_model = None
    cast_model_override = None
    
    for override in json_data.get("overrides", []):
        predicate = override.get("predicate", {})
        if predicate.get("custom_model_data") == cmd_value:
            # Check if this is a cast state for this CMD
            if predicate.get("cast", 0) == 1:
                cast_model_override = override["model"]
            # If no cast predicate, this is the normal model
            elif predicate.get("cast", 0) == 0:
                normal_model = override["model"]
    
    # If we don't have both models, we can't create a proper fishing rod entry
    if not normal_model:
        return None
        
    # Create fishing rod model structure with new format
    return {
        "type": "minecraft:condition",
        "property": "minecraft:fishing_rod/cast",
        "on_false": {
            "type": "minecraft:model",
            "model": normal_model
        },
        "on_true": {
            "type": "minecraft:model",
            "model": cast_model_override or normal_model
        }
    }

def is_shield_model(json_data, file_path=""):
    """
    Check if the JSON data represents a shield model based on file path and content
    
    Args:
        json_data (dict): Input JSON data
        file_path (str): Path to the JSON file
        
    Returns:
        bool: True if it's a shield model, False otherwise
    """
    normalized_path = os.path.basename(file_path).lower()
    
    # Check filename
    if normalized_path == "shield.json":
        return True
        
    # Check parent and overrides
    if (json_data.get("parent") == "builtin/entity" and 
        "overrides" in json_data and
        any("blocking" in o.get("predicate", {}) for o in json_data.get("overrides", []))):
        return True
        
    return False

def get_shield_model(cmd_value, base_model, blocking_model, json_data):
    """
    Generate shield model structure for a specific custom model data value
    
    Args:
        cmd_value (int): Custom model data value
        base_model (str): Base model path
        blocking_model (str): Model path for blocking state
        json_data (dict): Original JSON data
        
    Returns:
        dict: Shield model structure
    """
    # Find models for this CMD value
    normal_model = None
    blocking_model_override = None
    
    for override in json_data.get("overrides", []):
        predicate = override.get("predicate", {})
        if predicate.get("custom_model_data") == cmd_value:
            # Check if this is a blocking state for this CMD
            if predicate.get("blocking", 0) == 1:
                blocking_model_override = override["model"]
            # If no blocking predicate, this is the normal model
            elif "blocking" not in predicate:
                normal_model = override["model"]
    
    # If we don't have both models, we can't create a proper shield entry
    if not normal_model:
        return None
        
    # Create shield model structure with new format
    return {
        "type": "minecraft:condition",
        "property": "minecraft:using_item",
        "on_false": {
            "type": "minecraft:model",
            "model": normal_model
        },
        "on_true": {
            "type": "minecraft:model",
            "model": blocking_model_override or normal_model
        }
    }

def is_head_model(json_data, file_path=""):
    """
    Check if the JSON data represents a head/skull model based on file path
    
    Args:
        json_data (dict): Input JSON data (kept for backwards compatibility)
        file_path (str): Path to the JSON file
        
    Returns:
        tuple: (bool, str, str) - (is head model, head kind, base model path)
    """
    normalized_path = os.path.basename(file_path).lower()
    
    head_mappings = {
        "player_head.json": ("player", "minecraft:item/template_skull"),
        "piglin_head.json": ("piglin", "minecraft:item/template_skull"),
        "zombie_head.json": ("zombie", "minecraft:item/template_skull"),
        "creeper_head.json": ("creeper", "minecraft:item/template_skull"),
        "dragon_head.json": ("dragon", "minecraft:item/dragon_head"),
        "wither_skeleton_skull.json": ("wither_skeleton", "minecraft:item/template_skull"),
        "skeleton_skull.json": ("skeleton", "minecraft:item/template_skull")
    }
    
    if normalized_path in head_mappings:
        return True, head_mappings[normalized_path][0], head_mappings[normalized_path][1]
        
    return False, None, None

def is_damage_model(json_data):
    """
    Check if JSON data represents a damage-based model
    
    Args:
        json_data (dict): Input JSON data
        
    Returns:
        bool: True if it's a damage-based model, False otherwise
    """
    if "overrides" not in json_data:
        return False
    
    # Check for damage-based predicates without custom_model_data
    for override in json_data.get("overrides", []):
        predicate = override.get("predicate", {})
        if ("damage" in predicate and 
            "custom_model_data" not in predicate):
            return True
    return False

leather_dyeable_files = [
    "leather_helmet.json",
    "leather_chestplate.json",
    "leather_leggings.json",
    "leather_boots.json",
    "leather_horse_armor.json"
]
trimmable_files = [
    "leather_helmet.json",
    "leather_chestplate.json",
    "leather_leggings.json",
    "leather_boots.json",

    "chainmail_helmet.json",
    "chainmail_chestplate.json",
    "chainmail_leggings.json",
    "chainmail_boots.json",

    "iron_helmet.json",
    "iron_chestplate.json",
    "iron_leggings.json",
    "iron_boots.json",

    "gold_helmet.json",
    "gold_chestplate.json",
    "gold_leggings.json",
    "gold_boots.json",

    "diamond_helmet.json",
    "diamond_chestplate.json",
    "diamond_leggings.json",
    "diamond_boots.json",

    "netherite_helmet.json",
    "netherite_chestplate.json",
    "netherite_leggings.json",
    "netherite_boots.json"
]

def is_trimmable_model(json_data, file_path=""):
    normalized_path = os.path.basename(file_path).lower()
    return normalized_path in trimmable_files

def is_potion_model(json_data, file_path=""):
    """
    Check if the JSON data represents a potion model based on file path
    
    Args:
        json_data (dict): Input JSON data (kept for backwards compatibility)
        file_path (str): Path to the JSON file
        
    Returns:
        bool: True if it's a potion model, False otherwise
    """
    normalized_path = os.path.basename(file_path).lower()
    potion_files = [
        "potion.json",
        "splash_potion.json",
        "lingering_potion.json",
        "tipped_arrow.json"
    ]
    return normalized_path in potion_files or normalized_path in leather_dyeable_files

def is_chest_model(json_data, file_path=""):
    """
    Check if the JSON data represents a chest or trapped chest model based on file path
    
    Args:
        json_data (dict): Input JSON data (kept for backwards compatibility)
        file_path (str): Path to the JSON file
        
    Returns:
        tuple: (bool, str) - (is chest model, chest type)
    """
    normalized_path = os.path.basename(file_path).lower()
    
    if normalized_path == "chest.json":
        return True, "chest"
    elif normalized_path == "trapped_chest.json":
        return True, "trapped_chest"
        
    return False, None

def has_mixed_custom_damage(json_data):
    """
    Check if JSON data contains both custom_model_data and damage predicates
    
    Args:
        json_data (dict): Input JSON data
        
    Returns:
        bool: True if mixed predicates exist
    """
    if "overrides" not in json_data:
        return False
        
    cmd_with_damage = False
    for override in json_data["overrides"]:
        predicate = override.get("predicate", {})
        if ("custom_model_data" in predicate and 
            "damage" in predicate):
            cmd_with_damage = True
            break
    
    return cmd_with_damage

def convert_damage_model(json_data, base_texture=""):
    """
    Convert damage-based model JSON format to the new format.
    
    Args:
        json_data (dict): Original JSON data containing damage model information
        base_texture (str): Base texture path to use as fallback
        
    Returns:
        dict: Converted JSON in new format for damage-based models
    """
    # Extract base texture or parent path if not provided
    if not base_texture:
        base_texture = json_data.get("textures", {}).get("layer0", "")
        if not base_texture:
            base_texture = json_data.get("parent", "")

    # Create basic structure for damage model
    new_format = {
        "oversized_in_gui": True,
        "model": {
            "type": "range_dispatch",
            "property": "damage",
            "fallback": {
                "type": "model",
                "model": base_texture
            },
            "entries": []
        }
    }

    # Add display settings if present
    if "display" in json_data:
        new_format["display"] = json_data["display"]

    # Filter and sort overrides that have damage predicates
    damage_overrides = [
        override for override in json_data.get("overrides", [])
        if ("damage" in override.get("predicate", {}) and
            "custom_model_data" not in override.get("predicate", {}))
    ]
    
    damage_overrides.sort(
        key=lambda x: float(x.get("predicate", {}).get("damage", 0))
    )

    # Add entries for each damage threshold
    for override in damage_overrides:
        model_path = override["model"]
        # Apply path normalization
        if ":" not in model_path:
            model_path = f"minecraft:{model_path}"
        
        predicate = override.get("predicate", {})
        entry = {
            "threshold": float(predicate["damage"]),
            "model": {
                "type": "model",
                "model": model_path
            }
        }
        new_format["model"]["entries"].append(entry)

    return new_format

def convert_mixed_custom_damage_model(json_data):
    """
    Convert a model that has both custom_model_data and damage predicates.
    
    Args:
        json_data (dict): Original JSON data containing model information
        
    Returns:
        dict: Converted JSON in new format
    """
    # Extract base texture or parent
    base_texture = json_data.get("textures", {}).get("layer0", "")
    parent_path = json_data.get("parent", "")
    base_path = base_texture or parent_path

    if ":" not in base_path and base_path.startswith("item/"):
        base_path = f"minecraft:{base_path}"
    elif ":" not in base_path:
        base_path = f"minecraft:item/{base_path}"

    # Create basic structure
    new_format = {
        "oversized_in_gui": True,
        "model": {
            "type": "range_dispatch",
            "property": "custom_model_data",
            "fallback": {
                "type": "model",
                "model": base_path
            },
            "entries": []
        }
    }

    # Group overrides by custom_model_data
    cmd_groups = {}
    for override in json_data.get("overrides", []):
        predicate = override.get("predicate", {})
        cmd = predicate.get("custom_model_data")
        
        if cmd is None:
            continue
            
        if cmd not in cmd_groups:
            cmd_groups[cmd] = {
                "base_model": None,
                "damage_states": []
            }
        
        # Check if this is a damage state
        if "damage" in predicate:
            cmd_groups[cmd]["damage_states"].append({
                "damage": float(predicate["damage"]),
                "model": override["model"]
            })
        else:
            cmd_groups[cmd]["base_model"] = override["model"]

    # Process each custom_model_data group
    for cmd, group in sorted(cmd_groups.items()):
        base_model = group["base_model"] or base_path
        damage_states = sorted(group["damage_states"], key=lambda x: x["damage"])
        
        # Create entry for this CMD
        cmd_entry = {
            "threshold": int(cmd),
            "model": {
                "type": "range_dispatch",
                "property": "damage",
                "fallback": {
                    "type": "model",
                    "model": base_model
                },
                "entries": []
            }
        }

        # Add damage states
        for state in damage_states:
            damage_entry = {
                "threshold": state["damage"],
                "model": {
                    "type": "model",
                    "model": state["model"]
                }
            }
            cmd_entry["model"]["entries"].append(damage_entry)

        new_format["model"]["entries"].append(cmd_entry)

    # Add display settings if present
    if "display" in json_data:
        new_format["display"] = json_data["display"]

    return new_format

def convert_mixed_damage_model(json_data, cmd_value, base_model):
    """
    Convert a model that has both custom_model_data and damage predicates for a specific CMD value.
    
    Args:
        json_data (dict): Original JSON data containing model information
        cmd_value (int): The custom_model_data value to process
        base_model (str): Base model path to use as fallback
        
    Returns:
        dict: Converted JSON in new format for mixed damage model
    """
    # Create the basic structure
    new_json = {
        "model": {
            "type": "range_dispatch",
            "property": "damage",
            "fallback": {
                "type": "model",
                "model": base_model
            },
            "entries": []
        }
    }

    # Filter damage states for this CMD value
    damage_states = []
    for override in json_data.get("overrides", []):
        predicate = override.get("predicate", {})
        if (predicate.get("custom_model_data") == cmd_value and 
            "damage" in predicate):
            damage_states.append({
                "damage": float(predicate["damage"]),
                "model": override["model"]
            })

    # Sort damage states by threshold
    damage_states.sort(key=lambda x: x["damage"])

    # Add damage state entries
    for state in damage_states:
        entry = {
            "threshold": state["damage"],
            "model": {
                "type": "model",
                "model": state["model"]
            }
        }
        new_json["model"]["entries"].append(entry)

    return new_json

def convert_json_format(json_data, is_item_model=False, file_path=""):
    """
    Convert JSON format with special handling for different model types
    
    Args:
        json_data (dict): Original JSON data to convert
        is_item_model (bool): Whether in Item Model mode
        file_path (str): Path to the JSON file
        
    Returns:
        dict: Converted JSON in new format
    """
    # Extract and normalize base texture path or parent path
    base_texture = json_data.get("textures", {}).get("layer0", "")
    parent_path = json_data.get("parent", "")
    base_path = base_texture or parent_path

    # Special handling for potions
    is_potion = is_potion_model(json_data, file_path)
    if is_potion:
        textures = json_data.get("textures", {})
        normalized_filename = os.path.basename(file_path).lower()
        if normalized_filename == "tipped_arrow.json":
            base_path = "minecraft:item/tipped_arrow"
        elif "horse_armor" in normalized_filename:
            # Set base_path based on horse armor type
            #if "diamond" in normalized_filename:
            #    base_path = "minecraft:item/diamond_horse_armor"
            #elif "golden" in normalized_filename:
            #    base_path = "minecraft:item/golden_horse_armor"
            #elif "iron" in normalized_filename:
            #    base_path = "minecraft:item/iron_horse_armor"
            if "leather" in normalized_filename:
                base_path = "minecraft:item/leather_horse_armor"
            else:
                base_path = "minecraft:item/leather_horse_armor"

        elif normalized_filename == "leather_boots.json":
            base_path = "minecraft:item/leather_boots"
        elif normalized_filename == "leather_leggings.json":
            base_path = "minecraft:item/leather_leggings"
        elif normalized_filename == "leather_chestplate.json":
            base_path = "minecraft:item/leather_chestplate"
        elif normalized_filename == "leather_helmet.json":
            base_path = "minecraft:item/leather_helmet"

        elif textures.get("layer0") == "item/splash_potion_overlay":
            base_path = "minecraft:item/splash_potion"
        elif textures.get("layer0") == "item/lingering_potion_overlay":
            base_path = "minecraft:item/lingering_potion"
        else:
            base_path = "minecraft:item/potion"

    # Special handling for chests
    is_chest, chest_type = is_chest_model(json_data, file_path)
    
    # Special handling for heads/skulls
    is_head, head_kind, head_base = is_head_model(json_data, file_path)

    # Special handling for shields
    is_shield = is_shield_model(json_data, file_path)
    
    # Special handling for fishing rods
    is_fishing_rod = is_fishing_rod_model(json_data, file_path)

    is_trimmable = is_trimmable_model(json_data, file_path)

    # Special handling for bow and crossbow - moved before other conditions
    # Check the filename first for more accurate type detection
    normalized_filename = os.path.basename(file_path).lower()
    filename_without_ext = os.path.splitext(normalized_filename)[0]
    is_bow = (normalized_filename == "bow.json") or (not is_chest and filename_without_ext == "bow")
    is_crossbow = (normalized_filename == "crossbow.json") or (not is_chest and filename_without_ext == "crossbow")

    # First check for mixed custom_model_data and damage model
    if has_mixed_custom_damage(json_data):
        return convert_mixed_custom_damage_model(json_data)

    # Then check for pure damage model
    if is_damage_model(json_data):
        return convert_damage_model(json_data, base_path)

    if is_head:
        # Ensure base path is a full minecraft: path
        if not head_base.startswith("minecraft:"):
            head_base = f"minecraft:{head_base}"
        
        # Create basic structure for new format
        new_format = {
            "oversized_in_gui": True,
            "model": {
                "type": "range_dispatch" if not is_item_model else "model",
                "property": "custom_model_data" if not is_item_model else None,
                "fallback": {
                    "type": "minecraft:special",
                    "base": head_base,
                    "model": {
                        "type": "minecraft:head",
                        "kind": head_kind
                    }
                },
                "entries": [] if not is_item_model else None
            }
        }

        # Add display settings if present
        if "display" in json_data:
            new_format["display"] = json_data["display"]

        # Process overrides
        if "overrides" in json_data:
            for override in json_data.get("overrides", []):
                if "predicate" in override and "custom_model_data" in override["predicate"]:
                    cmd = int(override["predicate"]["custom_model_data"])
                    model_path = override["model"]
                    
                    # Ensure model path is a full path
                    if not model_path.startswith("minecraft:") and not ":" in model_path:
                        model_path = f"minecraft:item/{model_path}"
                    
                    # Special handling ONLY for player head
                    if head_kind == "player":
                        entry = {
                            "threshold": cmd,
                            "model": {
                                "type": "minecraft:special",
                                "base": model_path,
                                "model": {
                                    "type": "minecraft:head",
                                    "kind": head_kind
                                }
                            }
                        }
                    else:
                        # For other head types, use simple model type
                        entry = {
                            "threshold": cmd,
                            "model": {
                                "type": "model",
                                "model": model_path
                            }
                        }
                    
                    new_format["model"]["entries"].append(entry)

        return new_format

    elif is_chest:
        base_path = f"item/{chest_type}"
    else:
        # Normal path normalization for non-special items
        if base_texture and not is_potion:
            # Special handling for crossbow_standby
            if base_path == "item/crossbow_standby":
                base_path = "item/crossbow"
            elif base_path == "minecraft:item/crossbow_standby":
                base_path = "minecraft:item/crossbow"
            
            # Normal path normalization for textures
            if not parent_path:  # Only normalize if it's a texture path
                if base_path.startswith("minecraft:item/"):
                    base_path = base_path
                elif base_path.startswith("item/"):
                    base_path = f"minecraft:{base_path}"
                elif not base_path.startswith("minecraft:"):
                    base_path = f"minecraft:item/{base_path}"

    # Create fallback structure based on type
    if is_shield:
        # Shield fallback structure remains the same
        blocking_model = None
        for override in json_data.get("overrides", []):
            if ("predicate" in override and 
                "blocking" in override["predicate"] and 
                override["predicate"].get("blocking") == 1 and
                "custom_model_data" not in override["predicate"]):
                blocking_model = override["model"]
                break
                
        if not blocking_model:
            blocking_model = "minecraft:item/shield_blocking"
            
        if not blocking_model.startswith("minecraft:"):
            blocking_model = f"minecraft:{blocking_model}"
            
        base_path = "minecraft:item/shield"
            
        fallback = {
            "type": "minecraft:condition",
            "property": "minecraft:using_item",
            "on_false": {
                "type": "minecraft:special",
                "base": "minecraft:item/shield",
                "model": {
                    "type": "minecraft:shield"
                }
            },
            "on_true": {
                "type": "minecraft:special",
                "base": "minecraft:item/shield_blocking",
                "model": {
                    "type": "minecraft:shield"
                }
            }
        }
    elif is_head:
        # Create a simple conversion that doesn't use special head model type
        new_format = {
            "oversized_in_gui": True,
            "model": {
                "type": "range_dispatch" if not is_item_model else "model",
                "property": "custom_model_data" if not is_item_model else None,
                "fallback": {
                    "type": "model",
                    "model": head_base
                },
                "entries": [] if not is_item_model else None
            }
        }

        # Process overrides
        if "overrides" in json_data:
            for override in json_data.get("overrides", []):
                if "predicate" in override and "custom_model_data" in override["predicate"]:
                    cmd = int(override["predicate"]["custom_model_data"])
                    model_path = override["model"]
                    
                    entry = {
                        "threshold": cmd,
                        "model": {
                            "type": "model",
                            "model": model_path
                        }
                    }
                    new_format["model"]["entries"].append(entry)

        return new_format
    elif is_chest:
        fallback = {
            "type": "minecraft:select",
            "property": "minecraft:local_time",
            "pattern": "MM-dd",
            "cases": [
                {
                    "model": {
                        "type": "minecraft:special",
                        "base": base_path,
                        "model": {
                            "type": "minecraft:chest",
                            "texture": "minecraft:christmas"
                        }
                    },
                    "when": [
                        "12-24",
                        "12-25",
                        "12-26"
                    ]
                }
            ],
            "fallback": {
                "type": "minecraft:special",
                "base": base_path,
                "model": {
                    "type": "minecraft:chest",
                    "texture": "minecraft:normal"
                }
            }
        }
    elif is_potion:
        if normalized_filename in leather_dyeable_files:
            fallback = {
                "type": "model",
                "model": base_path,
                "tints": [{
                    "type": "minecraft:dye",
                    "default": -6265536
                }]
            }

        else:
            fallback = {
                "type": "model",
                "model": base_path,
                "tints": [{
                    "type": "minecraft:potion",
                    "default": -13083194
                }]
            }
    elif is_fishing_rod:
        base_model = None
        cast_model = None
        for override in json_data.get("overrides", []):
            predicate = override.get("predicate", {})
            if "custom_model_data" not in predicate:
                if predicate.get("cast", 0) == 1:
                    cast_model = override["model"]
                else:
                    base_model = override["model"]
        
        if not base_model:
            base_model = json_data.get("textures", {}).get("layer0", "minecraft:item/fishing_rod")
        if not cast_model:
            cast_model = "minecraft:item/fishing_rod_cast"
            
        if not base_model.startswith("minecraft:"):
            base_model = f"minecraft:{base_model}"
        if not cast_model.startswith("minecraft:"):
            cast_model = f"minecraft:{cast_model}"
            
        fallback = {
            "type": "minecraft:condition",
            "property": "minecraft:fishing_rod/cast",
            "on_false": {
                "type": "minecraft:model",
                "model": base_model
            },
            "on_true": {
                "type": "minecraft:model",
                "model": cast_model
            }
        }
    elif is_bow:
        fallback = {
            "type": "minecraft:condition",
            "property": "minecraft:using_item",
            "on_false": {
                "type": "minecraft:model",
                "model": "minecraft:item/bow"
            },
            "on_true": {
                "type": "minecraft:range_dispatch",
                "property": "minecraft:use_duration",
                "scale": 0.05,
                "fallback": {
                    "type": "minecraft:model",
                    "model": "minecraft:item/bow_pulling_0"
                },
                "entries": [
                    {
                        "threshold": 0.65,
                        "model": {
                            "type": "minecraft:model",
                            "model": "minecraft:item/bow_pulling_1"
                        }
                    },
                    {
                        "threshold": 0.9,
                        "model": {
                            "type": "minecraft:model",
                            "model": "minecraft:item/bow_pulling_2"
                        }
                    }
                ]
            }
        }
    elif is_crossbow:
        fallback = {
            "type": "minecraft:condition",
            "property": "minecraft:using_item",
            "on_false": {
                "type": "minecraft:select",
                "property": "minecraft:charge_type",
                "fallback": {
                    "type": "minecraft:model",
                    "model": "minecraft:item/crossbow"
                },
                "cases": [
                    {
                        "model": {
                            "type": "minecraft:model",
                            "model": "minecraft:item/crossbow_arrow"
                        },
                        "when": "arrow"
                    },
                    {
                        "model": {
                            "type": "minecraft:model",
                            "model": "minecraft:item/crossbow_firework"
                        },
                        "when": "rocket"
                    }
                ]
            },
            "on_true": {
                "type": "minecraft:range_dispatch",
                "property": "minecraft:crossbow/pull",
                "fallback": {
                    "type": "minecraft:model",
                    "model": "minecraft:item/crossbow_pulling_0"
                },
                "entries": [
                    {
                        "threshold": 0.58,
                        "model": {
                            "type": "minecraft:model",
                            "model": "minecraft:item/crossbow_pulling_1"
                        }
                    },
                    {
                        "threshold": 1.0,
                        "model": {
                            "type": "minecraft:model",
                            "model": "minecraft:item/crossbow_pulling_2"
                        }
                    }
                ]
            }
        }
    else:
        fallback = {
            "type": "model",
            "model": base_path
        }

    # Create basic structure
    new_format = {
        "oversized_in_gui": True,
        "model": {
            "type": "range_dispatch" if not is_item_model else "model",
            "property": "custom_model_data" if not is_item_model else None,
            "fallback": fallback,
            "entries": [] if not is_item_model else None
        }
    }

    # if is_trimmable:
    #     new_format["model"]["property"] = "minecraft:trim_material"

    # Add display settings if present
    if "display" in json_data:
        new_format["display"] = json_data["display"]

    if "overrides" not in json_data:
        return new_format

    # Handle different model types
    if is_crossbow:
        # Group overrides by custom_model_data for crossbow
        cmd_groups = {}
        for override in json_data["overrides"]:
            if "predicate" not in override or "model" not in override:
                continue
                
            predicate = override["predicate"]
            cmd = predicate.get("custom_model_data")
            
            if cmd is None:
                continue
                
            if cmd not in cmd_groups:
                cmd_groups[cmd] = {
                    "base": None,
                    "pulling_states": [],
                    "arrow": None,
                    "firework": None
                }
            
            if "pulling" in predicate:
                pull_value = predicate.get("pull", 0.0)
                cmd_groups[cmd]["pulling_states"].append({
                    "pull": pull_value,
                    "model": override["model"]
                })
            elif "charged" in predicate:
                if predicate.get("firework", 0):
                    cmd_groups[cmd]["firework"] = override["model"]
                else:
                    cmd_groups[cmd]["arrow"] = override["model"]
            else:
                cmd_groups[cmd]["base"] = override["model"]
        
        for cmd, group in cmd_groups.items():
            pulling_states = sorted(group["pulling_states"], key=lambda x: x.get("pull", 0))
            base_model = group["base"] or pulling_states[0]["model"] if pulling_states else base_path
            
            entry = {
                "threshold": int(cmd),
                "model": {
                    "type": "minecraft:condition",
                    "property": "minecraft:using_item",
                    "on_false": {
                        "type": "minecraft:select",
                        "property": "minecraft:charge_type",
                        "fallback": {
                            "type": "minecraft:model",
                            "model": base_model
                        },
                        "cases": []
                    },
                    "on_true": {
                        "type": "minecraft:range_dispatch",
                        "property": "minecraft:crossbow/pull",
                        "fallback": {
                            "type": "minecraft:model",
                            "model": pulling_states[0]["model"] if pulling_states else base_model
                        },
                        "entries": []
                    }
                }
            }

            cases = entry["model"]["on_false"]["cases"]
            if group["arrow"]:
                cases.append({
                    "model": {
                        "type": "minecraft:model",
                        "model": group["arrow"]
                    },
                    "when": "arrow"
                })
            if group["firework"]:
                cases.append({
                    "model": {
                        "type": "minecraft:model",
                        "model": group["firework"]
                    },
                    "when": "rocket"
                })

            if pulling_states:
                entries = entry["model"]["on_true"]["entries"]
                for state in pulling_states[1:]:
                    entries.append({
                        "threshold": state.get("pull", 0.0),
                        "model": {
                            "type": "minecraft:model",
                            "model": state["model"]
                        }
                    })

            new_format["model"]["entries"].append(entry)

    elif is_bow:
        # Group overrides by custom_model_data for bow
        cmd_groups = {}
        for override in json_data["overrides"]:
            if "predicate" not in override or "model" not in override:
                continue
                
            predicate = override["predicate"]
            cmd = predicate.get("custom_model_data")
            
            if cmd is None:
                continue
                
            if cmd not in cmd_groups:
                cmd_groups[cmd] = {
                    "base": None,
                    "pulling_states": []
                }
            
            if "pulling" in predicate:
                pull_value = predicate.get("pull", 0.0)
                cmd_groups[cmd]["pulling_states"].append({
                    "pull": pull_value,
                    "model": override["model"]
                })
            else:
                cmd_groups[cmd]["base"] = override["model"]
        
        for cmd, group in cmd_groups.items():
            pulling_states = sorted(group["pulling_states"], key=lambda x: x.get("pull", 0))
            base_model = group["base"] or pulling_states[0]["model"] if pulling_states else base_path
            
            entry = {
                "threshold": int(cmd),
                "model": {
                    "type": "minecraft:condition",
                    "property": "minecraft:using_item",
                    "on_false": {
                        "type": "minecraft:model",
                        "model": base_model
                    },
                    "on_true": {
                        "type": "minecraft:range_dispatch",
                        "property": "minecraft:use_duration",
                        "scale": 0.05,
                        "fallback": {
                            "type": "minecraft:model",
                            "model": base_model
                        },
                        "entries": []
                    }
                }
            }

            if pulling_states:
                for state in pulling_states:
                    if state["model"] != base_model:
                        entry["model"]["on_true"]["entries"].append({
                            "threshold": state.get("pull", 0.0),
                            "model": {
                                "type": "minecraft:model",
                                "model": state["model"]
                            }
                        })

            new_format["model"]["entries"].append(entry)

    else:
        # Handle normal items, chests, and fishing rods
        cmd_groups = {}  # Group overrides by cmd value
        
        # First pass: group overrides by CMD value
        for override in json_data.get("overrides", []):
            if "predicate" in override and "custom_model_data" in override["predicate"]:
                cmd = int(override["predicate"]["custom_model_data"])
                model_path = override["model"]
                
                if is_chest:
                    entry = {
                        "threshold": cmd,
                        "model": {
                            "type": "minecraft:select",
                            "property": "minecraft:local_time",
                            "pattern": "MM-dd",
                            "cases": [
                                {
                                    "model": {
                                        "type": "minecraft:special",
                                        "base": model_path,
                                        "model": {
                                            "type": "minecraft:chest",
                                            "texture": "minecraft:christmas"
                                        }
                                    },
                                    "when": [
                                        "12-24",
                                        "12-25",
                                        "12-26"
                                    ]
                                }
                            ],
                            "fallback": {
                                "type": "minecraft:special",
                                "base": model_path,
                                "model": {
                                    "type": "minecraft:chest",
                                    "texture": "minecraft:normal"
                                }
                            }
                        }
                    }
                    new_format["model"]["entries"].append(entry)
                elif is_shield:
                    if cmd not in cmd_groups:
                        cmd_groups[cmd] = []
                    cmd_groups[cmd].append(override)
                elif is_fishing_rod:
                    if cmd not in cmd_groups:
                        cmd_groups[cmd] = []
                    cmd_groups[cmd].append(override)
                else:
                    entry = {
                        "threshold": cmd,
                        "model": {
                            "type": "model",
                            "model": model_path
                        }
                    }
                    if normalized_filename == "tipped_arrow.json":
                        entry["model"]["tints"] = [{
                            "type": "minecraft:potion",
                            "default": -13083194
                        }]
                    elif "leather_horse_armor" in normalized_filename:
                        entry["model"]["tints"] = [{
                            "type": "minecraft:dye",
                            "default": -6265536
                        }]
                    new_format["model"]["entries"].append(entry)
        
        # Second pass: process shield and fishing rod models
        if is_shield:
            for cmd in sorted(cmd_groups.keys()):
                shield_entry = get_shield_model(
                    cmd,
                    base_path,
                    blocking_model,
                    json_data
                )
                if shield_entry:
                    entry = {
                        "threshold": cmd,
                        "model": shield_entry
                    }
                    new_format["model"]["entries"].append(entry)
        elif is_fishing_rod:
            for cmd in sorted(cmd_groups.keys()):
                # Find normal and cast models for this CMD
                normal_model = None
                cast_model = None
                
                # Get all overrides for this CMD
                cmd_overrides = cmd_groups[cmd]
                for override in cmd_overrides:
                    predicate = override.get("predicate", {})
                    if predicate.get("custom_model_data") == cmd:
                        if predicate.get("cast", 0) == 1:
                            cast_model = override["model"]
                        else:
                            normal_model = override["model"]
                
                if normal_model:
                    entry = {
                        "threshold": cmd,
                        "model": {
                            "type": "minecraft:condition",
                            "property": "minecraft:fishing_rod/cast",
                            "on_false": {
                                "type": "minecraft:model",
                                "model": normal_model
                            },
                            "on_true": {
                                "type": "minecraft:model",
                                "model": cast_model or normal_model
                            }
                        }
                    }
                    new_format["model"]["entries"].append(entry)

    return new_format

def process_mixed_damage_models(json_data, output_path):
    """
    Process models that have both custom_model_data and damage predicates
    """
    if "overrides" not in json_data:
        return

    # Group overrides by custom_model_data
    cmd_groups = {}
    for override in json_data.get("overrides", []):
        predicate = override.get("predicate", {})
        cmd = predicate.get("custom_model_data")
        
        if cmd is None:
            continue
            
        if cmd not in cmd_groups:
            cmd_groups[cmd] = {
                "base_model": None,
                "damage_states": []
            }
            
        # Check if this is a base model (no damage predicate)
        if "damage" not in predicate:
            cmd_groups[cmd]["base_model"] = override["model"]
        else:
            # Add to damage states if it has damage predicate
            if "damage" in predicate:
                cmd_groups[cmd]["damage_states"].append({
                    "damage": float(predicate["damage"]),
                    "model": override["model"]
                })

    # Process each custom_model_data group
    for cmd, group in cmd_groups.items():
        if not group["base_model"]:
            continue

        # Create the file structure based on the model path
        model_path = group["base_model"]
        if ":" in model_path:
            namespace, path = model_path.split(":", 1)
            file_name = os.path.join(output_path, namespace, path) + ".json"
        else:
            file_name = os.path.join(output_path, model_path + ".json")

        # Ensure directory exists
        os.makedirs(os.path.dirname(file_name), exist_ok=True)

        # Sort damage states by threshold
        damage_states = sorted(group["damage_states"], key=lambda x: x["damage"])

        # Create the new JSON structure
        new_json = {
            "model": {
                "type": "range_dispatch",
                "property": "damage",
                "fallback": {
                    "type": "model",
                    "model": group["base_model"]
                },
                "entries": []
            }
        }

        # Add damage state entries
        for state in damage_states:
            entry = {
                "threshold": state["damage"],
                "model": {
                    "type": "model",
                    "model": state["model"]
                }
            }
            new_json["model"]["entries"].append(entry)

        # Write the new JSON file
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(new_json, f, indent=4)

def convert_item_model_format(json_data, output_path, input_path=""):
    """
    Convert JSON format for Item Model mode with comprehensive handling of all model types
    
    Args:
        json_data (dict): Original JSON data containing model overrides
        output_path (str): Base path for output files
        input_path (str): Original input file path for type detection
    """
    if "overrides" not in json_data or not json_data["overrides"]:
        return None

    # Check if this is a fishing rod
    if is_fishing_rod_model(json_data, input_path):
        # Group overrides by custom_model_data
        cmd_groups = {}
        for override in json_data["overrides"]:
            if "predicate" not in override or "model" not in override:
                continue
                
            predicate = override["predicate"]
            cmd = predicate.get("custom_model_data")
            
            if cmd is None:
                continue

            if cmd not in cmd_groups:
                cmd_groups[cmd] = {
                    "cast": None,
                    "normal": None
                }

            # Sort into cast and normal states
            if predicate.get("cast", 0) == 1:
                cmd_groups[cmd]["cast"] = override["model"]
            else:
                cmd_groups[cmd]["normal"] = override["model"]

        # Process each CMD group
        for cmd, models in cmd_groups.items():
            if not models["normal"] or not models["cast"]:
                continue

            # Create JSON structure
            new_json = {
                "model": {
                    "type": "minecraft:condition",
                    "property": "minecraft:fishing_rod/cast",
                    "on_false": {
                        "type": "minecraft:model",
                        "model": models["normal"]
                    },
                    "on_true": {
                        "type": "minecraft:model",
                        "model": models["cast"]
                    }
                }
            }

            # Add display settings if present
            if "display" in json_data:
                new_json["display"] = json_data["display"]

            # Create the output file path
            normal_model = models["normal"]
            
            # Split namespace and path if present
            if ":" in normal_model:
                namespace, path = normal_model.split(":", 1)
                file_name = os.path.join(output_path, namespace, path + ".json")
            else:
                # If no namespace, handle as a regular path
                file_name = os.path.join(output_path, normal_model + ".json")

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_name), exist_ok=True)

            # Write the JSON file
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(new_json, f, indent=4)
                
        return

    # Group overrides by custom_model_data for other types
    cmd_groups = {}
    for override in json_data["overrides"]:
        if "predicate" not in override or "model" not in override:
            continue
            
        predicate = override["predicate"]
        cmd = predicate.get("custom_model_data")
        
        if cmd is None:
            continue

        # Initialize group structure if needed
        if cmd not in cmd_groups:
            cmd_groups[cmd] = {
                "base": None,                # Base model (without states)
                "damage_states": [],         # List of damage states
                "pulling_states": [],        # For bow/crossbow pulling states
                "arrow": None,               # For crossbow with arrow
                "firework": None,            # For crossbow with firework
                "blocking_model": None,      # For shield blocking state
                "has_damage": False          # Flag for damage-based models
            }

        # Check for damage states
        if "damage" in predicate:
            cmd_groups[cmd]["has_damage"] = True
            cmd_groups[cmd]["damage_states"].append({
                "damage": float(predicate["damage"]),
                "model": override["model"]
            })
        # Check for bow/crossbow states
        elif "pulling" in predicate:
            pull_value = predicate.get("pull", 0.0)
            cmd_groups[cmd]["pulling_states"].append({
                "pull": pull_value,
                "model": override["model"]
            })
        elif "charged" in predicate:
            if predicate.get("firework", 0):
                cmd_groups[cmd]["firework"] = override["model"]
            else:
                cmd_groups[cmd]["arrow"] = override["model"]
        # Check for shield blocking state
        elif "blocking" in predicate:
            if predicate.get("blocking", 0) == 1:
                cmd_groups[cmd]["blocking_model"] = override["model"]
            else:
                cmd_groups[cmd]["base"] = override["model"]
        else:
            # This is a base model for this CMD
            cmd_groups[cmd]["base"] = override["model"]

    # Process each custom_model_data group
    for cmd, group in cmd_groups.items():
        if not group["base"]:
            continue

        # Create file structure based on the base model path
        model_path = group["base"]
        if ":" in model_path:
            namespace, path = model_path.split(":", 1)
            file_name = os.path.join(output_path, namespace, path) + ".json"
        else:
            file_name = os.path.join(output_path, model_path + ".json")

        os.makedirs(os.path.dirname(file_name), exist_ok=True)

        # Handle shield
        if is_shield_model(json_data, input_path):
            new_json = {
                "model": {
                    "type": "minecraft:condition",
                    "property": "minecraft:using_item",
                    "on_false": {
                        "type": "minecraft:model",
                        "model": group["base"]
                    },
                    "on_true": {
                        "type": "minecraft:model",
                        "model": group["blocking_model"] or group["base"]
                    }
                }
            }

        # Handle crossbow
        elif "crossbow" in model_path:
            pulling_states = sorted(group["pulling_states"], key=lambda x: x.get("pull", 0))
            
            new_json = {
                "model": {
                    "type": "minecraft:condition",
                    "property": "minecraft:using_item",
                    "on_false": {
                        "type": "minecraft:select",
                        "property": "minecraft:charge_type",
                        "fallback": {
                            "type": "minecraft:model",
                            "model": group["base"]
                        },
                        "cases": []
                    },
                    "on_true": {
                        "type": "minecraft:range_dispatch",
                        "property": "minecraft:crossbow/pull",
                        "fallback": {
                            "type": "minecraft:model",
                            "model": pulling_states[0]["model"] if pulling_states else group["base"]
                        },
                        "entries": []
                    }
                }
            }

            # Add charge type cases
            cases = new_json["model"]["on_false"]["cases"]
            if group["arrow"]:
                cases.append({
                    "model": {
                        "type": "minecraft:model",
                        "model": group["arrow"]
                    },
                    "when": "arrow"
                })
            if group["firework"]:
                cases.append({
                    "model": {
                        "type": "minecraft:model",
                        "model": group["firework"]
                    },
                    "when": "rocket"
                })

            # Add pulling states
            if pulling_states:
                entries = new_json["model"]["on_true"]["entries"]
                for state in pulling_states[1:]:  # Skip first state as it's the fallback
                    entries.append({
                        "threshold": state.get("pull", 0.0),
                        "model": {
                            "type": "minecraft:model",
                            "model": state["model"]
                        }
                    })

        # Handle bow
        elif "bow" in model_path and "crossbow" not in model_path:
            pulling_states = sorted(group["pulling_states"], key=lambda x: x.get("pull", 0))
            
            new_json = {
                "model": {
                    "type": "minecraft:condition",
                    "property": "minecraft:using_item",
                    "on_false": {
                        "type": "minecraft:model",
                        "model": group["base"]
                    },
                    "on_true": {
                        "type": "minecraft:range_dispatch",
                        "property": "minecraft:use_duration",
                        "scale": 0.05,
                        "fallback": {
                            "type": "minecraft:model",
                            "model": group["base"]
                        },
                        "entries": []
                    }
                }
            }

            # Add pulling states
            if pulling_states:
                for state in pulling_states:
                    if state["model"] != group["base"]:
                        new_json["model"]["on_true"]["entries"].append({
                            "threshold": state.get("pull", 0.0),
                            "model": {
                                "type": "minecraft:model",
                                "model": state["model"]
                            }
                        })

        # Handle models with damage states
        elif group["has_damage"] and group["damage_states"]:
            # Sort damage states by threshold
            damage_states = sorted(group["damage_states"], key=lambda x: x["damage"])
            
            new_json = {
                "model": {
                    "type": "range_dispatch",
                    "property": "damage",
                    "fallback": {
                        "type": "model",
                        "model": model_path
                    },
                    "entries": []
                }
            }

            # Add sorted damage states
            for state in damage_states:
                entry = {
                    "threshold": state["damage"],
                    "model": {
                        "type": "model",
                        "model": state["model"]
                    }
                }
                new_json["model"]["entries"].append(entry)

        # Handle potions
        elif is_potion_model(json_data, input_path):
            new_json = {
                "model": {
                    "type": "model",
                    "model": model_path,
                    "tints": [{
                        "type": "minecraft:potion",
                        "default": -13083194
                    }]
                }
            }

        # Handle chest models
        elif is_chest_model(json_data, input_path)[0]:
            new_json = {
                "model": {
                    "type": "minecraft:select",
                    "property": "minecraft:local_time",
                    "pattern": "MM-dd",
                    "cases": [
                        {
                            "model": {
                                "type": "minecraft:special",
                                "base": model_path,
                                "model": {
                                    "type": "minecraft:chest",
                                    "texture": "minecraft:christmas"
                                }
                            },
                            "when": [
                                "12-24",
                                "12-25",
                                "12-26"
                            ]
                        }
                    ],
                    "fallback": {
                        "type": "minecraft:special",
                        "base": model_path,
                        "model": {
                            "type": "minecraft:chest",
                            "texture": "minecraft:normal"
                        }
                    }
                }
            }

        # Handle normal items
        else:
            new_json = {
                "model": {
                    "type": "model",
                    "model": model_path
                }
            }

        # Add display settings if present
        if "display" in json_data:
            new_json["display"] = json_data["display"]

        # Write the output file
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(new_json, f, indent=4)

def process_directory(input_dir, output_dir, mode="cmd"):
    """Process directory in specified mode
    
    Args:
        input_dir (str): Input directory containing files to process
        output_dir (str): Output directory for processed files
        mode (str): Conversion mode - "cmd" (Custom Model Data), "damage", or "item_model"
        
    Returns:
        list: List of processed file information
    """
    processed_files = []
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Copy all files first
    for root, dirs, files in os.walk(input_dir):
        relative_path = os.path.relpath(root, input_dir)
        output_root = os.path.join(output_dir, relative_path)
        os.makedirs(output_root, exist_ok=True)
        
        for file in files:
            input_file = os.path.join(root, file)
            output_file = os.path.join(output_root, file)
            relative_path = os.path.relpath(input_file, input_dir)
            
            try:
                shutil.copy2(input_file, output_file)
                if not file.lower().endswith('.json'):
                    processed_files.append({
                        "path": relative_path,
                        "type": "Other",
                        "status": get_text("status_copied")
                    })
            except Exception as e:
                console.print(f"[red]{get_text('error_occurred', str(e))}[/red]")

    # Process JSON files based on mode
    json_files = []
    
    # Item Model mode: only process files in models/item directory
    if mode == "item_model":
        models_item_dir = os.path.join(output_dir, "assets", "minecraft", "models", "item")
        if os.path.exists(models_item_dir):
            json_files = [os.path.join(models_item_dir, f) for f in os.listdir(models_item_dir)
                         if f.lower().endswith('.json')]
    # Other modes: process all JSON files
    else:
        for root, _, files in os.walk(input_dir):
            for file in files:
                if file.lower().endswith('.json'):
                    json_files.append(os.path.join(root, file))

    with get_progress_bar() as progress:
        task = progress.add_task(get_text("processing_files"), total=len(json_files))
        
        for json_file in json_files:
            relative_path = os.path.relpath(json_file, input_dir)
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)

                # Determine if file needs conversion based on mode
                should_convert = False
                if mode == "damage":
                    # Pure damage mode: only process files with damage predicates
                    should_convert = is_damage_model(json_data)
                elif mode == "cmd":
                    # Custom Model Data mode:
                    # - Process files with custom_model_data
                    # - Process files with both custom_model_data and damage
                    should_convert = (
                        "overrides" in json_data and 
                        any(
                            "custom_model_data" in o.get("predicate", {}) or
                            (
                                "custom_model_data" in o.get("predicate", {}) and
                                "damage" in o.get("predicate", {})
                            )
                            for o in json_data.get("overrides", [])
                        )
                    )

                if should_convert:
                    # Convert based on mode
                    if mode == "damage":
                        # Pure damage mode conversion
                        converted_data = convert_damage_model(json_data)
                    else:
                        # CMD or Item Model mode conversion
                        converted_data = convert_json_format(json_data, mode == "item_model", json_file)
                    
                    # Write converted data
                    output_file = os.path.join(output_dir, relative_path)
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(converted_data, f, indent=4)
                    
                    processed_files.append({
                        "path": relative_path,
                        "type": "JSON",
                        "status": get_text("status_converted")
                    })
                else:
                    processed_files.append({
                        "path": relative_path,
                        "type": "JSON",
                        "status": get_text("status_copied")
                    })
                    
            except Exception as e:
                console.print(f"[red]{get_text('error_occurred', str(e))}[/red]")
            
            progress.update(task, advance=1)
    
    return processed_files

def process_directory_item_model(input_dir, output_dir):
    """
    Process directory in Item Model mode
    Only processes files directly in the models/item directory,
    ignoring any files in subdirectories.
    
    Args:
        input_dir (str): Source directory containing files to convert
        output_dir (str): Destination directory for converted files
        
    Returns:
        list: List of processed file information dictionaries
    """
    processed_files = []
    
    # First copy all files to maintain complete structure
    for root, dirs, files in os.walk(input_dir):
        relative_path = os.path.relpath(root, input_dir)
        output_root = os.path.join(output_dir, relative_path)
        os.makedirs(output_root, exist_ok=True)
        
        for file in files:
            if hasattr(console, 'status_label'):
                console.print(get_text("current_file", file))
            
            input_file = os.path.join(root, file)
            output_file = os.path.join(output_root, file)
            shutil.copy2(input_file, output_file)
            
            if not file.lower().endswith('.json'):
                processed_files.append({
                    "path": os.path.relpath(input_file, input_dir),
                    "type": "Other",
                    "status": get_text("status_copied")
                })
    
    # Process only direct JSON files in models/item directory
    models_item_dir = os.path.join(output_dir, "assets", "minecraft", "models", "item")
    items_dir = os.path.join(output_dir, "assets", "minecraft", "items")
    
    if os.path.exists(models_item_dir):
        os.makedirs(items_dir, exist_ok=True)
        
        # Get only direct JSON files (not in subdirectories)
        direct_json_files = [f for f in os.listdir(models_item_dir) 
                           if os.path.isfile(os.path.join(models_item_dir, f)) 
                           and f.lower().endswith('.json')]
        
        total_files = len(direct_json_files)
        
        # Set up progress tracking
        with get_progress_bar() as progress:
            task = progress.add_task(get_text("processing_files"), total=total_files)
            
            # Process each direct JSON file
            for file in direct_json_files:
                if hasattr(console, 'status_label'):
                    console.print(get_text("current_file", file))
                
                src_path = os.path.join(models_item_dir, file)
                dst_path = os.path.join(items_dir, file)
                relative_path = os.path.relpath(dst_path, output_dir)
                
                try:
                    # Create backup if file exists
                    if os.path.exists(dst_path):
                        backup_path = f"{dst_path}.bak"
                        shutil.move(dst_path, backup_path)
                    
                    # Move file to new location
                    shutil.move(src_path, dst_path)
                    
                    # Read and process JSON content
                    with open(dst_path, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                    
                    # Check if file needs conversion
                    needs_conversion = (
                        "overrides" in json_data and 
                        any("custom_model_data" in o.get("predicate", {}) 
                            for o in json_data.get("overrides", []))
                    )
                    
                    if needs_conversion:
                        # Convert the model and save new files
                        convert_item_model_format(json_data, items_dir, file)
                        # Remove the original file after conversion
                        os.remove(dst_path)
                        processed_files.append({
                            "path": relative_path,
                            "type": "JSON",
                            "status": get_text("status_converted")
                        })
                    else:
                        # Just copy the file if no conversion needed
                        processed_files.append({
                            "path": relative_path,
                            "type": "JSON",
                            "status": get_text("status_copied")
                        })
                        
                except json.JSONDecodeError as e:
                    console.print(f"[red]{get_text('error_occurred', f'Invalid JSON in {file}: {str(e)}')}[/red]")
                    processed_files.append({
                        "path": relative_path,
                        "type": "JSON",
                        "status": "Error: Invalid JSON"
                    })
                except Exception as e:
                    console.print(f"[red]{get_text('error_occurred', str(e))}[/red]")
                    processed_files.append({
                        "path": relative_path,
                        "type": "JSON",
                        "status": f"Error: {str(e)}"
                    })
                
                progress.update(task, advance=1)
            
            # Only remove models/item if it's empty
            if os.path.exists(models_item_dir) and not os.listdir(models_item_dir):
                shutil.rmtree(models_item_dir)
    
    return processed_files

def create_file_table(processed_files):
    """Create report table"""
    table = Table(
        title=get_text("file_table_title"),
        show_header=True,
        header_style="bold magenta",
        border_style="blue",
        expand=True
    )
    
    table.add_column(get_text("file_name"), style="cyan", ratio=3)
    table.add_column(get_text("file_type"), style="green", justify="center", ratio=1)
    table.add_column(get_text("file_status"), style="yellow", justify="center", ratio=1)
    
    for file_info in processed_files:
        status_style = "green" if file_info["status"] == get_text("status_converted") else "blue"
        table.add_row(
            file_info["path"],
            file_info["type"],
            f"[{status_style}]{file_info['status']}[/{status_style}]"
        )
    
    return table

def adjust_folder_structure(base_dir):
    """
    Adjust the folder structure by moving files from models/item to items
    
    Args:
        base_dir (str): Base directory to adjust structure in
    """
    assets_path = os.path.join(base_dir, "assets", "minecraft")
    models_item_path = os.path.join(assets_path, "models", "item")
    items_path = os.path.join(assets_path, "items")
    
    if os.path.exists(models_item_path):
        # Only count direct files in models/item directory
        total_files = len([f for f in os.listdir(models_item_path) 
                         if os.path.isfile(os.path.join(models_item_path, f))])
        
        if total_files > 0:
            console.print(f"\n[cyan]{get_text('adjusting_structure')}[/cyan]")
            os.makedirs(items_path, exist_ok=True)
            
            with get_progress_bar() as progress:
                task = progress.add_task(get_text("moving_files"), total=total_files)
                
                # Only process files directly in models/item
                for item in os.listdir(models_item_path):
                    src_path = os.path.join(models_item_path, item)
                    
                    # Skip if it's a directory
                    if os.path.isdir(src_path):
                        continue
                        
                    if hasattr(console, 'status_label'):
                        console.print(get_text("current_file", item))
                    
                    dst_path = os.path.join(items_path, item)
                    
                    # Handle existing file
                    if os.path.exists(dst_path):
                        backup_path = f"{dst_path}.bak"
                        shutil.move(dst_path, backup_path)
                    
                    # Move file
                    shutil.move(src_path, dst_path)
                    progress.update(task, advance=1)
            
            # Only remove models/item if it's empty
            if os.path.exists(models_item_path) and not os.listdir(models_item_path):
                shutil.rmtree(models_item_path)
            
            console.print(f"[green]{get_text('moved_models', models_item_path, items_path)}[/green]")

def create_zip(folder_path, zip_path):
    """Create ZIP archive"""
    total_files = sum(len(files) for _, _, files in os.walk(folder_path))
    
    console.print(f"\n[cyan]{get_text('creating_zip')}[/cyan]")
    
    with get_progress_bar() as progress:
        task = progress.add_task(get_text("compressing_files"), total=total_files)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arc_name)
                    progress.update(task, advance=1)

def main(lang="zh"):
    """Main program entry point"""
    global CURRENT_LANG
    CURRENT_LANG = lang
    
    input_dir = "input"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_output_dir = f"temp_output_{timestamp}"
    zip_filename = f"converted_{timestamp}.zip"
    
    try:
        # Validate input directory
        if not os.path.exists(input_dir):
            console.print(Panel(
                get_text("input_dir_error", input_dir),
                style="red",
                expand=False
            ))
            return False
            
        # Check if input directory is empty
        if not any(os.scandir(input_dir)):
            console.print(Panel(
                get_text("no_files_found", input_dir),
                style="yellow",
                expand=False
            ))
            return False
        
        # Start processing
        console.print(Panel(
            get_text("processing_start"),
            style="cyan",
            expand=False
        ))
        
        # Create temporary directory
        os.makedirs(temp_output_dir, exist_ok=True)
        
        # Process files
        processed_files = process_directory(input_dir, temp_output_dir)
        
        # Adjust folder structure
        adjust_folder_structure(temp_output_dir)
        
        # Create output ZIP file
        create_zip(temp_output_dir, zip_filename)
        
        # Show completion message
        console.print(f"\n[green]{get_text('process_complete')}[/green]")
        
        # Display processing report
        table = create_file_table(processed_files)
        console.print("\n", table)
        
        # Show summary information
        summary_table = Table.grid(expand=True)
        summary_table.add_column(style="cyan", justify="left")
        
        converted_count = sum(1 for f in processed_files if f["status"] == get_text("status_converted"))
        
        summary_table.add_row(
            f"[bold]{get_text('converted_files_count', converted_count)}[/bold]"
        )
        summary_table.add_row(
            f"[bold]{get_text('output_file')}:[/bold] {zip_filename}"
        )
        
        console.print("\n", Panel(
            summary_table,
            border_style="blue",
            expand=False
        ))
        
        return True
        
    except Exception as e:
        console.print(Panel(
            get_text("error_occurred", str(e)),
            style="red",
            expand=False
        ))
        return False
    
    finally:
        # Clean up temporary directory
        if os.path.exists(temp_output_dir):
            try:
                shutil.rmtree(temp_output_dir)
            except Exception:
                pass

if __name__ == "__main__":
    main()
