from django.shortcuts import render
from django.http import HttpResponse #匯入http模組
#from web_tool.models import Gene,User
from web_tool import models, forms
from datetime import datetime
from django.http import JsonResponse
import ast,subprocess,json
import sys,os,requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from IPython.display import display
import copy

# def index(request):
#     '''
#     df = pd.read_csv('data/hw1_output_ans.csv')
#     df = df.head(10)
#     df = df.rename(columns={"Gene_ID": "id",
#                             "transcript_ID": "transcript",
#                             "# of transcripts": "number",
#                             })
#     json_string = df.to_json(orient='records')
#     genes = json.loads(json_string)
#     '''
#     genes = Gene.objects.all()
#     return render(request, 'index.html', locals())
# # def hello_world(request):
# #    time = datetime.now()
# #    return render(request, 'hello_world.html', locals())
# def form(request):
#     # ORM Test
#     try:
#         id2 = request.POST['user_id2']
#         password2 = request.POST['user_pass2']
#         user2 = User.objects.filter(user_id=id2, user_pass=password2)

#         if user2:
#             message2 = user2[0].user_content
#         else:
#             message2 = "ID or Password not found."
            
#     except:
#         pass

    
#     # ModelForm
#     if request.method == 'POST':
#         user_form = forms.UserForm(request.POST)
#         if user_form.is_valid():
#             user_form.save()
#             message3 = 'Saved successfully.'
#         else:
#             message3 = 'Something wrong, please check again.'
#     else:
#         user_form = forms.UserForm()
    
#     return render(request, 'forms.html', locals()) 

# def ajax_data(request):

#     search_value = request.POST['search']

#     if not search_value:
#         return JsonResponse({'message': 'No search value provided'}, status=400)
#     response = {'data': [], 'message': '','type':''}
#     # 查询数据库
#     try:
        
#         #  gene_id 查询
#         try:
#             gene = models.Gene.objects.get(gene_id=search_value)
            
#             gene_id= gene.gene_id,
#             transcript_id = ast.literal_eval(gene.transcript_id)
#             numbers= gene.numbers,
#             response['data'] ={
#                             'gene_id': gene.gene_id,
#                             'transcript_id': transcript_id,
#                             'numbers': gene.numbers
#                         }
#             response['type']='gene'
#             return JsonResponse(response)
#         except Gene.DoesNotExist:
#             pass  # 继续到下一个查询
#         #transcript查詢
#         gene = Gene.objects.filter(transcript_id__contains=search_value).first()
        
#         if not gene:
#             print('not')
#             return JsonResponse({'message': 'No matching Gene object found for the given search value.'})   
        

#         transcript_id = ast.literal_eval(gene.transcript_id)
#         response['data'] ={
#                             'gene_id': gene.gene_id,
#                             'transcript_id': transcript_id,
#                             'numbers': gene.numbers
#                         }
#         response['type']='transcript'
        
#         return JsonResponse(response)
#     except Exception as e:
#          return JsonResponse({'message': f'Unexpected error: {str(e)}'})
 
def crawl_data(request):
    
    if request.method == 'POST':
        transcript_id = request.POST.get('transcript_id')
        
        #data ={'spliced':}
        print(transcript_id)
        data ={'spliced':[],'unspliced':[],'protein':'','spliced_RNA':'','unspliced_RNA':'','specialspliced':[]}
        if transcript_id:
            
            try:
                url = f'https://wormbase.org/rest/widget/transcript/{transcript_id}/sequences'
                web = requests.get(url)
                soup = BeautifulSoup(web.text, "html.parser")
                data_crawl =json.loads(str(soup))
                data_crawl =data_crawl["fields"]
                strand = data_crawl['unspliced_sequence_context']['data']['strand']
                ##解析爬蟲
                if strand =="+":
                    transcriptdata = data_crawl["unspliced_sequence_context"]["data"]["positive_strand"]["features"]
                    unspliced_transcript = data_crawl["unspliced_sequence_context"]["data"]["positive_strand"]["sequence"]
                    spliced_transcript = data_crawl["spliced_sequence_context"]["data"]["positive_strand"]["sequence"]
                else:
                    transcriptdata = data_crawl["unspliced_sequence_context"]["data"]["negative_strand"]["features"]
                    unspliced_transcript = data_crawl["unspliced_sequence_context"]["data"]["negative_strand"]["sequence"]
                    spliced_transcript = data_crawl["spliced_sequence_context"]["data"]["negative_strand"]["sequence"]
                data['unspliced_RNA']=unspliced_transcript
                data['spliced_RNA']=spliced_transcript
                data['protein']=data_crawl['protein_sequence']['data']['sequence']
                unspliced_5UTR,unspliced_3UTR = get_UTR(unspliced_transcript)
                spliced_5UTR,spliced_3UTR = get_UTR(spliced_transcript)
                ###normal case
                if (unspliced_5UTR == spliced_5UTR and unspliced_3UTR==spliced_3UTR) :
                    print('this is normal case')
                    total_start,total_end,total_len,total_name =normal(unspliced_transcript)
                    table = pd.DataFrame({'Name':total_name,'Start':list(total_start),'End':list(total_end),'Length':list(total_len)})
                    # 将DataFrame转换为字典
                    unspliced_data = table.to_dict(orient='records')
                    
                    if unspliced_data:
                        #從unspliced中新增spliced資料
                        spliced_data = [entry for entry in unspliced_data if 'Exon' in entry['Name'] or entry['Name'] in ['five_prime_UTR', 'three_prime_UTR']]
                        print('1111111111111111',spliced_data)
                        #計算cds
                        # spliced_data[0]['Start'] = 1
                        # spliced_data[0]['End'] = spliced_data[0]['Start'] + spliced_data[0]['Length'] - 1

                        
                        # for i in range(1, len(spliced_data)):
                        #     spliced_data[i]['Start'] = spliced_data[i - 1]['End'] + 1
                        #     spliced_data[i]['End'] = spliced_data[i]['Start'] + spliced_data[i]['Length'] - 1
                        if spliced_data:
                            print("sucess spliced data")
                            five_prime_UTR_end = next(entry['End'] for entry in spliced_data if entry['Name'] == 'five_prime_UTR')

                            # 查找 'three_prime_UTR' 的 'Start' 值
                            three_prime_UTR_start = next(entry['Start'] for entry in spliced_data if entry['Name'] == 'three_prime_UTR')

                            # 计算 'CDS' 的 'Start' 和 'End' 值
                            cds_start = five_prime_UTR_end + 1
                            cds_end = three_prime_UTR_start - 1
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
                            
                        else:
                            print('spliced data fail')
                        unspliced_data.append({"Name": 'CDS', "Start": '-', "End": '-', "Length": '-'})
                        data['unspliced']=unspliced_data
                        print('2222222222',unspliced_data)
                        data['spliced']=spliced_data
                        
                    
                    
                        return JsonResponse(data, safe=False)
                            
                            
                ################### special case.##########################  
                else:
                    print('this is special case.')
                    
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
                    
                    data['unspliced']=unspliced_data
                    
                    exon_data = [copy.deepcopy(entry) for entry in unspliced_data if 'Exon' in entry['Name']]
                    print('exon',exon_data)
                    spliced_data =specialspliced(exon_data) 
                    print('spliced',spliced_data)
                    try:
                        UTR_5 = [copy.deepcopy(entry) for entry in unspliced_data if entry['Name'] == 'five_prime_UTR']
                        
                        five_prime_UTR_end = UTR_5[0]['End']
                        if five_prime_UTR_end:
                            cds_start = five_prime_UTR_end + 1
                            spliced_data.append( UTR_5[0] )
                            print('+utr5',spliced_data)
                        else:
                            cds_start = 1
                    except:
                        cds_start =1
                    print('splicedtable(+utr5)',spliced_data)
                    ####特例無法加入UTR(exon重排後加入utr)(若有多段UTR?)
                    # 查找 'three_prime_UTR' 的 'Start' 值# 计算 'CDS' 的 'Start' 和 'End' 值
                    try:
                        UTR_3 =  [copy.deepcopy(entry) for entry in unspliced_data if entry['Name'] == 'three_prime_UTR']
                        print('utr3',UTR_3)
                        three_prime_UTR_start = UTR_3[0]['Start']
                        print(three_prime_UTR_start)
                        if three_prime_UTR_start:
                            UTR_3[0]['End']=spliced_data[-1]['End']
                            UTR_3[0]['Start']=UTR_3[0]['End'] - UTR_3[0]['Length']
                            print('------------------')
                            print('------------',UTR_3)
                            spliced_data.append(UTR_3[0])
                            cds_end = three_prime_UTR_start - 1
                            
                        else:
                            print('cannot find utr3')
                            cds_end =unspliced_data[-1]['End']
                            
                    except:
                        cds_end =unspliced_data[-1]['End']
                    print('splicedtable(+utr3)',spliced_data)
                    
                        
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
                    print('splicedtable',spliced_data)
                    
                
                    
                    
                    print('9999999999999999',unspliced_data)
                    data['specialspliced']=spliced_data
            
                
                    
                    return JsonResponse(data, safe=False)
                
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        return JsonResponse({'error': 'No transcript_id provided'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)   
    
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
            total_name = np.append(total_name,["five_prime_UTR"])
        if i%2 !=0 and i!=0 and i!=(len(total_start)-1):
            total_name = np.append(total_name,'Exon{}'.format(No_Exon))
            No_Exon += 1
        elif i%2 ==0 and i!=0 and i!=(len(total_start)-1):
            total_name = np.append(total_name,'Intron{}'.format(No_Intron))
            No_Intron += 1
        elif i ==(len(total_start)-1):
            total_name = np.append(total_name,["three_prime_UTR"])
    return total_start,total_end,total_len,total_name
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