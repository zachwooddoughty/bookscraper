import re
import mechanize
from bs4 import BeautifulSoup, Tag, NavigableString

from data import Author, Book


def scrape(url):
    '''
        Scrape the HTML from a given url
    '''
    try:
        br = mechanize.Browser()
        br.set_handle_robots(False)
        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        # Cheat to win
        br.addheaders = [
            ('User-agent',
             'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')
        ]
        br.open(url.encode('utf8'), timeout=5)
        html = br.response().read()
        return html
    except Exception, e:
        print "Failed to scrape %s" % repr(url), e
        return None


def goodreads_scrape(url):
    '''
        Input: Goodreads search url
        Output: list of books and number of pages of results
    '''
    html = scrape(url)
    if not html:
        return [], 1
    soup = BeautifulSoup(html)

    # Look for the "previous page" link to find the number of result pages
    num_pages = 1
    previous_page = soup.find("span", attrs={"class": "previous_page"})
    if previous_page and previous_page.parent:
        for page_link in previous_page.parent.find_all("a"):
            link_number = page_link.text.strip()
            try:
                num_pages = max(num_pages, int(link_number))
                # print "We found %d pages" % num_pages
            except:
                pass

    # look for all the table rows listed as books
    books = []
    for tr in soup.find_all("tr", attrs={"itemtype": "http://schema.org/Book"}):
        # Find the book's title from the "bookTitle" link
        title_box = tr.find("a", attrs={"class": "bookTitle"})
        title =  title_box.find('span').text
        if title_box.has_attr('href'):
            link = "http://goodreads.com" + title_box['href']
        else:
            link = "/"


        # Look for the date in the "published by" text but fallback with 0
        #   This is b/c it's usually old/weird results that don't have this date field.
        try:
            small_text = tr.find("span", attrs={'class': 'greyText smallText uitext'}) 
            date = re.search('\s\d\d\d\d\s', small_text.text).group().strip()
            date = int(date)
        except:
            date = 0

        books.append((date, title, link))

    return books, num_pages


def scrape_author(author, earliest_year=0):
    '''
        This function searches goodreads.com for the given author name and compiles all results.
        If earliest_year is specified, only return books with a publication year >= earliest_year.
        Note: this isn't just an author search, so it may retrieve some literary criticism, etc.
    '''
    print "Scraping", author, 
    # Do our initial search without a page number specified, and then snag the "num_pages" data from that first search
    url = "http://www.goodreads.com/search?tab=books&q=" + "+".join(author.split()).lower()
    books, num_pages = goodreads_scrape(url)
    
    # Now that we have a value for num_pages, keep scraping each page until we get them all
    page_index = 1
    while page_index < num_pages:
        page_index += 1
        print "Scraping %d/%d" % (page_index, num_pages),
        # Our new url should specify which page it's targeting
        new_url = "http://www.goodreads.com/search?page=%d&tab=books&q=%s" % (page_index, "+".join(author.split()).lower())
        new_books, new_num_pages = goodreads_scrape(new_url)
        # Add the recent scrape to our list of books and update the total num_pages if necessary
        books += new_books
        num_pages = max(num_pages, new_num_pages)

    # Filter out books before our "earliest year" field and sort them by descending date
    books = [book for book in books if book[0] >= earliest_year]
    print "==> We found", len(books), "books by", author, "since", earliest_year
    books = sorted(books, key=lambda x: x[0], reverse=True)
    return books


def main():
    for author in Author.objects:
        books = scrape_author(author.name, author.year)
        for book in books:
            year = book[0]
            title = book[1].encode('ascii', 'ignore')
            link = book[2]
            if not Book.objects(author=author.name, title=title, year=year).count():
                Book(
                    author=author.name,
                    title=title,
                    link=link,
                    year=year,
                    read=False
                ).save()


if __name__ == "__main__":
    main()
