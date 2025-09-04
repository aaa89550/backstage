#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速測試腳本 - 驗證 PDF 擷取功能
"""

import sys
import os
from advanced_pdf_extractor import AdvancedPDFExtractor
import pandas as pd

def test_pdf_extractor():
    """測試 PDF 擷取功能"""
    print("PDF 擷取與分類程式 - 快速測試")
    print("=" * 50)
    
    # 初始化擷取器
    extractor = AdvancedPDFExtractor()
    
    # 檢查是否有 PDF 文件夾
    pdf_dir = "/workspaces/backstage/PDF"
    if os.path.exists(pdf_dir):
        pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
        
        if pdf_files:
            print(f"發現 {len(pdf_files)} 個 PDF 文件:")
            for i, pdf_file in enumerate(pdf_files, 1):
                print(f"  {i}. {pdf_file}")
            
            print("\n開始處理...")
            
            # 處理所有 PDF 文件
            df = extractor.process_multiple_pdfs(pdf_dir)
            
            if not df.empty:
                print(f"\n成功處理 {len(df)} 個 PDF 文件")
                print("\n處理結果:")
                print("-" * 50)
                
                # 顯示結果預覽
                for index, row in df.iterrows():
                    print(f"\n文件 {index + 1}:")
                    print(f"  標題: {row['Title']}")
                    print(f"  中文書名: {row['中文書名']}")
                    print(f"  類別: {row['Category']}")
                    print(f"  詳細內容: {row['Detail'][:100]}..." if len(str(row['Detail'])) > 100 else f"  詳細內容: {row['Detail']}")
                
                # 保存結果
                output_path = "/workspaces/backstage/pdf_extraction_results.xlsx"
                extractor.save_results(df, output_path, "excel")
                print(f"\n結果已保存到: {output_path}")
                
                # 也保存為 CSV
                csv_path = "/workspaces/backstage/pdf_extraction_results.csv"
                extractor.save_results(df, csv_path, "csv")
                print(f"CSV 結果已保存到: {csv_path}")
                
            else:
                print("未能從 PDF 文件中擷取到內容")
        else:
            print("PDF 文件夾中沒有找到 PDF 文件")
            print("請將 PDF 文件放入 /workspaces/backstage/PDF/ 目錄中")
    else:
        print("未找到 PDF 文件夾")
        print("請創建 /workspaces/backstage/PDF/ 目錄並放入 PDF 文件")
    
    print("\n" + "=" * 50)
    print("測試完成！")
    
    return True

def show_usage_info():
    """顯示使用資訊"""
    print("\n使用方法:")
    print("1. 將 PDF 文件放入 PDF/ 目錄")
    print("2. 執行: python test_pdf_extractor.py")
    print("3. 查看生成的 Excel 和 CSV 結果文件")
    
    print("\n手動測試單個文件:")
    print("python -c \"")
    print("from advanced_pdf_extractor import AdvancedPDFExtractor")
    print("extractor = AdvancedPDFExtractor()")
    print("data = extractor.process_pdf('path/to/your/file.pdf')")
    print("print(data)")
    print("\"")

if __name__ == "__main__":
    test_pdf_extractor()
    show_usage_info()
