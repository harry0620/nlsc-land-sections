# NLSC Land Section Original Info Crawler (國土測繪圖資服務雲 - 地段原始資訊抓取工具)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

本專案提供自動化爬取與解析中華民國內政部國土測繪圖資服務雲（NLSC）地籍地段「**地段原始資訊**」之工具，支援將數值代碼自動解譯為易讀中文（如測量方法、測量類別、坐標系統、比例尺、成圖年月等），並可依縣市、地政事務所或鄉鎮市區批次匯出 CSV。

亦可直接作為 **Google Antigravity / Gemini CLI** 的擴充技能（SKILL）使用。

---

## 專案結構

```text
.
├── SKILL.md                 # Antigravity 技能定義檔
├── README.md                # 專案說明文件
├── requirements.txt         # 依賴套件
├── .gitignore
├── scripts/
│   └── fetch_land_sections.py # 核心抓取程式 (支援 CLI 參數)
├── references/
│   └── api_reference.md     # NLSC API 逆向技術規格與對照表
└── 豐原地政事務所_地段原始資訊.csv # 範例成果資料
```

---

## 安裝方式

```bash
git clone https://github.com/<YOUR_USERNAME>/<REPO_NAME>.git
cd <REPO_NAME>
pip install -r requirements.txt
```

---

## 使用範例

### 1. 預設模式（查詢臺中市豐原地政事務所全部轄區）
涵蓋豐原區 (`B09`)、后里區 (`B15`)、神岡區 (`B16`)，共 180 個地段：
```bash
python scripts/fetch_land_sections.py
```

### 2. 指定單一行政區（如僅豐原區）
```bash
python scripts/fetch_land_sections.py --county B --towns B09 --output ./fengyuan.csv
```

### 3. 指定多個行政區
```bash
python scripts/fetch_land_sections.py --county B --towns B09,B15 --output ./output.csv
```

### 4. 查詢其他縣市（如臺北市中正區）
```bash
python scripts/fetch_land_sections.py --county A --towns A01 --output ./taipei_a01.csv
```

---

## 欄位說明

* **縣市**: 縣市名稱
* **鄉鎮市區**: 行政區名稱
* **地政事務所**: 所轄地政事務所
* **地段名稱**: 地段中文名稱（如豐圳段）
* **段代碼**: 4 碼地段代碼（如 2447）
* **段延伸碼**: 段延伸碼
* **鄉鎮市區代碼**: 2 碼鄉鎮市區代碼（如 09）
* **測量方法**: 數值法 / 圖解法 / 數化轉繪 / 數化整合
* **測量類別**: 地籍圖重測 / 市地重劃 / 日據時代地籍圖 等
* **成圖年月**: 原始地籍圖測繪完成年月
* **座標系統**: TWD67二度TM座標 / TWD97二度TM座標 等
* **比例尺**: 原始圖幅比例尺
* **數化年月**: 數化建檔年月

---

## 授權條款

MIT License.
