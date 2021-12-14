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

for index,row in pdjson.iterrows():
    # Morphological analysis
    parseline = tagger.parse(row['text']).rstrip()

    # labelsの単語を認識する
    for label in row['labels']:
        start = label[0]
        end = label[1]
        tag = label[2]
        
        # labelsと単語を格納
        labels.append(tag)
        words.append(row['text'][start:end]) 
    
    # 形態素解析したテキストへ置換
    pdjson.at[index,'text'] = parseline

    # labelsの単語とマッチした位置を新たにlabelsの位置とする
    position = 0
    for w,tag in zip(words,labels):
        
        ws = tagger.parse(w).rstrip()

        # wsにマッチする単語を検索
        p = re.compile(re.escape(ws))

        # ヒットした中を検索
        for m in p.finditer(parseline):
            # position以降を検索
            if((position != 0) and (m.start() < position)):
                continue
            start = m.start()
            end = m.end()
            break
            
        # 新しいlabelsを設定
        tmp_label = []
        tmp_label.append(start)
        tmp_label.append(end)
        tmp_label.append(str(tag))
        newlabels.append(tmp_label)
        position = end


    # 形態素解析したテキストへ置換
    pdjson.at[index,'labels'] = sorted(newlabels)


    # 辞書と配列の初期化
    labels = []
    words = []
    newlabels = []
    position = 0
        

pdjson.to_json(sys.argv[2],force_ascii=False,orient='records',lines=True)
