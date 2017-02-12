# -*- coding: utf-8 -*-

import scrapy

class ExtraNotebooksSpider(scrapy.Spider):

    name = 'extranotebooks'
    start_urls = [
        'http://www.extra.com.br/Informatica/Notebook/?Filtro=C56_C57'
    ]

    def parse(self, response):

        master_div = response.xpath(
            '//div[contains(@class, "lista-produto") and contains(@class, "prateleira")]'
        )
        #self.log("Master_div: {}".format(master_div.extract_first()))
        items = master_div.xpath(
            './/div[contains(@class, "hproduct")]'
        )
        #self.log("Item_first: {}".format(items.extract_first()))
        #self.log("number_items: {}".format(len(items)))
        for item in items:
            title = item.xpath(
                './/a[contains(@class, "link") and contains(@class, "url")]/@title'
            )
            #self.log("title: {}".format(title.extract_first()))

            url = item.xpath(
                './/a[contains(@class, "link") and contains(@class, "url")]/@href'
            ).extract_first()
            #self.log("URL: {}".format(url.extract_first()))
            yield scrapy.Request(
                url=url,
                callback=self.parse_detail
            )

        pagination_div = response.xpath(
            '//div[contains(@class, "result-busca")]'
        )
        pagination_li = pagination_div.xpath(
            './/li[contains(@class, "next")]'
        )
        next_page = pagination_li.xpath(
            './/a/@href'
        ).extract_first()

        self.log("\n\n{}\n\n".format(next_page))

        if next_page:
            yield scrapy.Request(
                url=next_page,
                callback=self.parse
            )

    def parse_detail(self, response):
        """
            Acessando a url do item: Notebook
            Colocando em dicionário o título, preço e a link
        """
        
        #self.log(response)
        item = {}
        price_div = response.xpath(
            '//div[contains(@class,"area-3-1-2-2")]'
        )
        #self.log(price_div.extract_first())
        price_i = price_div.xpath(
            './/i[contains(@class, "sale") and contains(@class, "price")]'
        )
        #self.log(price_i.extract_first())
        item['price'] = price_i.xpath('.//text()').extract_first()
        #self.log("price of item: {} ".format(item['price']))
        title_div = response.xpath('//div[contains(@class, "area-2")]')
        #self.log(title_div.extract_first())
        title_b = title_div.xpath(
            './/h1[contains(@class, "name") and contains(@class, "fn")]/b'
        )
        #self.log(title_b.extract_first())
        item['title'] = title_b.xpath('.//text()').extract_first()
        #self.log("title of item: {} ".format(item['title']))
        item['url'] = response.url
        #self.log("title of url: {} ".format(response.url))
        yield item
