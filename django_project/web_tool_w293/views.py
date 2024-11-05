from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from .models import AllTable,Duplicate
from bs4 import BeautifulSoup
import json,requests,copy,os
import pandas as pd

def index(request):
    return render(request, 'home.html', locals())
#check if mysql is connected
def show_data(request):
    data = AllTable.objects.all()[:10]
    data2 = Duplicate.objects.all()[:10]
    return render(request, 'index.html', {'data': data2})
def search(request):
    print('--------------------')
    query = request.POST.get('query', '')
    warning_message = ""
    data =[]
    try:
        # 查找 Duplicate 表中是否有 name 与 query 匹配的数据
        dup_record = Duplicate.objects.get(Q(name__icontains=query))  # 直接使用 .get()
        wormbase_ids = dup_record.wormbase_ids  # 获取 Wormbase_IDs 的值
        dup_number = 1
        print('匹配的 Duplicate 记录:', dup_record)
    except Duplicate.DoesNotExist:
        dup_number = 0
        print('No duplicated input')
    if dup_number == 1:
        print('Duplicate record found, searching AllTable for wormbase_id:', wormbase_ids)
        # 根据 wormbase_ids 在 AllTable 中查找相关记录
        wormbase_id_list = wormbase_ids.split(',')  # 以逗号分隔
        # 根据拆分后的 wormbase_id 列表在 AllTable 中查找相关记录
        results = AllTable.objects.filter(
            Q(wormbase_id__in=wormbase_id_list)  # 使用 __in 查询多个 wormbase_id
        ).values('wormbase_id', 'sequence_name', 'gene_name', 'other_names', 'transcript', 'status', 'type', 'count')
        
        data = list(results)  # 将 QuerySet 转换为列表
        print('AllTable 数据:', data)
    else:
        print("No Duplicate record found, searching AllTable by query =",query)
        if query:  # 确保查询字符串不为空
            # 在 wormbase_id、sequence_name、gene_name、other_names 和 transcript 字段中搜索包含查询的记录
            results = AllTable.objects.filter(
                Q(wormbase_id__exact=query) |      #本來使用 Q(wormbase_id__icontains=query) |，可搜尋相關字詞
                Q(sequence_name__exact=query) |
                Q(gene_name__exact=query) |
                Q(other_names__exact=query) |
                Q(transcript__exact=query) 
            ).values('wormbase_id', 'sequence_name', 'gene_name', 'other_names', 'transcript','status','type','count')  # 选择需要返回的字段
            
            # 将结果转换为列表
            data = list(results)
            print(data)
            for record in data:
                print('wormbase_id:', record['wormbase_id'])
            if not data:  # 如果 AllTable 中沒有找到匹配的結果
                warning_message = f"找不到與 {query} 匹配的資料。"
        else:
            data = []
            warning_message = f"沒有收到 {query} 的值。"
    if warning_message:  # 如果有警告信息，將其包含在返回的 JSON 中
        print('message:',warning_message)
        return JsonResponse({'data': data, 'warning': warning_message}, safe=False)
    else:
        return JsonResponse({'data': data,'query':query,'dup_number':dup_number}, safe=False)
##Browse Page   
def Browse(request):
 
    return render(request, 'browse.html', locals())
def find(request): 
    print("執行瀏覽模式")
    selected_ncRNA = request.POST.getlist('nc') #從input中的name="nc"取值
    print('勾選如下',selected_ncRNA)
    result = AllTable.objects.filter(type__in=selected_ncRNA).values(
        'wormbase_id', 'sequence_name', 'gene_name', 'other_names', 'transcript', 'status', 'type', 'count'
    )
    data=list(result)
    print("查询结果:", len(result))
    
    response_data = {
        #'draw': int(draw),  # DataTables 请求计数
        #'recordsTotal': paginator.count,   # 数据总数
        #'recordsFiltered': paginator.count,  # 筛选后的数据总数（此处没有进一步筛选）
        'data': data  # 当前页的数据
    }
    print(response_data)
    return JsonResponse(response_data, safe=False)
    


def crawl_data(request):
    
    if request.method == 'POST':
        transcript_id = request.POST.get('transcript_id')
           
        #data ={'spliced':}
        print(transcript_id)
        data ={'spliced':[],'unspliced':[],'protein':'','spliced_RNA':'','unspliced_RNA':'','specialspliced':[],'bedgraph':[]}
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
                ##---------------------------------
                ##     M79.1a.1 have reverse 3'UTR & 5'UTR ,but R01E6.4a.1 have correct rule of sequnce
                ##----------------------------------
                # 将DataFrame转换为字典
                unspliced_data = table.to_dict(orient='records')
                unspliced_data.append({"Name": 'CDS', "Start": '-', "End": '-', "Length": '-'})
                count_exon = 0
                count_intron = 0
                data['unspliced']=unspliced_data
                ##########splicedata
                table1 = pd.DataFrame(spliced_transcriptdata,columns=["type","start","stop"])
                table1["length"] = table1.apply(lambda x: count_len(x["start"],x["stop"]),axis=1) 
                print("before rename of spliced data is",table1)
                table1["type"] = table1.apply(rename_type, axis=1)
                
                table1.columns = ['Name', 'Start', 'End', 'Length']
                print("after rename of spliced data is",table1)
                spliced_data = table1.to_dict(orient='records')
                #print("spliced table without cds",spliced_data)
                ######spliced data :cds build
                print("spliced data:",spliced_data)
                try:
                    UTR_5 = [copy.deepcopy(entry) for entry in spliced_data if entry['Name'] in ['five_prime_UTR', 'three_prime_UTR'] and entry['Start'] == 1]
                    if UTR_5[0]['Name']=='three_prime_UTR':
                        for entry in spliced_data:
                            if entry['Name'] == 'three_prime_UTR':
                                entry['Name'] = 'five_prime_UTR'
                    print(f"the 5'UTR of {transcript_id} is:",UTR_5)
                    five_prime_UTR_end = UTR_5[0]['End']
                    print("let's check 5'UTR is end at",five_prime_UTR_end)
                    if five_prime_UTR_end:
                        cds_start = five_prime_UTR_end + 1
                        
                        
                    else:
                        cds_start = 1
                    print("5'UTR process complete!")
                except:
                    cds_start =1
                    print("5'UTR process complete!")
                #print("unspliceddata",unspliced_data)
                ####特例無法加入UTR(exon重排後加入utr)(若有多段UTR?)
                # 查找 'three_prime_UTR' 的 'Start' 值# 计算 'CDS' 的 'Start' 和 'End' 值
                try:
                    print("Let's check out 3'UTR!!!!")
                    UTR_3 = [copy.deepcopy(entry) for entry in spliced_data if entry['Name'] in ['five_prime_UTR', 'three_prime_UTR'] and entry['Start'] != 1]
                    if UTR_3[0]['Name']=='five_prime_UTR':
                        for entry in spliced_data:
                            if entry['Name'] == 'five_prime_UTR':
                                entry['Name'] = 'three_prime_UTR'
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
                data['bedgraph']=bedgraph(transcript_id)
                #print(data['bedgraph']['m0'])
                return JsonResponse(data, safe=False)
                
    
                    
def count_len(x,y):
    return y-x+1

def bedgraph( transcript_id):

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
    return data