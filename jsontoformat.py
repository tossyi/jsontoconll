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


def PrintFormat(text, words, labels, mode):
    # skip in case of labels = []
    if(len(labels) == 0):
        return

    for w in text.split():
        flag = 0
        parsew = tagger.parse(w)
        for tagw, tag in zip(words, labels):

            # match words and tag's words
            if w == tagw:
                B = 0

                for pw in parsew.split():
                    parsew2 = tagger2.parse(pw)

                    if B == 0:
                        PrintLine(parsew2, pw, tag, mode, "B")
                        B = 1
                    else:
                        PrintLine(parsew2, pw, tag, mode, "I")

                flag = 1
                break

        # word is not tag
        if flag == 0:
            for pw in parsew.split():
                parsew2 = tagger2.parse(pw)
                PrintLine(parsew2, pw, tag, mode, "O")


def WordsLabels(text, labels):

    words = []
    labels_list = []

    for label in labels:
        start = label[0]
        end = label[1]
        tag = label[2]

        # Store labels and words
        labels_list.append(tag)
        words.append(text[start:end])

    return words, labels_list


if __name__ == "__main__":
    tagger = MeCab.Tagger("-Owakati -d /usr/local/lib/mecab/dic/ipadic")
    tagger2 = MeCab.Tagger("--eos-format= -d /usr/local/lib/mecab/dic/ipadic")

    # Read jsonl file from doccano
    pdjson = pd.read_json(sys.argv[1], orient="records", lines=True)

    # Sort the elements "labels" in ascending order
    pdjson["label"] = [sorted(l) for l in pdjson["label"]]

    for index, row in pdjson.iterrows():
        position = 0

        # Store tag's words and labels
        words, labels = WordsLabels(row["text"], row["label"])

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
        PrintFormat(row["text"], words, labels, sys.argv[2])
        print("")
