# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 13:25:17 2017

@author: siksdad
Francis Kim
"""

from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LTTextBoxHorizontal
from pdfminer.pdfinterp import PDFPageInterpreter
from collections import namedtuple
import re
import csv

def line_combine(text):
    line_tol = 2
    y_previous = 1.0e6
    result = []

    line = []
    for i in range(len(text)):
        #print(text[i].text)
        if (y_previous - text[i].y) < line_tol:
            line.append(text[i])
        else:
            if line:
                line.sort(key=lambda row: row.x)
                result.append(line)
            line = [text[i]]
        y_previous = text[i].y
            
    return result

TextBlock= namedtuple("TextBlock", ["x", "y", "text"])
document = open(r'psdy110317_200IMrslts.pdf', 'rb')

#Create resource manager
rsrcmgr = PDFResourceManager()
# Set parameters for analysis.
#laparams = LAParams(char_margin=200,line_margin=0.01,boxes_flow=0.0)
laparams = LAParams(line_margin=0.01)
# Create a PDF page aggregator object.
device = PDFPageAggregator(rsrcmgr, laparams=laparams)
interpreter = PDFPageInterpreter(rsrcmgr, device)

count = 1
doc_result = []
event = None
for page in PDFPage.get_pages(document):
    interpreter.process_page(page)
    # receive the LTPage object for the page.
    layout = device.get_result()
    text_l = []
    text_r = []
    text = []
    for element in layout:
        if isinstance(element, LTTextBoxHorizontal):
            if element.get_text().strip():
                if element.x0 < 300.0:
                    element_text = element.get_text().strip()
                    text_l.append( TextBlock(element.x0, element.y1, element_text ))
                else:
                    element_text = element.get_text().strip()
                    text_r.append( TextBlock(element.x0, element.y1, element_text ))
    text_l.sort(key=lambda row: (-row.y, row.x))
    text_r.sort(key=lambda row: (-row.y, row.x))
    text = line_combine(text_l) + line_combine(text_r)
    
    #print(text)
    page_result = []

    for el_text in text:
        if len(el_text)==1:
            if re.match('^women',el_text[0].text,flags=re.I) or re.match('^men',el_text[0].text,flags=re.I)\
               or re.match('^girl',el_text[0].text,flags=re.I) or re.match('^boy',el_text[0].text,flags=re.I) or re.match('^mixed',el_text[0].text,flags=re.I):
                event = el_text[0].text  
                #print(event,'***************')          
        elif len(el_text)>=2:

            if re.match('^[a-zA-Z-]{1,12}[ ]{1,3}[a-zA-Z]{1,12}',el_text[0].text) or re.match('^[a-zA-Z-]{1,12}[ ]{1,3}[a-zA-Z]{1,12}',el_text[1].text):
                #print(el_text)
                text_line = []
                line =  []
                flag_split = False
                for iel in range(len(el_text)):
                    if re.match('.+\n.+',el_text[iel].text):
                        text_out = el_text[iel].text.split('\n') 
                        flag_split = True
                    else:
                        text_out = el_text[iel].text
                        flag_split = False
                        
                    line.append(text_out)

                if flag_split:
                    text_line = list(map(list,list(zip(*line))))
                    for itln in text_line:
                        itln.append(event)
                else:
                    line.append(event)
                    text_line = [line]
                page_result += text_line
    #print(page_result)
    doc_result += page_result
with open('result.csv','w') as csvfile:
    output = csv.writer(csvfile,delimiter=',')
    for row in doc_result:
        output.writerow(row)
#print(doc_result)

