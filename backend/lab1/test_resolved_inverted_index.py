from crawler import crawler

bot = crawler(None, "urls.txt")
bot.crawl(depth=1)
print bot.get_resolved_inverted_index()
