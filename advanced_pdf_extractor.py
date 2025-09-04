#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
進階 PDF 擷取與分類程式 - 支援自定義分類規則
"""

import os
import sys
import pandas as pd
import re
from typing import Dict, List, Tuple, Optional
import logging
import json
from text_processor import TextProcessor

try:
    import pymupdf as fitz  # PyMuPDF
except ImportError:
    print("請安裝 PyMuPDF: pip install pymupdf")
    sys.exit(1)

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AdvancedPDFExtractor:
    """進階 PDF 文字擷取和分類處理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.extracted_data = []
        self.classification_rules = self.load_classification_rules(config_file)
        self.text_processor = TextProcessor()  # 添加文字處理器
        
    def load_classification_rules(self, config_file: Optional[str]) -> Dict:
        """載入分類規則配置"""
        default_rules = {
            "title_patterns": [
                r"^[A-Z][A-Za-z\s:]+$",  # 英文標題格式
                r".{20,}",  # 長度超過20的文字
            ],
            "chinese_title_patterns": [
                r"[\u4e00-\u9fff]{3,}",  # 包含中文字符
            ],
            "author_keywords": ["author", "作者", "by"],
            "translator_keywords": ["translator", "翻譯", "translated by"],
            "illustrator_keywords": ["illustrator", "插畫", "illustrated by"],
            "publisher_keywords": ["publisher", "出版", "published by"],
            "category_keywords": ["category", "類別", "type", "genre"],
            "exclude_from_detail": [
                "publisher:", "date:", "pages:", "size:", "volume:",
                "isbn:", "price:", "format:"
            ]
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    custom_rules = json.load(f)
                    default_rules.update(custom_rules)
            except Exception as e:
                logger.warning(f"無法載入配置文件，使用默認設置: {e}")
        
        return default_rules
    
    def extract_text_with_styles(self, pdf_path: str) -> List[Dict]:
        """從 PDF 中擷取文字並保留字體樣式資訊"""
        try:
            doc = fitz.open(pdf_path)
            text_blocks = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
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
                                    
                                    # 檢查字體樣式
                                    is_italic = bool(font_flags & 2)
                                    is_bold = bool(font_flags & 16)
                                    
                                    # 也檢查字體名稱中是否包含斜體標示
                                    if "italic" in font_name.lower() or "oblique" in font_name.lower():
                                        is_italic = True
                                    
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
                                    "styles": line_styles,
                                    "avg_font_size": sum(s["font_size"] for s in line_styles) / len(line_styles) if line_styles else 0
                                })
            
            doc.close()
            return text_blocks
            
        except Exception as e:
            logger.error(f"擷取 PDF 文字時發生錯誤: {e}")
            return []
    
    def apply_html_formatting(self, text_block: Dict) -> str:
        """為文字應用 HTML 格式標籤"""
        if not text_block.get("styles"):
            return text_block.get("text", "")
        
        text = text_block.get("text", "")
        styles = text_block.get("styles", [])
        
        # 簡化的格式應用方法
        # 檢查整個文字塊是否包含斜體內容
        has_italic = any(style.get("is_italic", False) for style in styles)
        has_bold = any(style.get("is_bold", False) for style in styles)
        
        # 為整個段落應用格式（簡化處理）
        formatted_text = text
        
        # 更精確的斜體檢測和應用
        if has_italic:
            # 嘗試找出斜體部分並單獨標記
            italic_parts = []
            for style in styles:
                if style.get("is_italic", False):
                    style_text = style.get("text", "").strip()
                    if style_text and style_text in formatted_text:
                        italic_parts.append(style_text)
            
            # 標記斜體部分
            for italic_part in italic_parts:
                if f'<i>{italic_part}</i>' not in formatted_text:
                    formatted_text = formatted_text.replace(italic_part, f'<i>{italic_part}</i>')
        
        return formatted_text
    
    def smart_text_merge(self, text_blocks: List[Dict]) -> List[Dict]:
        """
        智能合併文字塊，處理不當的換行問題
        
Args:
            text_blocks: 原始文字塊列表
            
        Returns:
            合併後的文字塊列表
        """
        if not text_blocks:
            return text_blocks
        
        merged_blocks = []
        current_block = None
        
        for block in text_blocks:
            text = block["text"].strip()
            if not text:
                continue
            
            # 如果是新的段落開始（通常是大字體、粗體或新段落標識）
            is_new_paragraph = (
                # 字體較大
                block["avg_font_size"] > 14 or
                # 包含粗體樣式
                any(style["is_bold"] for style in block["styles"]) or
                # 以大寫字母開頭的英文標題
                re.match(r'^[A-Z][a-z].*', text) or
                # 中文標題模式
                re.match(r'^[\u4e00-\u9fff]{2,}[：:：]', text) or
                # 數字編號開頭
                re.match(r'^\d+[\.\)]\s*', text) or
                # 特殊標識開頭
                text.startswith(('Chapter', 'Part', '第', '章', '節', 'Section'))
            )
            
            if current_block is None or is_new_paragraph:
                # 開始新段落
                if current_block:
                    merged_blocks.append(current_block)
                current_block = block.copy()
            else:
                # 合併到當前段落
                # 檢查是否應該合併
                should_merge = self._should_merge_text(current_block["text"], text)
                
                if should_merge:
                    # 智能合併文字
                    merged_text = self._intelligent_text_join(current_block["text"], text)
                    current_block["text"] = merged_text
                    
                    # 合併樣式資訊
                    current_block["styles"].extend(block["styles"])
                    
                    # 更新平均字體大小
                    total_size = (current_block["avg_font_size"] + block["avg_font_size"]) / 2
                    current_block["avg_font_size"] = total_size
                else:
                    # 不合併，開始新段落
                    merged_blocks.append(current_block)
                    current_block = block.copy()
        
        # 添加最後一個段落
        if current_block:
            merged_blocks.append(current_block)
        
        return merged_blocks
    
    def _should_merge_text(self, text1: str, text2: str) -> bool:
        """
        判斷兩段文字是否應該合併
        
        Args:
            text1: 第一段文字
            text2: 第二段文字
            
        Returns:
            是否應該合併
        """
        # 如果第一段以完整句子結尾，通常不合併
        if re.search(r'[.!?。！？]$', text1.strip()):
            return False
        
        # 如果第二段以大寫字母或中文標題開頭，通常不合併
        if re.match(r'^[A-Z\u4e00-\u9fff]', text2.strip()):
            # 但如果第一段看起來像是被中斷的句子，則合併
            if re.search(r'[,，]$', text1.strip()) or not re.search(r'[.!?。！？]', text1):
                return True
            return False
        
        # 如果第一段以連字符、逗號等結尾，通常應該合併
        if re.search(r'[-,，\s]$', text1.strip()):
            return True
        
        # 如果第二段以小寫字母開頭，通常應該合併
        if re.match(r'^[a-z]', text2.strip()):
            return True
        
        # 預設合併短段落
        if len(text1.strip()) < 50 and len(text2.strip()) < 50:
            return True
        
        return False
    
    def _intelligent_text_join(self, text1: str, text2: str) -> str:
        """
        智能連接兩段文字
        
        Args:
            text1: 第一段文字
            text2: 第二段文字
            
        Returns:
            連接後的文字
        """
        text1 = text1.strip()
        text2 = text2.strip()
        
        # 如果第一段以連字符結尾，直接連接
        if text1.endswith('-'):
            return text1[:-1] + text2
        
        # 如果第一段以空格結尾，直接連接
        if text1.endswith(' '):
            return text1 + text2
        
        # 如果第二段以小寫字母開頭，用空格連接
        if re.match(r'^[a-z]', text2):
            return text1 + ' ' + text2
        
        # 預設用空格連接
        return text1 + ' ' + text2
    
    def smart_classify_content(self, text_blocks: List[Dict]) -> Dict:
        """智能分類內容到相應的欄位 - 改進版本"""
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
        
        # 使用文字處理器進行智能合併，處理不當換行
        merged_blocks = self.text_processor.clean_and_merge_paragraphs(text_blocks)
        
        # 按字體大小排序，通常標題字體較大
        sorted_blocks = sorted(merged_blocks, key=lambda x: x.get("avg_font_size", 12), reverse=True)
        
        # 處理所有文字塊
        all_formatted_text = []
        for block in merged_blocks:
            formatted_text = self.apply_html_formatting(block)
            # 清理文字內容
            cleaned_text = self.text_processor.clean_text_content(formatted_text)
            all_formatted_text.append(cleaned_text)
        
        # 改進標題檢測邏輯
        title_candidates = []
        for i, block in enumerate(sorted_blocks[:5]):  # 只檢查前5個最大字體的塊
            text = block["text"].strip()
            if len(text) > 10 and len(text) < 200:  # 標題長度合理範圍
                # 檢查字體大小和樣式
                is_large_font = block["avg_font_size"] >= 14
                has_bold = any(style.get("is_bold", False) for style in block["styles"])
                
                # 檢查內容特徵
                is_title_like = (
                    # 英文標題模式
                    re.match(r'^[A-Z][A-Za-z\s:]+$', text) or
                    # 包含英文但不是純數字或簡單詞彙
                    (re.search(r'[A-Za-z]', text) and len(text.split()) >= 2) or
                    # 中英文混合標題
                    (re.search(r'[\u4e00-\u9fff]', text) and re.search(r'[A-Za-z]', text))
                )
                
                # 排除明顯不是標題的內容
                is_not_title = (
                    'publisher' in text.lower() or 'isbn' in text.lower() or
                    'pages' in text.lower() or 'price' in text.lower() or
                    text.lower().startswith('by ') or
                    re.search(r'\d{4}', text) or  # 包含年份
                    len(text.split()) < 2  # 太短
                )
                
                if is_title_like and not is_not_title and (is_large_font or has_bold):
                    score = block["avg_font_size"]
                    if has_bold:
                        score += 2
                    title_candidates.append((text, score, block))
        
        # 選擇最佳標題候選
        if title_candidates:
            title_candidates.sort(key=lambda x: x[1], reverse=True)
            best_title = title_candidates[0][0]
            formatted_title = self.apply_html_formatting(title_candidates[0][2])
            if not formatted_title.startswith('<b>'):
                classified_data["Title"] = f"<b>{formatted_title}</b>"
            else:
                classified_data["Title"] = formatted_title
        
        # 尋找中文書名 - 改進檢測
        for block in merged_blocks:
            text = block["text"].strip()
            # 檢查是否為純中文或中文為主的標題
            chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
            total_chars = len(re.sub(r'\s', '', text))
            
            if (chinese_chars >= 3 and chinese_chars / max(total_chars, 1) > 0.6 and 
                len(text) > 5 and len(text) < 100 and
                text != classified_data["Title"].replace('<b>', '').replace('</b>', '')):
                
                # 排除出版資訊
                if not any(keyword in text for keyword in ['出版', '頁數', '價格', 'ISBN']):
                    formatted_text = self.apply_html_formatting(block)
                    cleaned_text = self.text_processor.clean_text_content(formatted_text)
                    classified_data["中文書名"] = cleaned_text
                    break
        
        # 改進作者、翻譯者、插畫家檢測
        used_lines = set()  # 追蹤已使用的行，避免重複分類
        
        for line in all_formatted_text:
            line_clean = line.strip()
            if not line_clean or line_clean in used_lines:
                continue
                
            line_lower = line_clean.lower()
            
            # 檢查作者 - 更精確的匹配
            if not classified_data["Author"]:
                for keyword in self.classification_rules["author_keywords"]:
                    if keyword in line_lower and "translator" not in line_lower and "illustrator" not in line_lower:
                        # 提取作者名字，排除頁碼和其他雜訊
                        author_match = re.search(rf"{keyword}[:\s]*([^,\n\d]+?)(?:\s*\d+\s*$|$)", line_clean, re.IGNORECASE)
                        if author_match:
                            author = author_match.group(1).strip()
                            # 清理作者名字
                            author = re.sub(r'\s*\d+\s*$', '', author)  # 移除結尾的數字
                            author = re.sub(r'[,，。\.]+$', '', author)  # 移除結尾標點
                            if len(author) > 1 and not re.search(r'^\d+$', author):
                                classified_data["Author"] = author
                                used_lines.add(line_clean)
                                break
            
            # 檢查翻譯者 - 更精確的匹配和清理
            if not classified_data["Translator"]:
                for keyword in self.classification_rules["translator_keywords"]:
                    if keyword in line_lower:
                        # 更精確的翻譯者匹配
                        translator_match = re.search(rf"{keyword}[:\s]*([^,\n]+?)(?:\s*\d+\s*$|$)", line_clean, re.IGNORECASE)
                        if translator_match:
                            translator = translator_match.group(1).strip()
                            # 清理翻譯者名字，移除頁碼等雜訊
                            translator = re.sub(r'\s*\d+\s*$', '', translator)  # 移除結尾數字
                            translator = re.sub(r'[,，。\.]+$', '', translator)  # 移除結尾標點
                            translator = re.sub(r'\s*pages?\s*\d*\s*$', '', translator, re.IGNORECASE)  # 移除頁數資訊
                            if len(translator) > 1 and not re.search(r'^\d+$', translator):
                                classified_data["Translator"] = translator
                                used_lines.add(line_clean)
                                break
            
            # 檢查插畫家 - 避免誤抓 publisher
            if not classified_data["Illustrator"]:
                for keyword in self.classification_rules["illustrator_keywords"]:
                    if (keyword in line_lower and 
                        "publisher" not in line_lower and "出版" not in line_lower):
                        # 確保不是 publisher 資訊
                        illustrator_match = re.search(rf"{keyword}[:\s]*([^,\n]+?)(?:\s*\d+\s*$|$)", line_clean, re.IGNORECASE)
                        if illustrator_match:
                            illustrator = illustrator_match.group(1).strip()
                            # 清理插畫家名字
                            illustrator = re.sub(r'\s*\d+\s*$', '', illustrator)
                            illustrator = re.sub(r'[,，。\.]+$', '', illustrator)
                            if (len(illustrator) > 1 and not re.search(r'^\d+$', illustrator) and
                                "publish" not in illustrator.lower()):
                                classified_data["Illustrator"] = illustrator
                                used_lines.add(line_clean)
                                break
        
        # 改進 Detail 內容收集 - 更精確的過濾
        detail_content = []
        for line in all_formatted_text:
            line_clean = line.strip()
            if not line_clean or line_clean in used_lines:
                continue
            
            line_lower = line_clean.lower()
            
            # 檢查是否為出版資訊或其他不相關內容
            is_exclude = any(keyword in line_lower for keyword in [
                'publisher', 'isbn', 'pages', 'price', 'format', 'volume',
                '出版社', '頁數', '價格', '格式', '尺寸', '版次',
                'copyright', '版權', 'printed', '印刷',
                'edition', '版本', 'publication date', '出版日期'
            ])
            
            # 檢查是否已經被其他欄位使用
            is_already_used = (
                line_clean == classified_data["Title"].replace('<b>', '').replace('</b>', '') or
                line_clean == classified_data["中文書名"] or
                (classified_data["Author"] and classified_data["Author"] in line_clean) or
                (classified_data["Translator"] and classified_data["Translator"] in line_clean) or
                (classified_data["Illustrator"] and classified_data["Illustrator"] in line_clean)
            )
            
            # 檢查是否為有意義的內容
            is_meaningful = (
                len(line_clean) > 10 and  # 內容長度合理
                not re.search(r'^\d+$', line_clean) and  # 不是純數字
                not re.search(r'^[A-Z]{2,}$', line_clean)  # 不是純大寫縮寫
            )
            
            if not is_exclude and not is_already_used and is_meaningful:
                detail_content.append(line_clean)
        
        # 限制 Detail 內容長度，避免過長
        if detail_content:
            detail_text = " ".join(detail_content)
            if len(detail_text) > 500:  # 限制長度
                detail_text = detail_text[:500] + "..."
            classified_data["Detail"] = detail_text
        
        # 收集出版資訊到 More Info
        info_content = []
        for line in all_formatted_text:
            line_clean = line.strip()
            if not line_clean or line_clean in used_lines:
                continue
                
            line_lower = line_clean.lower()
            is_publisher_info = any(keyword in line_lower for keyword in [
                'publisher', 'isbn', 'pages', 'price', 'format',
                '出版社', '頁數', '價格', '格式', '版權'
            ])
            
            if is_publisher_info:
                info_content.append(line_clean)
        
        if info_content:
            classified_data["More Info"] = " ".join(info_content)
        
        # 自動識別類別
        full_text = " ".join(all_formatted_text)
        full_text_lower = full_text.lower()
        if "comic" in full_text_lower or "manga" in full_text_lower or "漫畫" in full_text:
            classified_data["Category"] = "漫畫類"
        elif "novel" in full_text_lower or "小說" in full_text:
            classified_data["Category"] = "小說類"
        elif "textbook" in full_text_lower or "教科書" in full_text:
            classified_data["Category"] = "教育類"
        
        return classified_data

    def process_pdf(self, pdf_path: str) -> Dict:
        """處理單個 PDF 文件"""
        logger.info(f"正在處理 PDF: {pdf_path}")
        
        text_blocks = self.extract_text_with_styles(pdf_path)
        
        if not text_blocks:
            logger.warning(f"無法從 {pdf_path} 擷取文字")
            return {}
        
        classified_data = self.smart_classify_content(text_blocks)
        
        return classified_data
    
    def process_multiple_pdfs(self, pdf_directory: str) -> pd.DataFrame:
        """處理目錄中的多個 PDF 文件"""
        all_data = []
        
        for filename in os.listdir(pdf_directory):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(pdf_directory, filename)
                data = self.process_pdf(pdf_path)
                if data:
                    data["Source_File"] = filename  # 添加源文件名
                    all_data.append(data)
        
        if all_data:
            df = pd.DataFrame(all_data)
            return df
        else:
            return pd.DataFrame()
    
    def save_results(self, df: pd.DataFrame, output_path: str, format_type: str = "excel"):
        """保存結果到文件"""
        try:
            if format_type.lower() == "excel":
                if not output_path.endswith('.xlsx'):
                    output_path += '.xlsx'
                with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='PDF_Extract_Results')
            else:
                if not output_path.endswith('.csv'):
                    output_path += '.csv'
                df.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            logger.info(f"結果已保存到: {output_path}")
        except Exception as e:
            logger.error(f"保存文件時發生錯誤: {e}")


def create_sample_config():
    """創建示例配置文件"""
    config = {
        "title_patterns": [
            r"^[A-Z][A-Za-z\s:]+$",
            r".{20,}"
        ],
        "chinese_title_patterns": [
            r"[\u4e00-\u9fff]{3,}"
        ],
        "author_keywords": ["author", "作者", "by", "著"],
        "translator_keywords": ["translator", "翻譯", "translated by", "譯者"],
        "illustrator_keywords": ["illustrator", "插畫", "illustrated by", "插畫家"],
        "publisher_keywords": ["publisher", "出版", "published by", "出版社"],
        "category_keywords": ["category", "類別", "type", "genre"],
        "exclude_from_detail": [
            "publisher:", "date:", "pages:", "size:", "volume:",
            "isbn:", "price:", "format:", "出版社:", "日期:", "頁數:", "尺寸:"
        ]
    }
    
    with open('/workspaces/backstage/classification_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print("已創建示例配置文件: classification_config.json")


if __name__ == "__main__":
    # 創建示例配置文件
    create_sample_config()
    
    print("進階 PDF 擷取與分類程式")
    print("=" * 50)
    
    # 初始化擷取器
    extractor = AdvancedPDFExtractor("classification_config.json")
    
    # 示例：處理單個文件
    print("\n範例用法：")
    print("extractor = AdvancedPDFExtractor('classification_config.json')")
    print("data = extractor.process_pdf('your_pdf_file.pdf')")
    print("df = pd.DataFrame([data])")
    print("extractor.save_results(df, 'output.xlsx', 'excel')")
