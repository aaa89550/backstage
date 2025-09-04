#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文字處理模組 - 處理 PDF 擷取後的文字清理和合併
"""

import re
from typing import List, Dict


class TextProcessor:
    """處理 PDF 文字的清理和合併"""
    
    def __init__(self):
        pass
    
    def clean_and_merge_paragraphs(self, text_blocks: List[Dict]) -> List[Dict]:
        """
        清理和合併段落，處理不當的換行問題
        
        Args:
            text_blocks: 包含文字和樣式的字典列表
            
        Returns:
            處理後的文字塊列表
        """
        if not text_blocks:
            return text_blocks
        
        merged_blocks = []
        current_block = None
        
        for block in text_blocks:
            text = block.get("text", "").strip()
            if not text:
                continue
            
            # 判斷是否為新段落
            is_new_paragraph = self._is_new_paragraph(text, block)
            
            if current_block is None or is_new_paragraph:
                # 開始新段落
                if current_block:
                    merged_blocks.append(current_block)
                current_block = block.copy()
            else:
                # 嘗試合併到當前段落
                if self._should_merge_texts(current_block["text"], text):
                    # 合併文字
                    merged_text = self._smart_join_texts(current_block["text"], text)
                    current_block["text"] = merged_text
                    
                    # 合併樣式資訊（如果存在）
                    if "styles" in block and "styles" in current_block:
                        current_block["styles"].extend(block["styles"])
                    
                    # 更新平均字體大小（如果存在）
                    if "avg_font_size" in block and "avg_font_size" in current_block:
                        current_size = current_block.get("avg_font_size", 12)
                        block_size = block.get("avg_font_size", 12)
                        current_block["avg_font_size"] = (current_size + block_size) / 2
                else:
                    # 不合併，開始新段落
                    merged_blocks.append(current_block)
                    current_block = block.copy()
        
        # 添加最後一個段落
        if current_block:
            merged_blocks.append(current_block)
        
        return merged_blocks
    
    def _is_new_paragraph(self, text: str, block: Dict) -> bool:
        """
        判斷文字是否為新段落的開始
        
        Args:
            text: 文字內容
            block: 文字塊資訊
            
        Returns:
            是否為新段落
        """
        # 字體較大的文字通常是標題或新段落
        avg_font_size = block.get("avg_font_size", 12)
        if avg_font_size > 14:
            return True
        
        # 檢查是否有粗體樣式
        styles = block.get("styles", [])
        if any(style.get("is_bold", False) for style in styles):
            return True
        
        # 英文標題模式（以大寫字母開頭）
        if re.match(r'^[A-Z][a-zA-Z\s]{10,}', text):
            return True
        
        # 中文標題模式
        if re.match(r'^[\u4e00-\u9fff]{2,}[：:：]', text):
            return True
        
        # 數字編號開頭
        if re.match(r'^\d+[\.\)]\s*', text):
            return True
        
        # 特殊章節標識
        chapter_keywords = ['Chapter', 'Part', 'Section', '第', '章', '節', '篇']
        if any(text.startswith(keyword) for keyword in chapter_keywords):
            return True
        
        return False
    
    def _should_merge_texts(self, text1: str, text2: str) -> bool:
        """
        判斷兩段文字是否應該合併
        
        Args:
            text1: 第一段文字
            text2: 第二段文字
            
        Returns:
            是否應該合併
        """
        text1 = text1.strip()
        text2 = text2.strip()
        
        # 如果第一段以完整句子結尾，通常不合併
        if re.search(r'[.!?。！？]$', text1):
            return False
        
        # 如果第二段以大寫字母開頭，但第一段看起來不完整，則合併
        if re.match(r'^[A-Z]', text2):
            # 檢查第一段是否看起來被截斷
            if (re.search(r'[,，\-\s]$', text1) or 
                len(text1) < 30 or 
                not re.search(r'[.!?。！？]', text1)):
                return True
            return False
        
        # 如果第二段以小寫字母開頭，通常應該合併
        if re.match(r'^[a-z]', text2):
            return True
        
        # 如果第一段以連字符、逗號、空格結尾，通常應該合併
        if re.search(r'[-,，\s]$', text1):
            return True
        
        # 如果兩段都很短，傾向於合併
        if len(text1) < 50 and len(text2) < 50:
            return True
        
        # 預設不合併
        return False
    
    def _smart_join_texts(self, text1: str, text2: str) -> str:
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
        
        # 如果第一段以連字符結尾，直接連接（處理單詞被分割的情況）
        if text1.endswith('-'):
            return text1[:-1] + text2
        
        # 如果第一段已經以空格結尾，直接連接
        if text1.endswith(' '):
            return text1 + text2
        
        # 如果第二段以小寫字母開頭，用空格連接
        if re.match(r'^[a-z]', text2):
            return text1 + ' ' + text2
        
        # 如果第一段以標點符號結尾，用空格連接
        if re.search(r'[,，;；]$', text1):
            return text1 + ' ' + text2
        
        # 預設用空格連接
        return text1 + ' ' + text2
    
    def clean_text_content(self, text: str) -> str:
        """
        清理文字內容，移除多餘的空格和換行
        
        Args:
            text: 原始文字
            
        Returns:
            清理後的文字
        """
        if not text:
            return text
        
        # 移除多餘的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除行首行尾空格
        text = text.strip()
        
        # 修正常見的格式問題
        # 修正句號前的空格
        text = re.sub(r'\s+([.!?。！？])', r'\1', text)
        
        # 修正逗號前的空格
        text = re.sub(r'\s+([,，;；])', r'\1', text)
        
        # 修正括號內的空格
        text = re.sub(r'\(\s+', '(', text)
        text = re.sub(r'\s+\)', ')', text)
        
        return text
    
    def preserve_formatting(self, text: str, original_blocks: List[Dict]) -> str:
        """
        在清理文字的同時保留重要的格式標籤
        
        Args:
            text: 清理後的文字
            original_blocks: 原始文字塊（包含格式資訊）
            
        Returns:
            保留格式的文字
        """
        # 收集所有斜體內容
        italic_contents = set()
        bold_contents = set()
        
        for block in original_blocks:
            block_text = block.get("text", "")
            styles = block.get("styles", [])
            
            for style in styles:
                style_text = style.get("text", "").strip()
                if not style_text:
                    continue
                
                if style.get("is_italic", False):
                    italic_contents.add(style_text)
                
                if style.get("is_bold", False):
                    bold_contents.add(style_text)
        
        # 重新應用格式標籤
        for italic_text in italic_contents:
            if italic_text in text and f'<i>{italic_text}</i>' not in text:
                text = text.replace(italic_text, f'<i>{italic_text}</i>')
        
        for bold_text in bold_contents:
            if bold_text in text and f'<b>{bold_text}</b>' not in text:
                text = text.replace(bold_text, f'<b>{bold_text}</b>')
        
        return text
