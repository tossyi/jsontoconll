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
tagger2 = MeCab.Tagger("--eos-format= -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd")


# Read jsonl file from doccano
pdjson = pd.read_json(sys.argv[1],orient='records', lines=True)


# Sort the elements "labels" in ascending order
pdjson['labels'] = [sorted(l) for l in pdjson['labels']]

def PrintLine(parsew, pw, tag, mode, IOB):

    # Perform processing when parsew is divided into two lines
    if('\n' in parsew.rstrip() and mode == "crf"):
        for line in parsew.splitlines():
            if(IOB == "B"):
                print("{}\tB-{}".format('\t'.join(line.rstrip().split(',')),tag))  
            elif(IOB == "I"):
                print("{}\tI-{}".format('\t'.join(line.rstrip().split(',')),tag)) 
            else:
                print("{}\tO".format('\t'.join(line.rstrip().split(',')))) 
                            
    else:
        if(IOB == "B"):
            print("{} B-{}".format(pw,tag)) if mode=="conll" else print("{}\tB-{}".format('\t'.join(parsew.rstrip().split(',')),tag))  
        elif(IOB == "I"):
            print("{} I-{}".format(pw,tag)) if mode=="conll" else print("{}\tI-{}".format('\t'.join(parsew.rstrip().split(',')),tag))  
        else:
            print("{} O".format(pw,tag)) if mode=="conll" else print("{}\tO".format('\t'.join(parsew.rstrip().split(','))))


def PrintFormat(text,words,labels,mode):

    for w in text.split():
        flag = 0
        for tagw,tag in zip(words,labels):
            parsew = tagger.parse(w)            

            # match words and tag's words
            if(w == tagw):
                B = 0
                for pw in parsew.split():
                    parsew2 = tagger2.parse(pw)    

                    if(B==0):
                        PrintLine(parsew2, pw, tag, mode, "B")
                        B = 1
                    else:
                        PrintLine(parsew2, pw, tag, mode, "I")

                flag = 1
                break
            
        # word is not tag
        if(flag==0):
            for pw in parsew.split():
                parsew2 = tagger2.parse(pw)     
                PrintLine(parsew2, pw, tag, mode, "O")

def WordsLabels(text,labels):

    words = []
    labels_list = []
    
    for label in labels:
        start = label[0]
        end = label[1]
        tag = label[2]
        
        # Store labels and words
        labels_list.append(tag)
        words.append(text[start:end])
        
    return words,labels_list

for index,row in pdjson.iterrows():
    position = 0

    # Store tag's words and labels
    words,labels = WordsLabels(row['text'],row['labels'])

    # Remain tag's words and insert space before and after the words
    for w,tag in zip(words,labels):
        p = re.compile(re.escape(w))

        for m in p.finditer(row['text']):
            str_list = list(row['text'])
            
            # Search after position
            if(m.start() >= position):
                str_list.insert(int(m.end()),' ')
                str_list.insert(int(m.start()),' ')
                str_list = ''.join(str_list)
                position = int(m.end())
                break
            else:
                str_list = ''.join(str_list)

        row['text'] = str_list

    # Combine multiple consecutive blanks into one
    row['text'] = " ".join(row['text'].split())

    # Print Format
    PrintFormat(row['text'],words,labels,sys.argv[2])
    print("")

