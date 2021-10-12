import streamlit as st
import pandas as pd
import string
from newspaper import Article
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
    st.write("Vous n'avez pas le temps ou tout simplement la flemme de lire un texte ou un article? Cet algorithme vous permet de retenir l'essentiel d'un texte en un instant! Il vous affichera également un nuage de mot associé à votre texte. Ainsi que la fréquence des mots les plus récurrents! Vous pouvez modifier quelques paramètres, en deployant l'onglet sur votre gauche.")
   
    st.write('\n')
    st.header('Selectionner le type de fichier')
    type_txt = st.radio('', ['Texte manuel', 'URL'])
    st.write('\n')

    if type_txt == 'Texte manuel':
        st.header('Insérez ici votre texte, puis appuyez sur Ctrl + Entrée')
        text = st.text_area("", '')
    else:
        st.header('Insérez ici votre url, puis appuyez sur Entrée')
        user_input = st.text_input("", '')
        if len(user_input) > 0:
            text = scrap_url(user_input)

# Sidebar
    st.sidebar.title('Résumé')
    nb_sent = st.sidebar.number_input('Nombre de phrases pour le résumé', format="%i", value=3)
    st.sidebar.title('Nuage de mots')
    max_cld = st.sidebar.number_input('Nombre de mots dans le nuage', format="%i", value=100)
    st.sidebar.title('Graphique')
    max_plt = st.sidebar.number_input('Nombre de mots dans le graphique', format="%i", value=10)

    stop_words_fr = all_stopwords('stop_words_french.txt', ['falloir','être','faire','produit'])
    stop_words_en = all_stopwords('stop_words_english.txt', ['be'])

    st.write('\n')
    st.header('Langue de votre texte :')
    stop = st.radio('', ['Français', 'Anglais'])
    if stop =='Français':
        stop_words = stop_words_fr
    else:
        stop_words = stop_words_en


    if len(text) > 0:

        summ, clean, word = final(text, stop_words, 30, nb_sent)

        st.write('\n')
        st.header('Voici le résumé de votre texte :')
        st.write(summ)
        #st.write(text)

        st.write('\n')
        st.header('Voici le nuage de mots de votre texte :')
        wrd_cld(clean, max_cld)
        st.image('stylecloud.png')

        st.write('\n')
        st.header('Voici les mots les plus fréquents :')
        plot_top_words(word, max_plt)

        st.write('\n')
        st.subheader('Prévention :')
        st.write("Cela ne reste qu'un simple algorithme. Il ne remplacera pas une lecture complète de votre texte, mais permet d'obtenir les idées essentielles.")


# Bottom page
    st.write("\n") 
    st.write("\n")
    st.info("""By : Ligue des Datas [Instagram](https://www.instagram.com/ligueddatas/) / [Twitter](https://twitter.com/ligueddatas)""")



########## Import des données ##########

def scrap_url(user_url_input):
    article = Article(user_url_input)
    article.download()
    article.parse()
    txt = article.text
    return txt

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
    text = text.replace(r'\[[0-9]*\]'," ")
    # replace one or more spaces with single space
    text = text.replace(r'\s+'," ") 
    return text

def clean_final(text, stop_words):
    clean_text = text.lower()
    punc = string.punctuation + '«»“—”’'
    translator = str.maketrans(punc, ' '*len(punc)) #map punctuation to space
    clean_text = clean_text.translate(translator)
    clean_text = " ".join(clean_text.split())
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

def score(sentences, word_count, sen_size, nb_sen):
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
    df_sentence_score = pd.DataFrame.from_dict(sentence_score, orient = 'index').rename(columns={0: 'score'})
    df_sentence_score = df_sentence_score.sort_values(by='score', ascending = False).reset_index()
    summ = '      '.join(df_sentence_score.loc[0:nb_sen,'index'].to_list())
    return summ

def final(txt, stop_words, sen_size, nb_sen):
    text = clean_basic(txt)
    clean_text = clean_final(text, stop_words)
    sentences = tokenize(text)
    word_cnt = word_count(clean_text, stop_words)
    summ = score(sentences, word_cnt, sen_size, nb_sen-1)
    return summ, clean_text, word_cnt


########## Visualisation ##########

def wrd_cld(texte, max):
    stylecloud.gen_stylecloud(text = texte,
                          icon_name='fas fa-medkit',
                          #palette='colorbrewer.diverging.Spectral_11',
                          background_color='white',
                          gradient='horizontal',
                          max_words = max
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
