README LANGUAGES [ [English](README.md) | [中文](README-中文.md) | [**Spanish**](README-Spanish.md) | [German](README-German.md) ]  
# Minecraft-ResourcePack-Migrator 1.14 ~ 1.21.4+

Una herramienta diseñada para convertir paquetes de recursos de Minecraft de versiones antiguas (1.14) al formato 1.21.4+.  
Esta herramienta se centra principalmente en la conversión de formatos JSON de modelos de objetos, ayudando a los creadores a actualizar rápidamente sus paquetes de recursos.  

> [!Important]  
> Este convertidor solo procesa archivos JSON ubicados en el directorio `models/item` que incluyen `Custom Model Data` o `Custom Model Data + Damage`.  
> No maneja archivos JSON en otros directorios; deberás gestionar manualmente los archivos fuera de este directorio (en la mayoría de los casos, no se requiere procesamiento adicional).  
> 
> Este enfoque minimiza problemas inesperados y asegura la menor diferencia posible entre el paquete de recursos convertido y el original.  
> 
> Si descubres que los archivos JSON bajo el directorio `models/item` que contienen `Custom Model Data` o `Custom Model Data + Damage` no funcionan correctamente después de la conversión, esto es un error del convertidor. Por favor, asegúrate de reportarlo.  
> 
> Sin embargo, si el problema surge de archivos fuera del directorio `models/item`, o de archivos dentro de `models/item` que no contienen `Custom Model Data` o `Damage`, no es culpa del convertidor, ya que no procesa esos archivos.  

![image](https://github.com/user-attachments/assets/32cf80b9-9c9c-48a5-95a6-82ad753aec9a)

## Características principales

- Admite dos modos de conversión:
  1. Conversión de datos de modelo personalizados: convierte el formato antiguo de CustomModelData al nuevo formato.
  2. Conversión de modelo de objeto: convierte a archivos de modelo individuales según las rutas de CustomModelData.
  3. Conversión de modelo por daño: transforma predicados basados en daño.
- Ajusta automáticamente la estructura de carpetas (`assets/minecraft/models/item/*` → `assets/minecraft/items/*`).
- Maneja inteligentemente los prefijos de ruta `minecraft:item/`, `minecraft:block/` e `item/`.
- Procesa en lote paquetes de recursos completos.
- Muestra en tiempo real el progreso de la conversión.
- Empaqueta automáticamente en un paquete de recursos listo para usar.
- Interfaz gráfica para una operación fácil.
- Soporta interfaces en inglés y chino.

## Versiones soportadas

- Entrada: Paquetes de recursos de Minecraft desde la versión 1.14 hasta 1.21.3.
- Salida: Formato compatible con Minecraft 1.21.4+.

## Instalación y uso

### Método 1: Usar el ejecutable (recomendado)
1. Descarga la última versión desde la página de [Releases](https://github.com/BrilliantTeam/Minecraft-ResourcePack-Migrator/releases).
2. Ejecuta el archivo ejecutable (`MCPackConverter.exe`).
3. Elige tu idioma preferido (Inglés/中文).
4. Usa la interfaz gráfica para:
   - Seleccionar el modo de conversión.
   - Seleccionar la carpeta o archivo ZIP que contiene tu paquete de recursos.
   - Hacer clic en "Start Convert" para comenzar la conversión.
   - Encontrar el paquete de recursos convertido en la carpeta de salida.

### Método 2: Usar el código fuente
1. Clona el repositorio:
```bash
git clone https://github.com/BrilliantTeam/Minecraft-ResourcePack-Migrator
cd minecraft-resourcepack-migrator
```

2. Instala los requisitos:
```bash
pip install rich
```

3. Ejecuta el programa:
   - Versión GUI: `python gui_app.py`
   - Versión de línea de comandos: `python run.py`

### Método 3: Crear tu propio ejecutable
1. Clona el repositorio e instala los requisitos:
```bash
git clone https://github.com/BrilliantTeam/Minecraft-ResourcePack-Migrator
cd minecraft-resourcepack-migrator
pip install pyinstaller rich
```

2. Ejecuta el script de compilación:
```bash
python build.py
```

3. El ejecutable estará disponible en la carpeta `dist`.

Nota: Crear el ejecutable requiere privilegios de administrador.

## Ejemplos de conversión de formato

### Modo 1: Conversión de datos de modelo personalizados
Formato antiguo (1.14 ~ 1.21.3):
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
Comando: `/give @s minecraft:stick{CustomModelData:19002}`

Formato nuevo (1.21.4+):
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
Comando: `/give @p minecraft:stick[custom_model_data={floats:[19002]}]`

### Modo 2: Conversión de modelo de objeto  
Archivo original (`assets/minecraft/models/item/stick.json`):  
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
Comandos:  
- `/give @p minecraft:stick[custom_model_data={floats:[19002]}]`  
- `/give @p minecraft:stick[custom_model_data={floats:[19003]}]`  

Archivos convertidos:  
1. `assets/minecraft/items/custom_items/cat_hat/cat_hat_black.json`:  
```json
{
  "model": {
    "type": "model",
    "model": "custom_items/cat_hat/cat_hat_black"
  }
}
```
Comando: `/give @s itemname[item_model="custom_items/cat_hat/cat_hat_black"]`

2. `assets/minecraft/items/custom_items/cat_hat/cat_hat_british_shorthair.json`:  
```json
{
  "model": {
    "type": "model",
    "model": "custom_items/cat_hat/cat_hat_british_shorthair"
  }
}
```
Comando: `/give @s itemname[item_model="custom_items/cat_hat/cat_hat_british_shorthair"]`

### Modo 3: Conversión de daño  
Este modo está diseñado específicamente para conversiones puramente basadas en daño.  
Si tu archivo inicial utiliza un formato de datos de modelo personalizado + daño, usa el Modo 1 o el Modo 2.

Formato antiguo (1.14 ~ 1.21.3):  
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
Comandos:  
- `/give @s minecraft:wood_sword{damage:30}`  
- `/give @s minecraft:wood_sword{damage:45}`  

Formato nuevo (1.21.4+):  
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
Comandos:  
- `/give @s minecraft:wood_sword[damage=30]`  
- `/give @s minecraft:wood_sword[damage=45]`  

## Requisitos  

- Python 3.6 o más reciente.  
- pip (gestor de paquetes de Python).  

Paquetes instalados automáticamente:  
- `rich` (para mostrar la barra de progreso).  
- `pyinstaller` (si se construye el ejecutable). 

## Reglas de conversión

1. **Dos modos de conversión:**
   - **Modo de datos de modelo personalizados:** Actualiza al nuevo formato de modelo de objetos para 1.21.4+.
   - **Modo de modelo de objetos:** Crea archivos de modelo individuales basados en las rutas de CustomModelData.

2. **Manejo de rutas:**
   - Las rutas `minecraft:item/*` mantienen su prefijo.
   - Las rutas `item/*` conservan su formato original.
   - El formato `namespace:path` se preserva en la conversión de modelos de objetos.
   - Ajusta automáticamente la ubicación de almacenamiento de los modelos de objetos.

3. **Ajuste de estructura de carpetas:**
   - Mueve los archivos de `models/item/*` a `items/*`.
   - Crea subdirectorios basados en las rutas de modelo en el modo de modelos de objetos.
   - Conserva otras estructuras de carpetas.

## Notas importantes

1. **Respalda siempre tu paquete de recursos original antes de la conversión.**  
2. Asegúrate de que la estructura de tu paquete de recursos de entrada sea correcta.  
3. Prueba todos los modelos de objetos personalizados en el juego después de la conversión.  
4. Si encuentras algún problema, revisa los mensajes de error y ajusta según sea necesario.  

## Contribuciones

Se aceptan problemas y solicitudes de extracción. Áreas principales para contribuir:
- Soporte para más formatos de modelo.  
- Mejoras en la eficiencia de conversión.  
- Mejoras en el manejo de errores.  
- Mejoras en la experiencia del usuario.  

## Licencia

Licencia Pública General de GNU v3.0 (GNU General Public License v3.0).  
