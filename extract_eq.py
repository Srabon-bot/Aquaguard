import zipfile
import xml.etree.ElementTree as ET
import re

def extract_text_from_docx(docx_path):
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    text = []
    with zipfile.ZipFile(docx_path) as docx:
        tree = ET.XML(docx.read('word/document.xml'))
        for paragraph in tree.iterfind('.//w:p', namespaces):
            texts = [node.text for node in paragraph.iterfind('.//w:t', namespaces) if node.text]
            if texts:
                text.append(''.join(texts))
    return '\n'.join(text)

try:
    content = extract_text_from_docx('D:/Projects/pred_flood/AquaShield_Capstone_Project_Report_Final_Draft.docx')
    # find lines with broken math or strange characters
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'RMSE' in line or 'R2' in line or '=' in line or 'equation' in line.lower() or 'math' in line.lower() or '\\' in line:
            print(f"Line {i}: {line}")
except Exception as e:
    print(f'Error: {e}')
