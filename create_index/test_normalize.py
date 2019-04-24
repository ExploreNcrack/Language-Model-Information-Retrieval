import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
text=[" It i-s .html ... a pleasant evening.","Guests, who came from US arrived at the venue","Food was tasty."]
tokenized_docs=[word_tokenize(doc) for doc in text]
x=re.compile('[%s]' % re.escape(string.punctuation))
tokenized_docs_no_punctuation = []
for review in tokenized_docs:
	new_review = []
	for token in review: 
	    new_token = x.sub(u'', token)
	    if not new_token == u'':
	    	new_review.append(new_token)
	tokenized_docs_no_punctuation.append(new_review)	
print(tokenized_docs_no_punctuation)
print(string.punctuation)

stops=set(stopwords.words('english'))
words=["Don't", 'hesitate','to','ask','questions']
w = [word for word in words if word not in stops]
print(w)