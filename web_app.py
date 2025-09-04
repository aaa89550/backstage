#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 擷取與分類程式 - Web 介面
提供網頁介面來上傳和處理 PDF 文件
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import tempfile
import pandas as pd
from advanced_pdf_extractor import AdvancedPDFExtractor
import json
from werkzeug.utils import secure_filename
import io
import zipfile

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 初始化 PDF 擷取器
extractor = AdvancedPDFExtractor()

@app.route('/')
def index():
    """首頁"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """健康檢查端點"""
    return jsonify({'status': 'healthy', 'service': 'PDF Extractor'}), 200

@app.route('/upload', methods=['POST'])
def upload_file():
    """處理文件上傳"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': '沒有選擇文件'}), 400
        
        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            return jsonify({'error': '沒有選擇有效文件'}), 400
        
        results = []
        processed_files = []
        
        for file in files:
            if file and file.filename.lower().endswith('.pdf'):
                # 安全的文件名
                filename = secure_filename(file.filename)
                
                # 創建臨時文件
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    file.save(tmp_file.name)
                    
                    try:
                        # 處理 PDF
                        print(f"正在處理文件: {filename}")
                        file_results = extractor.extract_and_classify(tmp_file.name)
                        
                        for result in file_results:
                            result['filename'] = filename
                            results.append(result)
                        
                        processed_files.append(filename)
                        print(f"完成處理文件: {filename}, 提取了 {len(file_results)} 個項目")
                        
                    except Exception as e:
                        print(f"處理文件 {filename} 時發生錯誤: {str(e)}")
                        return jsonify({'error': f'處理文件 {filename} 時發生錯誤: {str(e)}'}), 500
                    finally:
                        # 清理臨時文件
                        try:
                            os.unlink(tmp_file.name)
                        except:
                            pass
        
        if not results:
            return jsonify({'error': '沒有找到可處理的內容'}), 400
        
        # 確保欄位順序
        column_order = ['filename', 'Title', 'Type', 'Authors', 'Translator', 
                       'Illustrator', 'Publisher', 'Detail', 'Year', 'Pages']
        
        # 轉換為 DataFrame 並重新排序欄位
        df = pd.DataFrame(results)
        
        # 確保所有欄位都存在
        for col in column_order:
            if col not in df.columns:
                df[col] = ''
            
        # 最終確保順序正確
        df = df[column_order]
        
        try:
            # 保存 Excel
            excel_path = "/workspaces/backstage/pdf_extraction_results.xlsx"
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='PDF_Extract_Results')
                
                # 格式化 Excel
                worksheet = writer.sheets['PDF_Extract_Results']
                
                # 調整欄位寬度
                column_widths = {
                    'A': 50, 'B': 30, 'C': 15, 'D': 20, 'E': 20,
                    'F': 20, 'G': 80, 'H': 20, 'I': 40, 'J': 20
                }
                
                for col, width in column_widths.items():
                    worksheet.column_dimensions[col].width = width
            
            # 保存 CSV
            csv_path = "/workspaces/backstage/pdf_extraction_results.csv"
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            
            print(f"成功處理 {len(processed_files)} 個文件，總共提取 {len(results)} 個項目")
            
        except Exception as e:
            print(f"保存文件時發生錯誤: {str(e)}")
            return jsonify({'error': f'保存文件時發生錯誤: {str(e)}'}), 500
        
        return jsonify({
            'success': True,
            'message': f'成功處理 {len(processed_files)} 個文件',
            'results': results,
            'processed_files': processed_files
        })
        
    except Exception as e:
        print(f"上傳處理時發生錯誤: {str(e)}")
        return jsonify({'error': f'處理文件時發生錯誤: {str(e)}'}), 500

@app.route('/download/excel', methods=['POST'])
def download_excel():
    """下載 Excel 文件"""
    try:
        # 從請求中獲取數據
        data = request.get_json()
        if not data or 'results' not in data:
            return jsonify({'error': '沒有數據可下載'}), 400
        
        results = data['results']
        
        # 確保欄位順序
        column_order = ['filename', 'Title', 'Type', 'Authors', 'Translator', 
                       'Illustrator', 'Publisher', 'Detail', 'Year', 'Pages']
        
        # 轉換為 DataFrame
        df = pd.DataFrame(results)
        
        # 確保所有欄位都存在並按正確順序排列
        for col in column_order:
            if col not in df.columns:
                df[col] = ''
        
        df = df[column_order]
        
        # 創建 Excel 文件在內存中
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='PDF_Extract_Results')
            
            # 格式化 Excel
            worksheet = writer.sheets['PDF_Extract_Results']
            
            # 調整欄位寬度
            column_widths = {
                'A': 20, 'B': 30, 'C': 15, 'D': 20, 'E': 20,
                'F': 20, 'G': 20, 'H': 40, 'I': 15, 'J': 15
            }
            
            for col, width in column_widths.items():
                worksheet.column_dimensions[col].width = width
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='pdf_extraction_results.xlsx'
        )
        
    except Exception as e:
        print(f"下載 Excel 時發生錯誤: {str(e)}")
        return jsonify({'error': f'下載失敗: {str(e)}'}), 500

@app.route('/download/csv', methods=['POST'])
def download_csv():
    """下載 CSV 文件"""
    try:
        # 從請求中獲取數據
        data = request.get_json()
        if not data or 'results' not in data:
            return jsonify({'error': '沒有數據可下載'}), 400
        
        results = data['results']
        
        # 確保欄位順序
        column_order = ['filename', 'Title', 'Type', 'Authors', 'Translator', 
                       'Illustrator', 'Publisher', 'Detail', 'Year', 'Pages']
        
        # 轉換為 DataFrame
        df = pd.DataFrame(results)
        
        # 確保所有欄位都存在並按正確順序排列
        for col in column_order:
            if col not in df.columns:
                df[col] = ''
        
        df = df[column_order]
        
        # 創建 CSV 文件在內存中
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8')
        output.seek(0)
        
        # 轉換為 BytesIO 以支持 UTF-8 BOM
        csv_output = io.BytesIO()
        csv_output.write('\ufeff'.encode('utf-8'))  # UTF-8 BOM
        csv_output.write(output.getvalue().encode('utf-8'))
        csv_output.seek(0)
        
        return send_file(
            csv_output,
            mimetype='text/csv',
            as_attachment=True,
            download_name='pdf_extraction_results.csv'
        )
        
    except Exception as e:
        print(f"下載 CSV 時發生錯誤: {str(e)}")
        return jsonify({'error': f'下載失敗: {str(e)}'}), 500

# 錯誤處理
@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': '文件過大，請上傳小於 16MB 的文件'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': '頁面不存在'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': '伺服器內部錯誤'}), 500

if __name__ == '__main__':
    # 確保模板目錄存在
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
    
    # 從環境變量獲取端口，預設為 5000
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
