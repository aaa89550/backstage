#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 擷取使用示例
展示如何使用 PDF 擷取程式處理您提供的參考資料格式
"""

import pandas as pd
from advanced_pdf_extractor import AdvancedPDFExtractor
import os

def create_sample_data():
    """創建基於您提供參考資料的示例數據"""
    sample_data = {
        "Title": "<b>Democracy on Fire: Breaking the Chains of Martial Law in 1977</b>",
        "中文書名": "民主星火：1977 衝破戒嚴的枷鎖",
        "Category": "漫畫類",
        "Author": "",
        "Translator": "Chen-Yu Chang, Noax Tao and Lee-Hang Chen",
        "Illustrator": "Michael Kearney",
        "Detail": "<i>In 1977, Ah Wen had been on the other side of history: recruited as a spy. His assignment was to infiltrate the campaign headquarters of an independent candidate.</i> As a spy, he met a promising young man named Ah Yu. The two young men engaged in intense debates about Taiwan's future. While working together to monitor the elections, they also met Elena, a participant in the democracy movement. Together they put up campaign posters, faced attacks from thugs, and attended inspiring rallies for independent candidates. Growing up, Ah Wen had never questioned the KMT, the ruling party that had imposed martial law in Taiwan. His father, a KMT member, had taught him to view those opposed to their party as \"communist spies.\" But during this time, Ah Wen's perspective began to change. On election day, tensions between the police and civilians escalated. Amidst the chaos, Ah Wen saw a sniper on the police station roof aiming at the crowd—with his friend Ah Yu in the line of fire. This historical backdrop resonates with recent issues in Taiwan, among them the Chinese Communist Party's interference in its democratic process.",
        "Rights Sold": "",
        "More Info": "Publisher: Avanguard Date: 1/2022 Pages:128 Size:17 x 23 cm Volume: 1",
        "Tags": "Comic Books,2024"
    }
    
    return sample_data

def demo_pdf_extraction():
    """示範 PDF 擷取功能"""
    print("PDF 擷取與分類程式 - 使用示例")
    print("=" * 60)
    
    # 創建示例數據
    sample_data = create_sample_data()
    
    print("基於您提供的參考資料格式，這是程式的預期輸出格式：")
    print("-" * 60)
    
    # 創建 DataFrame 並顯示
    df = pd.DataFrame([sample_data])
    
    # 設置顯示選項以完整顯示內容
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', 100)
    pd.set_option('display.width', None)
    
    print(df.to_string(index=False))
    
    print("\n" + "=" * 60)
    print("重要功能說明：")
    print("1. 標題自動加上 <b></b> 標籤")
    print("2. 斜體文字自動加上 <i></i> 標籤")
    print("3. 智能分類內容到對應欄位")
    print("4. 支援中英文內容識別")
    print("5. 保留原始格式和樣式")
    
    # 保存示例結果
    output_path = "/workspaces/backstage/sample_output.xlsx"
    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sample_Output')
        print(f"\n示例輸出已保存到: {output_path}")
    except Exception as e:
        print(f"保存示例文件時發生錯誤: {e}")

def usage_instructions():
    """使用說明"""
    print("\n" + "=" * 60)
    print("使用說明：")
    print("=" * 60)
    
    instructions = """
1. 安裝依賴項：
   pip install -r requirements.txt

2. 基本使用（單個 PDF）：
   python pdf_extractor.py
   
3. 進階使用（自定義分類規則）：
   python advanced_pdf_extractor.py
   
4. 程式化使用：
   from advanced_pdf_extractor import AdvancedPDFExtractor
   
   extractor = AdvancedPDFExtractor()
   data = extractor.process_pdf('your_file.pdf')
   df = pd.DataFrame([data])
   extractor.save_results(df, 'output.xlsx')

5. 批量處理：
   df = extractor.process_multiple_pdfs('/path/to/pdf/directory')
   extractor.save_results(df, 'batch_output.xlsx')

6. 自定義分類規則：
   - 編輯 classification_config.json 文件
   - 添加自己的關鍵字和模式
   - 調整分類邏輯

7. 支援的輸出格式：
   - Excel (.xlsx)
   - CSV (.csv)
   - 保留 HTML 格式標籤

注意事項：
- 確保 PDF 文件包含可提取的文字（非掃描圖片）
- 程式會自動識別字體樣式（粗體、斜體）
- 中文內容需要 UTF-8 編碼支援
- 複雜版面可能需要手動調整分類規則
"""
    
    print(instructions)

if __name__ == "__main__":
    demo_pdf_extraction()
    usage_instructions()
