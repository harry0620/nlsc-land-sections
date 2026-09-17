import requests
import urllib3
import xml.etree.ElementTree as ET
import csv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

urllib3.disable_warnings()

# 測量方法代碼對照表
MEASUR_METHOD = {
    '1': '數值法',
    '2': '圖解法',
    '3': '數化轉繪',
    '4': '數化整合'
}

# 測量類別代碼對照表
MEASUR_TYPE = {
    '1': '日據時代地籍圖',
    '2': '市地重劃',
    '3': '原住民保留地',
    '4': '修正測量',
    '5': '地籍圖重測',
    '6': '工業區整理',
    '7': '河川浮覆地',
    '8': '海岸土地測量',
    '9': '農地重劃',
    'A': '國有原野地',
    'B': '區段徵收',
    'C': '國有林班地',
    'D': '解除林班地',
    'E': '海埔新生地',
    'F': '農村社區重劃',
    'Z': '其他'
}

# 坐標系統代碼對照表
COOR_SYS = {
    '1': 'TWD67二度TM座標',
    '2': 'TWD67三度TM座標',
    '3': '地籍座標',
    '4': 'TWD67六度TM座標',
    '5': 'WGS84 座標',
    '6': 'TWD97二度TM座標',
    '7': 'TWD97[2010]',
    '8': 'TWD97[2020]',
    'Z': '其他'
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://maps.nlsc.gov.tw/'  # 關鍵：若無此 Referer 請求會被擋並回傳 PERMISSION DENIED
}

COUNTY_CODE = 'B'  # 臺中市

# 豐原地政事務所轄區包含：豐原區、后里區、神岡區
# 若僅需豐原區，可設定為 {'B09': '豐原區'}
TARGET_TOWNS = {
    'B09': '豐原區',
    'B15': '后里區',
    'B16': '神岡區'
}

def get_town_sections(county_code, town_code):
    """
    取得指定鄉鎮市區底下的所有地段清單
    API: https://api.nlsc.gov.tw/other/ListLandSection/{county_code}/{town_code}
    """
    url = f"https://api.nlsc.gov.tw/other/ListLandSection/{county_code}/{town_code}"
    r = requests.get(url, headers=HEADERS, verify=False, timeout=10)
    sections = []
    if r.status_code == 200:
        root = ET.fromstring(r.text)
        for it in root.findall('sectItem'):
            sc_no = it.findtext('sectcode', default='').strip()
            sc_name = it.findtext('sectstr', default='').strip()
            if sc_no:
                sections.append((sc_no, sc_name))
    return sections

def get_land_sec_info(county_code, sc_no, sc_name, town_code, town_name):
    """
    取得單一地段的詳細原始資訊
    API: https://api.nlsc.gov.tw/other/GetLandSecInfoNlsc/{county_code}/{sc_no}
    """
    url = f"https://api.nlsc.gov.tw/other/GetLandSecInfoNlsc/{county_code}/{sc_no}"
    try:
        r = requests.get(url, headers=HEADERS, verify=False, timeout=10)
        r.encoding = 'utf-8'
        text = r.text.strip()
        
        # 部分早期地段可能回傳「查無地段資訊」
        if not text.startswith('<'):
            return {
                '縣市': '臺中市',
                '鄉鎮市區': town_name,
                '地政事務所': '豐原',
                '地段名稱': sc_name,
                '段代碼': sc_no,
                '段延伸碼': '無',
                '鄉鎮市區代碼': town_code.replace('B', ''),
                '測量方法': '查無資料',
                '測量類別': '查無資料',
                '成圖年月': '-',
                '座標系統': '-',
                '比例尺': '-',
                '數化年月': '-'
            }
            
        root = ET.fromstring(text)
        
        city = root.findtext('city', default='臺中市')
        ldcode = root.findtext('ldcode', default='豐原')
        sc_no_res = root.findtext('scNo', default=sc_no)
        sc_no_ext = root.findtext('scNoExt', default='無')
        if sc_no_ext in ['Z', 'Y', '', 'None']:
            sc_no_ext = '無'
            
        town_id = root.findtext('town', default=town_code.replace('B', ''))
        
        svway_code = root.findtext('svway', default='')
        svway = MEASUR_METHOD.get(svway_code, svway_code or '---')
        
        svtype_code = root.findtext('svType', default='')
        svtype = MEASUR_TYPE.get(svtype_code, svtype_code or '---')
        
        m_year = root.findtext('mYear', default='')
        m_month = root.findtext('mMonth', default='')
        map_date = f"{m_year}-{m_month}" if (m_year and m_month) else '-'
        
        coor_code = root.findtext('coor', default='')
        coor = COOR_SYS.get(coor_code, coor_code or '---')
        
        scale = root.findtext('scale', default='-')
        
        ddate = root.findtext('dDate', default='0')
        if ddate and ddate != '0' and len(ddate) >= 6:
            digit_date = f"{ddate[:4]}-{ddate[4:]}"
        else:
            digit_date = '-'
            
        return {
            '縣市': city,
            '鄉鎮市區': town_name,
            '地政事務所': ldcode,
            '地段名稱': sc_name,
            '段代碼': sc_no_res,
            '段延伸碼': sc_no_ext,
            '鄉鎮市區代碼': town_id,
            '測量方法': svway,
            '測量類別': svtype,
            '成圖年月': map_date,
            '座標系統': coor,
            '比例尺': scale,
            '數化年月': digit_date
        }
    except Exception as e:
        return {
            '縣市': '臺中市',
            '鄉鎮市區': town_name,
            '地政事務所': '豐原',
            '地段名稱': sc_name,
            '段代碼': sc_no,
            '段延伸碼': '無',
            '鄉鎮市區代碼': town_code.replace('B', ''),
            '測量方法': f'錯誤: {e}',
            '測量類別': '-',
            '成圖年月': '-',
            '座標系統': '-',
            '比例尺': '-',
            '數化年月': '-'
        }

def main():
    all_results = []
    print(f"開始查詢豐原地政事務所轄區地段原始資訊...")
    
    for town_code, town_name in TARGET_TOWNS.items():
        print(f"\n[1/2] 正在獲取 {town_name} ({town_code}) 的地段清單...")
        sections = get_town_sections(COUNTY_CODE, town_code)
        print(f"  -> 找到 {len(sections)} 個地段，開始爬取詳細地段原始資訊...")
        
        # 多線程併發查詢
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(get_land_sec_info, COUNTY_CODE, sc[0], sc[1], town_code, town_name)
                for sc in sections
            ]
            for f in as_completed(futures):
                all_results.append(f.result())
                
    # 按照鄉鎮市區代碼與段代碼排序
    all_results.sort(key=lambda x: (x.get('鄉鎮市區代碼', ''), x.get('段代碼', '')))
    
    print(f"\n[2/2] 全部查詢完成！共計獲取 {len(all_results)} 筆地段原始資訊。")
    
    output_file = r'c:\Users\harry\Desktop\TEST\豐原地政事務所_地段原始資訊.csv'
    fieldnames = ['縣市', '鄉鎮市區', '地政事務所', '地段名稱', '段代碼', '段延伸碼', '鄉鎮市區代碼', '測量方法', '測量類別', '成圖年月', '座標系統', '比例尺', '數化年月']
    
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)
        
    print(f"成果已成功儲存至: {output_file}")

if __name__ == '__main__':
    main()
