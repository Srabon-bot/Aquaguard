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

print(extract_text('D:/Projects/pred_flood/AquaGuard_Capstone_Project_Report_Final_Draft.docx')[:500])
