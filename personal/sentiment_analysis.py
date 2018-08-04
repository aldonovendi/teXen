import re, math, collections, itertools, os
import nltk, nltk.classify.util, nltk.metrics
from nltk.classify import NaiveBayesClassifier
from nltk.metrics import BigramAssocMeasures
from nltk.probability import FreqDist, ConditionalFreqDist
from nltk import precision, recall

module_dir = os.path.dirname(__file__)
POLARITY_DATA_DIR = os.path.join(module_dir, 'corpus')
RT_POLARITY_POS_FILE = os.path.join(POLARITY_DATA_DIR, 'positive.txt')
RT_POLARITY_NEG_FILE = os.path.join(POLARITY_DATA_DIR, 'negative.txt')
RT_POLARITY_NEU_FILE = os.path.join(POLARITY_DATA_DIR, 'neutral.txt')

#creates a feature selection mechanism that uses all words
def make_full_dict(words):
    return dict([(word, True) for word in words])

#this function takes a feature selection mechanism and returns its performance in a variety of metrics
def evaluate_features(sample, word_scores):
    posFeatures = []
    negFeatures = []
    neuFeatures = []
    sampleFeatures = []
    #http://stackoverflow.com/questions/367155/splitting-a-string-into-words-and-punctuation
    #breaks up the sentences into lists of individual words (as selected by the input mechanism) and appends 'pos' or 'neg' after each list
    with open(RT_POLARITY_POS_FILE, 'r') as posSentences:
        for i in posSentences:
            posWords = re.findall(r"[\w']+|[.,!?;]", i.rstrip())
            posWords = [make_full_dict(posWords), 'pos']
            posFeatures.append(posWords)
    with open(RT_POLARITY_NEG_FILE, 'r') as negSentences:
        for i in negSentences:
            negWords = re.findall(r"[\w']+|[.,!?;]", i.rstrip())
            negWords = [make_full_dict(negWords), 'neg']
            negFeatures.append(negWords)
    with open(RT_POLARITY_NEU_FILE, 'r') as negSentences:
        for i in negSentences:
            neuWords = re.findall(r"[\w']+|[.,!?;]", i.rstrip())
            neuWords = [make_full_dict(neuWords), 'neu']
            neuFeatures.append(neuWords)
    
    
    for s in sample:
        sampleWords = re.findall(r"[\w']+|[.,!?;]", s.rstrip())
        sampleWords = [make_full_dict(sampleWords), 'sample']
        sampleFeatures.append(sampleWords)
#        print(s)
    
#    print (sampleFeatures)
    
    #selects 3/4 of the features to be used for training and 1/4 to be used for testing
    posCutoff = int(math.floor(len(posFeatures)*3/4))
    negCutoff = int(math.floor(len(negFeatures)*3/4))
    neuCutoff = int(math.floor(len(neuFeatures)*3/4))
    trainFeatures = posFeatures[:posCutoff] + negFeatures[:negCutoff] + neuFeatures[:neuCutoff]
    testFeatures = posFeatures[posCutoff:] + negFeatures[negCutoff:] + neuFeatures[neuCutoff:]
    
#    print(testFeatures)

    #trains a Naive Bayes Classifier
#    finalTrainFeatures = trainFeatures + testFeatures
#    classifier = NaiveBayesClassifier.train(trainFeatures+testFeatures)    
    classifier = NaiveBayesClassifier.train(trainFeatures)    

    #initiates referenceSets and testSets
    referenceSets = collections.defaultdict(set)
    testSets = collections.defaultdict(set)    
    sampleSets = collections.defaultdict(set)
    
    #puts correctly labeled sentences in referenceSets and the predictively labeled version in testsets
    for i, (features, label) in enumerate(sampleFeatures):
        predicted = classifier.classify(features)
        print(features.keys(), '\n', predicted)
#        print(features.keys(), ' ' , predicted)
        sampleSets[predicted].add(i)    
    
    for i, (features, label) in enumerate(testFeatures):
        referenceSets[label].add(i)
        predicted = classifier.classify(features)
#        print(features.keys(), '\n', predicted)
    #        print(features.keys(), ' ' , predicted)
        testSets[predicted].add(i)  
    
#    print(testSets['pos'])
    #prints metrics to show how well the feature selection did
    print ('train on %d instances, test on %d instances' % (len(trainFeatures), len(testFeatures)))
    print ('accuracy:', nltk.classify.util.accuracy(classifier, testFeatures))
    print ('pos precision:', precision(referenceSets['pos'], testSets['pos']))
    print ('pos recall:', recall(referenceSets['pos'], testSets['pos']))
    print ('neg precision:', precision(referenceSets['neg'], testSets['neg']))
    print ('neg recall:', recall(referenceSets['neg'], testSets['neg']))
    classifier.show_most_informative_features(10)
#    return testSets
    
    return sampleSets



#scores words based on chi-squared test to show information gain (http://streamhacker.com/2010/06/16/text-classification-sentiment-analysis-eliminate-low-information-features/)
def create_word_scores():
    #creates lists of all positive and negative words
    posWords = []
    negWords = []
    
    with open(RT_POLARITY_POS_FILE, 'r') as posSentences:
        for i in posSentences:
            posWord = re.findall(r"[\w']+|[.,!?;]", i.rstrip())
            posWords.append(posWord)    
    with open(RT_POLARITY_NEG_FILE, 'r') as negSentences:
        for i in negSentences:
            negWord = re.findall(r"[\w']+|[.,!?;]", i.rstrip())
            negWords.append(negWord)
    
    posWords = list(itertools.chain(*posWords))
    negWords = list(itertools.chain(*negWords))
            
    #build frequency distibution of all words and then frequency distributions of words within positive and negative labels
    word_fd = FreqDist()
   
    cond_word_fd = ConditionalFreqDist()
    for word in posWords:
        word_fd[word.lower()] += 1
        cond_word_fd['pos'][word.lower()] += 1
    for word in negWords:
        word_fd[word.lower()] += 1
        cond_word_fd['neg'][word.lower()] += 1
#    print(cond_word_fd['pos']['ugly'],'\n',cond_word_fd['neg']['ugly'],'\n',word_fd['ugly'])
#    print(cond_word_fd['pos']['ugly']/word_fd['ugly'])
#    print(cond_word_fd['neg']['ugly']/word_fd['ugly'])
    #finds the number of positive and negative words, as well as the total number of words
    pos_word_count = cond_word_fd['pos'].N()
    neg_word_count = cond_word_fd['neg'].N()
    total_word_count = pos_word_count + neg_word_count
    
    return cond_word_fd
    
    #builds dictionary of word scores based on chi-squared test
#    word_scores = {}
    
    """
    for word, freq in word_fd.items():
        pos_score = BigramAssocMeasures.chi_sq(cond_word_fd['pos'][word], (freq, pos_word_count), total_word_count)
        neg_score = BigramAssocMeasures.chi_sq(cond_word_fd['neg'][word], (freq, neg_word_count), total_word_count)
        word_scores[word] = pos_score + neg_score
    """
#    return pos_score, neg_score

#tries using all words as the feature selection mechanism
print ('using all words as features')
#word_scores = create_word_scores()
#evaluate_features(word_scores)
##finds word scores
#
#print(pos_scores['pos'].N())

"""
#finds the best 'number' words based on word scores
def find_best_words(word_scores, number):
    best_vals = sorted(word_scores, key=lambda w, s : s, reverse=True)[:number]
    best_words = set([w for w, s in best_vals])
    return best_words

#creates feature selection mechanism that only uses best words
def best_word_features(words):
    return dict([(word, True) for word in words if word in best_words])

#numbers of features to select
numbers_to_test = [10, 100, 1000, 10000, 15000]
#tries the best_word_features mechanism with each of the numbers_to_test of features
for num in numbers_to_test:
    print ('evaluating best %d word features' % (num))
    best_words = find_best_words(word_scores, num)
    evaluate_features(best_word_features)
"""