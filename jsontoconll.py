# -*- coding: utf-8 -*-
#!/usr/local/bin/python3
from tokenizers import Tokenizer
from tokenizers.models import WordPiece
from tokenizers.trainers import WordPieceTrainer
from tokenizers.pre_tokenizers import Whitespace
import MeCab
import pandas as pd
import re
import sys


tagger = MeCab.Tagger("-Owakati -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd")

# doccanoのjsonファイルを読み込む
pdjson = pd.read_json(sys.argv[1],orient='records', lines=True)


# "labels"の2次元配列の要素内を昇順に並び替える
pdjson['labels'] = [sorted(l) for l in pdjson['labels']]

labels = []
words = []

newlabels = []

def Morphological_jsonl_to_jsonl(pdjson):

    splitted = []
    position = 0
    
    # jsonl file each row
    for index,row in pdjson.iterrows():
        text = row['text']
        
        for label in row['labels']:
            start = label[0]
            end = label[1]
            tag = label[2]
            splitted.append({'text':text[position:start], 'label':0})
            splitted.append({'text':text[start:end], 'label':tag})
            position = end
        splitted.append({'text': text[position:], 'label':0})
        print(splitted)

        
def PrintConll(text,words,labels):


    for w in text.split():
        flag = 0
        for tagw,tag in zip(words,labels):

            # 形態素解析
            parsew = tagger.parse(w)
            
            # 単語がタグの単語と一致したら
            if(w == tagw):
                #print("{} {}".format(w,tag))

                #print("parsew={}".format(parsew))
                headflag = 0
                for pw in parsew.split():
                    if(headflag==0):
                        print("{} B-{}".format(pw,tag))
                        headflag = 1
                    else:
                        print("{} I-{}".format(pw,tag))                
                flag = 1
                break
            
        # 単語がタグでなかったら
        if(flag==0):
            for pw in parsew.split():
                print("{} O".format(pw))


#Morphological_jsonl_to_jsonl(pdjson)

def WordsLabels(text,labels):

    words = []
    labels_list = []
    
    for label in labels:
        start = label[0]
        end = label[1]
        tag = label[2]
        
        # labelsと単語を格納
        labels_list.append(tag)
        words.append(text[start:end])
        
    return words,labels_list

for index,row in pdjson.iterrows():
    position = 0

    # タグの単語とラベルを格納
    words,labels = WordsLabels(row['text'],row['labels'])

    # タグがついた単語を残し、単語の前後に空白を挿入
    for w,tag in zip(words,labels):
        #print("{} {}".format(w,tag))
        p = re.compile(re.escape(w))

        #print("type={}".format(type(row['text'])))
        #print(row['text'])

        for m in p.finditer(row['text']):
            #print("m={}".format(m))
            #print("m.start()={}".format(m.start()))
            #print("m.end()={}".format(m.end()))
            str_list = list(row['text'])
            
            # position以降を検索
            if(m.start() >= position):
                #print("postion={}".format(position))
                str_list.insert(int(m.end()),' ')
                str_list.insert(int(m.start()),' ')
                str_list = ''.join(str_list)
                position = int(m.end())
                break
            else:
                str_list = ''.join(str_list)

        row['text'] = str_list

    # 複数続いた空白を一つへする
    row['text'] = " ".join(row['text'].split())

    # Conll形式の出力
    PrintConll(row['text'],words,labels)
    print("")

