import os
import SQLite3database
import sys


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
			return -1
	return 1


def main():
	# first handle user input
	if len(sys.argv) != 2:
		# number of argument is not correct
		print("One argument is needed:")
		print("1. the path the index storage file")
		return 

	# check if the given file is a db file
	if ".db" not in sys.argv[1]:
		print("The given file is not a .db file")
		return

	# check if the index file exists
	if not os.path.isfile(sys.argv[1]):
		print("The given index storage file does not exist")
		return

	# open the database file that is given
	indexDatabase = SQLite3database.Database(sys.argv[1])
	# cursor
	cursor = indexDatabase.getCursor()

	# check if the tables needed exists in the index storage file
	tablesNeeded = ["dictionary", "document", "termPosition", "documentFrequency", "termFrequency"]
	if checkIfTableNeedExist(indexDatabase, cursor, tablesNeeded) == -1:
		print("The given index storage file does not contain Table: dictionary.")
		indexDatabase.close()
		return


	#####################################################################################

	# at this point, we can sure that the given database file is valid
	# and ready to proceed the print index process

	# first get all the unique term/vocabulary in the dictionary table
	sqlGetAllUniqueTerm = "SELECT * FROM dictionary;"
	cursor.execute(sqlGetAllUniqueTerm)
	results = cursor.fetchall() # ( ('xxx',),('xxx',),..)
	# put them into a list
	UniqueTermList = [] 
	for term in results:
		# term -> ('in',)
		UniqueTermList.append(term[0])
	# sort
	UniqueTermList.sort()
	# for each term
	# get their info
	for term in UniqueTermList:
		# get document frequency
		cursor.execute("SELECT frequency FROM documentFrequency WHERE word = ?;",(term,))
		docFrequency = cursor.fetchall()[0][0]
		print("{term}, {docFrequency} < ".format(term=term, docFrequency=docFrequency))
		# get all term frequency
		cursor.execute("SELECT * FROM termFrequency WHERE word= ?;",(term,))
		results = cursor.fetchall()
		# put them into a list
		allTermFrequency = []
		for i in results:
			allTermFrequency.append(list(i))
		# sort
		allTermFrequency.sort()    #[['xxx',1,1],['xxx',2,2],...]
		# for each term, doc
		for TermDoc in allTermFrequency:
			termDocPositionalIndex = "\t {docID}, {termFrequency}: < ".format(docID=TermDoc[1],termFrequency=TermDoc[2])
			cursor.execute("SELECT position FROM termPosition WHERE word = ? AND docID = ?;",(TermDoc[0],TermDoc[1]))
			results = cursor.fetchall()
			positions = []
			for i in results:
				positions.append(str(i[0]))
			positions.sort()
			termDocPositionalIndex += ", ".join(positions)
			termDocPositionalIndex += " >; "
			print(termDocPositionalIndex)
		print("\t > ")

	# close the database file at the end
	indexDatabase.close()





if __name__ == "__main__":
	main()