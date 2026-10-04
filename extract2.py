import zipfile
import xml.etree.ElementTree as ET

def extract_text(docx_path):
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
    content = extract_text('D:/Projects/pred_flood/AquaShield_Capstone_Project_Report_Final_Draft.docx')
    with open('D:/Projects/pred_flood/report_preview.txt', 'w', encoding='utf-8') as f:
        f.write(content)
except Exception as e:
    pass
