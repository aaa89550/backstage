# PDF 擷取與分類程式

這是一個專為書籍資訊擷取設計的 Python 程式，能夠從 PDF 文件中擷取文字內容並智能分類成表格形式。

## 主要功能

- ✅ **字體樣式識別**：自動識別斜體字並添加 `<i></i>` 標籤
- ✅ **標題格式化**：為標題自動添加 `<b></b>` 標籤
- ✅ **智能分類**：將內容自動分類到對應欄位（標題、作者、翻譯者等）
- ✅ **中英文支援**：同時支援中文和英文內容識別
- ✅ **多種輸出格式**：支援 Excel 和 CSV 格式輸出
- ✅ **批量處理**：可同時處理多個 PDF 文件
- ✅ **自定義規則**：支援自定義分類規則配置

## 輸出欄位

程式會將 PDF 內容分類到以下欄位：

| 欄位名稱 | 說明 | 示例 |
|---------|------|------|
| Title | 書籍英文標題（自動加上 `<b></b>`） | `<b>Democracy on Fire: Breaking the Chains of Martial Law in 1977</b>` |
| 中文書名 | 書籍中文標題 | 民主星火：1977 衝破戒嚴的枷鎖 |
| Category | 書籍類別 | 漫畫類 |
| Author | 作者 | |
| Translator | 翻譯者 | Chen-Yu Chang, Noax Tao and Lee-Hang Chen |
| Illustrator | 插畫家 | Michael Kearney |
| Detail | 詳細內容（斜體自動加上 `<i></i>`） | `<i>In 1977, Ah Wen had been on the other side of history...</i>` |
| Rights Sold | 版權銷售資訊 | |
| More Info | 出版資訊 | Publisher: Avanguard Date: 1/2022 Pages:128 |
| Tags | 標籤 | Comic Books,2024 |

## 安裝與設置

### 1. 安裝依賴項

```bash
pip install -r requirements.txt
```

所需套件：
- `pymupdf` - PDF 文字擷取
- `pandas` - 數據處理
- `openpyxl` - Excel 文件支援

### 2. 檢查安裝

```bash
python -c "import fitz, pandas, openpyxl; print('所有依賴項安裝成功！')"
```

## 使用方法

### 方法 1：互動式使用

```bash
python pdf_extractor.py
```

程式會引導您：
1. 選擇處理單個文件或批量處理
2. 輸入 PDF 文件路徑
3. 選擇輸出格式和路徑

### 方法 2：進階功能

```bash
python advanced_pdf_extractor.py
```

支援自定義分類規則和更精確的內容識別。

### 方法 3：程式化使用

```python
from advanced_pdf_extractor import AdvancedPDFExtractor
import pandas as pd

# 初始化擷取器
extractor = AdvancedPDFExtractor()

# 處理單個 PDF
data = extractor.process_pdf('your_file.pdf')
df = pd.DataFrame([data])

# 保存結果
extractor.save_results(df, 'output.xlsx', 'excel')
```

### 方法 4：批量處理

```python
# 處理整個目錄的 PDF 文件
df = extractor.process_multiple_pdfs('/path/to/pdf/directory')
extractor.save_results(df, 'batch_output.xlsx', 'excel')
```

## 自定義分類規則

編輯 `classification_config.json` 文件來自定義分類規則：

```json
{
  "title_patterns": [
    "^[A-Z][A-Za-z\\s:]+$",
    ".{20,}"
  ],
  "chinese_title_patterns": [
    "[\\u4e00-\\u9fff]{3,}"
  ],
  "author_keywords": ["author", "作者", "by", "著"],
  "translator_keywords": ["translator", "翻譯", "translated by", "譯者"],
  "illustrator_keywords": ["illustrator", "插畫", "illustrated by", "插畫家"]
}
```

## 範例輸出

基於您提供的參考資料，程式會產生如下格式的輸出：

```
Title: <b>Democracy on Fire: Breaking the Chains of Martial Law in 1977</b>
中文書名: 民主星火：1977 衝破戒嚴的枷鎖
Category: 漫畫類
Detail: <i>In 1977, Ah Wen had been on the other side of history: recruited as a spy...</i>
More Info: Publisher: Avanguard Date: 1/2022 Pages:128 Size:17 x 23 cm Volume: 1
```

## 執行示例

```bash
# 查看示例輸出
python example_usage.py
```

## 注意事項

1. **PDF 格式要求**：
   - PDF 必須包含可提取的文字（非掃描圖片）
   - 建議使用文字型 PDF 而非圖片型 PDF

2. **字體識別**：
   - 程式會檢查字體標誌位和字體名稱來識別斜體
   - 支援大多數標準字體的樣式識別

3. **編碼支援**：
   - 完全支援 UTF-8 中文字符
   - 輸出文件使用 UTF-8 編碼

4. **效能考量**：
   - 大型 PDF 文件可能需要較長處理時間
   - 批量處理會顯示進度資訊

## 故障排除

### 常見問題

1. **無法安裝 PyMuPDF**：
   ```bash
   pip install --upgrade pip
   pip install pymupdf
   ```

2. **中文顯示問題**：
   確保系統支援 UTF-8 編碼，輸出文件使用支援中文的編輯器開啟

3. **無法識別斜體**：
   某些 PDF 的字體樣式可能需要手動調整識別規則

4. **記憶體不足**：
   處理大型 PDF 時可能需要增加系統記憶體或分批處理

## 技術細節

- **PDF 解析**：使用 PyMuPDF (fitz) 進行低層級 PDF 分析
- **字體檢測**：檢查字體標誌位 (flags) 和字體名稱
- **文字分類**：使用正則表達式和關鍵字匹配
- **格式保留**：保持原始 HTML 標籤格式

## 授權

此程式為開源軟體，供學習和商業使用。