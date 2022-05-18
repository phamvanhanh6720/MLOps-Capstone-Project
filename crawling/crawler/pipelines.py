import dataclasses
import datetime
import time
import hashlib
import pandas as pd

from .spiders.bonbanh import BonbanhSpider
from .items import BonBanhRawItem, BonBanhItem
from .upload import upload_document, replace_document


class BonBanhPipeline:
    @staticmethod
    def _replace_all(text, dic):
        for i, j in dic.items():
            text = text.replace(i, j)

        return text

    def _normalize_car_type(self, car_type):
        car_type = car_type.lower()
        replacer = {
            'crossover': 'crossover',
            'suv': 'suv',
            'sedan': 'sedan',
            'convertible/cabriolet': 'convertible',
            'coupe': 'coupe',
            'hatchback': 'hatchback',
            'van/minivan': 'van',
            'bán tải / pickup': 'pickup',
            'wagon': 'wagon'
        }
        car_type = self._replace_all(car_type, replacer)

        return car_type

    def _normalize_fuels(self, fuels):
        replacer = {
            'Xăng': 'gasoline',
            'Dầu': 'diesel',
            'Diesel': 'diesel',
            'Hybrid': 'hybrid',
            'Điện': 'electric'
        }
        fuels = self._replace_all(fuels, replacer)

        return fuels

    @staticmethod
    def _normalize_km_driven(raw_km_driven):
        km_driven = None
        words = raw_km_driven.split(' ')
        words = [w.strip().replace(',', '') for w in words]

        numbers = []
        for w in words:
            try:
                numbers.append(float(w))
            except:
                pass
        if len(numbers):
            km_driven = numbers[0]

        return km_driven

    def _normalize_gearbox(self, gearbox):
        replacer = {
            'Số tự động': 'automatic',
            'Số tay': 'manual'
        }
        gearbox = self._replace_all(gearbox, replacer)

        return gearbox

    def _normalize_origin(self, origin):
        replacer = {
            'Nhập khẩu': 'imported',
            'nhập khẩu': 'imported',
            'Lắp ráp trong nước': 'domestic'
        }
        origin = self._replace_all(origin, replacer)

        return origin

    @staticmethod
    def _normalize_wheel_drive(raw_wheel_drive):
        wheel_drive = None
        if raw_wheel_drive is not None:
            wheel_drive = raw_wheel_drive.split('-')[0].strip(' ')
            wheel_drive = wheel_drive.replace('RFD', "RWD")

        return wheel_drive

    @staticmethod
    def _normalize_post_date(raw_post_date):
        raw_post_date = raw_post_date.replace('\t', ' ')
        post_date = raw_post_date.split(' ')[2].strip()
        post_date = datetime.datetime.strptime(post_date, '%d/%m/%Y').date()

        return post_date

    def process_item(self, item: BonBanhRawItem, spider: BonbanhSpider) -> BonBanhItem:
        car_type = item.car_type
        car_type = self._normalize_car_type(car_type)

        engine_info = item.engine_info.replace('\t', ' ')
        # print(engine_info)
        fuels, engine_capacity = None, None
        if engine_info is not None:
            fuels = engine_info.split(' ')[0]
            fuels = self._normalize_fuels(fuels)

            try:
                engine_capacity = engine_info.split(' ')[1].replace(',', '.')
                engine_capacity = float(engine_capacity)
            except:
                engine_capacity = None

        raw_km_driven = item.raw_km_driven
        km_driven = self._normalize_km_driven(raw_km_driven)

        gearbox = item.gearbox
        gearbox = self._normalize_gearbox(gearbox)

        raw_origin = item.raw_origin
        origin = self._normalize_origin(raw_origin)

        wheel_drive = item.wheel_drive
        wheel_drive = self._normalize_wheel_drive(wheel_drive)

        price = item.price
        if isinstance(price, str):
            price = float(price)
            price = price / 1e6

        year = int(item.year) if item.year is not None else None
        num_seats = item.num_seats
        if isinstance(num_seats, str):
            num_seats = num_seats.replace('chỗ', '').strip()
            try:
                num_seats = int(num_seats)
            except:
                num_seats = None

        raw_post_date = item.raw_post_date
        post_date = self._normalize_post_date(raw_post_date)

        data = BonBanhItem(
            title=item.title,
            url=item.url,
            year=year,
            price=price,
            location=item.location,
            branch=item.branch,
            model=item.model,
            origin=origin,
            km_driven=km_driven,
            external_color=item.external_color,
            internal_color=item.internal_color,
            num_seats=num_seats,
            fuels=fuels,
            engine_capacity=engine_capacity,
            gearbox=gearbox,
            wheel_drive=wheel_drive,
            car_type=car_type,
            post_date=post_date
        )

        # save data
        curr_date = datetime.date.today()
        if spider.mode == 'all':
            try:
                upload_document(
                    app_id=spider.app_id,
                    api_key=spider.api_key,
                    database=spider.database,
                    collection=spider.collection,
                    data_source=spider.datasource,
                    document=dataclasses.asdict(data)
                )
                spider.logger.info("Saved items to mongodb")

            except:
                replace_document(
                    app_id=spider.app_id,
                    api_key=spider.api_key,
                    database=spider.database,
                    collection=spider.collection,
                    data_source=spider.datasource,
                    filter={"url": data.url},
                    replacement=dataclasses.asdict(data)
                )
                spider.logger.info("Item is updated in the database")

            return data

        else:
            if (curr_date - post_date).days == 1:
                try:
                    upload_document(
                        app_id=spider.app_id,
                        api_key=spider.api_key,
                        database=spider.database,
                        collection=spider.collection,
                        data_source=spider.datasource,
                        document=dataclasses.asdict(data)
                    )
                    spider.logger.info("Saved items to mongodb")

                except:
                    replace_document(
                        app_id=spider.app_id,
                        api_key=spider.api_key,
                        database=spider.database,
                        collection=spider.collection,
                        data_source=spider.datasource,
                        filter={"url": data.url},
                        replacement=dataclasses.asdict(data)
                    )
                    spider.logger.info("Item is updated in the database")

                return data

            else:
                if (curr_date - post_date).days > 1:
                    spider.num_ood_posts += 1
                    spider.logger.info('Ignore out of date post')

                    return data
                else:
                    spider.logger.info('Ignore posts today')

                    return data