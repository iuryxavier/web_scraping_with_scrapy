# Web Scraping with Scrapy

## Desenvolvedor de Web Scraping Utilizando Scrapy

### arquivo: /extra/spiders/extra_notebooks.py

```python
import scrapy

class ExtraNotebooksSpider(scrapy.Spider):

    name = 'extranotebooks'
    start_urls = ['http://www.extra.com.br/Informatica/Notebook/?Filtro=C56_C57']

    def parse(self, response):
        master_div = response.xpath(
            '//div[contains(@class, "lista-produto") and contains(@class, "prateleira")]'
        )
        items = master_div.xpath(
            './/div[contains(@class, "hproduct")]'
        )
        for item in items:
            title = item.xpath(
                './/a[contains(@class, "link") and contains(@class, "url")]/@title'
            )
            url = item.xpath(
                './/a[contains(@class, "link") and contains(@class, "url")]/@href'
            )
            yield scrapy.Request(
                url=url.extract_first(),
                callback=self.parse_detail
                )

    def parse_detail(self, response):
        """
            Acessando a url do item: Notebook
            Colocando em dicionário o título, preço e a link
        """
        item = {}
        price_div = response.xpath(
            '//div[contains(@class,"area-3-1-2-2")]'
        )
        price_i = price_div.xpath(
            './/i[contains(@class, "sale") and contains(@class, "price")]'
        )
        item['price'] = price_i.xpath('.//text()').extract_first()
        title_div = response.xpath('//div[contains(@class, "area-2")]')
        title_b = title_div.xpath(
            './/h1[contains(@class, "name") and contains(@class, "fn")]/b'
        )
        item['title'] = title_b.xpath('.//text()').extract_first()
        item['url'] = response.url
        yield item

```

### arquivo: /extra/pipelines.py

```python
# -*- coding: utf-8 -*-

import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError

class ExtraNotebooksPipeline(object):

    def create_db_table(self):
        self.conn = r.connect('localhost', 28015)
        try:
            r.db_create("testdbnosql").run(self.conn)
            r.db("testdbnosql").table_create("items").run(self.conn)
            self.conn = r.connect(host='localhost', port=28015, db='testdbnosql')
            self.cursor = r.table("items").run(self.conn)
        except RqlRuntimeError as err:
            print(err.message)

    def check_db_table(self):
        self.conn = r.connect(host='localhost', port=28015, db='testdbnosql')
        try:
            self.cursor = r.table("items").run(self.conn)
        except RqlRuntimeError as err:
            if err.message == "Database `testdbnosql` does not exist.":
                print("CRIANDO A DATABASE E TABELA")
                self.create_db_table()
            else:
                print(err.message)

    def open_spider(self, spider):
        self.check_db_table()

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        print("PROCESSANDO ITEMS - DB")
        r.table('items').insert(item).run(self.conn)
        return item


```


### Programa feito em 2 h ; )

### Estudando [4 h]

### Referências:
  - [Docs Scrapy](https://doc.scrapy.org/en/1.3/ "Scrapy 1.3 - Docs")
  - [Parte I - Configurando e rodando o Scrapy](http://www.gilenofilho.com.br/usando-o-scrapy-e-o-rethinkdb-para-capturar-e-armazenar-dados-imobiliarios-parte-i/ "Gileno Filho Blog")
  - [Parte II - Instalando, configurando e armazenando os dados no RethinkdbParte II - Instalando, configurando e armazenando os dados no Rethinkdb](http://www.gilenofilho.com.br/usando-o-scrapy-e-o-rethinkdb-para-capturar-e-armazenar-dados-imobiliarios-parte-ii/ "Gileno Filho Blog")
  - [Parte III - Deploy do projeto ScrapyParte III - Deploy do projeto Scrapy](http://www.gilenofilho.com.br/usando-o-scrapy-e-o-rethinkdb-para-capturar-e-armazenar-dados-imobiliarios-parte-iii/ "Pycursos.com Gileno")
  - [Aprenda Análise de Dados com Python e Pandas](https://www.pycursos.com/pandas/ "Gileno Filho Blog")
  - [Getting started with RethinkDB and Python 3](https://rethinkdb.com/blog/chad-lung-python3/ "Rethinkdb with python3")
