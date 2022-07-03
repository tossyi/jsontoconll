# -*- coding: utf-8 -*-
#!/usr/local/bin/python3
import json
import re
import sys
import MeCab
import pandas as pd
from tokenizers import Tokenizer
from tokenizers.models import WordPiece
from tokenizers.pre_tokenizers import Whitespace
from tokenizers.trainers import WordPieceTrainer


def word_index_extract(text: str) -> list[str, int, int]:
    
    textjoin = "".join(text.split())

    word_span = []
    index = 0
    for w in text.split():
        # 単語がテキストのどの位置にあるかをイテレータで取得
        match_iter = re.finditer(re.escape(w), textjoin)

        for m in match_iter:
            if(int(m.start()) >= index):
                word_span.append([w, m.start(), m.end()])
                index = m.end()
                break
    return word_span


def PrintLine(parsew, pw, tag, mode, IOB):

    # Perform processing when parsew is divided into two lines
    if "\n" in parsew.rstrip() and mode == "crf":
        for line in parsew.splitlines():
            if IOB == "B":
                print("{}\tB-{}".format("\t".join(line.rstrip().split(",")), tag))
            elif IOB == "I":
                print("{}\tI-{}".format("\t".join(line.rstrip().split(",")), tag))
            else:
                print("{}\tO".format("\t".join(line.rstrip().split(","))))

    else:
        if IOB == "B":
            print("{} B-{}".format(pw, tag)) if mode == "conll" else print(
                "{}\tB-{}".format("\t".join(parsew.rstrip().split(",")), tag)
            )
        elif IOB == "I":
            print("{} I-{}".format(pw, tag)) if mode == "conll" else print(
                "{}\tI-{}".format("\t".join(parsew.rstrip().split(",")), tag)
            )
        else:
            print("{} O".format(pw)) if mode == "conll" else print(
                "{}\tO".format("\t".join(parsew.rstrip().split(",")))
            )


def PrintFormat(text, words, labels, position, mode):
    # skip in case of labels = []
    if(len(labels) == 0):
        return

    # extract word span
    word_span = word_index_extract(text)

    for w, w_span in zip(text.split(), word_span):

        flag = 0
        parsew = tagger.parse(w)
        for tagw, tag, tag_position in zip(words, labels, position):

            # match words and tag's words
            if w == tagw and w_span[1] == tag_position[0] and w_span[2] == tag_position[1]:
                B = 0
                for pw in parsew.split():
                    parsew2 = tagger2.parse(pw)

                    if B == 0:
                        PrintLine(parsew2, pw, tag, mode, "B")
                        B = 1
                    else:
                        PrintLine(parsew2, pw, tag, mode, "I")

                flag = 1
                # delete tagw, tag from list
                words.remove(tagw)
                labels.remove(tag)
                position.remove(tag_position)
                break

        # word is not tag
        if flag == 0:
            for pw in parsew.split():
                parsew2 = tagger2.parse(pw)
                PrintLine(parsew2, pw, tag, mode, "O")


def WordsLabels(text, labels):

    words = []
    labels_list = []
    position = []

    for label in labels:
        start = label[0]
        end = label[1]
        tag = label[2]

        # Store labels, words and label position
        labels_list.append(tag)
        words.append(text[start: end])
        position.append([start, end])

    return words, labels_list, position


if __name__ == "__main__":
    tagger = MeCab.Tagger("-Owakati -d /usr/local/lib/mecab/dic/ipadic")
    tagger2 = MeCab.Tagger("--eos-format= -d /usr/local/lib/mecab/dic/ipadic")

    # Read jsonl file from doccano
    pdjson = pd.read_json(sys.argv[1], orient="records", lines=True)

    # Sort the elements "labels" in ascending order
    pdjson["label"] = [sorted(l) for l in pdjson["label"]]

    for index, row in pdjson.iterrows():
        print("id={}".format(row["id"]))
        position = 0

        # Store tag's words and labels
        words, labels, label_position = WordsLabels(row["text"], row["label"])
        print(
            "words={}, labels={}, position={}".format(
                words, labels, label_position))

        # Remain tag's words and insert space before and after the words
        for w, tag in zip(words, labels):
            p = re.compile(re.escape(w))

            for m in p.finditer(row["text"]):
                str_list = list(row["text"])

                # Search after position
                if m.start() >= position:
                    str_list.insert(int(m.end()), " ")
                    str_list.insert(int(m.start()), " ")
                    str_list = "".join(str_list)
                    position = int(m.end())
                    break
                else:
                    str_list = "".join(str_list)

            row["text"] = str_list

        # Combine multiple consecutive blanks into one
        row["text"] = " ".join(row["text"].split())

        # Print Format
        PrintFormat(row["text"], words, labels, label_position, sys.argv[2])
        print("")
