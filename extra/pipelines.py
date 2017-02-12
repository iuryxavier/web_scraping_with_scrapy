# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

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
#                print("\nCRIANDO A DATABASE E TABELA\n")
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
        print("\nPROCESS ITEM\n")
        r.table('items').insert(item).run(self.conn)
        print(
            "\nlen(DB): {}\n".format(
                len(list(r.table(self.table).run(self.conn)))
            )
        )
        return item
