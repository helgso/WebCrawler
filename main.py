#!/usr/bin/env -u
# The line let's the first python instance found in PATH to be
# executed aswell as it allows for unbuffered sys.stdout.write.

import sys
from Crawler import Crawler

def main():
	urls = raw_input("\n Pages to crawl: ")
	maxLinksToCrawl = int(raw_input(" Maximum amount of links to crawl: "))
	
	crawler = Crawler(urls, maxLinksToCrawl)
	crawler.crawl()

if __name__ == '__main__':
	main()