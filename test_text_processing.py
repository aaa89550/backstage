#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試文字處理功能
"""

from text_processor import TextProcessor
from advanced_pdf_extractor import AdvancedPDFExtractor
import pandas as pd

def test_text_processing():
    """測試文字處理功能"""
    print("測試文字處理功能 - 處理不當換行問題")
    print("=" * 60)
    
    # 創建測試數據（模擬 PDF 擷取的文字塊）
    test_blocks = [
        {
            "text": "Democracy on Fire: Breaking the Chains of",
            "styles": [{"text": "Democracy on Fire: Breaking the Chains of", "is_italic": False, "is_bold": True}],
            "avg_font_size": 16
        },
        {
            "text": "Martial Law in 1977",
            "styles": [{"text": "Martial Law in 1977", "is_italic": False, "is_bold": True}],
            "avg_font_size": 16
        },
        {
            "text": "民主星火：1977 衝破戒嚴",
            "styles": [{"text": "民主星火：1977 衝破戒嚴", "is_italic": False, "is_bold": False}],
            "avg_font_size": 14
        },
        {
            "text": "的枷鎖",
            "styles": [{"text": "的枷鎖", "is_italic": False, "is_bold": False}],
            "avg_font_size": 14
        },
        {
            "text": "In 1977, Ah Wen had been on the other side of history: recruited as a",
            "styles": [{"text": "In 1977, Ah Wen had been on the other side of history: recruited as a", "is_italic": True, "is_bold": False}],
            "avg_font_size": 12
        },
        {
            "text": "spy. His assignment was to infiltrate the campaign headquarters",
            "styles": [{"text": "spy. His assignment was to infiltrate the campaign headquarters", "is_italic": True, "is_bold": False}],
            "avg_font_size": 12
        },
        {
            "text": "of an independent candidate.",
            "styles": [{"text": "of an independent candidate.", "is_italic": True, "is_bold": False}],
            "avg_font_size": 12
        },
        {
            "text": "As a spy, he met a promising young man named Ah Yu. The two young men",
            "styles": [{"text": "As a spy, he met a promising young man named Ah Yu. The two young men", "is_italic": False, "is_bold": False}],
            "avg_font_size": 12
        },
        {
            "text": "engaged in intense debates about Taiwan's future.",
            "styles": [{"text": "engaged in intense debates about Taiwan's future.", "is_italic": False, "is_bold": False}],
            "avg_font_size": 12
        }
    ]
    
    # 創建文字處理器
    processor = TextProcessor()
    
    print("原始文字塊:")
    print("-" * 30)
    for i, block in enumerate(test_blocks):
        print(f"{i+1}. {block['text']}")
    
    # 處理文字
    merged_blocks = processor.clean_and_merge_paragraphs(test_blocks)
    
    print(f"\n處理後的文字塊 (從 {len(test_blocks)} 個合併為 {len(merged_blocks)} 個):")
    print("-" * 30)
    for i, block in enumerate(merged_blocks):
        cleaned_text = processor.clean_text_content(block['text'])
        print(f"{i+1}. {cleaned_text}")
        print(f"   (字體大小: {block.get('avg_font_size', 12)}, 樣式數: {len(block.get('styles', []))})")
    
    # 測試完整的 PDF 處理流程
    print(f"\n測試完整 PDF 處理流程:")
    print("-" * 30)
    
    extractor = AdvancedPDFExtractor()
    classified_data = extractor.smart_classify_content(test_blocks)
    
    print("分類結果:")
    for key, value in classified_data.items():
        if value:
            print(f"  {key}: {value}")
    
    # 創建 DataFrame 並顯示
    df = pd.DataFrame([classified_data])
    print(f"\n表格格式:")
    print("-" * 30)
    for col in df.columns:
        if df[col].iloc[0]:
            print(f"{col}: {df[col].iloc[0]}")

if __name__ == "__main__":
    test_text_processing()
