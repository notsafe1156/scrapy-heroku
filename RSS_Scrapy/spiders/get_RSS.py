import scrapy
from RSS_Scrapy.items import RssReader
import psycopg2
import uuid
from scrapy import FormRequest


def get_info(item, rss, id):
    # 　判斷此ID 有無在DataBase，有的話就跳過
    rss['id'] = str(uuid.uuid3(uuid.NAMESPACE_DNS, rss['id'] + item.xpath('guid/text()').extract_first().split('=')[-1]))
    if rss['id'] in id:
        # print('---------------')
        # print(item.xpath('title/text()').extract_first())
        # print('already exist ')
        # print('================')
        return True
    rss['link'] = item.xpath('link/text()').extract_first()
    rss['title'] = item.xpath('title/text()').extract_first()
    categories = item.xpath('category/text()').extract()
    rss['category'] = []
    rss['id'] += item.xpath('guid/text()').extract_first().split('=')[-1]
    #   ID轉為UUID
    for category in categories:
        rss['category'].append(category)
    print(rss['link'])


def process_text(article, item):
    item['text'] = []
    item['images'] = []
    for data in article:
        text = data.xpath('text()').extract()
        if text:
            text = data.xpath('.//text()').extract()
            te = ''.join(text)
            text[0] = te
            item['text'].append(text[0])

        # 找圖片第二種
        if data.xpath('@src'):
            img = data.xpath('@src').extract_first()
            if img[0:4] == 'http':
                item['text'].append('img')
                item['images'].append(img)


# 月份轉換
def map_month(mon):
    return {
        'Jan': '01',
        'Feb': '02',
        'Mar': '03',
        'Apr': '04',
        'May': '05',
        'Jun': '06',
        'Jul': '07',
        'Aug': '08',
        'Sep': '09',
        'Oct': '10',
        'Nov': '11',
        'Dec': '12'
    }.get(mon, 'Non')


def get_tagbypost(self, item):
    return scrapy.Request(url="https://api2.sstrm.net/util/api/dummyAPI",
                          method='POST',
                          headers={
                              'Content-Type': 'application/json'
                          },
                          meta={"id": item['id'],
                                "title": item['title'],
                                "content": item['text'],
                                "url": item['link'],
                                "image": item['images'],
                                "item": item
                                },
                          # meta={"id": "sad",
                          #       "title": "rss['title']",
                          #       "content": "rss['text']",
                          #       "url": "rss['link']",
                          #       "image": "rss['images']"},
                          dont_filter=True,
                          callback=self.after_post)


class RSSpider(scrapy.Spider):
    name = 'RSS'

    def start_requests(self):
        conn = psycopg2.connect(database="d5bohq4onavh67",
                                user="gcrsthkibrpxux",
                                password="f3eb802b01d69e072ad072e7680ae91ff47be8e6af23f58fc4e74be33cf50fd7",
                                host="ec2-54-235-92-244.compute-1.amazonaws.com",
                                port="5432")
        cursor = conn.cursor()
        cursor.execute("select id from data")
        spiders_id = cursor.fetchall()
        conn.close()

        id = []
        for i in spiders_id:
            id.append(i[0])
        # yield scrapy.Request('https://api2.sstrm.net/util/api/dummyAPI', self.get_tagbypost)

        yield scrapy.Request('http://feeds.feedburner.com/yuminghui', self.parse_yuminghui, meta={'id': id})
        yield scrapy.Request('http://feeds.feedburner.com/CommaTravel', self.parse_Commatravel, meta={'id': id})
        yield scrapy.Request('https://www.weekendhk.com/feed/', self.parse_weekendhk, meta={'id': id})
        yield scrapy.Request('https://itravelblog.net/feed/', self.parse_itravelblog, meta={'id': id})
        yield scrapy.Request('https://viablog.okmall.tw/blog/rss.php', self.parse_viablog, meta={'id': id})

    custom_settings = {
        'FEED_EXPORT_ENCODING': 'utf-8',
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'ITEM_PIPELINES': {
            'RSS_Scrapy.pipelines.PostgresqlPipeline': 300
        }
    }

    def after_post(self, response):
        # print(response)
        # print('-------')
        # print(type(response.text))

        item = response.meta['item']
        item['tag'] = response.text.split(':')[2].split('[')[1].split(']')[0]
        # print(item)

        yield item
        # return

    def parse_yuminghui(self, response):
        items = response.xpath('//item')
        id = response.meta['id']
        for item in items:
            rss = RssReader()

            # 此網頁的id開頭
            rss['id'] = 'yu'
            rss['source'] = 'yumingui'
            if get_info(item, rss, id):
                print(rss['id'], ' already exist')
                continue
            time = item.xpath('pubDate/text()').extract_first().split(' ')
            date = [time[3], map_month(time[2]), time[1]]
            rss['time'] = '/'.join(date)

            yield scrapy.Request(
                url=rss['link'], meta={'item': rss}, callback=self.web_yuminghui
            )

    def web_yuminghui(self, response):
        item = response.meta['item']
        item['author'] = 'morries'
        article = response.xpath('//article//p | //article//img')
        process_text(article, item)

        yield get_tagbypost(self, item)

    def parse_Commatravel(self, response):
        items = response.xpath('//item')
        id = response.meta['id']
        for item in items:
            rss = RssReader()

            # 此網頁的id開頭
            rss['id'] = 'c'
            rss['source'] = 'Commatravel'
            if get_info(item, rss, id):
                print(rss['id'], ' already exist')
                continue
            time = item.xpath('pubDate/text()').extract_first().split(' ')
            date = [time[3], map_month(time[2]), time[1]]
            rss['time'] = '/'.join(date)

            yield scrapy.Request(
                url=rss['link'], meta={'item': rss}, callback=self.web_Commatravel
            )

    def web_Commatravel(self, response):
        item = response.meta['item']
        article = response.xpath('//article')
        item['author'] = article.xpath('.//p[@class="post-byline"]//a/text()').extract_first()
        process_text(article.xpath(
            './/div[@class="entry-inner"]//p | '
            './/div[@class="entry-inner"]/child::*[not(@id="wp_rp_first")]//img')
            , item)

        yield get_tagbypost(self, item)

    def parse_weekendhk(self, response):
        items = response.xpath('//item')
        id = response.meta['id']
        for item in items:
            rss = RssReader()

            # 此網頁的id開頭
            rss['id'] = 'whk'
            rss['source'] = 'weekendhk'
            if get_info(item, rss, id):
                print(rss['id'], ' already exist')
                continue
            time = item.xpath('pubDate/text()').extract_first().split(' ')
            date = [time[3], map_month(time[2]), time[1]]
            rss['time'] = '/'.join(date)

            yield scrapy.Request(
                url=rss['link'], meta={'item': rss}, callback=self.web_weekendhk
            )

    def web_weekendhk(self, response):
        item = response.meta['item']
        item['author'] = response.xpath('//a[@itemprop="author"]/text()').extract_first()
        adasia = response.xpath('//div[@class="_content_ AdAsia"]')
        article = adasia.xpath('.//p | .//img | .//figcaption | .//h2')
        process_text(article, item)

        yield get_tagbypost(self, item)

    def parse_itravelblog(self, response):
        items = response.xpath('//item')
        id = response.meta['id']
        for item in items:
            rss = RssReader()

            # 此網頁的id開頭
            rss['id'] = 'it'
            rss['source'] = 'itravelblog'
            if get_info(item, rss, id):
                print(rss['id'], ' already exist')
                continue
            time = item.xpath('pubDate/text()').extract_first().split(' ')
            date = [time[3], map_month(time[2]), time[1]]
            rss['time'] = '/'.join(date)

            yield scrapy.Request(
                url=rss['link'], meta={'item': rss}, callback=self.web_itravelblog
            )

    def web_itravelblog(self, response):
        item = response.meta['item']
        article = response.xpath('//article')
        author = article.xpath('.//span[@class="entry-author"]/a/span/text()').extract_first()
        item['author'] = author
        text = article.xpath('./div[@class="entry-content"]//p |./div[@class="entry-content"]//img')
        process_text(text[0:len(text) - 2], item)

        yield get_tagbypost(self, item)

    def parse_viablog(self, response):
        items = response.xpath('//item')
        id = response.meta['id']
        for item in items:
            rss = RssReader()

            # 此網頁的id開頭
            rss['id'] = 'v'
            rss['source'] = 'viablog'
            if get_info(item, rss, id):
                print(rss['id'], ' already exist')
                continue
            time = item.xpath('pubDate/text()').extract_first()
            date = time[0:4], time[5:7], time[8:10]
            rss['time'] = '/'.join(date)

            yield scrapy.Request(
                url=rss['link'], meta={'item': rss}, callback=self.web_viablog
            )

    def web_viablog(self, response):
        item = response.meta['item']
        author = response.xpath('//div[@class="media-body"]/h4/text()').extract_first()
        item['author'] = author
        item['text'] = []
        item['images'] = []
        article = response.xpath('//div[@id="border-none"]')[1].xpath('div')

        for data in article:
            texts = data.xpath('text() | strong/text() | img')
            text_temp = ''
            for text in texts:
                text_ex = text.extract()
                if text_ex[0:2] != '\r\n':
                    if text.xpath('@src'):
                        img = text.xpath('@src').extract_first()
                        if img[0:4] == 'http':
                            item['text'].append('img')
                            item['images'].append(img)
                    else:
                        text_temp += text_ex
                    continue
                item['text'].append(text_temp)
                text_temp = text_ex.replace('\r\n', '')
            item['text'].append(text_temp)

        yield get_tagbypost(self, item)
