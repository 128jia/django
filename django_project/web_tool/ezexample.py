import numpy
from bs4 import BeautifulSoup
import json
import pandas as pd
import requests
import numpy as np
from IPython.display import display
import sys,os
count_exon = 0
count_intron = 0
def extract_Part(text: str) -> str:
    
    paragraphs =[]
    current_paragraph = ''
    for char in text:
        if char.islower():
         current_paragraph += char
        elif char.upper() and current_paragraph:  # 如果遇到小寫且已有大寫字符，則視為段落結束
            paragraphs.append(current_paragraph)
            current_paragraph = ''
        else:
            continue
    if current_paragraph:
        paragraphs.append(current_paragraph)
def parser(crawlerdata: BeautifulSoup):
    data =json.loads(str(soup))
    #print(f"the type of data is{type(data)}")
    #print(data)
    data =data["fields"]
    strand = data['unspliced_sequence_context']['data']['strand']
    protein=data['protein_sequence']['data']['sequence']
    print(protein)
    #print(data)#print('---------------------------')# print(data.keys())# print('data.values')# spliced_sequence_context = data.get('spliced_sequence_context')
    if strand =="+":
        transcriptdata = data["unspliced_sequence_context"]["data"]["positive_strand"]["features"]
        unspliced_transcript = data["unspliced_sequence_context"]["data"]["positive_strand"]["sequence"]
        spliced_transcript = data["spliced_sequence_context"]["data"]["positive_strand"]["sequence"]
    else:
        transcriptdata = data["unspliced_sequence_context"]["data"]["negative_strand"]["features"]
        unspliced_transcript = data["unspliced_sequence_context"]["data"]["negative_strand"]["sequence"]
        spliced_transcript = data["spliced_sequence_context"]["data"]["negative_strand"]["sequence"]
    # print('data',transcriptdata)
    # print('---------------------------')
    # print(unspliced_transcript)
    # print('---------------------------')
    # print(spliced_transcript)
    unspliced_5UTR,unspliced_3UTR = get_UTR(unspliced_transcript)
    spliced_5UTR,spliced_3UTR = get_UTR(spliced_transcript)
    if (unspliced_5UTR == spliced_5UTR and unspliced_3UTR==spliced_3UTR) :
        print('this is normal case')
        total_start,total_end,total_len,total_name =normal(unspliced_transcript)
        frame = pd.DataFrame({'Name':total_name,'Start':list(total_start),'End':list(total_end),'Length':list(total_len)})
        frame.loc[len(frame.index)] = ['CDS','-','-','-']
        frame.set_index('Name',inplace = True)
        return frame
    else:
        print('this is special case.')
        
        table = pd.DataFrame(columns=["type","start","stop"])
        for i in range(len(transcriptdata)):
            table.loc[i] = transcriptdata[i]
        #增添一欄為長度值
        table["length"] = table.apply(lambda x: count_len(x["start"],x["stop"]),axis=1)
        #重新定義TYPE

        table['type'] = table.apply(rename_type, axis=1)
        table.loc[len(table.index)] = ['CDS','-','-','-']
        #table = table.to_string(index=False)
        print(type(table))
        return table
def rename_type(row):
    global count_exon,count_intron
    if row['type'] == 'exon':
        count_exon += 1
        return f'exon{count_exon}'
    elif row['type'] == 'intron':
        count_intron += 1
        return f'intron{count_intron}'
    else:
        return row['type']  
def count_len(x,y):
    return y-x+1
def get_UTR(spliced_file):
    paragraphs = []
    length = []
    current_paragraph = ''
    #分割
    for char in spliced_file:
        if char.islower():
            current_paragraph += char
        else:
            if current_paragraph:
                paragraphs.append(current_paragraph)
                current_paragraph = ''
    if current_paragraph:
        paragraphs.append(current_paragraph)
    UTR_5 = paragraphs[0]
    UTR_3 = paragraphs[-1]
    
    return UTR_3,UTR_5
def normal(file):
    arr =np.array(list(file))
    utr5 = 0
    utr3 = 0
    No_Exon =1
    No_Intron = 1
    iter = 0
    total_len = np.array([],dtype = np.uint32)
    total_end = np.array([],dtype = np.uint32)
    total_start = np.array([],dtype = np.uint32)
    total_name = np.array([])
    total_pd = pd.DataFrame(arr.tolist(),columns = ['lower'])
    total_pd['test'] = total_pd['lower'].apply(lambda x: 1 if x.islower() else 0)
    total_arr = total_pd['test']
    for i in range(0,len(total_arr)):
        if i == len(total_arr)-1 :
            iter +=1
            total_len = np.append(total_len,iter)
            iter = 0
        elif total_arr[i] == total_arr[i+1]:
            iter +=1
        else:
            iter +=1
            total_len = np.append(total_len,iter)
            iter = 0
    for i in range(len(total_len)):
        iter = total_len[i] + iter
        total_end = np.append(total_end,iter)
    for i in range(len(total_end)):
        if i<2:
            total_start = np.append(total_start,[1])
        else:
            total_start = np.append(total_start,total_end[i-1]+1)
    total_end[len(total_end)-2] = total_end[len(total_end)-1]   
    total_len =total_end - total_start + 1
    for i in range(len(total_start)):
        if i ==0:
            total_name = np.append(total_name,["UTR'5"])
        if i%2 !=0 and i!=0 and i!=(len(total_start)-1):
            total_name = np.append(total_name,'Exon{}'.format(No_Exon))
            No_Exon += 1
        elif i%2 ==0 and i!=0 and i!=(len(total_start)-1):
            total_name = np.append(total_name,'Intron{}'.format(No_Intron))
            No_Intron += 1
        elif i ==(len(total_start)-1):
            total_name = np.append(total_name,["UTR'3"])
    return total_start,total_end,total_len,total_name

user_input = input("請輸入序列名稱: ")
url = f'https://wormbase.org/rest/widget/transcript/{user_input}/sequences'
web = requests.get(url)
soup = BeautifulSoup(web.text, "html.parser")
a=parser(soup)
# with pd.option_context('display.max_rows',None,'display.max_columns',None):
#             display(parser(soup))

# if __name__ == '__main__':
#     transcript_id = sys.argv[1] if len(sys.argv) > 1 else None
#     if transcript_id:
#         url = f'https://wormbase.org/rest/widget/transcript/{transcript_id}/sequences'
#         web = requests.get(url)
#         soup = BeautifulSoup(web.text, "html.parser")
        
#         # with pd.option_context('display.max_rows',None,'display.max_columns',None):
#         #     display(parser(soup))
#         parsed_data = parser(soup)
#         # 将DataFrame转换为字典
#         data_dict = parsed_data.to_dict(orient='records')
        
#         # 将字典转换为JSON字符串
#         json_output = json.dumps(data_dict, ensure_ascii=False)
        
#         # 输出JSON数据
#         print(json_output)
#     else:
#         print(json.dumps({"error": "No transcript ID provided"}))
    