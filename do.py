import sys

import extraction

def main(path, lang, output):
    sentences=[]
    f=open(path, mode='r', encoding='utf-8')
    for l in f:
        sentences.append(l.strip())
    f.close()
    FEs=extraction.extract_FEs(sentences, lang)
    f=open(output, mode='w', encoding='utf-8')
    for FE in sorted(FEs, reverse=True, key=lambda x: FEs[x]):
        print("{}\t{}".format(FE, FEs[FE]), file=f)
    f.close()

if __name__=='__main__':
    if len(sys.argv)!=4:
        sys.exit('usage: python3 do.py path lang output')
    main(sys.argv[1], sys.argv[2], sys.argv[3])
