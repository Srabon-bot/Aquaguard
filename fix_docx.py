import zipfile
import re
import shutil
import os

source_docx = 'D:/Projects/pred_flood/AquaShield_Capstone_Project_Report_Final_Draft.docx'
temp_docx = 'D:/Projects/pred_flood/temp_report.docx'
out_docx = 'D:/Projects/pred_flood/AquaGuard_Capstone_Project_Report_Final_Draft.docx'

shutil.copy2(source_docx, temp_docx)

# AI terms and equation replacements
replacements = {
    'AquaShield': 'AquaGuard',
    'R': 'R²',
    'R?': 'R²',
    'C': '°C',
    '?C': '°C',
    '?0.05': '±0.05',
    '?0.15': '±0.15',
    '?0.4': '±0.4',
    'delves into': 'examines',
    'robust': 'reliable',
    'comprehensive': 'detailed',
    'seamlessly': 'smoothly',
    'pivotal': 'important',
    'paradigm shift': 'major change',
    'vital role': 'key role',
    'crucial': 'important',
    'additionally, ': 'also, ',
    'Furthermore, ': '',
    'In conclusion, ': 'Overall, ',
    
    # Fix broken LaTeX equations to readable text formats (since Word equations need OMML, simple text is safer)
    r'\mathrm{pH} = 7.0 + \frac{V_{cal,7} - V_{out}}{S} \tag{3.1}': 'pH = 7.0 + (V_cal,7 - V_out) / S    (Eq 3.1)',
    r'V_{comp} = \frac{V_{adc}}{1.0 + 0.02\,(T - 25.0)} \tag{3.2}': 'V_comp = V_adc / [1.0 + 0.02 * (T - 25.0)]    (Eq 3.2)',
    r'\mathrm{Water\_Level} = \mathrm{Pond\_Depth} - \frac{t_{echo}\, v_{sound}}{2} \tag{3.3}': 'Water_Level = Pond_Depth - (t_echo * v_sound) / 2    (Eq 3.3)',
    r'\mathrm{RMSE} = \sqrt{\frac{1}{N}\sum \left(y_i - \hat{y}_i\right)^2} \tag{3.4}': 'RMSE = sqrt( sum(y_i - y_pred)^2 / N )    (Eq 3.4)',
    r'\mathrm{NSE} = 1.0 - \frac{\sum \left(y_i - \hat{y}_i\right)^2}{\sum \left(y_i - \bar{y}_{obs}\right)^2} \tag{3.5}': 'NSE = 1.0 - [ sum(y_i - y_pred)^2 / sum(y_i - y_mean)^2 ]    (Eq 3.5)',
    r'\mathrm{POD} = \frac{\mathrm{Hits}}{\mathrm{Hits} + \mathrm{Misses}} \tag{3.6}': 'POD = Hits / (Hits + Misses)    (Eq 3.6)',
    r'\mathrm{FAR} = \frac{\mathrm{False\_Alarms}}{\mathrm{Hits} + \mathrm{False\_Alarms}} \tag{3.7}': 'FAR = False_Alarms / (Hits + False_Alarms)    (Eq 3.7)'
}

def replace_text_in_xml(xml_content):
    text = xml_content.decode('utf-8')
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Also catch any rogue R? or 
    text = re.sub(r'R\?', 'R²', text)
    text = re.sub(r'32\?C', '32°C', text)
    text = re.sub(r'R', 'R²', text)
    text = re.sub(r'32C', '32°C', text)
    return text.encode('utf-8')

with zipfile.ZipFile(source_docx, 'r') as zin:
    with zipfile.ZipFile(out_docx, 'w') as zout:
        for item in zin.infolist():
            content = zin.read(item.filename)
            if item.filename == 'word/document.xml':
                content = replace_text_in_xml(content)
            zout.writestr(item, content)

os.remove(temp_docx)
print("Docx created:", out_docx)
