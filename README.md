# Web Scraping with Scrapy

## Desenvolvedor de Web Scraping Utilizando Scrapy

### arquivo: /extra/pipelines.py

```python3
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
