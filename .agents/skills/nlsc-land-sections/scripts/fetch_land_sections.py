#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NLSC Land Section Crawler (國土測繪圖資服務雲 - 地段原始資訊抓取工具)
"""

import os
import sys
import csv
import argparse
import requests
import urllib3
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed

urllib3.disable_warnings()

MEASUR_METHOD = {
    '1': '數值法',
    '2': '圖解法',
    '3': '數化轉繪',
    '4': '數化整合'
}

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
    'Referer': 'https://maps.nlsc.gov.tw/'
}

def get_towns_dict(county_code):
    """取得縣市轄下所有鄉鎮市區代碼與名稱"""
    url = f"https://api.nlsc.gov.tw/other/ListTown/{county_code}"
    r = requests.get(url, headers=HEADERS, verify=False, timeout=10)
    r.encoding = 'utf-8'
    towns = {}
    if r.status_code == 200 and r.text.strip().startswith('<'):
        root = ET.fromstring(r.text)
        for it in root.findall('townItem'):
            code = it.findtext('towncode', default='').strip()
            name = it.findtext('townname', default='').strip()
            if code:
                towns[code] = name
    return towns

def get_town_sections(county_code, town_code):
    """取得指定鄉鎮市區底下的地段清單"""
    url = f"https://api.nlsc.gov.tw/other/ListLandSection/{county_code}/{town_code}"
    r = requests.get(url, headers=HEADERS, verify=False, timeout=10)
    r.encoding = 'utf-8'
    sections = []
    if r.status_code == 200 and r.text.strip().startswith('<'):
        root = ET.fromstring(r.text)
        for it in root.findall('sectItem'):
            sc_no = it.findtext('sectcode', default='').strip()
            sc_name = it.findtext('sectstr', default='').strip()
            if sc_no:
                sections.append((sc_no, sc_name))
    return sections

def get_land_sec_info(county_code, sc_no, sc_name, town_code, town_name):
    """查詢單一地段的詳細原始資訊"""
    url = f"https://api.nlsc.gov.tw/other/GetLandSecInfoNlsc/{county_code}/{sc_no}"
    try:
        r = requests.get(url, headers=HEADERS, verify=False, timeout=10)
        r.encoding = 'utf-8'
        text = r.text.strip()
        
        if not text.startswith('<'):
            return {
                '縣市': '',
                '鄉鎮市區': town_name,
                '地政事務所': '',
                '地段名稱': sc_name,
                '段代碼': sc_no,
                '段延伸碼': '無',
                '鄉鎮市區代碼': town_code[1:] if len(town_code) > 1 else town_code,
                '測量方法': '查無資料',
                '測量類別': '查無資料',
                '成圖年月': '-',
                '座標系統': '-',
                '比例尺': '-',
                '數化年月': '-'
            }
            
        root = ET.fromstring(text)
        
        city = root.findtext('city', default='')
        ldcode = root.findtext('ldcode', default='')
        sc_no_res = root.findtext('scNo', default=sc_no)
        sc_no_ext = root.findtext('scNoExt', default='無')
        if sc_no_ext in ['Z', 'Y', '', 'None']:
            sc_no_ext = '無'
            
        town_id = root.findtext('town', default=town_code[1:] if len(town_code) > 1 else town_code)
        
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
        digit_date = f"{ddate[:4]}-{ddate[4:]}" if (ddate and ddate != '0' and len(ddate) >= 6) else '-'
            
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
            '縣市': '',
            '鄉鎮市區': town_name,
            '地政事務所': '',
            '地段名稱': sc_name,
            '段代碼': sc_no,
            '段延伸碼': '無',
            '鄉鎮市區代碼': town_code[1:] if len(town_code) > 1 else town_code,
            '測量方法': f'錯誤: {e}',
            '測量類別': '-',
            '成圖年月': '-',
            '座標系統': '-',
            '比例尺': '-',
            '數化年月': '-'
        }

def crawl_sections(county_code='B', target_towns=None, output_path=None, max_workers=10):
    all_towns = get_towns_dict(county_code)
    
    if not target_towns:
        # 預設：豐原地政事務所轄區 (豐原區 B09, 后里區 B15, 神岡區 B16)
        target_towns = {
            'B09': all_towns.get('B09', '豐原區'),
            'B15': all_towns.get('B15', '后里區'),
            'B16': all_towns.get('B16', '神岡區')
        }
        
    all_results = []
    print(f"[*] 開始查詢縣市 [{county_code}]，目標鄉鎮市區: {list(target_towns.values())}")
    
    for t_code, t_name in target_towns.items():
        print(f"[*] 正在抓取 {t_name} ({t_code}) 地段清單...")
        sections = get_town_sections(county_code, t_code)
        print(f"    -> 取得 {len(sections)} 個地段，併發查詢原始資料中...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(get_land_sec_info, county_code, sc[0], sc[1], t_code, t_name)
                for sc in sections
            ]
            for f in as_completed(futures):
                all_results.append(f.result())
                
    all_results.sort(key=lambda x: (x.get('鄉鎮市區代碼', ''), x.get('段代碼', '')))
    print(f"[+] 查詢完成！共計獲取 {len(all_results)} 筆地段原始資訊。")
    
    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        fieldnames = ['縣市', '鄉鎮市區', '地政事務所', '地段名稱', '段代碼', '段延伸碼', '鄉鎮市區代碼', '測量方法', '測量類別', '成圖年月', '座標系統', '比例尺', '數化年月']
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
        print(f"[+] 結果已成功寫入: {output_path}")
        
    return all_results

def main():
    parser = argparse.ArgumentParser(description="內政部國土測繪圖資服務雲 - 地段原始資訊抓取工具")
    parser.add_argument("--county", default="B", help="縣市代碼 (預設: B 為臺中市)")
    parser.add_argument("--towns", default=None, help="鄉鎮市區代碼，多個以逗號隔開 (例如: B09 或 B09,B15,B16)。預設為豐原地政事務所轄區")
    parser.add_argument("--output", default="豐原地政事務所_地段原始資訊.csv", help="輸出 CSV 檔案路徑")
    parser.add_argument("--workers", type=int, default=10, help="併發執行緒數 (預設: 10)")
    
    args = parser.parse_args()
    
    target_towns = None
    if args.towns:
        all_towns = get_towns_dict(args.county)
        target_towns = {}
        for t in args.towns.split(','):
            t_clean = t.strip()
            target_towns[t_clean] = all_towns.get(t_clean, t_clean)
            
    crawl_sections(
        county_code=args.county,
        target_towns=target_towns,
        output_path=args.output,
        max_workers=args.workers
    )

if __name__ == '__main__':
    main()
