#!/usr/bin/env -u
# The line let's the first python instance found in PATH to be
# executed aswell as it allows for unbuffered sys.stdout.write.

from PageParser import PageParser # Our class that parses websites

from urlparse import urlparse # Parses urls
from urllib2 import URLError  # For urlopen error handling
import sys # Printing, file I/O etc.
import time # For pausing execution
import utils # Our helper functions

class Crawler():
    # pre:  urls is either an absolute url in string format
    #       or a list of absolute urls in string format.
    #       maxLinksToCrawl is an integer.
    # post: An instance of Crawler is initiated. When future
    #       crawl will be started, the crawler starts by
    #       crawling the given urls. In total, it will
    #       not crawl any more websites than maxLinksToCrawl.
    def __init__(self, urls, maxLinksToCrawl):
        self.linksToVisit = utils.elementToList(urls)
        if maxLinksToCrawl == 0:
            self.maxLinksToCrawl = sys.maxint
        else:
            self.maxLinksToCrawl = maxLinksToCrawl
        self.linksVisited = []     # The links we have visited.
        self.websitesVisited = []  # The websites we have visited.
        self.pathsNotToCrawl = []  # As defined in robots.txt.
        self.parser = PageParser() # Used to parse the websites we crawl.

    # pre:  urls is a string or a list of strings of websites to crawl.
    #       maxLinksToCrawl is the maximum amount of pages to crawl.
    #       if equal to zero, there's "no" limit for pages to crawl.
    # post: Crawls the web beginning with the given urls. Writes the 
    #       visible text on the webpages to disk in the folder Mapped.
    def crawl(self):
        sys.stdout.write("\n")
        while len(self.linksVisited) < self.maxLinksToCrawl and len(self.linksToVisit) > 0:
            url = self.linksToVisit[0] # Fetch the url to parse
            self.linksToVisit = self.linksToVisit[1:] # Delete it from linksToVisit

            # If we've reached a new website, obey defined robots exclusion rules.
            if urlparse(url).netloc not in self.websitesVisited:
                self.obeyRobotsExclusion(url)
                self.websitesVisited.append(urlparse(url).netloc)
            
            self.manageLinksAndData(url)

            # Crawler's politeness. Wait 2 seconds before crawling next link.
            time.sleep(2)

    # pre:  We have reached a new website during the crawl.
    # post: The url's website' robots.txt file is consulted if it exists.
    #       The crawler will take note of which paths are not to be crawled,
    #       as defined in the .txt file. In other words, the .txt file's
    #       content is used for following the robot exclusion standard.
    def obeyRobotsExclusion(self, url):
        sys.stdout.write(" -> Entering a new website. ")
        disallowedPaths = self.parser.getRobotsTXTDisallowedPathsFrom(url)
        if not disallowedPaths:
            sys.stdout.write("The website allows all paths to be crawled.\n")
        else:
            sys.stdout.write("Disallowed paths will be respected.\n")
            self.pathsNotToCrawl += disallowedPaths

    # post: Lets the PageParser retrieve the url's webpage links and data.
    #       Furthermore, filters out links that are not to be crawled and
    #       stores the remaining links for future crawling.
    def manageLinksAndData(self, url):
        sys.stdout.write(" [" + str(len(self.linksVisited)) + "] Crawling: " + url + "\n")
        try:
            self.linksVisited = self.linksVisited + [url]
            self.parser.parse(url)
            self.linksToVisit = self.linksToVisit \
                                + utils.filterOutLinks(self.parser.links, \
                                                       self.pathsNotToCrawl \
                                                       + self.linksVisited \
                                                       + self.linksToVisit)
            sys.stdout.write(" -> Success.\n")
        except URLError:
            sys.stdout.write(" -> Failed.\n")