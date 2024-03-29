from abc import ABC, abstractmethod
from requests.models import Response
from pypdf import PdfReader
from io import BytesIO
import re
import urllib.request
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from html.parser import HTMLParser

HTTP_URL_PATTERN = r'^http[s]{0,1}://.+$'
PROTOCOL_BLACKLIST = ["#", "mailto:", "tel:"]

class IHandler(ABC):
    @abstractmethod
    def parseText(content: Response) -> str:
        pass

    @abstractmethod
    def findLinks(content: Response, local_domain: str, seen, queue, depth, baseDirectory):
        pass

    @staticmethod
    @abstractmethod
    def addLinks(links: list[str], seen, queue, depth, baseDirectory):
        if not baseDirectory:
            baseDirectory = ["http"]
        for link in links:
            if link not in seen.keys() and link.startswith(tuple(baseDirectory)):
                queue.put((link, depth + 1))
                seen[link] = 1



class HTMLHandler(IHandler):
    class HyperlinkParser(HTMLParser):
        def __init__(self):
            super().__init__()
            # Create a list to store the hyperlinks
            self.hyperlinks = []

        # Override the HTMLParser's handle_starttag method to get the hyperlinks
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)

            # If the tag is an anchor tag and it has an href attribute, add the href attribute to the list of hyperlinks
            if tag == "a" and "href" in attrs:
                self.hyperlinks.append(attrs["href"])

    @staticmethod
    def parseText(content: Response) -> str:
        return BeautifulSoup(content.text, "html.parser").get_text()

    @staticmethod
    def get_hyperlinks(content):
        # Try to open the URL and read the HTML
        try:
            html = content.content.decode('utf-8')
        except Exception as e:
            print(e)
            return []

        # Create the HTML Parser and then Parse the HTML to get hyperlinks
        parser = HTMLHandler.HyperlinkParser()
        parser.feed(html)

        return parser.hyperlinks

    # Function to get the hyperlinks from a URL that are within the same domain
    @staticmethod
    def get_domain_hyperlinks(local_domain, content):
        clean_links = []
        for link in set(HTMLHandler.get_hyperlinks(content)):
            clean_link = None

            # If the link is a URL, check if it is within the same domain
            if re.search(HTTP_URL_PATTERN, link):
                # Parse the URL and check if the domain is the same
                url_obj = urlparse(link)

                # Makes sure new url is on the same domain
                # if url_obj.netloc == local_domain:
                #    clean_link = link
                clean_link = link
            # If the link is not a URL, check if it is a relative link
            else:
                if link.startswith("/"):
                    link = link[1:]
                elif link.startswith(tuple(PROTOCOL_BLACKLIST)):
                    continue
                clean_link = "https://" + local_domain + "/" + link

            if clean_link is not None:
                if clean_link.endswith("/"):
                    clean_link = clean_link[:-1]
                clean_links.append(clean_link)

        # Return the list of hyperlinks that are within the same domain
        return list(set(clean_links))

    @staticmethod
    def findLinks(content: Response, local_domain: str, seen, queue, depth, baseDirectory):
        links = HTMLHandler.get_domain_hyperlinks(local_domain, content)
        HTMLHandler.addLinks(links, seen, queue, depth, baseDirectory)


class PDFHandler(IHandler):
    @staticmethod
    def parseText(content: Response) -> str:
        text = ""
        reader = PdfReader(BytesIO(content.content))
        for page in reader.pages:
            text += page.extract_text()
        return text

    @staticmethod
    def findLinks(content: Response, local_domain: str, seen, queue, depth, baseDirectory):
        links = []
        reader = PdfReader(BytesIO(content.content))
        pages = len(reader.pages)
        key = '/Annots'
        uri = '/URI'
        ank = '/A'

        for page in range(pages):
            pageSliced = reader.pages[page]
            pageObject = pageSliced.get_object()
            if key in pageObject.keys():
                ann = pageObject[key]
                for a in ann:
                    u = a.get_object()
                    if uri in u[ank].keys() and not uri.startswith(tuple(PROTOCOL_BLACKLIST)):
                        links.append(u[ank][uri])

        PDFHandler.addLinks(links, seen, queue, depth, baseDirectory)

