import glob
import sys

import spacy
    
def proc_file(path, nlp):
    f=open(path, mode='r')
    for l in f:
        l=l.strip()
        if '。' not in l:
            continue
        doc=nlp(l)
        for sent in doc.sents:
            print(sent.text)
    f.close()

if __name__=='__main__':
    if len(sys.argv)!=2:
        sys.exit('designate dir.')
    nlp=spacy.load('ja_core_news_lg')
    for path in glob.glob(sys.argv[1]+'*'):
        proc_file(path, nlp)

