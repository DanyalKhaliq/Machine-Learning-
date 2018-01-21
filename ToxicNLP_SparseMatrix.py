# -*- coding: utf-8 -*-
"""
Created on Tue Dec 26 21:38:58 2017

@author: Danyal
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MaxAbsScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
    #for regex

import warnings
warnings.filterwarnings('ignore')


train_df = pd.read_csv('D:\\Kaggle\\ToxicWiki\\train.csv\\train.csv')
test_df = pd.read_csv('D:\\Kaggle\\ToxicWiki\\test.csv\\test.csv')
subm = pd.read_csv('D:\\Kaggle\\ToxicWiki\\sample_submission.csv\\sample_submission.csv')

nrow_train = train_df.shape[0]

cols_target = ['obscene','insult','toxic','severe_toxic','identity_hate','threat']
print(train_df[cols_target].sum())
test_df.fillna('unknown',inplace=True)


#marking comments without any tags as "clean"
rowsums=train_df.iloc[:,2:].sum(axis=1)
x=rowsums.value_counts()
train_df['clean']=(rowsums==0)
#count number of clean entries
train_df['clean'].sum()

print("Total comments = ",len(train_df))
print("Total clean comments = ",train_df['clean'].sum())
print("Total tags =",x.sum())

#%%
arrBad = [
'2g1c',
'2 girls 1 cup',
'acrotomophilia',
'anal',
'anilingus',
'anus',
'arsehole',
'ass',
'asshole',
'assmunch',
'auto erotic',
'autoerotic',
'babeland',
'baby batter',
'ball gag',
'ball gravy',
'ball kicking',
'ball licking',
'ball sack',
'ball sucking',
'bangbros',
'bareback',
'barely legal',
'barenaked',
'bastardo',
'bastinado',
'bbw',
'blood',
'bloody',
'badass'
'bdsm',
'beaver cleaver',
'beaver lips',
'bestiality',
'bi curious',
'big black',
'big breasts',
'big knockers',
'big tits',
'bimbos',
'birdlock',
'bitch',
'black cock',
'blonde action',
'blonde on blonde action',
'blow j',
'blow your l',
'blue waffle',
'blumpkin',
'bollocks',
'bondage',
'boner',
'boob',
'boobs',
'booty call',
'brown showers',
'brunette action',
'bukkake',
'bulldyke',
'bullet vibe',
'bung hole',
'bunghole',
'busty',
'butt',
'buttcheeks',
'butthole',
'camel toe',
'camgirl',
'camslut',
'camwhore',
'carpet muncher',
'carpetmuncher',
'chocolate rosebuds',
'circlejerk',
'cleveland steamer',
'clit',
'clitoris',
'clover clamps',
'clusterfuck',
'cock',
'cocks',
'coprolagnia',
'coprophilia',
'cornhole',
'cum',
'cumming',
'cunnilingus',
'cunt',
'darkie',
'date rape',
'daterape',
'deep throat',
'deepthroat',
'dick',
'dildo',
'dirty pillows',
'dirty sanchez',
'dog style',
'doggie style',
'doggiestyle',
'doggy style',
'doggystyle',
'dolcett',
'domination',
'dominatrix',
'dommes',
'donkey punch',
'double dong',
'double penetration',
'dp action',
'eat my ass',
'ecchi',
'ejaculation',
'erotic',
'erotism',
'escort',
'ethical slut',
'eunuch',
'faggot',
'fecal',
'felch',
'fellatio',
'feltch',
'female squirting',
'femdom',
'figging',
'fingering',
'fisting',
'foot fetish',
'footjob',
'frotting',
'fuck',
'fucking',
'fuck buttons',
'fudge packer',
'fudgepacker',
'futanari',
'g-spot',
'gang bang',
'gay sex',
'genitals',
'giant cock',
'girl on',
'girl on top',
'girls gone wild',
'goatcx',
'goatse',
'gokkun',
'golden shower',
'goo girl',
'goodpoop',
'goregasm',
'grope',
'group sex',
'guro',
'hand job',
'handjob',
'hard core',
'hardcore',
'hentai',
'homoerotic',
'honkey',
'hooker',
'hot chick',
'how to kill',
'how to murder',
'huge fat',
'humping',
'incest',
'intercourse',
'jack off',
'jail bait',
'jailbait',
'jerk off',
'jigaboo',
'jiggaboo',
'jiggerboo',
'jizz',
'juggs',
'kike',
'kinbaku',
'kinkster',
'kinky',
'knobbing',
'kiss',
'kiss off',
'leather restraint',
'leather straight jacket',
'lemon party',
'lolita',
'lovemaking',
'make me come',
'male squirting',
'masturbate',
'menage a trois',
'milf',
'missionary position',
'motherfucker',
'mound of venus',
'mr hands',
'muff diver',
'muffdiving',
'nambla',
'nonsense?',
'nawashi',
'negro',
'neonazi',
'nig nog',
'nigga',
'nigger',
'nimphomania',
'nipple',
'nipples',
'nsfw images',
'nude',
'nudity',
'nympho',
'nymphomania',
'octopussy',
'omorashi',
'one cup two girls',
'one guy one jar',
'orgasm',
'orgy',
'paedophile',
'panties',
'panty',
'pedobear',
'pedophile',
'pegging',
'penis',
'phone sex',
'piece of shit',
'piss pig',
'pissing',
'pisspig',
'playboy',
'pleasure chest',
'pole smoker',
'ponyplay',
'poof',
'poop chute',
'poopchute',
'porn',
'porno',
'pornography',
'prince albert piercing',
'pthc',
'pubes',
'pussy',
'queaf',
'raghead',
'raging boner',
'rape',
'raping',
'rapist',
'rectum',
'reverse cowgirl',
'rimjob',
'rimming',
'rosy palm',
'rosy palm and her 5 sisters',
'rusty trombone',
's&m',
'sadism',
'scat',
'schlong',
'scissoring',
'semen',
'sex',
'sexo',
'sexy',
'shaved beaver',
'shaved pussy',
'shemale',
'shibari',
'shit',
'shota',
'shrimping',
'slanteye',
'slut',
'smut',
'snatch',
'snowballing',
'sodomize',
'sodomy',
'spic',
'spooge',
'spread legs',
'strap on',
'strapon',
'strappado',
'strip club',
'style doggy',
'suck',
'sucks',
'suicide girls',
'sultry women',
'swastika',
'swinger',
'tainted love',
'taste my',
'tea bagging',
'threesome',
'throating',
'tied up',
'tight white',
'tit',
'tits',
'titties',
'titty',
'tongue in a',
'topless',
'tosser',
'towelhead',
'tranny',
'tribadism',
'tub girl',
'tubgirl',
'tushy',
'twat',
'twink',
'twinkie',
'two girls one cup',
'undressing',
'upskirt',
'urethra play',
'urophilia',
'vagina',
'venus mound',
'vibrator',
'violet blue',
'violet wand',
'vorarephilia',
'voyeur',
'vulva',
'wank',
'wet dream',
'wetback',
'white power',
'women rapping',
'wrapping men',
'wrinkled starfish',
'xx',
'xxx',
'yaoi',
'yellow showers',
'yiffy',
'zoophilia']


#%%
import re
merge=pd.concat([train_df.iloc[:,0:2],test_df.iloc[:,0:2]])
df=merge.reset_index(drop=True)
#Sentense count in each comment:
df['count_sent']=df["comment_text"].apply(lambda x: len(re.findall("\n",str(x)))+1)
#Unique word count
df['count_unique_word']=df["comment_text"].apply(lambda x: len(set(str(x).split())))
#upper case words count
df["count_words_upper"] = df["comment_text"].apply(lambda x: len([w for w in str(x).split() if w.isupper()]))

df["count_toxic_words"] = df["comment_text"].apply(lambda x: len([w for w in x.lower().split() if w in arrBad]))

train_feats=df.iloc[0:len(train_df),]
test_feats=df.iloc[len(train_df):,]

#join the tags back again
train_tags=train_df.iloc[:,2:]
train_feats=pd.concat([train_feats,train_tags],axis=1)
#check
train_feats.head(2)

##any(word in df[1:3]["comment_text"].str.lower().to_string() for word in arrBad)
#%%
import nltk

stop_re = '\\b'+'\\b|\\b'.join(nltk.corpus.stopwords.words('english'))+'\\b'

vectorizer = TfidfVectorizer(analyzer='char', stop_words='english', max_features=25000, ngram_range=(1,2),min_df=2)

df['comment_text'] = df['comment_text'].str.replace('[^a-zA-Z]',' ').str.lower()
df['comment_text'] = df['comment_text'].str.replace(stop_re, '')

data = vectorizer.fit_transform(df['comment_text'])

df['comment_text'].head(10)

XX = MaxAbsScaler().fit_transform(data)

from scipy import sparse
train_csr = train_feats.iloc[:,2:6].replace(0, np.nan).to_sparse()
train_csr = sparse.csr_matrix(train_csr.to_coo())

test_csr = test_feats.iloc[:,2:6].replace(0, np.nan).to_sparse()
test_csr = sparse.csr_matrix(test_csr.to_coo())

#%%
#Normalization
from sklearn import preprocessing
train_csr = preprocessing.scale(train_csr,with_mean=False)

test_csr = preprocessing.scale(test_csr,with_mean=False)

#%% sparse matrix creation
import scipy.sparse as sp
X = sp.hstack((train_csr,XX[:nrow_train]))
X = sparse.csr_matrix(X)


Y = sp.hstack((test_csr,XX[nrow_train:]))
Y = sparse.csr_matrix(Y)

#%%
col = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']

preds = np.zeros((test_df.shape[0], len(col)))

loss = []

for i, j in enumerate(col):
    print('===Fit '+j)
    model = LogisticRegression(penalty='l2',C=9)
    #model.fit(train_feats.iloc[:,2:6], train_df[j])
    model.fit( X[:nrow_train], train_df[j])
    
    preds[:,i] = model.predict_proba(Y)[:,1]
    
    pred_train = model.predict_proba(X[:nrow_train])[:,1]
    print('log loss:', log_loss(train_df[j], pred_train))
    loss.append(log_loss(train_df[j], pred_train))
    
print('mean column-wise log loss:', np.mean(loss))

#%%
submid = pd.DataFrame({'id': subm["id"]})
submission = pd.concat([submid, pd.DataFrame(preds, columns = col)], axis=1)
submission.to_csv('D:\\Kaggle\\ToxicWiki\\submission.csv', index=False)


#%%
#Visualization Part

import seaborn as sns
from scipy import stats, integrate
df_plt = pd.concat([df[:nrow_train],train_df['clean']],axis=1)
#Get Max Value of the specified Column with row data
y_axis_max = df.loc[df['count_toxic_words'].idxmax()]['count_toxic_words']

sns.set_style("whitegrid")
#ax = sns.boxplot(x="clean", y="count_toxic_words", data=df_plt)
ax = sns.distplot(df_plt['count_toxic_words'],bins=5);
#ax.set(ylim=(0, 10),xlim=(0,10))
