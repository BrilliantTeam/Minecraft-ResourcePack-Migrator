README LANGUAGES [ [English](README.md) | [**中文**](README-中文.md) | [Spanish](README-Spanish.md) | [German](README-German.md) ]
# Minecraft-ResourcePack-Migrator 1.14 ~ 1.21.4+

一個專門用於將 Minecraft 資源包（Resource Pack）從舊版本（1.14）轉換至 1.21.4+ 版本的工具。  
這個工具主要處理物品模型的 JSON 格式轉換，協助創作者快速更新他們的資源包。  

> [!Important]
> 此轉換器僅處理於` model/item `目錄下，帶有` Custom Model Data `、` Custom Model Data + Damage `的 JSON 檔案，  
> 它不會幫你處理於其他目錄下的 JSON 檔案，你需要自行處理在其他目錄的檔案（一般使用情況下也不需要處理）。  
> 這是為了避免更多的意外情況發生，以保證轉換後資源包的與原先資源包的最小差異，  
> 如果你在轉換後，發現於` model/item `目錄下，帶有` Custom Model Data `、` Custom Model Data + Damage `的 JSON 檔案沒有正確運作，  
> 那麼，這確實是轉換器的疏漏，請務必回報給我，  
>   
> 但如果你發現出問題的點在非` model/item `目錄，或者於` model/item `但是沒有` Custom Model Data `或` Damage `，  
> 那麼這並非轉換器的疏漏，因為轉換器根本不會處理這些檔案。  

![image](https://github.com/user-attachments/assets/ae194619-5f2e-4b30-b7f8-c314cc7fc593)

## 主要功能

- 支援兩種轉換模式：
  1. Custom Model Data 轉換：將舊版 CustomModelData 格式轉換為新格式
  2. Item Model 轉換：根據 CustomModelData 的路徑轉換為獨立的模型檔案
  3. Damage 模型轉換：轉換基於傷害的模型謂詞
- 自動調整資料夾結構（`assets/minecraft/models/item/*` → `assets/minecraft/items/*`）
- 智慧處理 `minecraft:item/` 、 ` minecraft:block/ ` 和 `item/` 的路徑前綴
- 批次處理整個資源包
- 即時顯示轉換進度
- 自動打包為可直接使用的資源包
- 圖形使用者介面，操作簡單
- 支援中文和英文介面

## 支援版本

- 輸入：Minecraft 1.14 ~ 1.21.3 的資源包
- 輸出：Minecraft 1.21.4+ 相容格式

## 安裝與使用

### 方法一：使用執行檔（推薦）
1. 從 [Releases](https://github.com/BrilliantTeam/Minecraft-ResourcePack-Migrator/releases) 頁面下載最新版本
2. 執行 MCPackConverter.exe
3. 選擇你偏好的語言（中文/English）
4. 使用圖形介面：
   - 選擇轉換模式
   - 選擇資料夾或 ZIP 檔案
   - 點擊「開始轉換」
   - 在輸出資料夾中找到轉換後的資源包

### 方法二：使用原始碼
1. 複製專案：
```bash
git clone https://github.com/BrilliantTeam/Minecraft-ResourcePack-Migrator
cd minecraft-resourcepack-migrator
```

2. 安裝需求套件：
```bash
pip install rich
```

3. 執行程式：
   - 圖形介面版本：`python gui_app.py`
   - 命令列版本：`python run.py`

### 方法三：自行建構執行檔
1. 複製專案並安裝需求套件：
```bash
git clone https://github.com/BrilliantTeam/Minecraft-ResourcePack-Migrator
cd minecraft-resourcepack-migrator
pip install pyinstaller rich
```

2. 執行建構腳本：
```bash
python build.py
```

3. 執行檔將會在 `dist` 資料夾中

注意：建構執行檔需要系統管理員權限。

## 格式轉換示例

### 模式一：Custom Model Data 轉換
舊版本格式（1.14 ~ 1.21.3）：
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
指令：`/give @s minecraft:stick{CustomModelData:19002}`

新版本格式（1.21.4+）：
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
指令：`/give @s minecraft:stick[custom_model_data={floats:[19002]}]`

### 模式二：Item Model 轉換
原始檔案（`assets/minecraft/models/item/stick.json`）：
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
指令：`/give @s minecraft:stick{CustomModelData:19002}`  
指令：`/give @s minecraft:stick{CustomModelData:19003}`  

轉換後的檔案：
1. `assets/minecraft/items/custom_items/cat_hat/cat_hat_black.json`：
```json
{
  "model": {
    "type": "model",
    "model": "custom_items/cat_hat/cat_hat_black"
  }
}
```
指令：`/give @s 任意物品[item_model="custom_items/cat_hat/cat_hat_black"]`

2. `assets/minecraft/items/custom_items/cat_hat/cat_hat_british_shorthair.json`：
```json
{
  "model": {
    "type": "model",
    "model": "custom_items/cat_hat/cat_hat_british_shorthair"
  }
}
```
指令：`/give @s 任意物品[item_model="custom_items/cat_hat/cat_hat_british_shorthair"]`

### 模式三：Damage 轉換
這是針對單純的 damage 所設計的轉換，
如果您的初始檔案為 custom model data + damage 的格式，
請使用 模式一 或者 模式二 。

舊版本格式（1.14 ~ 1.21.3）：
```json
{
    "parent": "item/handheld",
    "textures": {
        "layer0": "item/wood_sword"
    },
    "overrides": [
        {"predicate": {"damaged": 1, "damage": 0.25}, "model":"custom_items/wood_sword1"}
        {"predicate": {"damaged": 1, "damage": 0.50}, "model":"custom_items/wood_sword2"}
    ]
}
```
指令：`/give @s minecraft:wood_sword{damage:30}`  
指令：`/give @s minecraft:wood_sword{damage:45}`  

新版本格式（1.21.4+）：
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
指令：`/give @s minecraft:wood_sword[damage=30]`  
指令：`/give @s minecraft:wood_sword[damage=45]`  

## 使用需求

- Python 3.6 或更新版本
- pip（Python 套件管理器）

自動安裝的套件：
- rich（用於顯示進度條）
- pyinstaller（如果要建構執行檔）

## 轉換規則

1. 兩種轉換模式：
   - Custom Model Data 模式：更新為 1.21.4+ 的新物品模型格式
   - Item Model 模式：根據 CustomModelData 的路徑建立獨立的模型檔案

2. 路徑處理：
   - `minecraft:item/*` 路徑會保持其前綴
   - `item/*` 路徑保持原有格式
   - `命名空間:路徑` 格式在 Item Model 轉換中會被保留
   - 自動調整物品模型的存放位置

3. 資料夾結構調整：
   - 將 `models/item/*` 中的檔案移動至 `items/*`
   - 在 Item Model 模式中根據模型路徑建立子目錄
   - 保留其他資料夾的原始結構

## 注意事項

1. 轉換前請務必備份你的原始資源包
2. 確保輸入的資源包結構正確
3. 轉換後請在遊戲中測試所有自訂物品模型
4. 如果發生問題，請檢查輸出的錯誤訊息

## 貢獻

歡迎提交 Issue 或 Pull Request。主要的貢獻方向：
- 支援更多的模型格式
- 改善轉換效率
- 擴充錯誤處理
- 提升使用者體驗

## 授權

GNU General Public License v3.0
