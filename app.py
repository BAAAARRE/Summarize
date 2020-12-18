import streamlit as st
import pandas as pd
#import re
import plotly_express as px

# spacy for lemmatization
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
import stylecloud


########## Front-End ##########

def main():

# Set configs
    st.set_page_config(
	layout="centered",  # Can be "centered" or "wide". In the future also "dashboard", etc.
	initial_sidebar_state="collapsed",  # Can be "auto", "expanded", "collapsed"
	page_title='Text Summarize',  # String or None. Strings get appended with "• Streamlit". 
	page_icon=None,  # String, anything supported by st.image, or None.
    )
    
    st.title('Bienvenue sur Text Summarize ! 📖')
    
    st.write('\n')
    st.header('Présentation : ')
    st.write("Vous n'avez pas le temps ou tout simplement la flemme de lire un texte ou un article? Cet algorithme vous permet de retenir l'essentiel d'un texte en un instant! Vous pouvez selectionner sur votre gauche, le nombre de phrases à retenir. Il vous affichera également un nuage de mot associé à votre texte. Ainsi que la fréquence des mots les plus récurrents!")
   
    st.write('\n')
    st.header('Insérez ici votre texte, puis appuyez sur Ctrl + Entrée')
    user_input = st.text_area("", '')

    nb_sent = st.sidebar.number_input('Nombre de phrases pour le résumé', format="%i", value=3)

    stop_words = all_stopwords('stop_words_french.txt', ['falloir','être','faire','produit'])
    summ, clean, word = final(user_input, stop_words, 30, nb_sent)

    if len(user_input) > 0:
        st.write('\n')
        st.header('Voici le résumé de votre texte :')
        st.write(summ)

        st.write('\n')
        st.header('Voici le nuage de mots de votre texte :')
        wrd_cld(clean)
        st.image('stylecloud.png')

        st.write('\n')
        st.header('Voici les mots les plus fréquents :')
        plot_top_words(word, 20)


# Bottom page
    st.write("\n") 
    st.write("\n")
    st.info("""By : Ligue des Datas [Instagram](https://www.instagram.com/ligueddatas/) / [Twitter](https://twitter.com/ligueddatas)""")



########## Nettoyage des données ##########

@st.cache
def all_stopwords(filename, adds):
    stopwords = pd.read_csv(filename, header=None)
    stopwords = stopwords.values.tolist()
    final_stop_words = [item for sublist in stopwords for item in sublist]
    final_stop_words.extend(adds)
    return final_stop_words

def clean_basic(file_data):
    text = file_data
    # replace reference number with empty space, if any..
    #text = re.sub(r'\[[0-9]*\]',' ',text) 
    # replace one or more spaces with single space
    #text = re.sub(r'\s+',' ',text)
    return text

def clean_final(text, stop_words):
    # convert all uppercase characters into lowercase characters
    clean_text = text.lower()
    # replace characters other than [a-zA-Z0-9], digits & one or more spaces with single space
    #regex_patterns = [r'\W',r'\d',r'\s+']
    #for regex in regex_patterns:
    #    clean_text = re.sub(regex,' ',clean_text)
    text_tokens = word_tokenize(clean_text)
    tokens_without_sw = [word for word in text_tokens if not word in stop_words]
    clean_text = ' '.join(tokens_without_sw)
    return clean_text

def tokenize(text):
    sentences = nltk.sent_tokenize(text)
    return sentences

def word_count(clean_text, stop_words):
    # create an empty dictionary to house the word count
    word_count = {}
    # loop through tokenized words, remove stop words and save word count to dictionary
    for word in nltk.word_tokenize(clean_text):
        # remove stop words
        if word not in stop_words:
            # save word count to dictionary
            if word not in word_count.keys():
                word_count[word] = 1
            else:
                word_count[word] += 1
    return word_count

def score(sentences, word_count, sen_size):
    # create empty dictionary to house sentence score    
    sentence_score = {}
    # loop through tokenized sentence, only take sentences that have less than 30 words, then add word score to form sentence score
    for sentence in sentences:
        # check if word in sentence is in word_count dictionary
        for word in nltk.word_tokenize(sentence.lower()):
            if word in word_count.keys():
                # only take sentence that has less than 30 words
                if len(sentence.split(' ')) < sen_size:
                    # add word score to sentence score
                    if sentence not in sentence_score.keys():
                        sentence_score[sentence] = word_count[word]
                    else:
                        sentence_score[sentence] += word_count[word]
    return sentence_score

def nlargest(n, iterable, key=None):
    """Find the n largest elements in a dataset.
    Equivalent to:  sorted(iterable, key=key, reverse=True)[:n]
    """

    # Short-cut for n==1 is to use max()
    if n == 1:
        it = iter(iterable)
        sentinel = object()
        result = max(it, default=sentinel, key=key)
        return [] if result is sentinel else [result]

    # When n>=size, it's faster to use sorted()
    try:
        size = len(iterable)
    except (TypeError, AttributeError):
        pass
    else:
        if n >= size:
            return sorted(iterable, key=key, reverse=True)[:n]

    # When key is none, use simpler decoration
    if key is None:
        it = iter(iterable)
        result = [(elem, i) for i, elem in zip(range(0, -n, -1), it)]
        if not result:
            return result
        heapify(result)
        top = result[0][0]
        order = -n
        _heapreplace = heapreplace
        for elem in it:
            if top < elem:
                _heapreplace(result, (elem, order))
                top, _order = result[0]
                order -= 1
        result.sort(reverse=True)
        return [elem for (elem, order) in result]

    # General case, slowest method
    it = iter(iterable)
    result = [(key(elem), i, elem) for i, elem in zip(range(0, -n, -1), it)]
    if not result:
        return result
    heapify(result)
    top = result[0][0]
    order = -n
    _heapreplace = heapreplace
    for elem in it:
        k = key(elem)
        if top < k:
            _heapreplace(result, (k, order, elem))
            top, _order, _elem = result[0]
            order -= 1
    result.sort(reverse=True)
    return [elem for (k, order, elem) in result]

# If available, use C implementation
try:
    from _heapq import *
except ImportError:
    pass
try:
    from _heapq import _heapreplace_max
except ImportError:
    pass
try:
    from _heapq import _heapify_max
except ImportError:
    pass
try:
    from _heapq import _heappop_max
except ImportError:
    pass

def summarize(sentences,sentence_score, nb_sen):
    # display the best 3 sentences for summary             
    best_sentences = nlargest(nb_sen, sentence_score, key=sentence_score.get)
    # display top sentences based on their sentence sequence in the original text
    best_sum = []
    for sentence in sentences:
        if sentence in best_sentences:
            best_sum.append(sentence)
    sum_txt = '\n'.join(best_sum)
    return sum_txt
            


def final(txt, stop_words, sen_size, nb_sen):
    text = clean_basic(txt)
    clean_text = clean_final(text, stop_words)
    sentences = tokenize(text)
    word_cnt = word_count(clean_text, stop_words)
    sco = score(sentences, word_cnt, sen_size)
    summ = summarize(sentences, sco, nb_sen)
    return summ, clean_text, word_cnt


########## Visualisation ##########

def wrd_cld(texte):
    stylecloud.gen_stylecloud(text = texte,
                          icon_name='fas fa-file',
                          #palette='colorbrewer.diverging.Spectral_11',
                          background_color='white',
                          gradient='horizontal'
                         ) 

# helper function for plotting the top words.
def plot_top_words(word_count_dict, top):
    word_count_table = pd.DataFrame.from_dict(word_count_dict, orient = 'index').rename(columns={0: 'score'}).reset_index()
    data = word_count_table.sort_values('score').iloc[-top:]
    data.columns = ['Mot', 'Fréquence']
    fig = px.bar(data, x='Fréquence', y='Mot', orientation='h')
    st.write(fig)

if __name__ == "__main__":
    main()
