# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

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
