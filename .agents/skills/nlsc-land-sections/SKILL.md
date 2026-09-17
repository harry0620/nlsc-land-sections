---
name: nlsc-land-sections
description: >-
  Query, inspect, and export land section original metadata ("地段原始資訊", survey methods, coordinate systems, scales, mapping dates) from Taiwan's National Land Surveying and Mapping Center (NLSC / 國土測繪圖資服務雲) for any county, land office, or township.
---

# NLSC Land Section Original Info Crawler (國土測繪圖資服務雲 - 地段原始資訊)

本技能提供查詢與批次匯出台灣地政事務所轄區內各「地段原始資訊」（測量方法、測量類別、成圖年月、座標系統、比例尺、數化年月等）的能力。

## 適用情境
- 使用者詢問或欲抓取特定地段、鄉鎮市區、或地政事務所的地段原始資訊與測量歷史。
- 分析圖資來源精度（數值法 vs 圖解法、地籍圖重測、日據時期地籍等）。
- 匯出地政事務所或行政區的地籍屬性清冊為 CSV。

---

## 快速使用指令

工具腳本位於 `./scripts/fetch_land_sections.py`。

### 1. 預設執行（查詢臺中市豐原地政事務所全部轄區）
涵蓋豐原區 (`B09`)、后里區 (`B15`)、神岡區 (`B16`)：
```bash
python ./scripts/fetch_land_sections.py
```

### 2. 指定單一行政區（例如僅豐原區）
```bash
python ./scripts/fetch_land_sections.py --county B --towns B09 --output ./fengyuan.csv
```

### 3. 查詢其他縣市或轄區
例如臺北市中正區 (`A01`)：
```bash
python ./scripts/fetch_land_sections.py --county A --towns A01 --output ./taipei_a01.csv
```

---

## 核心 API 與呼叫規則

底層 API 來自內政部國土測繪圖資服務雲，詳細規格請參閱 [API Reference](./references/api_reference.md)。

> [!IMPORTANT]
> 呼叫 `GetLandSecInfoNlsc` API 時，**必須**在 Request Headers 中附帶 `Referer: https://maps.nlsc.gov.tw/`，否則伺服器會阻擋並回傳 HTTP 404 及 `PERMISSION DENIED`。

---

## 輸出欄位說明

| 欄位名稱 | 說明 | 範例值 |
| :--- | :--- | :--- |
| **縣市** | 縣市名稱 | 臺中市 |
| **鄉鎮市區** | 行政區名稱 | 豐原區 |
| **地政事務所** | 所轄地政事務所代碼/名稱 | 豐原 |
| **地段名稱** | 地段中文名稱 | 豐圳段 |
| **段代碼** | 4 碼地段代碼 | 2447 |
| **段延伸碼** | 段延伸碼 | 無 |
| **鄉鎮市區代碼** | 行政區代碼後兩碼 | 09 |
| **測量方法** | 數值法 / 圖解法 / 數化轉繪 / 數化整合 | 數值法 |
| **測量類別** | 地籍圖重測 / 市地重劃 / 日據時代地籍圖 等 | 地籍圖重測 |
| **成圖年月** | 地籍圖測繪完成年月 | 1998-5 |
| **座標系統** | TWD67二度TM座標 / TWD97二度TM座標 等 | TWD67二度TM座標 |
| **比例尺** | 原始圖幅比例尺 | 500 |
| **數化年月** | 數位化建檔年月 | - |
