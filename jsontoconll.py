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
sorted_labels = [sorted(l) for l in pdjson['labels']]

# key: word, value: tag
labelword = {}

newlabels = []

for index,row in pdjson.iterrows():
    # Morphological analysis
    parseline = tagger.parse(row['text']).rstrip()

    # labelsの単語を認識する
    for label in row['labels']:
        start = label[0]
        end = label[1]
        tag = label[2]
        # labelsの単語を格納
        labelword[row['text'][start:end]] = tag

    
    # 形態素解析したテキストへ置換
    pdjson.at[index,'text'] = parseline

    # labelsの単語とマッチした位置を新たにlabelsの位置とする
    for w,tag in labelword.items():

        if(re.search(w,parseline) == None):
        # 単語のマッチだと単語が形態素解析後に別れたときにマッチしない
        # そのため、最初の文字と最後の文字の位置をマッチさせて、位置を取得する
            span = re.search(r'{}.*{}'.format(w[0],w[-1]),parseline)
        else:
            span = re.search(w,parseline)

        # 新しいlabelsを設定
        tmp_label = []
        tmp_label.append(span.start())
        tmp_label.append(span.end())
        tmp_label.append(str(tag))
        newlabels.append(tmp_label)

    # 形態素解析したテキストへ置換
    pdjson.at[index,'labels'] = newlabels

    # 辞書と配列の初期化
    labelword = {}
    newlabels = []
        

pdjson.to_json(sys.argv[2],force_ascii=False,orient='records',lines=True)
