from urlparse import urlparse # Parses urls
import re # Regular expressions
from bisect import bisect_left # Fast search in sorted list
from bisect import insort_left # Fast sorted list insertion 

# pre:  url is an url in string format.
# post: Returns True if the given url is absolute.
#       F.x.: is_absolute("/home/about.html") = False
#             is_absolute("www.google.com") = False
#             is_absolute("http://www.google.com") = True
def isAbsolute(url):
    return bool(urlparse(url).netloc)

# pre:  bsElement is a BeautifulSoup element.
# post: Returns True if the data contained within the bsElement
#       is visible on the webpage.
def isVisible(bsElement):
    if bsElement.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    # Doesn't find multiline comments:
    #elif re.match('<!--.*-->', str(bsElement)):
    # Finds multiline comments:
    elif re.match('<!--.*-->', str(bsElement), flags=re.DOTALL):
        return False
    return True

# pre:  text is a string that potentially
#       contains HTML tags.
# post: Returns the string stripped of it's HTML tags.
def stripHTML(text):
    return re.sub('<[^<]+?>|&.*;', '', text)

# pre: number and amount are integers > 0.
#      number is the number to be padded, amount
#      is the amount number will be padded.
# post ex.: padded(6, 0) = "6"
#           padded(6, 1) = "6"
#           padded(6, 2) = "06"
#           padded(6, 3) = "006"
def padded(number, amount):
	paddedNumber = str(number)
	while len(str(paddedNumber)) < amount:
		paddedNumber = '0' + paddedNumber
	return paddedNumber

# pre:  element is a string, a list formatted string,
#       a float, an int, a char or a list
# post: If element is a list, returns it as is. If not,
#       returns it as a one item list.
def elementToList(element):
    listed = []
    try: # Is element a string formatted list?
        listed = eval(element)
        if isinstance(listed, list):
            return listed
    except: 
        outcome = []
        if isinstance(element, list): # Is the element a list?
            outcome = element
        else: # Otherwise we box it into a list
            outcome = [element]
        return outcome

# pre: string is a url in a string format
# post ex.: urlToFilename("http://www.concordia.ca/section/la.html")
#           returns "concordia-ca-section-la-html". However,
#           limits the length of the filename to 150 characters
def urlToFilename(string):
    url  = urlparse(string)
    link = re.sub("www.", "", url.netloc) + url.path # Remove www.
    link += "-" + url.params + url.query
    text = re.sub("\.", "-", link) # Replace dots with dashes
    return re.sub("/", "-", text)[:150]  # Replace forward slashed with dashes

# pre:  oldLinkList is a list of absolute urls. excludeThesePaths is
#       a list of absolute paths. If onlyIncludeConcordia = True,
#       all links not part of concordia.ca will be excluded from oldLinkList.
# post: Returns the urls of oldLinkList that none of the paths in
#       excludeThesePaths are substring of.
def filterOutLinks(oldLinkList, excludeThesePaths, onlyIncludeConcordia=True):
    newLinkList = []

    if len(excludeThesePaths) == 0:
        return oldLinkList
    else:
        # No link in excludeThesePaths can be a
        # substring of any link in oldLinkList
        for link in oldLinkList:
            bareURL = bareLink(link)
            for i, excludedPath in enumerate(excludeThesePaths):
                barePath = bareLink(excludedPath)
                if barePath.startswith(bareURL):
                    break # Skip it. This link is to be excluded.
                if onlyIncludeConcordia:
                    website = urlparse(link).netloc.lower()
                    if website != "www.concordia.ca" and \
                       website != "concordia.ca":
                        break
                # If the following is True, none of the paths
                # were a substring of the link. Therefore, we
                # will include this link in our resulting links.
                if i+1 == len(excludeThesePaths):
                    newLinkList = newLinkList + [stripLinkFragment(link)]

    return newLinkList

# pre:  link is an absolute link in a string format
# post: drops the scheme and www., ww2., etc. and
#       returns the bare link with it's path, params and query
def bareLink(link):
    url = urlparse(link)
    netloc = url.netloc
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc + url.path + url.params + url.query

# pre:  link is an absolute link in string format
# post: returns the equivalance of link without it's fragment
#       F.x. http://www.exmple.com#index has the fragment #index
def stripLinkFragment(link):
    url = urlparse(link)
    urlquery = url.query
    if len(urlquery) > 0:
        urlquery = "?" + urlquery
    return url.scheme + "://" + url.netloc + url.path + url.params + urlquery

# pre:  list is a list
# post: returns the index of item in list, otherwise returns -1
def binarySearch(item, list, lo=0, hi=None):
    # If this is the first call, hi = len(list), otherwise the value isn't modified
    hi = hi if hi is not None else len(list)
    # Find the insertion position
    pos = bisect_left(list, item, lo, hi)
    # Measures so that the search doesn't go out of bounds
    return (pos if pos != hi and list[pos] == item else -1)

def sortedInsert(item, inlist):
    insort_left(inlist, item)