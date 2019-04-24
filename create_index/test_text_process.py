import Normalization
import Tokenization

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

normalization = Normalization.Normalizer()
tokenization = Tokenization.Tokenizer()

dd=cleanText("adad.adad ada...adad..ad 1941.http u.s.a. #Dadad #Rats sgsgs...",tokenization, normalization)
print(dd)