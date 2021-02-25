import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from leihkassestammheim.items import Article


class LeihkassestammheimSpider(scrapy.Spider):
    name = 'leihkassestammheim'
    start_urls = ['https://www.leihkasse-stammheim.ch/']

    def parse(self, response):
        articles = response.xpath('//div[@class="news-latest"]//article')
        for article in articles:
            link = article.xpath('.//a[@class="read-more"]/@href').get()
            date = " ".join(article.xpath('.//div[@class="date"]/span/text()').getall())
            if date:
                date = date.strip()

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//div[@class="NewsDetail"]/h1/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="NewsDetail"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
