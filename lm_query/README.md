# Language Model Query
## Main program: lm_query.py
## How to execute?
Four arguments are needed:
- 1. a path to the index file
- 2. k (the maximum number of answers)
- 3. [y/n] indicating whether to print the scores
- 4. followed by a list of keywords
```
> python3 lm_query.py [path] [k] "[whitespace-separated multi-term query]"
```
example: **python3 lm_query.py [path] [k] [y/n] "[whitespace-separated multi-term query]"**

## Goal
The goal is to use the language model information that is built from the part1(create index) to calculate the probability of each document model generate the query terms. We do so by first perform text processing on the query terms and then for each document, we use the information to calculate the probability and lastly rank and return the top k document by the probability.

## Language Model Used
The Maximum Likelyhood Estimation(MLE) model with unigram assumption is being used. 
</br>The probability of generating the query for each document is computed by:
</br>p_hat(Given document model M_d, the probability of query generate) = product of each probability of each query term generate given the document language model 
</br>The probability of generating a single query term for each document is computed by:
p_hat(Given document model M_d, the probability of query term generate) = (term frequency of the query term in the document)/(document Length)
</br>
</br>For terms that does not appear in the document, when computing their probability, I use log() for the document length. Such that it will minize the effect by the document length.

## Text Processing for Query Term
The text processing for query term is pretty much the same as the text processing used in create_index, but this time with STOP words filtered. Because the STOP words are not informative terms and should be ignore for the precision of the information need.

## Smoothing
I decided not to use the  Jelinek-Mercer smoothing. Because this smoothing method does not handle a case when a query term does not appear in the whole corpus.
</br>Thus I decided to use the +epsilon method.</br>
Insteading of using add 1 to those query terms that do not actually appear in a document, I add a very small number epsilon=0.0001. In this way, I can avoid the probability of generating the whole query terms will be zero if one of the query term does not appear in a document. And also using a very small epsilon can prevent the actual distribution of the terms being distorted.
