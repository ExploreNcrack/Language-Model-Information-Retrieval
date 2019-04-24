#!/usr/bin/python3 
# Copyright 2019 Zhaozhen Liang
import sys
import os


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
	return tokens

def dropTable(database):
	SQL = """
		  DROP TABLE IF EXISTS dictionary;
		  DROP TABLE IF EXISTS documentFrequency;
		  DROP TABLE IF EXISTS document;
		  DROP TABLE IF EXISTS termPosition;
		  DROP TABLE IF EXISTS termFrequency;
		  """
	database.execute(SQL)
	database.commit()

def createBtreeIndex(database):
	SQL = """
	      CREATE INDEX IF NOT EXISTS btreeINDEX_dicWord ON dictionary(word);
	      CREATE INDEX IF NOT EXISTS btreeINDEX_dfWord ON documentFrequency(word);
	      CREATE INDEX IF NOT EXISTS btreeINDEX_docID ON document(id);
	      CREATE INDEX IF NOT EXISTS btreeINDEX_tpWord ON termPosition(word);
	      CREATE INDEX IF NOT EXISTS btreeINDEX_tpDocID ON termPosition(docID);
	      CREATE INDEX IF NOT EXISTS btreeINDEX_tfWord ON termFrequency(word);
	      CREATE INDEX IF NOT EXISTS btreeINDEX_tfDocID ON termFrequency(docID);
		  """
	database.execute(SQL)
	database.commit()

def createTable(database):
	dropTable(database)
	SQL = "CREATE TABLE IF NOT EXISTS "\
          "dictionary( word TEXT,"\
                      "PRIMARY KEY(word) );"\
          "CREATE TABLE IF NOT EXISTS "\
		  "documentFrequency( word TEXT, "\
		                     "frequency INTEGER, "\
		                     "PRIMARY KEY(word), "\
		                     "FOREIGN KEY(word) REFERENCES dictionary(word) "\
		                     "ON UPDATE CASCADE   ON DELETE CASCADE );"\
          "CREATE TABLE IF NOT EXISTS "\
		  "document( id INTEGER, "\
		            "fileName TEXT, "\
		            "length INTEGER, "\
		            "PRIMARY KEY(id) );"\
          "CREATE TABLE IF NOT EXISTS "\
          "termPosition( word TEXT, "\
                        "docID INTEGER, "\
                        "position INTEGER, "\
                        "FOREIGN KEY(word) REFERENCES dictionary(word) "\
                        "ON UPDATE CASCADE   ON DELETE CASCADE, "\
                        "FOREIGN KEY(docID) REFERENCES document(id) "\
                        "ON UPDATE CASCADE   ON DELETE CASCADE );"\
          "CREATE TABLE IF NOT EXISTS "\
          "termFrequency( word TEXT, "\
                         "docID INTEGER, "\
                         "frequency INTEGER, "\
                         "PRIMARY KEY(word, docID), "\
                         "FOREIGN KEY(word) REFERENCES dictionary(word) "\
                         "ON UPDATE CASCADE   ON DELETE CASCADE, "\
                         "FOREIGN KEY(docID) REFERENCES document(id) "\
                         "ON UPDATE CASCADE   ON DELETE CASCADE );"
	database.execute(SQL)
	database.commit()

def main():
	"""
	The program must accept two command line arguments: 
	the first is the directory containing the documents to be indexed, 
	and the second must be the directory where the index will be stored.
	"""
	# first handle user input
	if len(sys.argv) != 3:
		# number of argument is not correct
		print("Two arguments are needed:")
		print("1. the directory containing the documents to be indexed")
		print("2. the directory where the index will be stored")
		return 
	docDir = sys.argv[1]
	indexDir = sys.argv[2]
	if not os.path.isdir(docDir) or not os.path.isdir(indexDir):
		# the given input dir are invalid
		print("The given directory is invalid")
		return 
	# append / if not present in the directory
	if docDir[-1] != "/":
		docDir += "/"
	if indexDir[-1] != "/":
		indexDir += "/"
	if indexDir == "/":
		indexDir = "." + indexDir
	if docDir == "/":
		docDir = "." + docDir
	# retrieve all documents in the given directory
	allDoc = []
	for subDir in os.walk(docDir):
		# recursively retrieve all files in each subDir
		# docDir is also a subDir of itself
		for doc in subDir[2]:
			# all documents in subDir
			allDoc.append(doc)

	#######################################################################################################################

	# intialization for building index
	import Normalization 
	import Tokenization 
	import SQLite3database 
	# init text processing classes
	normalization = Normalization.Normalizer()
	tokenization = Tokenization.Tokenizer()
	# create a SQLite3 database
	indexDatabase = SQLite3database.Database(indexDir+"index.db")
	# create title index database
	titleDatabase = SQLite3database.Database(indexDir+"title.db")
	# create table
	createTable(indexDatabase)
	createTable(titleDatabase)
	# init final insert string
	indexDatabase.initInsertString()
	indexDatabase.addBeginTransactionString()
	titleDatabase.initInsertString()
	titleDatabase.addBeginTransactionString()
	# intializing insert string
	insertDocument = "INSERT INTO document VALUES"
	insertDictionary = "INSERT INTO dictionary VALUES"
	insertTermPosition = "INSERT INTO termPosition VALUES"
	insertDocumentFrequency = "INSERT INTO documentFrequency VALUES"
	insertTermFrequency = "INSERT INTO termFrequency VALUES"

	insertDocumentTitle = "INSERT INTO document VALUES"
	insertDictionaryTitle = "INSERT INTO dictionary VALUES"
	insertTermPositionTitle = "INSERT INTO termPosition VALUES"
	insertDocumentFrequencyTitle = "INSERT INTO documentFrequency VALUES"
	insertTermFrequencyTitle = "INSERT INTO termFrequency VALUES" 

	# store document frequency of each vocabulary
	dictionary = {} # contain all vocabulary over all (vocabulary as key, document frequncy as value)
	titleDic = {} 
	for doc in allDoc:
		# First read and process text from the current document
		# open file to read
		text = open(docDir+doc,"r").read()

		noTxt = doc.rstrip(".txt")
		title = " ".join(noTxt.split("_")[2:])

		# process raw text from document
		tokens = cleanText(text, tokenization, normalization) # return a list of term/vocabulary after tokenization and normalization
		titleTokens = cleanText(title.lower(), tokenization, normalization) 
		# Then
		# Traverse the term/vocabulary list and record the information
		# -position 
		# -count
		# init 
		termFrequency = {} # (vocabulary and documentID as key, term frequency as value)
		titleTermFrequency = {}
		documentID = int(doc.split("_")[1]) # extract document ID
		insertDocument += """ ({docID},"{docName}",{docLength}),""".format(docID=documentID, docName=doc, docLength=len(tokens))
		insertDocumentTitle += """ ({docID},"{docName}",{docLength}),""".format(docID=documentID, docName=doc, docLength=len(titleTokens))
		alreadyIncrement = {} # use for check if the document frequency in this document is already increment
		alreadyIncrementTitle = {}
		for index,token in enumerate(tokens):
			# insert position of this token in the document
			insertTermPosition += """ ("{word}",{docID},{position}),""".format(word=token, docID=documentID, position=index+1)
			if token not in dictionary:
				dictionary[token] = 1
				alreadyIncrement[token] = None
				# insert if this token is the first time encounter overall 
				insertDictionary += """ ("{word}"),""".format(word=token)
			elif token not in alreadyIncrement:
				dictionary[token] += 1
				alreadyIncrement[token] = None
			if token not in termFrequency:
				termFrequency[token] = 1
			else:
				termFrequency[token] += 1
		for key,val in termFrequency.items():
			insertTermFrequency += """ ("{word}",{docID},{termFreq}),""".format(word=key, docID=documentID, termFreq=val)

		for index,token in enumerate(titleTokens):
			# insert position of this token in the document
			insertTermPositionTitle += """ ("{word}",{docID},{position}),""".format(word=token, docID=documentID, position=index+1)
			if token not in titleDic:
				titleDic[token] = 1
				alreadyIncrementTitle[token] = None
				# insert if this token is the first time encounter overall 
				insertDictionaryTitle += """ ("{word}"),""".format(word=token)
			elif token not in alreadyIncrementTitle:
				titleDic[token] += 1
				alreadyIncrementTitle[token] = None
			if token not in titleTermFrequency:
				titleTermFrequency[token] = 1
			else:
				titleTermFrequency[token] += 1
		for key,val in titleTermFrequency.items():
			insertTermFrequencyTitle += """ ("{word}",{docID},{termFreq}),""".format(word=key, docID=documentID, termFreq=val)


	# insert the document frequency
	for key,val in dictionary.items():
		insertDocumentFrequency += """ ("{word}",{docFrequency}),""".format(word=key, docFrequency=val)

	for key,val in titleDic.items():
		insertDocumentFrequencyTitle += """ ("{word}",{docFrequency}),""".format(word=key, docFrequency=val)

	# get rid of the ',' at the end of each insert string
	# replace it with ';'
	insertDocument = insertDocument[:-1] + ";"
	insertDictionary = insertDictionary[:-1] + ";"
	insertTermPosition = insertTermPosition[:-1] + ";"
	insertTermFrequency = insertTermFrequency[:-1] + ';'
	insertDocumentFrequency = insertDocumentFrequency[:-1] + ";"


	insertDocumentTitle = insertDocumentTitle[:-1] + ";"
	insertDictionaryTitle = insertDictionaryTitle[:-1] + ";"
	insertTermPositionTitle = insertTermPositionTitle[:-1] + ";"
	insertTermFrequencyTitle = insertTermFrequencyTitle[:-1] + ';'
	insertDocumentFrequencyTitle = insertDocumentFrequencyTitle[:-1] + ";"

	# add all insert string to the final insert string
	indexDatabase.addInsertString(insertDocument)
	indexDatabase.addInsertString(insertDictionary)
	indexDatabase.addInsertString(insertTermPosition)
	indexDatabase.addInsertString(insertTermFrequency)
	indexDatabase.addInsertString(insertDocumentFrequency)
	indexDatabase.addCommitString()
	indexDatabase.execute(indexDatabase.getInsertString())
	createBtreeIndex(indexDatabase)
	indexDatabase.close()

	titleDatabase.addInsertString(insertDocumentTitle)
	titleDatabase.addInsertString(insertDictionaryTitle)
	titleDatabase.addInsertString(insertTermPositionTitle)
	titleDatabase.addInsertString(insertTermFrequencyTitle)
	titleDatabase.addInsertString(insertDocumentFrequencyTitle)
	titleDatabase.addCommitString()
	titleDatabase.execute(titleDatabase.getInsertString())
	createBtreeIndex(titleDatabase)
	titleDatabase.close()

if __name__ == "__main__":
	main()

