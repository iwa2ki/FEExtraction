import sys

import spacy
spacy.require_gpu()

def create_ngrams(list_words, minimum_length=4, maximum_length=10):
    ngrams=[]
    if len(list_words)>=minimum_length:
        for start in range(0, len(list_words)-minimum_length+1):
            for length in range(minimum_length, len(list_words)-start+1):
                if length>maximum_length:
                    break
                ngrams.append(list_words[start:start+length])
    return ngrams

def acceptable(candidates, frequency, minimum=3):
    maximum=([], 0)
    for candidate in sorted(candidates, reverse=True, key=lambda x: len(x)):
        key=list_to_str(candidate)
        if key not in frequency:
            #sys.stderr("{} was not found in ngrams.".format(key))
            continue
        if len(maximum[0]) > len(candidate):
            break
        if frequency[key]>=minimum and frequency[key]>maximum[1]:
            maximum=(candidate, frequency[key])
    if maximum[0]==[]:
        return None
    return maximum[0]

def list_to_str(l, lang='default'):
    sep=''
    if lang in ['ja']:
        sep=''
    elif lang in ['default', 'fi']:
        sep=' '
    return sep.join(l)

def extract_FEs(sentences, language, minimum_frequency=3):
    languages={'ja': 'ja_core_news_lg', 'fi': 'spacy_fi_experimental_web_md'}
    nlp=spacy.load(languages[language], disable=['parser', 'ner', 'textcat'])
    ngrams={}
    debug=[0, len(sentences)]
    for sentence in sentences:
        doc=nlp(sentence)
        ngram_stack=[]
        for token in doc:
            if token.text in '.,!?':
                continue
            if language in ['ja']:
                ngram_stack.append(token.text)
            else:
                ngram_stack.append(token.lower_)
        if len(ngram_stack)!=0:
            if language=='ja':
                ngram_combination=create_ngrams(ngram_stack, 5) # [([ngram], (start, start+length))]
            else:
                ngram_combination=create_ngrams(ngram_stack) # [([ngram], (start, start+length))]
            for ngram in ngram_combination:
                ngram=list_to_str(ngram)
                if ngram not in ngrams:
                    ngrams[ngram]=0
                ngrams[ngram]+=1
        debug[0]+=1
        if debug[0] % 100 == 0:
            print("ngram counting: {}/{}".format(debug[0], debug[1]), file=sys.stderr)
    FEs={}
    debug=[0, len(sentences)]
    languages={'ja': 'ja_core_news_lg', 'fi': '../train_spacy/fi-ner/model-last/'}
    nlp=spacy.load(languages[language], disable=['textcat'])
    for j, sentence in enumerate(sentences):
        sentence=nlp(sentence)
        root_flag=False
        stack=[]
        best_ngram=([], 0, -1) # ngram, freq, count
        best_root_ngram=([], 0, -1)
        count=0
        num_tokens=len(sentence)
        for i, token in enumerate(sentence):
            if token.dep_=='punct' and i!=num_tokens-1:
                continue
            if len(stack)!=0 and (token.ent_iob_!='O' or i==num_tokens-1):
                candidate=acceptable(create_ngrams(stack), ngrams)
                if candidate is not None:
                    ngram=list_to_str(candidate)
                    if len(best_ngram[0])<len(candidate) or (len(best_ngram[0])==len(candidate) and best_ngram[1]<ngrams[ngram]):
                        best_ngram=(candidate, ngrams[ngram], count)
                    if root_flag and (len(best_root_ngram[0])<len(candidate) or (len(best_root_ngram[0])==len(candidate) and best_root_ngram[1]<ngrams[ngram])):
                        best_root_ngram=(candidate, ngrams[ngram], count)
                count+=1
                root_flag=False
                stack=[]
                continue
            if token.dep_=='ROOT':
                root_flag=True
            if language in ['ja']:
                stack.append(token.text)
            else:
                stack.append(token.lower_)
        if best_ngram[2]==-1:
            continue
        if best_root_ngram[2]==-1 or best_root_ngram[2]==best_ngram[2]:
            FE=best_ngram[0]
        elif best_ngram[2]<best_root_ngram[2]:
            FE=best_ngram[0]+['*']+best_root_ngram[0]
        elif best_root_ngram[2]<best_ngram[2]:
            FE=best_root_ngram[0]+['*']+best_ngram[0]
        else:
            FE=None
        if FE is not None:
            FE=list_to_str(FE, language)
            if FE not in FEs:
                FEs[FE]=0
            FEs[FE]+=1
        debug[0]=j
        if i % 100==0:
            print("FE counting: {}/{}".format(debug[0], debug[1]), file=sys.stderr)
    for k in list(FEs.keys()):
        if FEs[k]<minimum_frequency:
            del FEs[k]
    return FEs
            
