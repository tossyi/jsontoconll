from doccano_transformer.datasets import NERDataset
from doccano_transformer.utils import read_jsonl
import sys

dataset = read_jsonl(filepath=sys.argv[1], dataset=NERDataset, encoding='utf-8')

conll = dataset.to_conll2003(tokenizer=str.split)
with open(sys.argv[2], 'w') as f:
  for item in conll:
    f.write(item['data'])
