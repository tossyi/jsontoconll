file="./data/all.conll"
if [ -e $file ]; then
    rm ./data/all.conll
fi

files="./data/*"
for filepath in $files; do
    echo $filepath
    cat $filepath/admin.jsonl | awk '{sub("label","labels",$0);print $0}' | awk '{sub("data","text",$0); print $0}' > $filepath/admin_new.jsonl

    python jsontoconll.py $filepath/admin_new.jsonl $filepath/output.jsonl
    rm $filepath/admin_new.jsonl
    
    python doccano-transformer.py $filepath/output.jsonl $filepath/dataset.conll
    rm $filepath/output.jsonl
done


touch ./data/all.conll
for filepath in $files; do
    if [ $filepath = "./data/all.conll" ]; then
	echo "skip"
	continue
    fi
	
    echo $filepath
    cat $filepath/dataset.conll | grep -v DOCSTART | cat -s >> ./data/all.conll
done
