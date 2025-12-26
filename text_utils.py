import os
import re
import json
import csv
from pythainlp import word_tokenize
from pythainlp.util import dict_trie, num_to_thaiword
from pythainlp.corpus import thai_words
import config

# Global Variables
custom_tokenizer = None
my_custom_dict = {}
TEMP_MARKER = "###_NB_SPACE_###" # กาวสำหรับเชื่อมคำไม่ให้ขาดออกจากกัน

# Dictionary สำหรับแปลงเดือน
THAI_MONTHS = {
    '1': 'มกราคม', '01': 'มกราคม',
    '2': 'กุมภาพันธ์', '02': 'กุมภาพันธ์',
    '3': 'มีนาคม', '03': 'มีนาคม',
    '4': 'เมษายน', '04': 'เมษายน',
    '5': 'พฤษภาคม', '05': 'พฤษภาคม',
    '6': 'มิถุนายน', '06': 'มิถุนายน',
    '7': 'กรกฎาคม', '07': 'กรกฎาคม',
    '8': 'สิงหาคม', '08': 'สิงหาคม',
    '9': 'กันยายน', '09': 'กันยายน',
    '10': 'ตุลาคม',
    '11': 'พฤศจิกายน',
    '12': 'ธันวาคม'
}

def load_custom_dict(file_path):
    custom_dict = {}
    if not os.path.exists(file_path):
        return {}
    if file_path.endswith('.json'):
        with open(file_path, 'r', encoding='utf-8') as f:
            custom_dict = json.load(f)
    elif file_path.endswith('.csv'):
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    custom_dict[row[0].strip()] = row[1].strip()
    return custom_dict

def setup_tokenizer():
    global custom_tokenizer, my_custom_dict
    my_custom_dict = load_custom_dict(config.LEXICON_PATH)
    all_words = set(thai_words())
    all_words.update(my_custom_dict.keys())
    custom_tokenizer = dict_trie(all_words)
    print(f"✅ Loaded Dictionary: {len(my_custom_dict)} words")

def replace_dates(text):
    """
    ค้นหาแพทเทิร์น DD/MM/YYYY และแปลงเป็นคำอ่านภาษาไทย
    Logic: ใช้ TEMP_MARKER เชื่อมคำให้ติดกันเป็นก้อนเดียว (ไม่โดนตัด Space)
    และใส่ \n ต่อท้ายเพื่อบังคับจบประโยค
    """
    def date_replacer(match):
        d, m, y = match.groups()
        d_val = str(int(d)) 
        m_name = THAI_MONTHS.get(m, m) 
        
        # ใช้ TEMP_MARKER แทน Space เพื่อมัดรวมเป็นก้อนเดียว
        # เช่น: วันที่###18###เดือน###ธันวาคม###พุทธศักราช###2567
        return f"{TEMP_MARKER}{d_val}{TEMP_MARKER}{TEMP_MARKER}{m_name}{TEMP_MARKER}{TEMP_MARKER}{y}\n"

    pattern = r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b'
    return re.sub(pattern, date_replacer, text)

def split_long_sentence(text, max_length=150):
    text = text.strip()
    if len(text) <= max_length:
        return [text]

    if custom_tokenizer is None: setup_tokenizer()
    words = word_tokenize(text, engine="newmm", custom_dict=custom_tokenizer)

    chunks = []
    current_chunk = ""

    for word in words:
        if len(current_chunk) + len(word) <= max_length:
            current_chunk += word
        else:
            if current_chunk: chunks.append(current_chunk)
            current_chunk = word

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def intelligent_split(text):
    if not text: return []
    text = text.strip()
    
    # 1. แปลงวันที่ (จะได้ก้อนวันที่ติดกัน + \n)
    text = replace_dates(text)
    
    # 2. ล็อก Space ระหว่างตัวเลขไทย-อังกฤษ
    text = re.sub(r'(?<=[ก-๙])\s+(?=\d)', TEMP_MARKER, text)
    text = re.sub(r'(?<=\d)\s+(?=[ก-๙])', TEMP_MARKER, text)

    # 3. ตัดด้วย Newline (ซึ่งวันที่ของเราจะโดนตัดแยกออกมาตรงนี้)
    raw_chunks = re.split(r'[\n\r]+', text)
    
    final_segments = []
    for chunk in raw_chunks:
        # 4. ตัดด้วย Whitespace (วันที่เราเชื่อมด้วย Marker ไว้ จะไม่โดนตัดตรงนี้)
        sub_chunks = re.split(r'\s+', chunk)
        for sub in sub_chunks:
            sub = sub.strip()
            if sub:
                # 5. คืนค่า Marker กลับเป็นช่องว่าง เพื่อให้โมเดลอ่านได้ถูกต้อง
                restored = sub.replace(TEMP_MARKER, " ")
                
                # Check Length
                if len(restored) > 120:
                    micro_segments = split_long_sentence(restored, max_length=150)
                    final_segments.extend(micro_segments)
                else:
                    final_segments.append(restored)
                    
    return final_segments

def normalize_text(text):
    if custom_tokenizer is None:
        setup_tokenizer()
    
    # 🔥 Fix Preview: เรียก replace_dates เพื่อให้หน้าเว็บเห็นคำอ่านวันที่
    text = replace_dates(text)
    # ล้าง Marker ออกให้เป็นช่องว่างปกติ คนอ่านจะได้ไม่งง
    text = text.replace(TEMP_MARKER, " ")
    
    raw_tokens = word_tokenize(text, engine="newmm", custom_dict=custom_tokenizer)
    processed_tokens = []
    
    for token in raw_tokens:
        val = token
        
        if token in my_custom_dict:
            val = my_custom_dict[token]
        elif token.isdigit():
            try: val = num_to_thaiword(int(token))
            except: pass
        elif re.match(r'^([0-2]?[0-9])[:.]([0-5][0-9])$', token):
            try:
                parts = re.split(r'[:.]', token)
                hh, mm = int(parts[0]), int(parts[1])
                val = f"{num_to_thaiword(hh)}นาฬิกา"
                if mm > 0: val += f"{num_to_thaiword(mm)}นาที"
            except: pass
        elif re.match(r'^\d+(\.\d+)?$', token):
             try: val = num_to_thaiword(float(token))
             except: pass
             
        val = val.strip()
        if val in ["น.", "น"]:
            continue
        if val: processed_tokens.append(val)
        
    final_text = " ".join(processed_tokens)
    return final_text, processed_tokens