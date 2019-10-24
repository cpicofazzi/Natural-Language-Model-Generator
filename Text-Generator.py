
############################################################
# CMPSC 442: Homework 6
############################################################

student_name = "Christian Picofazzi"

############################################################
# Imports
############################################################

# Include your imports here, if any are used.

import string
import collections
import random
import time
import math
import os

############################################################
# Section 1: Markov Models
############################################################

def tokenize(text):
    
    tokenList= []
    word = ""
    count = 0
    text = text.strip()
    size = len(text)-1
    #print(text)
    for char in text:
        #print(char)
        #whitespace
        if char is " " or char is '':
            if word is not " " and word is not "":
                tokenList.append(word)
            word = ""
        #punctuation
        elif char in string.punctuation:
            if word is not "" and word is not " ":
                tokenList.append(word)
            word = char
            tokenList.append(word)
            word = ""
        #everything else
        else:
            word += char
            if count is size:
               tokenList.append(word) 
        count+=1
        #print(count)
            

       
        #print("TOKEN LIST",tokenList)
    return tokenList
        

def ngrams(n, tokens):
    start = "<START>"
    end = "<END>"
    listNGrams = []
    leftTuple = []
    
    #INITIAL WITH STARTS
    for i in range(n-1):
        leftTuple.append(start)
        
    listNGrams.append((tuple(leftTuple), tokens[0]))

    tokens = [start] + tokens + [end]
    #print(tokens)
    if n != 1:
        leftTuple.pop(0)
        leftTuple.append(tokens[0])
    for i in range(2,len(tokens)):
        if n != 1:
            leftTuple.pop(0)
            leftTuple.append(tokens[i-1])
        listNGrams.append((tuple(leftTuple), tokens[i]))
        
    #print("NGRAMS lIST ",listNGrams)
    return listNGrams

class NgramModel(object):

    def __init__(self, n):
        self.n = n
        self.ngrams=[]
        self.tokens=[]
        self.counts = collections.Counter()
        self.startingContext = ()
        self.totalCount = 0
        self.oneNtokens = []
    def update(self, sentence):
       # s=time.time()
        tokens = tokenize(sentence)
       # e=time.time()
        #print("Tokenize %.20f"%float(e-s))
       # j=time.time()
        nGrams = ngrams(self.n,tokens)
        #f=time.time()
        self.totalCount += len(nGrams)
        #print("NGrams %.20f"%float(f-j))
        if self.startingContext is () and self.n is not 1:
            self.startingContext = nGrams[0][0] 
        #print(self.ngrams)
    
        #g = time.time()
        for i in range(len(nGrams)):
            #print("        ",nGrams[i])
            self.counts[nGrams[i]]+= 1
        #t = time.time()
        #print("Updating %.20f"%float(t-g))        

    def prob(self, context, token):
        subset = collections.Counter()
        totalContext=0
        #need a set of all values with context 
        #print(self.counts)
        for cont in self.counts.keys():
            
            if cont[0] == context:
                #print("found")
                subset[cont] = self.counts[cont]
                totalContext += self.counts[cont]
       # print(subset,totalContext)
        if totalContext is 0:
            return 0.0

        #print(token,float(subset[(context,token)]) / float(totalContext) )
        return float(subset[(context,token)]) / float(totalContext)



    def random_token(self, context):
        #generate the set of tokens from the context
        subset = collections.Counter()
        totalContext=0
        tokenProbs = []
        #need a set of all values with context
        if not self.oneNtokens :
            #print("inside")
            for cont in self.counts.keys():
                if cont[0] == context:
                    #print("found")
                    subset[cont] = self.counts[cont]
                    totalContext += self.counts[cont]


        #make the set of each probabilty tuples with (prob i, ti) ordered by the prob
        #tokenProbs [(Tuple)]   :> Tuple =   (context, token, prob)

            for cont in subset.keys():
                if totalContext is 0:
                    prob = 0.0
                else:
                    prob = float(subset[cont]) / float(totalContext)
                tokenProbs.append(  [ cont[1], prob, 0    ]   )

            tokenProbs.sort(key = lambda x: x[0] )
            for i in range(len(tokenProbs)):
                for j in range(i+1):
                    tokenProbs[i][2] += tokenProbs[j][1]
            if self.n is 1:
                #print(tokenProbs)
                self.oneNtokens = tokenProbs

        else:
            tokenProbs = self.oneNtokens
            totalContext = self.totalCount

        #generate a random number r from 0<= r < 1
        r = random.random()
        #return a token with the probability of token i-1 <= r < probability of token i
        if not tokenProbs:
            #print("SUPER EMPTY LIST")
            return -1000000
        #print(r)
       # print(tokenProbs)
        if r < tokenProbs[0][2]:
            #print(tokenProbs[0][0])
            #print()
            return tokenProbs[0][0]
        for i in range(len(tokenProbs)):
            if tokenProbs[i-1][2] <= r and r < tokenProbs[i][2]:
                #print(tokenProbs[i][0])
                #print()
                return tokenProbs[i][0]
        
        #print("SUPER ERRRO CALCULATING")
        return -1000000

    def random_text(self, token_count):
        string = ""
        starting_context = list(self.startingContext)
       
        context_hist= starting_context
        #print(context_hist)
        
        #initialize the context

        for i in range(token_count):
            tok = self.random_token(tuple(context_hist))
            string += tok + " "
            if tok == "<END>":
                context_hist = list(self.startingContext)   
            else:
                if self.n is not 1:
                    context_hist.pop(0)
                    context_hist.append(tok)
                else:
                    context_hist = list(self.startingContext) 
        #print(string)
        return string.strip()
    
    def perplexity(self, sentence):
        tokens = tokenize(sentence)
        n_grams = ngrams(self.n, tokens)
        #print(len(n_grams))
        logProb = 0

        for gram in n_grams:
            
            probly = self.prob(gram[0],gram[1])
            #print(gram[0],gram[1], probly, float(1/float(len(n_grams))))
            logProb += math.log(1)- math.log(probly)
        regProb = math.e ** (logProb)
        
        perplex = math.pow(regProb, float(1/float(len(n_grams))))

        return perplex

def create_ngram_model(n, path):
   
    m = NgramModel(n)

    with open(path,'Ur') as myFile:
        for chunk in myFile:
            m.update(chunk)

    return m








############################################################
# Section 2: Feedback
############################################################

feedback_question_1 = """
15
"""

feedback_question_2 = """
Time efficiency was the most challenging
"""

feedback_question_3 = """
How I could see the how much better the different levels of n improved the program
"""
