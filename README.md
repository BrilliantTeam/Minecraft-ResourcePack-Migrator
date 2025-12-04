README LANGUAGES [ [**English**](README.md) | [中文](README-中文.md) | [Spanish](README-Spanish.md) | [German](README-German.md)]
# Minecraft-ResourcePack-Migrator 1.14 ~ 1.21.4+

A tool designed to convert Minecraft resource packs from older versions (1.14) to 1.21.4+ format.  
This tool primarily handles the conversion of item model JSON formats, helping creators quickly update their resource packs.  

> [!Important]  
> This converter only processes JSON files located in the `models/item` directory that include `Custom Model Data` or `Custom Model Data + Damage`.  
> It does not handle JSON files in other directories; you will need to manually manage files outside this directory (in most cases, no additional processing is required).  
> 
> This approach minimizes unexpected issues and ensures the smallest possible difference between the converted resource pack and the original.  
> 
> If you find that JSON files under the `models/item` directory containing `Custom Model Data` or `Custom Model Data + Damage` do not work correctly after conversion, this is indeed a mistake on the converter's part. Please make sure to report it to me.  
> 
> However, if the issue arises from files outside the `models/item` directory, or from files within `models/item` that do not contain `Custom Model Data` or `Damage`, this is not a fault of the converter, as it does not process those files.  

![image](https://github.com/user-attachments/assets/6faa4cc0-f224-4b90-8142-7a0b7b22d4ca)

## Key Features

- Supports two conversion modes:
  1. Custom Model Data Conversion: Converts old CustomModelData format to new format
  2. Item Model Conversion: Converts to individual model files based on CustomModelData paths
  3. Damage Model Conversion: Transforms damage-based model predicates
- Automatically adjusts folder structure (`assets/minecraft/models/item/*` → `assets/minecraft/items/*`)
- Intelligently handles `minecraft:item/` , ` minecraft:block/ ` and `item/` path prefixes
- Batch processes entire resource packs
- Real-time conversion progress display
- Automatically packages into a ready-to-use resource pack
- GUI interface for easy operation
- Supports English, Chinese and German interfaces

## Supported Versions

- Input: Minecraft resource packs from 1.14 to 1.21.3
- Output: Minecraft 1.21.4+ compatible format

## Installation & Usage

### Method 1: Using Executable (Recommended)
1. Download the latest release from the [Releases](https://github.com/BrilliantTeam/Minecraft-ResourcePack-Migrator/releases) page
2. Run the executable file (MCPackConverter.exe)
3. Choose your preferred language (English/中文)
4. Use the GUI to:
   - Select conversion mode
   - Select folder or ZIP file containing your resource pack
   - Click "Start Convert" to begin conversion
   - Find the converted resource pack in the output folder

### Method 2: Using Source Code
1. Clone the repository:
```bash
git clone https://github.com/BrilliantTeam/Minecraft-ResourcePack-Migrator
cd minecraft-resourcepack-migrator
```

2. Install requirements:
```bash
pip install rich
```

3. Run the program:
   - GUI Version: `python gui_app.py`
   - Command Line Version: `python run.py`

### Method 3: Build Your Own Executable
1. Clone the repository and install requirements:
```bash
git clone https://github.com/BrilliantTeam/Minecraft-ResourcePack-Migrator
cd minecraft-resourcepack-migrator
pip install pyinstaller rich
```

2. Run the build script:
```bash
python build.py
```

3. The executable will be available in the `dist` folder

Note: Building the executable requires administrator privileges.

## Format Conversion Examples

### Mode 1: Custom Model Data Conversion
Old format (1.14 ~ 1.21.3):
```json
{
    "parent": "item/handheld",
    "textures": {
        "layer0": "item/stick"
    },
    "overrides": [
        {"predicate": {"custom_model_data": 19002}, "model":"custom_items/cat_hat/cat_hat_black"}
    ]
}
```
Command: `/give @s minecraft:stick{CustomModelData:19002}`

New format (1.21.4+):
```json
{
  "model": {
    "type": "range_dispatch",
    "property": "custom_model_data",
    "fallback": {
      "type": "model",
      "model": "item/stick"
    },
    "entries": [
      {
        "threshold": 19002,
        "model": {
          "type": "model",
          "model": "custom_items/cat_hat/cat_hat_black"
        }
      }
    ]
  }
}
```
Command: `/give @p minecraft:stick[custom_model_data={floats:[19002]}]`

### Mode 2: Item Model Conversion
Original file (`assets/minecraft/models/item/stick.json`):
```json
{
    "parent": "item/handheld",
    "textures": {
        "layer0": "item/stick"
    },
    "overrides": [
        {"predicate": {"custom_model_data": 19002}, "model":"custom_items/cat_hat/cat_hat_black"},
        {"predicate": {"custom_model_data": 19003}, "model":"custom_items/cat_hat/cat_hat_british_shorthair"}
    ]
}
```
Command: `/give @p minecraft:stick[custom_model_data={floats:[19002]}]`  
Command: `/give @p minecraft:stick[custom_model_data={floats:[19003]}]`  

Converted files:
1. `assets/minecraft/items/custom_items/cat_hat/cat_hat_black.json`:
```json
{
  "model": {
    "type": "model",
    "model": "custom_items/cat_hat/cat_hat_black"
  }
}
```
Command: `/give @s itemname[item_model="custom_items/cat_hat/cat_hat_black"]`

2. `assets/minecraft/items/custom_items/cat_hat/cat_hat_british_shorthair.json`:
```json
{
  "model": {
    "type": "model",
    "model": "custom_items/cat_hat/cat_hat_british_shorthair"
  }
}
```
Command: `/give @s itemname[item_model="custom_items/cat_hat/cat_hat_british_shorthair"]`

### Mode 3: Damage Conversion
This mode is designed specifically for pure damage-based conversions.
If your initial file is in a custom model data + damage format,
please use Mode 1 or Mode 2 instead.

Old format (1.14 ~ 1.21.3):
```json
{
    "parent": "item/handheld",
    "textures": {
        "layer0": "item/wood_sword"
    },
    "overrides": [
        {"predicate": {"damaged": 1, "damage": 0.25}, "model":"custom_items/wood_sword1"},
        {"predicate": {"damaged": 1, "damage": 0.50}, "model":"custom_items/wood_sword2"}
    ]
}
```
Command: `/give @s minecraft:wood_sword{damage:30}`  
Command: `/give @s minecraft:wood_sword{damage:45}`  

New format (1.21.4+):
```json
{
    "model": {
        "type": "range_dispatch",
        "property": "damage",
        "fallback": {
            "type": "model",
            "model": "items/wood_sword"
        },
        "entries": [
            {
                "threshold": 0.25,
                "model": {
                    "type": "model",
                    "model": "custom_items/wood_sword1"
                }
            },
            {
                "threshold": 0.50,
                "model": {
                    "type": "model",
                    "model": "custom_items/wood_sword2"
                }
            }
        ]
    }
}
```
Command: `/give @s minecraft:wood_sword[damage=30]`  
Command: `/give @s minecraft:wood_sword[damage=45]`  

## Requirements

- Python 3.6 or newer
- pip (Python package manager)

Automatically installed packages:
- rich (for progress bar display)
- pyinstaller (if building executable)

## Conversion Rules

1. Two Conversion Modes:
   - Custom Model Data Mode: Updates to 1.21.4+ new item model format
   - Item Model Mode: Creates individual model files based on CustomModelData paths

2. Path Handling:
   - `minecraft:item/*` paths maintain their prefix
   - `item/*` paths maintain original format
   - `namespace:path` format is preserved in item model conversion
   - Automatically adjusts item model storage location

3. Folder Structure Adjustment:
   - Moves files from `models/item/*` to `items/*`
   - Creates subdirectories based on model paths in Item Model mode
   - Preserves other folder structures

## Important Notes

1. Always backup your original resource pack before conversion
2. Ensure correct input resource pack structure
3. Test all custom item models in-game after conversion
4. Check error messages if any issues are found

## Contributing

Issues and Pull Requests are welcome. Main areas for contribution:
- Support for more model formats
- Conversion efficiency improvements
- Error handling enhancements
- User experience improvements

## License

GNU General Public License v3.0
