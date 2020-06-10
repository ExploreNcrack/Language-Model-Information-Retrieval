# Language Model Ranking
## Written by: [Zhaozhen Liang(zhaozhen)](https://github.com/ExploreNcrack)
## Goal
The Goal of this project is to make a mini search engine program over a movie folder using **language model**(which contains 2000 file/document about movie reviews).
</br></br>**"Instead of overtly modeling the probability P(R=1|q,d) of relevance of a document d to query q, as in the traditional probabilistic approach to IR, the basic language modeling approach instead builds a probabilistic language model Md from each document d, and ranks documents based on the probability of the model generating the query: P(q|Md)."**[p237,Introduction to Information Retrieval, By Christopher D. Manning, Prabhakar Raghavan & Hinrich Schütze © 2008 Cambridge University Press.]
</br></br>**Intuition**
</br>Good queries: contain words likely appear in a relevant document
</br>**Key Idea**
</br>The language modeling approach to IR directly models that idea: a document is a good match to a query if the document model is likely to generate the query, which will in turn happen if the document contains the query words often.
The Basic language modeling approach builds a probilistic language model Md from each document d, and ranks documents based on the probability of the model generating the query: P(q|Md). 
</br>
</br>**Reference**
</br>[Introduction to Information Retrieval, By Christopher D. Manning, Prabhakar Raghavan & Hinrich Schütze © 2008 Cambridge University Press.]

## Libraries
All libraries are listed in requirements.txt
<br>Please run following command to install all the library that are needed: 
</br></br>First make the bash script executable by:
```
> chmod +x download.sh 
```
run the script by:
```
> ./download.sh
```
## Parts
There are two parts in this project.
</br>The **first part** is [**create_index**](https://github.com/ExploreNcrack/Language-Model-Information-Retrieval/tree/master/create_index): which take in the input source directory(which contain bunch of files/documents) and collect some statistic information that is needed for later ranking computations.
</br>The **second part** is [**lm_query**](https://github.com/ExploreNcrack/Language-Model-Information-Retrieval/tree/master/lm_query)(language model query): which uses the index statistic information(language model) that is collected in part1(create index) to perform the language model ranking.
