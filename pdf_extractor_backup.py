#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 擷取與分類程式
功能：
1. 從 PDF 文件中擷取文字內容
2. 識別字體樣式（斜體）
3. 分類內容並輸出成表格形式
4. 為標題添加 <b></b> 標籤
5. 為斜體文字添加 <i></i> 標籤
"""

import os
import sys
import pandas as pd
import re
from typing import Dict, List, Tuple, Optional
import logging

try:
    import pymupdf as fitz  # PyMuPDF
except ImportError:
    print("請安裝 PyMuPDF: pip install pymupdf")
    sys.exit(1)

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PDFExtractor:
    """PDF 文字擷取和分類處理器"""
    
    def __init__(self):
        self.extracted_data = []
        self.font_styles = {}
        
    def extract_text_with_styles(self, pdf_path: str) -> List[Dict]:
        """
        從 PDF 中擷取文字並保留字體樣式資訊
        
        Args:
            pdf_path: PDF 文件路徑
            
        Returns:
            包含文字和樣式資訊的字典列表
        """
        try:
            doc = fitz.open(pdf_path)
            text_blocks = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # 獲取頁面中的文字塊資訊
                blocks = page.get_text("dict")
                
                for block in blocks["blocks"]:
                    if "lines" in block:
                        for line in block["lines"]:
                            line_text = ""
                            line_styles = []
                            
                            for span in line["spans"]:
                                text = span["text"].strip()
                                if text:
                                    font_name = span["font"]
                                    font_flags = span["flags"]
                                    font_size = span["size"]
                                    
                                    # 檢查是否為斜體 (flags & 2 表示斜體)
                                    is_italic = bool(font_flags & 2)
                                    # 檢查是否為粗體 (flags & 16 表示粗體)
                                    is_bold = bool(font_flags & 16)
                                    
                                    line_text += text + " "
                                    line_styles.append({
                                        "text": text,
                                        "is_italic": is_italic,
                                        "is_bold": is_bold,
                                        "font_name": font_name,
                                        "font_size": font_size
                                    })
                            
                            if line_text.strip():
                                text_blocks.append({
                                    "page": page_num + 1,
                                    "text": line_text.strip(),
                                    "styles": line_styles
                                })
            
            doc.close()
            return text_blocks
            
        except Exception as e:
            logger.error(f"擷取 PDF 文字時發生錯誤: {e}")
            return []
    
    def apply_html_formatting(self, text_block: Dict) -> str:
        """
        為文字應用 HTML 格式標籤
        
        Args:
            text_block: 包含文字和樣式資訊的字典
            
        Returns:
            格式化後的 HTML 文字
        """
        formatted_text = ""
        current_text = ""
        is_italic_section = False
        
        for style_info in text_block["styles"]:
            text = style_info["text"]
            
            if style_info["is_italic"]:
                if not is_italic_section:
                    if current_text:
                        formatted_text += current_text
                        current_text = ""
                    formatted_text += "<i>"
                    is_italic_section = True
                current_text += text + " "
            else:
                if is_italic_section:
                    formatted_text += current_text.strip() + "</i>"
                    current_text = ""
                    is_italic_section = False
                current_text += text + " "
        
        # 處理剩餘的文字
        if is_italic_section:
            formatted_text += current_text.strip() + "</i>"
        else:
            formatted_text += current_text
        
        return formatted_text.strip()
    
    def clean_and_merge_text(self, text_blocks: List[str]) -> List[str]:
        """
        清理和合併文字，處理不當的換行
        
        Args:
            text_blocks: 原始文字塊列表
            
        Returns:
            清理後的文字塊列表
        """
        if not text_blocks:
            return text_blocks
        
        cleaned_blocks = []
        current_text = ""
        
        for text in text_blocks:
            text = text.strip()
            if not text:
                continue
            
            # 如果當前文字是新段落的開始
            is_new_paragraph = (
                # 以大寫字母開頭的英文
                re.match(r'^[A-Z][a-z].*', text) or
                # 中文標題模式
                re.match(r'^[\u4e00-\u9fff]{2,}[：:：]', text) or
                # 數字編號
                re.match(r'^\d+[\.\)]\s*', text) or
                # 特殊標識
                any(text.startswith(keyword) for keyword in ['Chapter', 'Part', '第', '章', '節'])
            )
            
            if not current_text or is_new_paragraph:
                # 儲存之前的段落
                if current_text:
                    cleaned_blocks.append(current_text)
                current_text = text
            else:
                # 合併到當前段落
                if self._should_merge_simple(current_text, text):
                    current_text = self._join_text_simple(current_text, text)
                else:
                    cleaned_blocks.append(current_text)
                    current_text = text
        
        # 添加最後一個段落
        if current_text:
            cleaned_blocks.append(current_text)
        
        return cleaned_blocks
    
    def _should_merge_simple(self, text1: str, text2: str) -> bool:
        """簡單的文字合併判斷"""
        # 如果第一段以句號結尾，不合併
        if re.search(r'[.!?。！？]$', text1.strip()):
            return False
        
        # 如果第二段以小寫字母開頭，合併
        if re.match(r'^[a-z]', text2.strip()):
            return True
        
        # 如果第一段以逗號或連字符結尾，合併
        if re.search(r'[-,，\s]$', text1.strip()):
            return True
        
        # 短段落傾向合併
        if len(text1) < 50 and len(text2) < 50:
            return True
        
        return False
    
    def _join_text_simple(self, text1: str, text2: str) -> str:
        """簡單的文字連接"""
        text1 = text1.strip()
        text2 = text2.strip()
        
        if text1.endswith('-'):
            return text1[:-1] + text2
        elif text1.endswith(' '):
            return text1 + text2
        else:
            return text1 + ' ' + text2
    
    def classify_content(self, text_blocks: List[Dict]) -> Dict:
        """
        分類內容到相應的欄位
        
        Args:
            text_blocks: 文字塊列表
            
        Returns:
            分類後的內容字典
        """
        classified_data = {
            "Title": "",
            "中文書名": "",
            "Category": "",
            "Author": "",
            "Translator": "",
            "Illustrator": "",
            "Detail": "",
            "Rights Sold": "",
            "More Info": "",
            "Tags": ""
        }
        
        # 提取純文字並進行清理合併
        text_list = []
        formatted_list = []
        
        for block in text_blocks:
            formatted_text = self.apply_html_formatting(block)
            text_list.append(block["text"])
            formatted_list.append(formatted_text)
        
        # 清理和合併文字
        cleaned_texts = self.clean_and_merge_text(text_list)
        
        # 重新應用格式（簡化版）
        full_text = "\n".join(cleaned_texts)
        """
        classified_data = {
            "Title": "",
            "中文書名": "",
            "Category": "",
            "Author": "",
            "Translator": "",
            "Illustrator": "",
            "Detail": "",
            "Rights Sold": "",
            "More Info": "",
            "Tags": ""
        }
        
        full_text = ""
        for block in text_blocks:
            formatted_text = self.apply_html_formatting(block)
            full_text += formatted_text + "\n"
        
        # 尋找標題（通常是第一個較大的文字塊或包含英文的行）
        title_found = False
        lines = cleaned_texts
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # 識別標題 - 通常是英文且較長的句子
            if not title_found and re.search(r'[A-Za-z]', line) and len(line) > 20:
                # 為標題添加粗體標籤
                if not line.startswith('<b>'):
                    classified_data["Title"] = f"<b>{line}</b>"
                else:
                    classified_data["Title"] = line
                title_found = True
                continue
            
            # 尋找中文書名
            if re.search(r'[\u4e00-\u9fff]', line) and not classified_data["中文書名"]:
                classified_data["中文書名"] = line
                continue
        
        # 將剩餘內容放入 Detail 欄位，重新應用格式
        detail_content = []
        skip_lines = 2  # 跳過標題和中文書名
        for i, line in enumerate(lines[skip_lines:], skip_lines):
            line = line.strip()
            if line and not any(keyword in line.lower() for keyword in ['publisher:', 'date:', 'pages:', 'size:']):
                # 重新檢查並應用斜體格式
                formatted_line = self._reapply_formatting(line, formatted_list)
                detail_content.append(formatted_line)
        
        if detail_content:
            classified_data["Detail"] = ' '.join(detail_content)
        
        # 尋找出版資訊
        publisher_info = []
        for line in lines:
            if any(keyword in line.lower() for keyword in ['publisher:', 'date:', 'pages:', 'size:', 'volume:']):
                publisher_info.append(line.strip())
        
        if publisher_info:
            classified_data["More Info"] = ' '.join(publisher_info)
        
        return classified_data
    
    def process_pdf(self, pdf_path: str) -> Dict:
        """
        處理單個 PDF 文件
        
        Args:
            pdf_path: PDF 文件路徑
            
        Returns:
            處理後的數據字典
        """
        logger.info(f"正在處理 PDF: {pdf_path}")
        
        # 擷取文字和樣式
        text_blocks = self.extract_text_with_styles(pdf_path)
        
        if not text_blocks:
            logger.warning(f"無法從 {pdf_path} 擷取文字")
            return {}
        
        # 分類內容
        classified_data = self.classify_content(text_blocks)
        
        return classified_data
    
    def process_multiple_pdfs(self, pdf_directory: str) -> pd.DataFrame:
        """
        處理目錄中的多個 PDF 文件
        
        Args:
            pdf_directory: PDF 文件目錄路徑
            
        Returns:
            包含所有處理結果的 DataFrame
        """
        all_data = []
        
        for filename in os.listdir(pdf_directory):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(pdf_directory, filename)
                data = self.process_pdf(pdf_path)
                if data:
                    all_data.append(data)
        
        if all_data:
            df = pd.DataFrame(all_data)
            return df
        else:
            return pd.DataFrame()
    
    def save_to_excel(self, df: pd.DataFrame, output_path: str):
        """
        將結果保存為 Excel 文件
        
        Args:
            df: 要保存的 DataFrame
            output_path: 輸出文件路徑
        """
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='PDF_Extract_Results')
            logger.info(f"結果已保存到: {output_path}")
        except Exception as e:
            logger.error(f"保存 Excel 文件時發生錯誤: {e}")
    
    def save_to_csv(self, df: pd.DataFrame, output_path: str):
        """
        將結果保存為 CSV 文件
        
        Args:
            df: 要保存的 DataFrame
            output_path: 輸出文件路徑
        """
        try:
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            logger.info(f"結果已保存到: {output_path}")
        except Exception as e:
            logger.error(f"保存 CSV 文件時發生錯誤: {e}")


def main():
    """主函數"""
    extractor = PDFExtractor()
    
    # 示例用法
    print("PDF 擷取與分類程式")
    print("=" * 50)
    
    # 選擇處理方式
    choice = input("請選擇處理方式：\n1. 處理單個 PDF 文件\n2. 處理目錄中的所有 PDF 文件\n請輸入選擇 (1 或 2): ")
    
    if choice == "1":
        pdf_path = input("請輸入 PDF 文件路徑: ").strip()
        if not os.path.exists(pdf_path):
            print("文件不存在！")
            return
        
        data = extractor.process_pdf(pdf_path)
        if data:
            df = pd.DataFrame([data])
            print("\n擷取結果:")
            print(df.to_string(index=False))
            
            # 保存結果
            save_choice = input("\n是否要保存結果？(y/n): ").lower()
            if save_choice == 'y':
                output_format = input("選擇輸出格式 (csv/excel): ").lower()
                output_path = input("輸入輸出文件路徑: ").strip()
                
                if output_format == 'excel':
                    if not output_path.endswith('.xlsx'):
                        output_path += '.xlsx'
                    extractor.save_to_excel(df, output_path)
                else:
                    if not output_path.endswith('.csv'):
                        output_path += '.csv'
                    extractor.save_to_csv(df, output_path)
        
    elif choice == "2":
        directory = input("請輸入 PDF 文件目錄路徑: ").strip()
        if not os.path.exists(directory):
            print("目錄不存在！")
            return
        
        df = extractor.process_multiple_pdfs(directory)
        if not df.empty:
            print(f"\n成功處理 {len(df)} 個 PDF 文件")
            print("\n擷取結果預覽:")
            print(df.head().to_string(index=False))
            
            # 保存結果
            save_choice = input("\n是否要保存結果？(y/n): ").lower()
            if save_choice == 'y':
                output_format = input("選擇輸出格式 (csv/excel): ").lower()
                output_path = input("輸入輸出文件路徑: ").strip()
                
                if output_format == 'excel':
                    if not output_path.endswith('.xlsx'):
                        output_path += '.xlsx'
                    extractor.save_to_excel(df, output_path)
                else:
                    if not output_path.endswith('.csv'):
                        output_path += '.csv'
                    extractor.save_to_csv(df, output_path)
        else:
            print("沒有找到可處理的 PDF 文件或處理失敗")
    
    else:
        print("無效的選擇！")


if __name__ == "__main__":
    main()
