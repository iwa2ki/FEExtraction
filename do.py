import sys

import extraction

def main(path, lang):
    sentences=[]
    f=open(path, mode='r')
    for l in f:
        sentences.append(l.strip())
    f.close()
    FEs=extraction.extract_FEs(sentences, lang)
    for FE in sorted(FEs, reverse=True, key=lambda x: FEs[x]):
        print("{}\t{}".format(FE, FEs[FE]))

if __name__=='__main__':
    if len(sys.argv)!=3:
        sys.exit('usage: python3 do.py path lang')
    main(sys.argv[1], sys.argv[2])
