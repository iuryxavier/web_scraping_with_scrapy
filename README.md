# Web Scraping with Scrapy
## Desenvolvedor de Web Scraping Utilizando Scrapy
### Arch Linux

```bash
$ sudo pacman -S rethinkdb
$ rethinkdb
```

## Browser *: [127.0.0.1:8080](http://127.0.0.1:8080)

```bash
$ mkdir test_project
$ cd test_project
$ virtualenv -p /bin/python3.6 venv
$ source venv/bin/activate
$ git clone https://github.com/iuryxavier/web_scraping_with_scrapy
$ cd web_scraping_with_scrapy
$ pip install -r requirements.txt
$ scrapy crawl extranotebooks
```

### Target: [www.extra.com.br](http://www.extra.com.br/Informatica/Notebook/?Filtro=C56_C57 "Loja Virtual Extra - Notebooks")
### Objetivos:
 - Utilização de xpath nas buscas por links (Ok!)
 - Persistência das informações (Ok!)
    - PostgreSQL(Testado)
    - MongoDB(Testado)
    - RethinkDB(Testado) - Utilizado nesta documentação - (Ok!)
 - Submissão de formulários (Em Construção)
 - Tratamento de paginação (Ok!)
 - Manipulação de querystrings (Em Construção)
 - Autenticação (Em Construção)
 - Utilizar logs para sinalizar ocorrências durante o scraping - Estão comentadas - (Ok!)

### Arquivo: [/extra/spiders/extra_notebooks.py](https://github.com/iuryxavier/web_scraping_with_scrapy/blob/master/extra/spiders/extra_notebooks.py)

```python

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
        items = master_div.xpath(
            './/div[contains(@class, "hproduct")]'
        )
        for item in items:
            title = item.xpath(
                './/a[contains(@class, "link") and contains(@class, "url")]/@title'
            )
            url = item.xpath(
                './/a[contains(@class, "link") and contains(@class, "url")]/@href'
            ).extract_first()
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

### Arquivo: /extra/pipelines.py

```python

# -*- coding: utf-8 -*-

import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError

class ExtraNotebooksPipeline(object):

    host = 'localhost'
    port_client = 28015
    db = "testdbnosql"
    table = "items"

    def create_db_table(self):
        self.conn = r.connect(self.host, self.port_client)
        try:
            r.db_create(self.db).run(self.conn)
            r.db(self.db).table_create(self.table).run(self.conn)
            self.check_db_table()
        except RqlRuntimeError as err:
            print(err.message)

    def check_db_table(self):
        self.conn = r.connect(host=self.host, port=self.port_client, db=self.db)
        try:
            self.cursor = r.table(self.table).run(self.conn)
        except RqlRuntimeError as err:
            if err.message == "Database `testdbnosql` does not exist.":
                self.create_db_table()
            else:
                print(err.message)

    def drop_db_table(self,drop_db=False):
        if drop_db:
            r.db_drop(self.db).run(self.conn)

    def open_spider(self, spider):
        self.check_db_table()

    def close_spider(self, spider):
        self.drop_db_table(False)
        self.conn.close()

    def process_item(self, item, spider):
        r.table('items').insert(item).run(self.conn)
        return item

```

### Arquivo: /extra/settings.py

```python

# -*- coding: utf-8 -*-

# Scrapy settings for extra project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'extra'

SPIDER_MODULES = ['extra.spiders']
NEWSPIDER_MODULE = 'extra.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'extra (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 1
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'extra.middlewares.ExtraSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'extra.middlewares.MyCustomDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'extra.pipelines.ExtraNotebooksPipeline': 100,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

```

### Programa feito em 3 h ; )

### Estudando [7 h]

### Referências:
  - [Docs Scrapy](https://doc.scrapy.org/en/1.3/ "Scrapy 1.3 - Docs")
  - [Parte I - Configurando e rodando o Scrapy](http://www.gilenofilho.com.br/usando-o-scrapy-e-o-rethinkdb-para-capturar-e-armazenar-dados-imobiliarios-parte-i/ "Gileno Filho Blog")
  - [Parte II - Instalando, configurando e armazenando os dados no RethinkdbParte II - Instalando, configurando e armazenando os dados no Rethinkdb](http://www.gilenofilho.com.br/usando-o-scrapy-e-o-rethinkdb-para-capturar-e-armazenar-dados-imobiliarios-parte-ii/ "Gileno Filho Blog")
  - [Parte III - Deploy do projeto ScrapyParte III - Deploy do projeto Scrapy](http://www.gilenofilho.com.br/usando-o-scrapy-e-o-rethinkdb-para-capturar-e-armazenar-dados-imobiliarios-parte-iii/ "Pycursos.com Gileno")
  - [Aprenda Análise de Dados com Python e Pandas](https://www.pycursos.com/pandas/ "Gileno Filho Blog")
  - [Getting started with RethinkDB and Python 3](https://rethinkdb.com/blog/chad-lung-python3/ "Rethinkdb with python3")
