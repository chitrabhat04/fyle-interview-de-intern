# Your imports go here
import logging

import os
import json
import re
import spacy

logger = logging.getLogger(__name__)

'''
    Given a directory with receipt file and OCR output, this function should extract the amount

    Parameters:
    dirpath (str): directory path containing receipt and ocr output

    Returns:
    float: returns the extracted amount

'''
def extract_amount(dirpath: str) -> float:

    dirpath = os.path.join(dirpath, 'ocr.json')
    #Extracting the text from ocr.json
    with open(dirpath, 'r', encoding='utf-8') as f:
        db =json.load(f)
    text = ""
    for i in range(len(db["Blocks"])):
        if 'Text' in db["Blocks"][i]:
            text += " " + db["Blocks"][i]["Text"]
    f.close()
    #Text pre-processing
    text = re.sub(r"[,;@#?!&:]+", ' ', text.lower())
    text = text.replace("usd", "$")
    text = text.replace('$ ', '$')
    token_list = text.split()
    #Extracting all money-related terms using NLP and regex
    final_amount = None
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    common_words = ["payments", "total", "amount", "credit", "payment"]
    extracted_text = [ent.text for ent in doc.ents if ent.label_ == 'MONEY']
    regex = r"[£$€]\s*[.,\d ]+"
    extracted_text.extend(re.findall(regex, text, re.I))
    for i in range(len(extracted_text)):
        extracted_text[i] = extracted_text[i].replace('$', '')
        try:
            extracted_text[i] = float(extracted_text[i].strip().replace(' ', '.'))
        except:
            extracted_text[i] = 0.0
            #print("Cannot convert to float, taking value as 0.0")
    if len(extracted_text) == 0 or extracted_text.count(extracted_text[0]) == len(extracted_text):
        for word in common_words:
            if word in token_list:
                index = token_list.index(word)
                amount = ".".join(token_list[index+1:index+2]).replace('$', '').replace(' ', '')
                try:
                    final_amount = float(amount)
                except:
                    continue
                    #print("Cannot convert to float, passing")
    else: final_amount = max(extracted_text)
    if final_amount is None:
        regex = r"[£$€]\s*[.,\d ]+"
        final_amount = float(re.findall(regex, text, re.I)[0].replace('$', '').replace(' ', ''))
    return final_amount
