#-*- coding: utf-8 -*-

import requests
from lxml import html

class Parser:
    DATA = {'action':'get_schedules',
        'from':'',
        'to':''}

    URL = 'http://www.pobeda.aero/services/flight_schedule'
    session = requests.session()


    def get_iata(self):



        first_page = requests.get(self.URL).content.decode('utf-8')

        page = html.fromstring(first_page)
        table_of_cities = page.xpath('//p/span')

        for city in table_of_cities:
            yield city.get('data-iata')

    def get_data(self):

        for iata in self.get_iata():
            self.DATA['from'] = iata

            r = requests.post(self.URL, data=self.DATA).content

            page = html.fromstring(r.decode('utf-8'))

            table = page.xpath('//div[@class="schedule-table__wrapper"]')

            for i in table:
                data_from = i.get('data-from')
                data_to = i.get('data-to')
                print data_from, '-', data_to
                body = i.xpath('.//table[@class="schedule-table"]//tr')[1:]
                for i in body:
                    row = i.xpath('.//td/text()')
                    print u'First flight: {}   |   Last flight: {}   |   Weekdays: {}'.format(row[1], row[2], row[3])
                print ''



if __name__ == "__main__":
    q = Parser()
    q.get_data()

