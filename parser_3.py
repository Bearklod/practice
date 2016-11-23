#-*- coding: utf-8 -*-

import requests
from lxml import html

class Parser(object):

    """parser class have 2 func:
    1. get_iata
    2. get_data
    """

    DATA = {'action':'get_schedules', 'from':'', 'to':''}
    URL = 'http://www.pobeda.aero/services/flight_schedule'

    session = requests.session()

    def get_iata(self):

        """get IATA codes from started page"""

        first_page = requests.get(self.URL).content.decode('utf-8')

        page = html.fromstring(first_page)
        table_of_cities = page.xpath('//p/span')

        for city in table_of_cities:
            yield city.get('data-iata')

    def get_data(self):

        """get data from page"""

        for iata in self.get_iata():
            self.DATA['from'] = iata

            response = requests.post(self.URL, data=self.DATA).content

            page = html.fromstring(response.decode('utf-8'))

            table = page.xpath('//div[@class="schedule-table__wrapper"]')

            for i in table:
                data_from = i.get('data-from')
                data_to = i.get('data-to')
                print data_from, '-', data_to
                body = i.xpath('.//table[@class="schedule-table"]//tr')[1:]
                for i in body:
                    row = i.xpath('.//td/text()')
                    print u'First flight: {}   |' \
                          u'   Last flight: {}   |' \
                          u'   Weekdays: {}'.format(row[1], row[2], row[3])
                print ''



if __name__ == "__main__":
    E_1 = Parser()
    E_1.get_data()