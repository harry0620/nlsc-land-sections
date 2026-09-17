# 內政部國土測繪圖資服務雲 (NLSC) 地段原始資訊 API 規格

本文檔記錄從 `https://maps.nlsc.gov.tw/` 逆向分析所得之地籍與地段 API 端點及代碼對照表。

---

## 1. 核心 API 端點

### 1.1 查詢行政區之地段清單
* **URL**: `https://api.nlsc.gov.tw/other/ListLandSection/{COUNTY_CODE}/{TOWN_CODE}`
* **方法**: `GET`
* **Headers**:
  * `Referer: https://maps.nlsc.gov.tw/`
  * `User-Agent: Mozilla/5.0 ...`
* **範例**:
  * 臺中市豐原區: `https://api.nlsc.gov.tw/other/ListLandSection/B/B09`
* **回傳格式**: XML
  ```xml
  <sectList>
      <sectItem>
          <sectcode>2447</sectcode>
          <sectstr>豐圳段</sectstr>
      </sectItem>
  </sectList>
  ```

### 1.2 查詢單一地段之原始資訊
* **URL**: `https://api.nlsc.gov.tw/other/GetLandSecInfoNlsc/{COUNTY_CODE}/{SECT_CODE}`
  *(若有段延伸碼 sno，則為 `/{COUNTY_CODE}/{SECT_CODE}/{sno}`)*
* **方法**: `GET`
* **Headers**:
  * `Referer: https://maps.nlsc.gov.tw/` *(**必填**，否則伺服器回傳 404 PERMISSION DENIED)*
* **範例**:
  * 臺中市豐圳段: `https://api.nlsc.gov.tw/other/GetLandSecInfoNlsc/B/2447`
* **回傳格式**: XML
  ```xml
  <SysdatSecBean>
      <city>臺中市</city>
      <ldcode>豐原</ldcode>
      <scNo>2447</scNo>
      <scNoExt>無</scNoExt>
      <town>09</town>
      <svway>1</svway>
      <svType>5</svType>
      <mYear>1998</mYear>
      <mMonth>5</mMonth>
      <coor>1</coor>
      <scale>500</scale>
      <dDate>0</dDate>
  </SysdatSecBean>
  ```

---

## 2. 官方代碼對照表 (Code Mappings)

### 2.1 測量方法 (`svway`)
| 代碼 | 名稱 | 說明 |
| :--- | :--- | :--- |
| `1` | 數值法 | 現代電子測量儀器 (GPS、全測站) 實測座標 |
| `2` | 圖解法 | 傳統平板測量，繪於圖紙上 |
| `3` | 數化轉繪 | 圖紙掃描轉繪數化 |
| `4` | 數化整合 | 數化地籍圖整合成果 |

### 2.2 測量類別 (`svType`)
| 代碼 | 名稱 |
| :--- | :--- |
| `1` | 日據時代地籍圖 |
| `2` | 市地重劃 |
| `3` | 原住民保留地 |
| `4` | 修正測量 |
| `5` | 地籍圖重測 |
| `6` | 工業區整理 |
| `7` | 河川浮覆地 |
| `8` | 海岸土地測量 |
| `9` | 農地重劃 |
| `A` | 國有原野地 |
| `B` | 區段徵收 |
| `C` | 國有林班地 |
| `D` | 解除林班地 |
| `E` | 海埔新生地 |
| `F` | 農村社區重劃 |
| `Z` | 其他 |

### 2.3 座標系統 (`coor`)
| 代碼 | 名稱 |
| :--- | :--- |
| `1` | TWD67二度TM座標 |
| `2` | TWD67三度TM座標 |
| `3` | 地籍座標 |
| `4` | TWD67六度TM座標 |
| `5` | WGS84 座標 |
| `6` | TWD97二度TM座標 |
| `7` | TWD97[2010] |
| `8` | TWD97[2020] |
| `Z` | 其他 |
