from django.test import TestCase
from django.shortcuts import render
from django.http import JsonResponse

from bs4 import BeautifulSoup
import json,requests,copy
import pandas as pd,os

def crawl_data():
    
    # if request.method == 'POST':
    #     transcript_id = request.POST.get('transcript_id')
        transcript_id = input("transcript_id:?")    
        #data ={'spliced':}
        print(transcript_id)
        data ={'spliced':[],'unspliced':[],'protein':'','spliced_RNA':'','unspliced_RNA':'','specialspliced':[]}
        if transcript_id:
            
            
                url = f'https://wormbase.org/rest/widget/transcript/{transcript_id}/sequences'
                web = requests.get(url)
                soup = BeautifulSoup(web.text, "html.parser")
                data_crawl =json.loads(str(soup))
                data_crawl =data_crawl["fields"]
                strand = data_crawl['unspliced_sequence_context']['data']['strand']
                ##解析爬蟲
                if strand =="+":
                    transcriptdata = data_crawl["unspliced_sequence_context"]["data"]["positive_strand"]["features"]
                    spliced_transcriptdata = data_crawl["spliced_sequence_context"]["data"]["positive_strand"]["features"]
                    unspliced_transcript = data_crawl["unspliced_sequence_context"]["data"]["positive_strand"]["sequence"]
                    spliced_transcript = data_crawl["spliced_sequence_context"]["data"]["positive_strand"]["sequence"]
                else:
                    transcriptdata = data_crawl["unspliced_sequence_context"]["data"]["negative_strand"]["features"]
                    spliced_transcriptdata = data_crawl["spliced_sequence_context"]["data"]["positive_strand"]["features"]
                    unspliced_transcript = data_crawl["unspliced_sequence_context"]["data"]["negative_strand"]["sequence"]
                    spliced_transcript = data_crawl["spliced_sequence_context"]["data"]["negative_strand"]["sequence"]
                data['unspliced_RNA']=unspliced_transcript
                data['spliced_RNA']=spliced_transcript
                
                try:
                    data['protein']=data_crawl['protein_sequence']['data']['sequence']
                except:
                    pass
                #print(data)
                #print(spliced_transcriptdata)
                #print(spliced_transcript)
                
                table = pd.DataFrame(transcriptdata,columns=["type","start","stop"])
                #增添一欄為長度值
                table["length"] = table.apply(lambda x: count_len(x["start"],x["stop"]),axis=1)
                #重新定義TYPE
                count_exon = 0
                count_intron = 0

                def rename_type(row):
                    nonlocal count_exon, count_intron  # 使用 nonlocal 關鍵字來存取外層函式中的變數
                    
                    if row['type'] == 'exon':
                        count_exon += 1
                        return f'Exon{count_exon}'
                    elif row['type'] == 'intron':
                        count_intron += 1
                        return f'Intron{count_intron}'
                    else:
                        return row['type']
                table["type"] = table.apply(rename_type, axis=1)
                table.columns = ['Name', 'Start', 'End', 'Length']
                
                # 将DataFrame转换为字典
                unspliced_data = table.to_dict(orient='records')
                unspliced_data.append({"Name": 'CDS', "Start": '-', "End": '-', "Length": '-'})
                count_exon = 0
                count_intron = 0
                data['unspliced']=unspliced_data
                ##########splicedata
                table1 = pd.DataFrame(spliced_transcriptdata,columns=["type","start","stop"])
                table1["length"] = table1.apply(lambda x: count_len(x["start"],x["stop"]),axis=1)
                table1["type"] = table1.apply(rename_type, axis=1)
                table1.columns = ['Name', 'Start', 'End', 'Length']
                spliced_data = table1.to_dict(orient='records')
                #print("spliced table without cds",spliced_data)
                ######spliced data :cds build
                try:
                    UTR_5 = [copy.deepcopy(entry) for entry in spliced_data if entry['Name'] == 'five_prime_UTR']
                    print("utr5:",UTR_5)
                    five_prime_UTR_end = UTR_5[0]['End']
                    if five_prime_UTR_end:
                        cds_start = five_prime_UTR_end + 1
                        
                        
                    else:
                        cds_start = 1
                except:
                    cds_start =1
                #print("unspliceddata",unspliced_data)
                ####特例無法加入UTR(exon重排後加入utr)(若有多段UTR?)
                # 查找 'three_prime_UTR' 的 'Start' 值# 计算 'CDS' 的 'Start' 和 'End' 值
                try:
                    UTR_3 =  [copy.deepcopy(entry) for entry in spliced_data if entry['Name'] == 'three_prime_UTR']
                    print("utr3:",UTR_3)
                    three_prime_UTR_start = UTR_3[0]['Start']
                    if three_prime_UTR_start:
                        cds_end = three_prime_UTR_start - 1
                        
                    else:
                        print('cannot find utr3')
                        cds_end =spliced_data[-1]['End'] 
                        
                except:
                    cds_end =spliced_data[-1]['End']
                
                
                
                    
                cds_length = cds_end - cds_start + 1

                # 创建 'CDS' 的新项
                cds_entry = {
                    "Name": "CDS",
                    "Start": cds_start,
                    "End": cds_end,
                    "Length": cds_length
                }

                # 将 'CDS' 项添加到 filtered_data 中
                spliced_data.append(cds_entry)
                #print("==============================================================================")
                #print('splicedtable with cds:',spliced_data)
                data['spliced']=spliced_data
            
                
    
                    
def count_len(x,y):
    return y-x+1
def specialspliced(spliced_data):
    
    if not spliced_data:
        return spliced_data

    # 初始化第一個元素的 Start 和 End
    spliced_data[0]['Start'] = 1
    spliced_data[0]['End'] = spliced_data[0]['Start'] + spliced_data[0]['Length'] - 1

    # 從第二個元素開始依次更新
    for i in range(1, len(spliced_data)):
        spliced_data[i]['Start'] = spliced_data[i - 1]['End'] + 1
        spliced_data[i]['End'] = spliced_data[i]['Start'] + spliced_data[i]['Length'] - 1
    
    return spliced_data
def specialspliced1(spliced_data):
    if not spliced_data:
        return spliced_data

    # 找到最後一個 Exon 的 End 位置，這將被用於 three_prime_UTR 的 End
    last_exon_end = None
    for entry in spliced_data:
        if entry['Name'].startswith('Exon'):
            last_exon_end = entry['End']
    
    # 處理 three_prime_UTR
    for entry in spliced_data:
        if entry['Name'] == 'three_prime_UTR':
            if last_exon_end is not None:
                entry['End'] = last_exon_end
                entry['Start'] = entry['End'] - entry['Length'] + 1
            break  # 找到 three_prime_UTR 後即可退出循環

    # 從第二個元素開始依次更新
    for i in range(1, len(spliced_data)):
        # 跳過 Exon1 和 five_prime_UTR
        if spliced_data[i]['Name'] in ['Exon1', 'five_prime_UTR', 'three_prime_UTR']:
            continue
        # 重新計算其他 Exon
        spliced_data[i]['Start'] = spliced_data[i - 1]['End'] + 1
        spliced_data[i]['End'] = spliced_data[i]['Start'] + spliced_data[i]['Length'] - 1
    print('--------------------------------------')
    print(spliced_data)
    return spliced_data
def bedgraph(transcript_id):
    # 定义 CSV 文件路径
    base_dir = r'D:\2024.8\django_project\data'  # 更新此处

    csv_files = {
        "m0": "SRR20334757_m0_bedgraph.csv",
        "m1": "SRR20334757_m1_bedgraph.csv",
        "m2": "SRR20334757_m2_bedgraph.csv"
    }

    data = {}
    for key, file_name in csv_files.items():
        file_path = os.path.join(base_dir, file_name)
        df = pd.read_csv(file_path, header=None, names=["init_pos", "end_pos", "evenly_rc", "ref_id"])
        
        # 根據 transcript_id 過濾資料，並儲存在 data 字典中
        filtered_data = df[df['ref_id'] == transcript_id]
        data[key] = filtered_data.to_dict('records') 
    print(data['m1'])
if __name__ == "__main__":
    transcript_id ="2L52.1a.1"
    bedgraph(transcript_id)