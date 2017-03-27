# -*- coding: utf-8 -*-
from RISJbot.spiders.basespiders import NewsSitemapSpider
from RISJbot.loaders import NewsLoader
# Note: mutate_selector_del_xpath is somewhat naughty. Read its docstring.
from RISJbot.utils import mutate_selector_del_xpath
from scrapy.loader.processors import Identity, TakeFirst
from scrapy.loader.processors import Join, Compose, MapCompose
from scrapy.utils.gz import gunzip, is_gzipped

class NYTimesSpider(NewsSitemapSpider):
    name = 'nytimes'
    # allowed_domains = ['nytimes.com']
    # A list of XML sitemap files, or suitable robots.txt files with pointers.
    sitemap_urls = ['http://www.nytimes.com/sitemaps/sitemap_news/sitemap.xml.gz'] 

    def parse_page(self, response):
        """@url https://www.nytimes.com/2017/02/28/science/california-aging-dams.html
        @returns items 1
        @scrapes bodytext bylines fetchtime firstpubtime modtime headline
        @scrapes keywords section source summary url
        """
        s = response.selector
        # Remove any content from the tree before passing it to the loader.
        # There aren't native scrapy loader/selector methods for this.        
        mutate_selector_del_xpath(s, '//footer[contains(@class, "story-footer")]')
        mutate_selector_del_xpath(s, '//*[contains(@class, "nocontent")]')

        l = NewsLoader(selector=s)

        l.add_value('source', 'New York Times')
        # Response header from NYT leads to non-canonical URL with ?_r=0 at end
        l.add_xpath('url', 'head/link[@rel="canonical"]/@href')

        l.add_xpath('bodytext', '//*[contains(@class, "story-body")]//text()')

        # Add a number of items of data that should be standardised across
        # providers. Can override these (for TakeFirst() fields) by making
        # l.add_* calls above this line, or supplement gaps by making them
        # below.
        l.add_fromresponse(response)
        l.add_htmlmeta()
        l.add_schemaorg(response)
        l.add_opengraph()
        l.add_scrapymeta(response)

        return l.load_item()

