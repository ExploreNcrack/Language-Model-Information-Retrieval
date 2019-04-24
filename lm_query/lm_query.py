#!/usr/bin/python3 
# set your own path

# execute the program by:
# python3 lm_query.py [path] [k] [y/n] [list of keywords]
"""
Goal of this program:
Implement and document programs in your favourite programming language to 
score documents with respect to a keyword query, 
read from the command line, using a language model as described in Chapter 12 of the textbook.

Language model used: Maximum Likelyhood Estimation(MLE) with unigram assumption(each term occurance is independent from each other)
p_hat(Given document model M_d, the probability of query generate) = product of each probability of each query term generate given the document language model  
p_hat(Given document model M_d, the probability of query term generate) = (term frequency of the query term in the document)/(document Length)

Smoothing: use +1 for each if query term does not appear in the document 
(this way it will avoid 0 probability if one of the term does not appear in the document)
"""
import os
import SQLite3database
import sys
import math

def checkIfTableNeedExist(database, cursor, tableNameList):
	"""
	Input: the connected database 
	this function will check if the tables that is needed for this program exists or not
	if yes:
		return 1
	if no: 
		return -1
	"""
	for tableName in tableNameList:
		cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;",(tableName,))
		results = cursor.fetchall()
		if len(results) == 0:
			return False
	return True


def cleanText(text, tokenization, normalization):
	"""
	Input: string of text
	Return: a list of term/vocabulary after tokenization and normalization 
	"""
	# perform tokenization
	tokens = tokenization.tokenize(text)
	# perform normalization
	tokens = normalization.lemmatize(tokens)
	# get rid of non-meaningful character after tokenization
	tokens = tokenization.getRidPuncuation(tokens)
	# get rid of stop word
	tokens = tokenization.getRidStopWord(tokens)
	return tokens


def checkInput():
	"""
	This program should take following inputs
	- a path to the index file (or directory, depending on your design), 
	- k (the maximum number of answers), 
	- [y/n] indicating whether to print the scores, 
	- followed by a list of keywords.
	"""
	if len(sys.argv) != 5:
		# number of argument is not correct
		print("Four arguments are needed:")
		print("1. a path to the index file")
		print("2. k (the maximum number of answers)")
		print("3. [y/n] indicating whether to print the scores")
		print("4. followed by a list of keywords")
		print('python3 lm_query.py [path] [k] [y/n] "[whitespace-separated multi-term query]"')
		sys.exit(-1)
	indexFilePath = sys.argv[1]
	k = sys.argv[2]
	printScore = sys.argv[3]
	queryTermString = sys.argv[4]
	if not os.path.isfile(indexFilePath):
		# check if the training json file exists
		print("The given index file path is invalid")
		sys.exit(-1)
	try:
		# check input k
		k = int(k)
	except:
		print("The given k(the maximum number of answers) is invalid")
		sys.exit(-1)
	if printScore.lower() != 'y' and printScore.lower() != 'n':
		# check y/n
		print("Third argument has to be either y or n.")
		sys.exit(-1)
	return indexFilePath,k,printScore,queryTermString


def ComputeProbabilityGeneratingQueryTerms(queryTermsList, cursor, k):
	"""
	This function will compute the probability of generating query term using unigram MLE
	Input: query term list, index database, k
	Return: a list of Top k document rank by probability
	"""
	cursor.execute("SELECT * FROM document;")
	documentList = cursor.fetchall()
	documentLanguageModelProbability = []
	for document in documentList:
		# For each document language model, compute the probability 
		# First get all the information of the term appear in this document
		queryTermInfo = {}
		queryTermInDocument = []
		documentID = document[0]
		add1times = 0  # this records the number of times add 1 to the other query term that is actually in the document
		for term in queryTermsList:
			cursor.execute("SELECT frequency FROM termFrequency WHERE docID=? and word=?;",(documentID,term,))
			tf = cursor.fetchall()
			if len(tf) == 0:
				# If the query term not appear in the document
				queryTermInfo[term] = 0.0001
				add1times += 1
			else:
				# If the query term appear in the document
				queryTermInfo[term] = tf[0][0]
				queryTermInDocument.append(term)
		for term in queryTermInDocument:
			queryTermInfo[term] += add1times * 0.0001
		totalLength = (document[2]+add1times)*0.0001+document[2]
		probability = 1
		for term,frequency in queryTermInfo.items():
			if frequency < 1:
				probability = probability * (frequency/math.log(totalLength))	
			else:
				probability = probability * (frequency/totalLength)
		documentLanguageModelProbability.append([document[1],probability])

	documentLanguageModelProbability.sort(key=lambda x:x[1],reverse=True)
	return documentLanguageModelProbability[:k]



def checkTermInDocument(term, cursor, documentID):
	cursor.execute("SELECT * FROM termFrequency WHERE docID=? and term=?;",(documentID,term,))
	if len(cursor.fetchall()) == 0:
		return False
	return True

def main():
	# First of all check the user input
	indexFilePath,k,printScore,queryTermString = checkInput()
	# open the database file that is given
	indexDatabase = SQLite3database.Database(sys.argv[1]) #This also handle file error
	# cursor
	cursor = indexDatabase.getCursor()
	# check if the tables needed exists in the index storage file
	tablesNeeded = ["dictionary", "document", "termPosition", "documentFrequency", "termFrequency"]
	if checkIfTableNeedExist(indexDatabase, cursor, tablesNeeded) == False:
		print("The given index storage file does not contain the required Tables.")
		indexDatabase.close()
		return
	# last check for k
	cursor.execute("SELECT COUNT(*) FROM document;")
	NumberOfDocument = cursor.fetchall()[0][0]
	if k > int(NumberOfDocument):
		print("The second argument k is larger than the number of document in the input collection.")
		print("Arugmnet k should be less or equal to: %d"%(int(NumberOfDocument)))
		indexDatabase.close()
		sys.exit(-1)

	##################################################################################################################################

	"""
	At this point, all input should be all validated,
	and database file has opened,
	The database file has all the information represent the each document language model
	-tf (term frequency) in each of the document
	-document length for each document
	and along with some other extra information
	"""
	
	# First of all, do text processing(clean text) on the query term
	# (The same way that is done to the input data document terms)
	import Normalization 
	import Tokenization 

	normalization = Normalization.Normalizer()
	tokenization = Tokenization.Tokenizer()
	queryTermsList = cleanText(queryTermString, tokenization, normalization)
	print("Query Terms:")
	print(queryTermsList)
	# Perform the computation of probability of generating the query terms on the document model
	topKdocument = ComputeProbabilityGeneratingQueryTerms(queryTermsList, cursor, k)
	if printScore == "y":
		print(" %4s %63s"%("Document Name:","Query Likelyhood:"))
		for index,document in enumerate(topKdocument):
			print("%4d. %-60s"%(index+1,document[0]),end="")
			print(document[1])
	else:
		print(" %4s"%("Document Name:"))
		for index,document in enumerate(topKdocument):
			print("%4d. %-60s"%(index+1,document[0]))
	# close the database file after
	indexDatabase.close()


if __name__ == "__main__":
	main()