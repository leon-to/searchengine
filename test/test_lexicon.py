from crawler import crawler

bot = crawler(None, "urls.txt")
bot.crawl(depth=1)

print bot._lexicon
