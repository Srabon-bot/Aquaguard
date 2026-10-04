import zipfile
import xml.etree.ElementTree as ET

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
    with open('D:/Projects/pred_flood/extracted_docx.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Extraction successful.')
except Exception as e:
    print(f'Error: {e}')
