README LANGUAGES [ [**English**](README.md) | [中文](README-中文.md) | [Spanish](README-Spanish.md) | [German](README-German.md) ]
# Minecraft-ResourcePack-Migrator 1.14 ~ 1.21.4+

Ein Werkzeug, mit dem Minecraft Resourcenpakete aus älteren Versionen (1.14) in das neue Format (1.21.4+) umgewandelt werden können.
Dieses Werkzeug fokussiert sich auf die Umwandlung von Itemmodellen im JSON-Format, wodurch Entwicker ihre Resourcenpakete schneller auf den neusten Stand bringen können.

> [!Important]
> Diese Software verarbeitet nur JSON-Dateien, die sich im Ordner `models/item` befinden und `Custom Model Data` oder `Custom Model Data + Damage` enthalten.
> Sie verarbeitet keine JSON-Dateien in anderen Ordnern, diese Dateien müssen manuell bearbeitet werden.
> Es verarbeitet keine JSON-Dateien in anderen Verzeichnissen; es müssen Dateien außerhalb dieses Verzeichnisses manuell verwaltet werden (in den meisten Fällen ist keine zusätzliche Verarbeitung erforderlich).
> 
> Dieser Ansatz minimiert unerwartete Probleme und stellt sicher, dass der Unterschied zwischen dem konvertierten Resource Pack und dem Original so gering wie möglich ist.
>
> Wenn du bemerkst, dass Dateien im Ordner `models/item`, die `Custom Model Data` oder `Custom Model Data + Damage` enthalten, nach der Umwandlung nicht korrekt funktionieren, ist das ein Fehler dieser Software. Bitte melde dies sofort an mich.
> 
> Tritt das Problem jedoch durch Dateien außerhalb des Verzeichnisses `models/item` auf – oder durch Dateien innerhalb von `models/item`,
> die weder `Custom Model Data` noch `Damage` enthalten –, liegt dies nicht am Konverter, da diese Dateien von ihm nicht verarbeitet werden.

![image](https://github.com/user-attachments/assets/6faa4cc0-f224-4b90-8142-7a0b7b22d4ca)

## Hauptfunktionen

- Unterstützung von zwei Umwandlungsmethoden:
  1. Custom Model Data Conversion: Wandelt das alte CustomModelData-Format in das neue um
  2. Item Model Conversion: Wandelt in einzelne Modelldateien basierend auf den CustomModelData-Pfaden um.
  3. Damage Model Conversion: Wandelt modellbezogene Prädikate auf Basis von Schadenswerten um.
- Aktualisiert automatisch die Ordnerstruktur (`assets/minecraft/models/item/*` → `assets/minecraft/items/*`)
- Verarbeitet intelligent `minecraft:item/` , ` minecraft:block/ ` und `item/` Dateipfadpräfixe
- Verarbeitet effizient ganze Resource Packs.
- Echtzeit-Fortschrittsanzeige
- Verpackt alle Änderungen automatisch in ein Resource Pack, das sofort verwendet werden kann.
- Benutzeroberfläche für eine leichte Nutzung
- Unterstützt Englisch, Chinesisch und Deutsch als Sprachen

## Unterstützte Versionen

- Eingang: Minecraft-Resourcenpakete ab 1.14 bis 1.21.3
- Ergebnis: kompatibles Format für Minecraft 1.21.4 und höher

## Installation & Nutzung

### Methode 1: Nutzung der ausführbaren Datei (empfohlen)
1. Lade die neuste Version von [Releases](https://github.com/BrilliantTeam/Minecraft-ResourcePack-Migrator/releases) herunter
2. Führe die Datei aus (MCPackConverter.exe)
3. Wähle deine bevorzugte Sprache (English/中文/Deutsch)
4. Nutze die Oberfläche, um
   - Den Umwandlungsmodus auszuwählen
   - Den Ordner oder die ZIP-Datei mit deinem Resourcenpaket auszuwählen
   - Klicke auf "Umwandlung starten" um die den Vorgang zu beginnen
   - Das aktualisierte Resourcenpaket ist im `output`-Ordner zu finden

### Methode 2: Nutzung des Source Codes
1. Klone die Repository:
```bash
git clone https://github.com/BrilliantTeam/Minecraft-ResourcePack-Migrator
cd minecraft-resourcepack-migrator
```

2. Installiere alle nötigen Abhängigkeiten:
```bash
pip install rich
```

3. Führe das Programm aus:
   - Version mit Oberfläche: `python gui_app.py`
   - Version nur in der Kommandozeile: `python run.py`

### Methode 3: Erstelle deine eigene ausführbare Datei
1. Klone die Repository und installiere alle Abhängigkeiten:
```bash
git clone https://github.com/BrilliantTeam/Minecraft-ResourcePack-Migrator
cd minecraft-resourcepack-migrator
pip install pyinstaller rich
```

2. Führe das Build-Skript aus:
```bash
python build.py
```

3. Die fertige Datei befindet sich im `dist`-Ordner.

Wichtig: Um die Datei selbst zu erstellen, sind Administratorrechte notwendig.

## Format-Umwandlung - Beispiele

### Modus 1: Custom Model Data Conversion
Altes Format (1.14 ~ 1.21.3):
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
Befehl: `/give @s minecraft:stick{CustomModelData:19002}`

Neues Format (1.21.4+):
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
Befehl: `/give @p minecraft:stick[custom_model_data={floats:[19002]}]`

### Modus 2: Item Model Conversion
Originale Datei (`assets/minecraft/models/item/stick.json`):
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
Befehl: `/give @p minecraft:stick[custom_model_data={floats:[19002]}]`  
Befehl: `/give @p minecraft:stick[custom_model_data={floats:[19003]}]`  

Umgewandelte Dateien:
1. `assets/minecraft/items/custom_items/cat_hat/cat_hat_black.json`:
```json
{
  "model": {
    "type": "model",
    "model": "custom_items/cat_hat/cat_hat_black"
  }
}
```
Befehl: `/give @s itemname[item_model="custom_items/cat_hat/cat_hat_black"]`

2. `assets/minecraft/items/custom_items/cat_hat/cat_hat_british_shorthair.json`:
```json
{
  "model": {
    "type": "model",
    "model": "custom_items/cat_hat/cat_hat_british_shorthair"
  }
}
```
Befehl: `/give @s itemname[item_model="custom_items/cat_hat/cat_hat_british_shorthair"]`

### Modus 3: Damage Conversion
Dieser Modus ist speziell für reine Schadensbasierte Konvertierungen konzipiert.
Wenn deine Ausgangsdatei im Format „Custom Model Data + Damage“ vorliegt,
verwende bitte stattdessen Modus 1 oder Modus 2.

Altes Format (1.14 ~ 1.21.3):
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
Befehl: `/give @s minecraft:wood_sword{damage:30}`  
Befehl: `/give @s minecraft:wood_sword{damage:45}`  

Neues Format (1.21.4+):
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
Befehl: `/give @s minecraft:wood_sword[damage=30]`  
Befehl: `/give @s minecraft:wood_sword[damage=45]`  

## Voraussetzungen

- Python 3.6 oder neuer
- pip (Python package manager)

Automatisch installierte Pakete:
- rich (für die Anzeige des Echtzeit-Fortschritts)
- pyinstaller (wenn die ausführbare Datei selbst erstellt wird)

## Umwandlungsregeln

1. Zwei Umwandlungsmodi:
- **Custom Model Data Mode**: Aktualisiert auf das neue Item-Modell-Format ab Version 1.21.4+
- **Item Model Mode**: Erstellt einzelne Modelldateien basierend auf den CustomModelData-Pfaden


2. Pfad-Verarbeitung:
   - `minecraft:item/*` Pfade behalten ihren Präfix bei
   - `item/*` Pfade behalten ihr originales Format bei
   - `namespace:path` Format wird bei der Item-Modell-Konvertierung beibehalten
   - Passt den Speicherort der Item-Modelle automatisch an

3. Ordnerstruktur-Anpassung:
   - Verschiebt Dateien von `models/item/*` nach `items/*`
   - Erstellt Unterordner basierend auf den Modellpfaden im Item Model Modus
   - Erhält andere Ordnerstrukturen

## Wichtige Informationen

1. Erstelle **immer** vor der Umwandlung ein Backup deines Resourcenpakets!
2. Stelle sicher, dass dein Resourcenpaket die richtige Struktur hat.
3. Teste alle Custom-Models nach der Umwandlung im Spiel.
4. Überprüfe Fehlernachrichten, wenn du Probleme hast.

## Mitwirken

Fehlermeldungen und Pull Requests sind immer willkommen. Hauptbereiche zum Mitwirken:
- Unterstützung für mehr Modellformate
- Verbesserungen der Effizienz
- Fehlerverarbeitungsverbesserungen
- Verbesserungen der Benutzererfahrung

## Lizenz

GNU General Public License v3.0
