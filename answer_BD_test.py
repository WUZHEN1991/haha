# coding: utf-8

import time
import json
import random
import requests
import webbrowser
import urllib
import pandas as pd
import numpy as np
weight=[0.2,0.25,0.3,0.3]
questions = []
import datetime
from wechat_sender import Sender


    
headers1 = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Connection': 'keep-alive',
    'Host': 'baike.baidu.com',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    }
headers2 = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Connection': 'keep-alive',
    'Host': 'zhidao.baidu.com',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    }
headers3 = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Connection': 'keep-alive',
    'Host': 'www.zhihu.com',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    }

    
def words_zhihu_count(question,choices):
    print ("根据知乎词频:")
    req = requests.get(url='https://www.zhihu.com/search?type=content&q='+str(question),headers=headers3)
    body = req.text.encode(req.encoding).decode('utf-8')
    counts = []
    for answer in choices:
        num = body.count(answer)
        counts.append(num)
        print (answer + " >>>>>>> " + str(num))
    return counts;   

   
def words_zhidao_count(question,choices):
    print ("根据知道词频:")
    req = requests.get(url='https://zhidao.baidu.com/search?pn=0&&rn=50&lm=0&fr=bks0000&word='+str(question),headers=headers2)
    body = req.text.encode('latin1').decode('gbk')
    counts = []
    for answer in choices:
        num = body.count(answer)
        counts.append(num)
        print (answer + " >>>>>>> " + str(num))
    return counts;       
    
    
def words_baike_count(question,choices):
    print ("根据百科词频:")
    req = requests.get(url='https://baike.baidu.com/search?word='+str(question)+'&pn=0&rn=0&enc=utf8',headers=headers1)
    body = req.text.encode(req.encoding).decode('utf-8')
    body = body.replace('<em>', '')
    counts = []
    for answer in choices:
        num = body.count(answer)
        counts.append(num)
        print (answer + " >>>>>>> " + str(num))
    return counts;    
    
    #根据问题搜索结果计算每个选项出现的次数
def words_count(question,choices):
    print ("根据词频:")
    req = requests.get(url='http://www.baidu.com/s', params={'wd': question})
    body = req.text
    counts = []
    for answer in choices:
        num = body.count(answer)
        counts.append(num)
        print (answer + " >>>>>>> " + str(num))
    return counts;

#计算问题＋每个选项搜索的结果数
def search_count(question,choices):
    print ("根据结果数量：")
    counts = []
    for answer in choices:
        req = requests.get(url='http://www.baidu.com/s', params={'wd': question +"%20"+answer})
        body = req.text
        start = body.find(u'百度为您找到相关结果约') + 11
        body = body[start:]
        end = body.find(u"个")
        num = body[:end]
        num = num.replace(',', '')
        num=int(num)
        counts.append(num)
        print (answer + " >>>>>>> " + str(num))
    return counts


def get_answer():
    resp = requests.get('http://htpmsg.jiecaojingxuan.com/msg/current',timeout=4).text
    resp_dict = json.loads(resp)
    if resp_dict['msg'] == 'no data':
        return '等待题目中...'
    else:
        resp_dict = eval(str(resp))
        question = resp_dict['data']['event']['desc']
        question = question[question.find('.') + 1:question.find('?')]
        if question not in questions:
            questions.append(question)
            choices = eval(resp_dict['data']['event']['options'])
            (defen,answer,df)=get_result(question,choices,weight)
            sendanswer(defen,answer,df,question)
            time.sleep(6)
        else:
            return '等待新题目中...'

def sendanswer(defen,answer,df,question):
    msg=str('参考答案：'+answer+'。'+'\n'+df+'\n'+'选项得分分别为：'+str(tuple(defen))+'\n'+'问题：'+question+'\n'+'仅供参考，更多内容请关注SQuant')
    Sender(receivers='吴震,吴明,朱依心',port=10111).send(msg)



def get_result(question,choices,weight):
    print (u"问题 ：" + question)
    for i in range(0,len(choices)):
        print (u"选项" + str(i + 1) + u" : " +choices[i])

    is_min = (question.find(u"不") != -1)
    r1 = words_count(question,choices)
    #r2 = search_count(question,choices)
    r3 = words_baike_count(question,choices)
    r4 = words_zhidao_count(question,choices)
    r5 = words_zhihu_count(question,choices)
    r=[r1,r3,r4,r5]
    df=pd.DataFrame(r,index=['百度：','百科：','知道：','知乎：'],columns=choices)
    df1=df
    df1=df1.to_string()

    df['temp']=0.1
    print(df)
    df=df.apply(lambda x: x/np.sum(x),axis=1) 
    del df['temp']
    print(df)

    score=list(np.dot(weight,df))
    print(score)
    Score = [round(float(x), 2) for x in score]
    print(Score)
    select = 0;
    if is_min == False:
        select = score.index(max(score)) 
    else:
        print (u"注意否定")
        select = score.index(min(score))
    
    print(u"参考答案：" + choices[select])
    return Score,choices[select],df1




def main():
    question = '目前亚洲迪士尼乐园中占地面积最大的是?'
    choices = ['东京迪士尼乐园', '香港迪士尼乐园', '上海迪士尼乐园']
    (defen,answer,df)=get_result(question,choices,weight)
    sendanswer(defen,answer,df,question)


if __name__ == '__main__':
    main()
