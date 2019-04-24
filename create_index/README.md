# Build inverted positional index
## Main program: create_index.py
### How to execute?
python3 create_index.py [the directory contain all document to be index] [the directory to save the index file]
</br>or 
</br>chmod +x create_index.py 
</br>./create_index.py [the directory contain all document to be index] [the directory to save the index file]
</br>**Example: python3 create_index.py cmput397_2k_movies/ /**
</br>The program does handle cases where the input directory doesn't have "/" at the end
### After execetion of the program
There will be two database file generated:
- index.db (This is the database for the content of document) 
- title.db (This is for the zoning title of the document)
### **Print index**
**program: print_index.py**
</br>**execute by: python3 print_index.py [the path of the index.db file]**
</br>**For printing title or zoning index:**
</br>python3 print_index.py [path where **title.db** is]
</br>**For printing body index:**
</br>python3 print_index.py [path where **index.db** is]
</br>For example:
</br>python3 print_index.py title.db
</br>python3 print_index.py index.db
### Time 
Around **2min35sec** to finish building **2000 document**.
### Statistic:
For **index.db** body index
</br>Total number of **unique word/term**: **39395**
</br>Total number of **word/term over all document**: **1203582**
</br>For **title.db** zoning index
</br>Total number of **unique word/term**: **2620**
</br>Total number of **word/term over all document**: **5658**

## Persistance storage for Indexes
All index information will be store in a **relational database (SQLite3)**:
</br>**index.db** and **title.db** for zoning indexes on document title
</br>With consideration for **MapReduce** the Reduce and Map functions But did not implement
</br>There are 5 tables in total in this databse (**both index.db and title.db**):
* **dictionary**: word(TEXT) 
</br> which contains all terms over all documents
* **document**: id(INTEGER), fileName(TEXT), length(INTEGER)
</br> documentID and the origin file name
* **documentFrequency**: word(TEXT), frequency(INTEGER)
</br> which contain the document frequency for each word 
* **termPosition**: word(TEXT), docID(INTEGER), position(INTEGER)
</br> which contain all the word position that appear in the document
* **termFrequency**: word(TEXT), docID(INTEGER), frequency(INTEGER)
</br> which contain each term frequency in each document they appear in

**All table are also built with Btree indexes to speed up the search process**

# Modules
These modules are created to divde the specific task that is needed:
- Normalization.py
- Tokenization.py
- SQLite3database.py

# Testing
## Final test on 2000 movie documents:
by: python3 create_index.py cmput397_2k_movies/ /
## test term frequency for example document in directory test1
by: python3 create_index.py test1/ /
## test normalization handling in directory test2
by: python3 create_index.py test2/ /


# Limiations
## Tokenization 
NLTK Tweettokenizer() and plus some encoding method is used 
</br>which can preserved cases like "5,000", "U.S.A", "O'Neil", ("he's", "I'd", "Peter's", etc), "father-in-law", "9:00", "3.1415", ".html"->"html", "index.html" to consider as one token
</br>which ensure the meaning of the token are preserved and add precision to the query result later on
</br>However there are still cases that it will not be handled
</br>For example: "$5,000", "96.4%" or "95%" to consider them as one token may be more meaning for the query
## Normalization
I choose lemmatization rather than stemming for the text normalization. Since lemmatization is more precise but it is not so easy to do it.
</br>Why lemmatization is better than stemming?
</br>For example: in stemming, the word "organization" will reduce to "organ", even though they have different meaning
</br>Casefolding are used after lemmatization (just convert all words into lowercase for simplicity)
</br>The program handled cases: 
</br>tenses:"planted"-->"plant", plural:"cats"-->"cat", "has"-->"have", "is"/"are" --> be, persons name:"Cody Banks" "Banks"-->"Banks"
</br>However, it failed to hanle some cases where their gramma is incorrect for example: "I flew fought caught"
</br>And it failed to detect when a word appear at the beginning of the sentence "Knowing that ..."  such that 
</br>"Knowing"-->"Knowing" since its first character is upper case.
</br>There are also problem that is not handled for the contraction "they're" should be converted to "they are" and store indexes to each.
</br>weird ascii code character like 8211 which looks like 45 but they are different and will not be preserved
</br>there may be cases like "adadad.adada" will still preserved because we want to keep "xxx.com", "xxx.html", at this time, not enough time to handle all these cases
</br>In conclusion, I have handled most of the common cases.</br>
</br>Did not filter the stop words. Because this database can also use for phrase query.

