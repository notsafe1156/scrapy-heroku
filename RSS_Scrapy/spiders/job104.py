import time
import scrapy


class JobItem(scrapy.Item):
    job_name = scrapy.Field()
    company = scrapy.Field()
    job_list = scrapy.Field()
    job_list_item = scrapy.Field()
    job_request = scrapy.Field()


class JobSpider(scrapy.Spider):
    name = 'job104'
    allowed_domains = ['104.com.tw']
    start_urls = [
        'https://www.104.com.tw/jobs/search/?ro=0&jobcat=2007000000&order=11&asc=0&page=1&mode=s&jobsource=2018indexpoc']
    custom_settings = {
        'FEED_EXPORT_ENCODING': 'utf-8',
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True
    }

    def parse(self, response):
        for i in range(1, 10):
            url = "https://www.104.com.tw/jobs/search/?ro=0&jobcat=2007000000&order=11&asc=0&page=" + \
                  str(i) + "&mode=s&jobsource=2018indexpoc"
            yield scrapy.Request(
                url, callback=self.get_job_link
            )

    def get_job_link(self, response):
        jobs = response.xpath('//div[@id="js-job-content"]/article')
        for job in jobs:
            link = 'http:' + job.xpath("div[1]/h2/a/@href").extract()[0]

            request = scrapy.Request(
                link,
                callback=self.get_job,
            )
            yield request

    def get_job(self, response):
        item = JobItem()
        job_contant = response.xpath("//div[@id='job']/article")

        item['job_name'] = job_contant.xpath("header/div/h1/text()").extract()[0].strip()
        item['company'] = job_contant.xpath("header/div/h1/span/a[1]/text()").extract()[0].strip()
        item['job_list'] = job_contant.xpath("div[@class='grid-left']/main/section[1]/div/p/text()").extract()
        item['job_list_item'] = []
        item['job_request'] = []

        for list in job_contant.xpath("div[@class='grid-left']/main/section[1]/div/dl/*"):
            list_item = list.xpath("text()").extract_first().strip()
            if list_item:
                item['job_list_item'].append(list_item)
            else:
                item['job_list_item'].append(list.xpath("descendant::span/text()").extract())

        for requset in job_contant.xpath("div[@class='grid-left']/main/section[2]/div/dl/*"):
            requset_item = requset.xpath("text()").extract_first()
            if requset_item and requset_item != '、':
                item['job_request'].append(requset_item)
            elif item['job_request'][-1] == '語文條件：':
                i = requset.xpath("descendant::*/text()").extract()
                item['job_request'].append(i[1] + i[2])
            elif item['job_request'][-1] == '擅長工具：':
                item['job_request'].append(requset.xpath("descendant::a/text()").extract())
        yield item
