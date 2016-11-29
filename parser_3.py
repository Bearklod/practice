#-*- coding: utf-8 -*-
"""
This module get data on flights from http://www.pobeda.aero/
have main class Parser
"""

import requests
from lxml import html

class Parser(object):
    """
    This class have 2 func:
    get_IATA -- method get IATA codes from site
    get_data -- method iterates IATA codes and get data for each
    """
    try:
        DATA = {'action':'get_schedules', 'from':'', 'to':''}
        URL = 'http://www.pobeda.aero/services/flight_schedule'
        def get_IATA(self):
            """This method get IATA codes from started page and return these as generator"""
            first_page = requests.get(self.URL).content.decode('utf-8')
            page = html.fromstring(first_page)
            table_of_cities = page.xpath('//p/span')
            for city in table_of_cities:
                yield city.get('data-iata')

        def get_data(self):
            """
            Get IAGA from get_IATA() in iterator for iata in self.get_IATA(),
            and return data for each.
            """
            for iata in self.get_IATA():
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
                        print u'First flight: {:<10} | ' \
                              u'Last flight: {:^12} | ' \
                              u'Weekdays: {:<15}'.format(row[1], row[2], row[3])
                    print ''
    except:
        print 'was something strange'

if __name__ == "__main__":
    E_1 = Parser()
    E_1.get_data()