import sys

import spacy

def create_ngrams(list_words, minimum_length=4, maximum_length=10):
    ngrams=[]
    if len(list_words)>=minimum_length:
        for start in range(0, len(list_words)-minimum_length+1):
            for length in range(minimum_length, len(list_words)-start+1):
                if length>maximum_length:
                    break
                ngrams.append((list_words[start:start+length], (start, start+length)))
    return ngrams

def acceptable(candidates, frequency, minimum=3):
    maximum=(([], (-1, -1)), 0)
    for candidate in sorted(candidates, reverse=True, key=lambda x: len(x[0])):
        key=list_to_str(candidate[0])
        if key not in frequency:
            #sys.stderr("{} was not found in ngrams.".format(key))
            continue
        if len(maximum[0][0]) > len(candidate[0]):
            break
        if frequency[key]>=minimum and frequency[key]>maximum[1]:
            maximum=(candidate, frequency[key])
    if maximum[0]==[]:
        return (None, (-1, -1))
    return maximum[0]

def list_to_str(l, lang='default'):
    sep=''
    if lang in ['ja']:
        sep=''
    elif lang in ['default', 'fi']:
        sep=' '
    return sep.join(l)

def extract_FEs(sentences, language, minimum_frequency=3):
    languages={'ja': 'ja_core_news_lg', 'fi': '../train_spacy/fi-ner/model-last/'}
    nlp=spacy.load(languages[language])
    ngrams_per_sentence=[]
    ngrams_root_per_sentence=[]
    ngrams={}
    debug=[0, len(sentences)]
    for sentence in sentences:
        doc=nlp(sentence)
        sentence_ngram=[]
        sentence_ngram_root=[]
        root_flag=False
        ngram_stack=[]
        for token in doc:
            if token.dep_=='ROOT':
                root_flag=True
            if token.dep_=='punct':
                continue
            if token.ent_iob_!='O':
                if len(ngram_stack)!=0:
                    if language=='ja':
                        ngram_combination=create_ngrams(ngram_stack, 5) # [([ngram], (start, start+length))]
                    else:
                        ngram_combination=create_ngrams(ngram_stack) # [([ngram], (start, start+length))]
                    for ngram, pos in ngram_combination:
                        ngram=list_to_str(ngram)
                        if ngram not in ngrams:
                            ngrams[ngram]=0
                        ngrams[ngram]+=1
                    if root_flag:
                        sentence_ngram_root.extend(ngram_combination)
                    sentence_ngram.extend(ngram_combination)
                    ngram_stack=[]
                root_flag=False
                continue
            if language in ['ja']:
                ngram_stack.append(token.text)
            else:
                ngram_stack.append(token.lower_)
        if len(ngram_stack)!=0:
            ngram_combination=create_ngrams(ngram_stack)
            for ngram, pos in ngram_combination:
                ngram=list_to_str(ngram)
                if ngram not in ngrams:
                    ngrams[ngram]=0
                ngrams[ngram]+=1
                if root_flag:
                    sentence_ngram_root.extend(ngram_combination)
                sentence_ngram.extend(ngram_combination)
        ngrams_per_sentence.append(sentence_ngram)
        ngrams_root_per_sentence.append(sentence_ngram_root)
        debug[0]+=1
        print("{}/{}".format(debug[0], debug[1]), file=sys.stderr)
    FEs={}
    debug=[0, len(ngrams_per_sentence)]
    for i, sentence_ngram in enumerate(ngrams_per_sentence):
        sentence_root_ngram=ngrams_root_per_sentence[i] # [ngram, (start, start+length)]
        longest_FE, pos0=acceptable(sentence_ngram, ngrams)
        longest_FE_root, pos1=acceptable(sentence_root_ngram, ngrams)
        if longest_FE is None:
            continue
        FE=None
        if longest_FE_root is None:
            FE=longest_FE
        else:
            if longest_FE==longest_FE_root:
                FE=longest_FE
            elif pos0[1]==pos1[0]:
                FE=longest_FE+longest_FE_root
            elif pos1[1]==pos0[0]:
                FE=longest_FE_root+longest_FE
            elif pos0[0]<pos1[0]:
                FE=longest_FE+['*']+longest_FE_root
            else:
                FE=longest_FE_root+['*']+longest_FE
        FE=list_to_str(FE, language)
        if FE not in FEs:
            FEs[FE]=0
        FEs[FE]+=1
        debug[0]=i
        print("{}/{}".format(debug[0], debug[1]), file=sys.stderr)
    for k in list(FEs.keys()):
        if FEs[k]<minimum_frequency:
            del FEs[k]
    return FEs
            
