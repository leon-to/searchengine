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

# store into db
con = lite.connect("table.db")
cur = con.cursor()
cur.execute("CREATE TABLE Lexicon (word_id integer, word text)")
cur.execute("CREATE TABLE DocIndex (doc_id integer, url text)")
cur.execute("CREATE TABLE InvertedIndex (word_id integer, doc_id integer)")
cur.execute("CREATE TABLE PageRank (doc_id integer, rank double)")

for word_id in range(len(lexicon)):
    cur.execute("INSERT INTO Lexicon VALUES('{}', '{}')".format(word_id, lexicon[word_id]))

for doc_id in range(len(document_index)):
    doc = document_index[doc_id]
    cur.execute("""INSERT INTO DocIndex VALUES("{0}","{1}")""".format(doc_id, doc._url.replace('"', '').replace("'", '')))

for word_id, doc_id_set in inverted_index.iteritems():
    for doc_id in doc_id_set:
        cur.execute("INSERT INTO InvertedIndex VALUES('{}','{}')".format(word_id, doc_id))

for doc_id, rank in sorted_rank:
    cur.execute("INSERT INTO PageRank VALUES('{}','{}')".format(doc_id, rank))

con.commit()
con.close()
