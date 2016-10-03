# Scraping Structured Data

ChemDataExtractor contains a `scrape` package for extracting structured information from HTML and XML files. This is
most useful for obtaining bibliographic data, but can be used for any kind of data that has been marked up with HTML or XML tags in source documents.

## Included Scrapers

ChemDataExtractor comes with ready-made scraping tools for web pages on the RSC and ACS web sites, as wells as for XML
files in the NLM JATS format as used by PubMed Central and others.

    >>> from chemdataextractor.scrape import Selector
    >>> from chemdataextractor.scrape.pub.rsc import RscHtmlDocument
    >>> 
    >>> htmlstring = open('rsc_example.html').read()
    >>> sel = Selector.from_text(htmlstring)
    >>> scrape = RscHtmlDocument(sel)
    >>> print(scrape.publisher)
    'Royal Society of Chemistry'
    >>> scrape.serialize()
    {'publisher': 'Royal Society of Chemistry', 'language': 'en', 'title': 'The Title'}
    

## Custom Scrapers

As an example, here is a very simple HTML file that we want to scrape some data from:

    <html>
      <head>
        <title>Example document</title>
        <meta name="citation_publication_date" content="2016-10-03">
      </head>
      <body>
        <p class="abstract">Abstract goes here...</p>
        <p class="para">Another paragraph here...</p>
      </body>
    </html>

### Defining an Entity

To use the `scrape` package, we define an `Entity` that contains `Fields` that describe how to extract the desired 
content in a [declarative fashion](https://en.wikipedia.org/wiki/Declarative_programming):

    from chemdataextractor.scrape import Entity

    class ExampleDocument(Entity):
        title = StringField('title')
        abstract = StringField('.abstract')
        date_published = DateTimeField('meta[name="citation_publication_date"]::attr("content")')

Each field uses a [CSS selector](https://developer.mozilla.org/en-US/docs/Web/Guide/CSS/Getting_Started/Selectors) to
describe where to find the data in the document.

### XPath Expressions

It is possible to use XPath expressions instead of CSS selectors, if desired. Just add the parameter `xpath=True` to the field arguments:

    date_published = DateTimeField('//meta[@name="citation_publication_date"]/@content', xpath=True)

### Cleaners

Cleaners make modifications to the HTML or XML tree, prior to the text content being extracted.

### Processors

Processors perform transformations on the extracted text.

## The Selector

The `Selector` is inspired by the [Scrapy](https://scrapy.org/) text mining tool. It provides a convenient unified interface for 'selecting' parts of XML and HTML documents for extraction. `Entity` classes make use of it behind the scenes, but for simple cases, it can be quicker and easier to use it directly to extract information.

Create a selector from a file:

    >>> htmlstring = open('rsc_example.html').read()
    >>> sel = Selector.from_text(htmlstring)

Now, instead of passing the selector to an Entity, you can query it with CSS:

    >>> sel.css('head')

This returns a `SelectorList`, meaning you can chain queries. Call `extract()` or `extract_first()` on the returned `SelectorList` to get the extracted content.

    >>> sel.css('head').css('title').extract_first()
    'Example document'
    >>> sel.css('p')
    ['Abstract goes here...', 'Another paragraph here...']
