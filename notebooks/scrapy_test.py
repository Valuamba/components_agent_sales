import scrapy
from scrapy.crawler import CrawlerProcess


class MySpider(scrapy.Spider):
    name = "my_spider"
    start_urls = ["https://lms.tough-dev.school/"]

    def parse(self, response):
        # Extract the title of the current page
        title = response.css("title::text").get()

        # Extract the URL of the current page
        url = response.url

        # Return the extracted information
        yield {"title": title, "url": url}

        # Follow links to other pages
        for next_page in response.css("a::attr(href)").getall():
            yield response.follow(next_page, self.parse)
