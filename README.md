README LANGUAGES [ [**English**](README.md) | [中文](README-中文.md) ]
# Minecraft-ResourcePack-Migrator 1.14 ~ 1.21.4+

A tool designed to convert Minecraft resource packs from older versions (1.14) to 1.21.4+ format.
This tool primarily handles the conversion of item model JSON formats, helping creators quickly update their resource packs.

## Key Features

- Automatically converts old item model JSON formats to 1.21.4+ new format
- Automatically adjusts folder structure (`assets/minecraft/models/item/*` → `assets/minecraft/items/*`)
- Intelligently handles `minecraft:item/` and `item/` path prefixes
- Batch processes entire resource packs
- Real-time conversion progress display
- Automatically packages into a ready-to-use resource pack
- GUI interface for easy operation

## Supported Versions

- Input: Minecraft resource packs from 1.14 to 1.21.3
- Output: Minecraft 1.21.4+ compatible format

## Installation & Usage

### Method 1: Using Executable (Recommended)
1. Download the latest release from the [Releases](https://github.com/BrilliantTeam/Minecraft-ResourcePack-Migrator/releases) page
2. Run the executable file (MCPackConverter.exe)
3. Choose your preferred language (English/中文)
4. Use the GUI to:
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
1. Clone the repository:
```bash
git clone https://github.com/BrilliantTeam/Minecraft-ResourcePack-Migrator
cd minecraft-resourcepack-migrator
```

2. Install required packages:
```bash
pip install pyinstaller rich
```

3. Run the build script:
```bash
python build.py
```

4. Find the executable:
   - The built executable will be in the `dist` folder
   - You can run `MCPackConverter.exe` directly from there

Note: Building the executable requires administrator privileges due to file path configurations.

## Format Conversion Example

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
` /give @s minecraft:stick{CustomModelData:19002} `

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
` /give @p minecraft:stick[custom_model_data={floats:[19002]}] `

## Requirements

- Python 3.6 or newer
- pip (Python package manager)

Automatically installed packages:
- rich (for progress bar display)
- pyinstaller (If you are building the executable)

## Detailed Usage Steps

1. Prepare resource pack:
   - Place your complete resource pack content in the `input` folder
   - Maintain the original folder structure

2. Run conversion:
   - Windows: Double-click `run.py` or use command `python run.py`
   - Mac/Linux: Execute `python3 run.py` in terminal

3. View results:
   - The program generates a timestamped ZIP file (e.g., `converted_20240326_123456.zip`)
   - This ZIP file can be directly used as a Minecraft 1.21.4+ resource pack

## Conversion Rules

1. JSON Format Update:
   - Updates to 1.21.4+ new item model format
   - Preserves all custom model data

2. Path Handling:
   - `minecraft:item/*` paths maintain their prefix
   - `item/*` paths maintain original format
   - Automatically adjusts item model storage location

3. Folder Structure Adjustment:
   - Moves files from `models/item/*` to `items/*`
   - Preserves other folder structures

## Important Notes

1. Always backup your original resource pack before conversion
2. Ensure correct input resource pack structure
3. Test all custom item models in-game after conversion
4. Check error messages if any issues are found

## Troubleshooting

If you encounter issues, check:
1. Input folder structure correctness
2. JSON file format validity
3. Python version compatibility
4. File read/write permissions

## Contributing

Issues and Pull Requests are welcome to help improve this tool. Main areas for contribution:
- Support for more model formats
- Conversion efficiency improvements
- Error handling enhancements
- User experience improvements

## License

GNU General Public License v3.0