from crawler import crawler

bot = crawler(None, "urls.txt")
bot.crawl(depth=1)
print bot.get_inverted_index()
