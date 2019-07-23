from crawler import crawler

crawler = crawler(None, 'urls.txt')
crawler.crawl(depth=1)

for i, doc_info in enumerate(crawler._doc_index):
    print "ID: ", i
    print "URL: ", doc_info.getUrl()
    print "Title: ", doc_info.getTitle()
    print "Description: ", doc_info.getDescription()
    print ""
