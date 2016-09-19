import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import sentiwordnet as swn
import re
from synonym_feature import main_feature
from score_feat_dict import feature_score
import MySQLdb
from review_rep_remove import remove_rep
from fetch_features import get_features
from pie_chat_plot import plotting_sentiment
NEGATION = r"""
    (?:
        ^(?:never|no|nothing|nowhere|noone|none|not|
            havent|hasnt|hadnt|cant|couldnt|shouldnt|
            wont|wouldnt|dont|doesnt|didnt|isnt|arent|aint
        )$
    )
    |

    n't"""
stopwords=['i\n', 'me\n', 'my\n', 'myself\n', 'we\n', 'our\n', 'ours\n', 'ourselves\n', 'you\n', 'your\n', 'yours\n', 'yourself\n', 'yourselves\n', 'he\n', 'him\n', 'his\n', 'himself\n', 'she\n', 'her\n', 'hers\n', 'herself\n', 'it\n', 'its\n', 'itself\n', 'they\n', 'them\n', 'their\n', 'theirs\n', 'themselves\n', 'what\n', 'which\n', 'who\n', 'whom\n', 'this\n', 'that\n', 'these\n', 'those\n', 'am\n', 'is\n', 'are\n', 'was\n', 'were\n', 'be\n', 'been\n', 'being\n', 'have\n', 'has\n', 'had\n', 'having\n', 'do\n', 'does\n', 'did\n', 'doing\n', 'a\n', 'an\n', 'the\n', 'and\n', 'but\n', 'if\n', 'or\n', 'because\n', 'as\n', 'until\n', 'while\n', 'of\n', 'at\n', 'by\n', 'for\n', 'with\n', 'about\n', 'against\n', 'between\n', 'into\n', 'through\n', 'during\n', 'before\n', 'after\n', 'above\n', 'below\n', 'to\n', 'from\n', 'up\n', 'down\n', 'in\n', 'out\n', 'on\n', 'off\n', 'over\n', 'under\n', 'again\n', 'further\n', 'then\n', 'once\n', 'here\n', 'there\n', 'when\n', 'where\n', 'why\n', 'how\n', 'all\n', 'any\n', 'both\n', 'each\n', 'few\n', 'more\n', 'most\n', 'other\n', 'some\n', 'such\n', 'no\n', 'nor\n', 'not\n', 'only\n', 'own\n', 'same\n', 'so\n', 'than\n', 'too\n', 'very\n', 's\n', 't\n', 'can\n', 'will\n', 'just\n', 'don\n', 'should\n', 'now\n', '\n']
NEGATION_RE = re.compile(NEGATION, re.VERBOSE)

CLAUSE_PUNCT = r'^[.:;!?]$'
CLAUSE_PUNCT_RE = re.compile(CLAUSE_PUNCT)

# Happy and sad emoticons

# HAPPY = set([
#     ':-)', ':)', ';)', ':o)', ':]', ':3', ':c)', ':>', '=]', '8)', '=)', ':}',
#     ':^)', ':-D', ':D', '8-D', '8D', 'x-D', 'xD', 'X-D', 'XD', '=-D', '=D',
#     '=-3', '=3', ':-))', ":'-)", ":')", ':*', ':^*', '>:P', ':-P', ':P', 'X-P',
#     'x-p', 'xp', 'XP', ':-p', ':p', '=p', ':-b', ':b', '>:)', '>;)', '>:-)',
#     '<3'
#     ])

# SAD = set([
#     ':L', ':-/', '>:/', ':S', '>:[', ':@', ':-(', ':[', ':-||', '=L', ':<',
#     ':-[', ':-<', '=\\', '=/', '>:(', ':(', '>.<', ":'-(", ":'(", ':\\', ':-c',
#     ':c', ':{', '>:\\', ';('
#     ])




#negation marking function 
def self_mark_negation(list_sen):
    
    punc = [".","?",","]
    flag = 0
    for i in xrange(len(list_sen)):
        if  NEGATION_RE.search(list_sen[i][0]):
            list_sen[i][1].append("neg_y")
            flag = 1
            continue
        elif list_sen[i][0] == "but" or list_sen[i][0] in punc:
            flag = 0
        elif flag == 1:

            list_sen[i][1].append("neg_y")
            
        else:
            list_sen[i][1].append("neg_n")
 

#Score calculation function
def polarity_cal(word):
    senti_synset = list(swn.senti_synsets(word))
    
    if senti_synset:
        
        if senti_synset[0].pos_score() == 0 and senti_synset[0].neg_score() == 0:
            return  [senti_synset[0].obj_score(),"pos"]
        elif senti_synset[0].pos_score() >= senti_synset[0].neg_score():
            return  [senti_synset[0].pos_score(),"pos"]
        elif senti_synset[0].obj_score() >= senti_synset[0].neg_score():
            return  [senti_synset[0].obj_score(),"pos"]
        
        else:
            return  [senti_synset[0].neg_score(),"neg"]

    else:
        return [0,"no"]
#three below fuction are tagger
class Splitter(object):
    def __init__(self):
        self.nltk_splitter = nltk.data.load('tokenizers/punkt/english.pickle')
        self.nltk_tokenizer = nltk.tokenize.TreebankWordTokenizer()

    def split(self, text):
        """
        input format: a paragraph of text
        output format: a list of lists of words.
            e.g.: [['this', 'is', 'a', 'sentence'], ['this', 'is', 'another', 'one']]
        """
        sentences = self.nltk_splitter.tokenize(text)
        tokenized_sentences = [self.nltk_tokenizer.tokenize(sent) for sent in sentences]
        return tokenized_sentences


class POSTagger(object):
    def __init__(self):
        pass
        
    def pos_tag(self, sentences):
        pos = [nltk.pos_tag(sentence) for sentence in sentences]
        #adapt format
        pos = [[(word, [postag]) for (word, postag) in sentence] for sentence in pos]
        return pos

def tagging(text):
    splitter = Splitter()
    postagger = POSTagger()

    splitted_sentences = splitter.split(text)

    
    
    pos_tagged_sentences = postagger.pos_tag(splitted_sentences)

    return pos_tagged_sentences


def list_req_pos(tagged_list):
    sentiment = ""
    tag_list = ["VBN","VB","VBP","VBS","VBG","VBD","VBZ","JJR","JJS","JJ","JJR"]
    adv_tag = ["RB","RBS","RBP"]
    

    adv_flag = 0
    sen_count = 0
    feature_list = []
    score_dict = {}
    # feature_sen_score={}
    for j in xrange(len(tagged_list)):
        sen_count+=1
        score =0
        self_mark_negation(tagged_list[j])
        for k in tagged_list[j]:
            
                    # if k[0] not in feature_sen_score:
                    #     feature_sen_score[k[0]]=[[tagged_list],[0]]
                    # else:
                    #     feature_sen_score.get(k[0])[0].append(tagged_list)
                    #     feature_sen_score.get(k[0])[1].append(0)
#increase the score of JJ/VB after countering an adverb
            if k[1][0] in adv_tag:
                adv_flag = 1
            elif k[1][0] in tag_list and k[0]+"\n" not in stopwords:
                if adv_flag == 1:
                    
                    
                    k[1].extend([polarity_cal(k[0])[0]*1.5,polarity_cal(k[0])[1]])
                    if k[1][3] == "pos" and k[1][1] == "neg_n":
                        score +=  k[1][2]
                    elif k[1][3] == "pos" and k[1][1] == "neg_y":
                        
                        score -=  k[1][2]
                    elif k[1][3] == "neg" and k[1][1] == "neg_y":
                        score +=  k[1][2]
                    else:
                        score -=  k[1][2]
                    adv_flag = 0
                else:

                    k[1].extend([polarity_cal(k[0])[0],polarity_cal(k[0])[1]])
                    if k[1][3] == "pos" and k[1][1] == "neg_n":
                        score +=  k[1][2]
                    elif k[1][3] == "pos" and k[1][1] == "neg_y":
                        score -=  k[1][2]
                    elif k[1][3] == "neg" and k[1][1] == "neg_y":
                        score +=  k[1][2]
                    else:
                        score -= k[1][2]
                    
            else:
                k[1].extend([0,"no"])
                score += 0
        if sen_count not in score_dict:
            score_dict[sen_count] = score
    sum1 =0
    for k,v in score_dict.iteritems():
        sum1 += v
    
    if sum1 >0:
        sentiment="positive"
    elif sum1==0:
        sentiment="neutral"
    else:
        sentiment="negative"
    # print tagged_list
    # print feature_list
    return sum1,sentiment
# def find_feature():
#     #find all the noun attributes
#     if 
# def overall_score(tagged_list):


def tagging_review_main(company_id,product_id):
    feature_dict = {}
    name_file = str(product_id)+str(company_id)+"reviews.txt"
    review_score_dict={}
    feature_sen_score={}
    main_tagged_list= [] 
    review_number=0
    feature_list =get_features(product_id)
    f=open(name_file,"w")
    db = MySQLdb.connect("localhost","root","ssdn","reviewprocessing" )

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Prepare SQL query to INSERT a record into the database.
    sql = "SELECT review FROM review WHERE company_id={}".format(company_id)
    try:
       # Execute the SQL command
        cursor.execute(sql)
       # Fetch all the rows in a list of lists.
        results = cursor.fetchall()
        for row in results:
            review = remove_rep(row[0])
            f.write(review+"\n")
            review_number+=1
            score = 0
            sentiment=""
            tagged_list_new = []
            splitted_sentence = review.split()
            tagged_list = tagging(review)
            
            #now  extracting  a list of verbs adjective and nouns of that sentence
            # print tagged_list
            score,sentiment= list_req_pos(tagged_list)
            # main_tagged_list+=tagged_list_new
            for j in tagged_list:
                f_list=[]
                for k in j:
                    
                    if k[1][0] in ['NN',"NNP","NNS"]:
                    # noun = k[0]+"\n"
                        if k[0]+"\n" not in stopwords:
                            # print k[0]
                            f_list.append(k[0])
                            f_list = list(set(f_list))
                for e in f_list :
                    if e in feature_list:           
                        if e not in feature_sen_score:
                            feature_sen_score[e]=[j]
                        else:
                            feature_sen_score.get(e).append(j)
                    else:
                        pass
            review_score_dict[review_number]=[score,sentiment]
    except:
    
       print "Error: unable to fecth data"

    # disconnect from server
    
    f.close()
    db.close()
    print review_score_dict
    # print main_tagged_list
    P_score=0
    N_score=0
    Neu_score=0
    for k,v in review_score_dict.iteritems():
        sentiment = review_score_dict.get(k)[1]
        if sentiment=="positive":
            P_score+=1
        elif sentiment=="negative":
            N_score+=1
        else:
            Neu_score+=1
    
    plotting_sentiment(P_score,N_score,Neu_score,"Main Product flipkart")
    feature_score(feature_sen_score,"flipkart")
    # feature_score(feature_sen_score)

        

    
    # feature_dict,feature_list = main_feature()
    # for i in splitted_sentence:

    #     if i in feature_list and i.lower() == "delivery":
    #         print i

            
    # print feature_dict


tagging_review_main(1,2)
