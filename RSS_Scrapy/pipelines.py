# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import psycopg2


class RssScrapyPipeline(object):
    def process_item(self, item, spider):
        return item


class PostgresqlPipeline(object):

    def process_item(self, item, spider):
        conn = psycopg2.connect(database="d5bohq4onavh67",
                                user="gcrsthkibrpxux",
                                password="f3eb802b01d69e072ad072e7680ae91ff47be8e6af23f58fc4e74be33cf50fd7",
                                host="ec2-54-235-92-244.compute-1.amazonaws.com",
                                port="5432")
        # conn = psycopg2.connect(database="d7jtuha77ma0q1",
        #                         user="eklmwiezzzuyfz",
        #                         password="12e338a1e992399d0b57bfce5691f20aafa834a9f439291701761a6d2289007c",
        #                         host="ec2-184-73-232-93.compute-1.amazonaws.com",
        #                         port="5432")
        cursor = conn.cursor()
        insert_sql = """ insert into data (id, title, time, link, author, text, images, category, tag, display, source)
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
        cursor.execute(insert_sql,
                       (
                           item['id'],
                           item['title'],
                           item['time'],
                           item['link'],
                           item['author'],
                           item['text'],
                           item['images'],
                           item['category'],
                           item['tag'],
                           't',
                           item['source'],))

        conn.commit()

        conn.close()
