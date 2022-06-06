import scrapy
import logging
import datetime
from decouple import config

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from urllib3.connectionpool import log
try:
    from importlib import resources
except ImportError:
    import importlib_resources as resources

from ..items import BonBanhRawItem

log.setLevel(logging.WARNING)


class BonbanhSpider(scrapy.Spider):
    name = 'bonbanh'
    allowed_domains = ['bonbanh.com']
    start_urls = ['http://bonbanh.com/']

    def __init__(self):
        super(BonbanhSpider, self).__init__()
        with resources.open_text('crawler.spiders', 'url_list.txt') as file:
            url_list = file.readlines()
        url_list = [url.strip('\n') for url in url_list]
        self.start_urls = url_list
        self.num_ood_posts = 0

        self.mode = config('MODE')
        self.app_id = config('APP_ID')
        self.api_key = config('API_KEY')
        self.collection = config('COLLECTION')
        self.database = config('DATABASE')
        self.datasource = config('DATASOURCE')

    @staticmethod
    def _extract_page(page_info: str):
        page_info = page_info.replace('Trang', '')
        page_info = page_info.replace('(', '')
        page_info = page_info.strip()
        words = page_info.split('/')
        words = [w.strip() for w in words if w != '']
        numbers = [int(w) for w in words if w.isdigit()]

        if len(numbers) == 2:
            return numbers[0], numbers[1]
        else:
            return None, None

    def parse(self, response):
        item_url_list = response.css('li.car-item a::attr(href)').getall()
        year_list = response.css('li.car-item div.cb1 b::text').getall()
        price_list = response.css('li.car-item div.cb3 b::attr(content)').getall()
        location_list = response.css('li.car-item div.cb4 b::text').getall()
        title_list = response.css('li.car-item div.cb2_02 h3::text').getall()

        actual_curr_page: str = response.url.split(',')[-1].strip()
        actual_curr_page = int(actual_curr_page) if actual_curr_page.isdigit() else None

        page_info: str = response.css('div.cpage::text').get()
        curr_page, max_page = self._extract_page(page_info=page_info)

        if actual_curr_page is not None and curr_page == actual_curr_page:
            for i in range(len(item_url_list)):
                item_url = item_url_list[i]
                new_url = response.urljoin(item_url)

                data: dict = {
                    'year': year_list[i],
                    'price': price_list[i],
                    'location': location_list[i],
                    'title': title_list[i]
                }

                yield scrapy.Request(url=new_url, callback=self.parse_info, cb_kwargs=data)

            next_page = curr_page + 1
            if next_page <= max_page:
                next_page_url = response.url.split(',')[0] + ',{}'.format(next_page)

                if self.num_ood_posts <= self.settings['MAX_OOD_POSTS']:
                    yield scrapy.Request(url=next_page_url, callback=self.parse)

    @staticmethod
    def parse_info(response, **kwargs):

        url = response.url
        title = kwargs['title']
        year = kwargs['year']
        price = kwargs['price']
        location = kwargs['location']

        raw_post_date = response.css('div.notes::text').get()

        car_info_list = response.css('div.breadcrum span[itemprop="name"] strong::text').getall()
        branch, model = None, None
        if len(car_info_list) == 3:
            branch = car_info_list[0]
            model = car_info_list[1]

        detail_car = []
        detail_car_info = []

        rows_list = response.css('div.row')
        for row_item in rows_list:
            key = row_item.css('div.label label::text').get()
            key = key.replace(u'\xa0', u' ').strip('\t :')

            value = row_item.css('div.txt_input span::text').get()
            value = value.strip(' \t')

            if key is not None and value is not None:
                detail_car.append(key)
                detail_car_info.append(value)

        if 'Số chỗ ngồi' in detail_car:
            detail_car.remove('Số chỗ ngồi')

        raw_origin = None
        if 'Xuất xứ' in detail_car:
            idx = detail_car.index('Xuất xứ')
            raw_origin = detail_car_info[idx]

        raw_km_driven = None
        if 'Số Km đã đi' in detail_car:
            idx = detail_car.index('Số Km đã đi')
            raw_km_driven = detail_car_info[idx]

        external_color = None
        if 'Màu ngoại thất' in detail_car:
            idx = detail_car.index('Màu ngoại thất')
            external_color = detail_car_info[idx]

        internal_color = None
        if 'Màu nội thất' in detail_car:
            idx = detail_car.index('Màu nội thất')
            internal_color = detail_car_info[idx]

        num_seats = response.css('div.col div#mail_parent div.inputbox span.inp::text').get()

        engine_info = None
        if 'Động cơ' in detail_car:
            idx = detail_car.index('Động cơ')
            engine_info = detail_car_info[idx]

        gearbox = None
        if 'Hộp số' in detail_car:
            idx = detail_car.index('Hộp số')
            gearbox = detail_car_info[idx]

        wheel_drive = None
        if 'Dẫn động' in detail_car:
            idx = detail_car.index('Dẫn động')
            wheel_drive = detail_car_info[idx]

        car_type = None
        if 'Dòng xe' in detail_car:
            idx = detail_car.index('Dòng xe')
            car_type = detail_car_info[idx]

        raw_item = BonBanhRawItem(
            title=title,
            url=url,
            year=year,
            price=price,
            location=location,
            branch=branch,
            model=model,
            raw_origin=raw_origin,
            raw_km_driven=raw_km_driven,
            external_color=external_color,
            internal_color=internal_color,
            num_seats=num_seats,
            engine_info=engine_info,
            gearbox=gearbox,
            wheel_drive=wheel_drive,
            car_type=car_type,
            raw_post_date=raw_post_date
        )

        return raw_item


if __name__ == '__main__':
    setting = get_project_settings()
    process = CrawlerProcess(get_project_settings())
    process.crawl(BonbanhSpider)
    process.start()
