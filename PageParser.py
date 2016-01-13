from urllib2 import urlopen             # To fetch the HTML source code of a website
from urllib2 import URLError            # For urlopen error handling
from BeautifulSoup import BeautifulSoup # To parse the HTML source code
from urlparse import urljoin            # To join absolute and relative urls
from urlparse import urlparse           # Parses urls
import sys   # Printing, file I/O etc.
import os    # For looking into this system's folders
import utils # Our helper functions
import re    # Regular expressions

class PageParser():
    # pre:  outputDir is a local relative path in string format
    # post: An instance of PageParser is initiated. When
    #       the parser's parse method will be called, parsed
    #       data will be stored within the outputDir folder.
    def __init__(self, outputDir="Mapped/"):
        self.links = [] # Links that the parser finds while parsing a webpage
        self.outputDir = outputDir

    # pre:  baseURL is a local or internet url.
    # post: Parses text from the baseURL location and writes to the local folder Mapped.
    def parse(self, baseURL):
        self.links = []
        self.baseURL = baseURL
        try:
            response = urlopen(baseURL)

            # So that we're not parsing pdf, javascript, css etc.
            if response.info().gettype() == 'text/html':
                htmlString = response.read()     # Fetch the HTML
                soup = BeautifulSoup(htmlString) # Prepare the HTML for navigating

                text = self.extractTextFrom(soup) # Extract visible text from the HTML
                self.writeToDisk(text)
                self.extractLinksFrom(soup) # Store the links from the HTML
        except URLError:
            raise URLError('Failed to parse URL: ' + baseURL)

    # pre:  soup is a BeaituflSoup instance.
    # post: Returns the visible text on the webpage from the given soup.
    def extractTextFrom(self, soup):
        text = soup.findAll(text=True)
        return utils.stripHTML(" ".join(filter(utils.isVisible, text)).encode('utf-8'))

    # pre:  text is a string.
    # post: Each word in text is written in it's
    #       own line into a file in the folder Mapped.
    def writeToDisk(self, text):
        # Prepare the output directory
        if not os.path.exists(self.outputDir):
            os.makedirs(self.outputDir)

        # A single file will hold the parsed data from the HTML
        outputFilePath = self.outputDir + utils.urlToFilename(self.baseURL) + ".txt"
        outputFile = open(outputFilePath, "w")
        # The file starts with the url which is the docID of the webpage
        outputFile.write(self.baseURL + "\n")

        for token in text.split():
            if isinstance(token, unicode):
                token = token.encode('utf-8')
            outputFile.write(token + "\n")
        outputFile.close()

    # pre:  soup is a BeautifulSoup instance.
    # post: self.links now includes all external links in the soup.
    def extractLinksFrom(self, soup):
        for a in soup.findAll('a', href=True):
            newURL = a['href']
            # Links starting with # or javascript aren't real links
            if newURL.startswith("#") or newURL.startswith("javascript") \
               or newURL.endswith(".pdf"):
                continue # Skip them
            if not utils.isAbsolute(newURL):
                newURL = urljoin(self.baseURL, newURL)
            # To avoid duplicates
            if newURL not in self.links:
                self.links = self.links + [newURL.encode('utf-8')]

    # pre:  websiteURL is a url in string format.
    # post: Checks if the website contains the robots.txt file. If so,
    #       returns a list of the file's mentioned disallowed paths
    #       for crawling
    def getRobotsTXTDisallowedPathsFrom(self, websiteURL):
        disallowedLinks = []

        try:
            url = urlparse(websiteURL)
            absoluteURL = url.scheme + "://" + url.netloc
            robotsTXT = urlopen(absoluteURL + "/robots.txt")

            for line in robotsTXT:
                if line.startswith("Disallow:"):
                    link = urljoin(absoluteURL, re.sub("^(.*?)/", "", line, 1)).rstrip()
                    disallowedLinks.append(link)
            return disallowedLinks
        except:
            return []