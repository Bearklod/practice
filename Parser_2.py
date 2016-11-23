# -*- coding: utf-8 -*-

import requests
from lxml import html

fromStation = 'VKO'
toStation = 'GYD'
beginDate = '25-11-2016'
endDate = '28-11-2016'


class Parser:

    def __init__(self, fromStation, toStation, beginDate, endDate):
        self.fromStation = fromStation
        self.toStation = toStation
        self.beginDate = beginDate
        self.endDate = endDate

    def get_Element_html(self):
        session = requests.session()
        url = 'https://booking.pobeda.aero/ExternalSearch.aspx?marketType=RoundTrip&fromStation={}&toStation={}&beginDate={}&endDate={}&adultCount=1&childrenCount=0&infantCount=0&currencyCode=RUB&utm_source=pobeda&culture=en-US'.format(self.fromStation, self.toStation, self.beginDate, self.endDate)
        r = session.get(url)
        return html.fromstring(r.content)

    def get_data(self):

        page = self.get_Element_html()

        title = page.xpath('//div[@class="header"]/text()')

        print title

        group = page.xpath('//ul[@class="tabsHeader"]/li')
        print '------------------------------------------'
        print '|{:^8}|{:^15}|{:>15}|'.format('day', 'month', 'price')

        print '------------------------------------------'
        for i in group:
            price = i.xpath('.//div[@class="price"]/text()')[0]
            if price != u'——':
                day = i.xpath('.//div[@class="day"]/text()')[0]
                month = i.xpath('.//div[@class="month"]/text()')[0]
                print u'|{:^8}|{:^15}|{:>15}|'.format(day, month, price.strip())
        print '------------------------------------------'


if __name__ == '__main__':
    x = Parser(fromStation, toStation, beginDate, endDate)
    y = Parser('ALA', 'EGO', beginDate, endDate)
    x.get_data()
    y.get_data()







