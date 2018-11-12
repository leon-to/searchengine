import sqlite3 as lite
import crawler
import pagerank
import pprint

# run the crawler
bot = crawler.crawler(None, "urls.txt")
bot.crawl(depth=1)

lexicon         = bot._lexicon
document_index  = bot._doc_index
inverted_index  = bot.get_inverted_index()
rank            = pagerank.page_rank (bot._link)    
sorted_rank     = sorted(rank.items(), key=lambda(k,v): v, reverse=True)

# pretty prints the PageRank scores   
pprint.pprint (sorted_rank)

#for k, v in sorted(page_rank.iteritems()):
    #print k, v


# store into db
con = lite.connect("backend.db")
cur = con.cursor()
cur.execute("CREATE TABLE lexicon (word_id integer, word text)")
cur.execute("CREATE TABLE document_index (doc_id integer, url text)")
cur.execute("CREATE TABLE inverted_index (word_id integer, doc_id integer)")
cur.execute("CREATE TABLE page_rank (doc_id integer, score double)")

for word_id in range(len(lexicon)):
    cur.execute("INSERT INTO lexicon VALUES('{}', '{}')".format(word_id, lexicon[word_id]))

for doc_id in range(len(document_index)):
    doc = document_index[doc_id]
    cur.execute("INSERT INTO document_index VALUES('{}','{}')".format(doc_id, doc._url))

for word_id, doc_id_set in inverted_index.iteritems():
    for doc_id in doc_id_set:
        cur.execute("INSERT INTO inverted_index VALUES('{}','{}')".format(word_id, doc_id))

for doc_id, score in sorted_rank:
    cur.execute("INSERT INTO page_rank VALUES('{}','{}')".format(doc_id, score))

con.commit()
con.close()
