#-*- coding: utf-8 -*-;
"""Parser for site: /www.flyniki.com/.
Parser() -- main class
MyIOError -- exception (class) raised when Parser inserted wrong data
"""

import requests
from lxml import html

class Parser(object):

    """class Parser

    Keyword arguments:
    departure -- IATA code.
    destination -- IATA code.
    outbound_date -- departure date (day.month.year  or year-month-day).
    if the day or month are less than 10, then put a '0' in front like '01'
    return_date -- (default '').
    Functions:
    __init__
    get_page -- get html page.
    get_full_url -- make first request to www.flyniki.com.
    get_sesid -- get session ID for final request.
    set_ajax -- The final request for the page.
    find_data -- main func in class.
    """

    oneway = 0
    SESSION = requests.session()

    def __init__(self):
        """ The class constructor has 4 args entered from the keyboard"""
        self.departure = str(raw_input('Departure plase: '))
        self.destination = str(raw_input('Destination plase: '))
        self.outbound_date = str(raw_input('Departure date: '))
        self.return_date = str(raw_input('Return date: '))

    def get_page(self):
        """
        This func check data format and return html page from final request: set_ajax()
        """
        self.outbound_date = self.date_error_checker(self.outbound_date)
        if self.return_date == '':
            self.oneway = 1
            self.return_date = self.outbound_date
        else:
            self.return_date = self.date_error_checker(self.return_date)
        return self.set_ajax()

    def get_full_url(self):
        """
        hit func makes first get request with params to www.flyniki.com
        """
        url = 'http://www.flyniki.com/en/booking/flight/vacancy.php?'
        params = {'departure': self.departure,
                  'destination': self.destination,
                  'outbound_date': self.outbound_date,
                  'return_date': self.return_date,
                  'oneway': self.oneway,
                  'openDateOverview': '0',
                  'adultCount': '1',
                  'childCount': '0',
                  'infantCount': '0'}
        return self.SESSION.get(url, params=params)

    def get_sesid(self):
        """Return url for final request snd session ID into SESSION"""
        url = 'http://www.flyniki.com/static/site/loader/' \
              'nl,js:nzf,jquery%7Cjquery.flightdatepickers,' \
              'jquery%7Cjquery.fancybox.js'
        return self.SESSION.head(url)

    def set_ajax(self):
        """ This final func makes post request and send data."""
        self.oneway = '' if not self.oneway else 'on'
        data = {'_ajax[templates][]' : ['main', 'priceoverview',
                                        'infos', 'flightinfo'],
                '_ajax[requestParams][departure]' : self.departure,
                '_ajax[requestParams][destination]' : self.destination,
                '_ajax[requestParams][returnDeparture]' : '',
                '_ajax[requestParams][returnDestination]' : '',
                '_ajax[requestParams][outboundDate]' : self.outbound_date,
                '_ajax[requestParams][returnDate]' : self.return_date,
                '_ajax[requestParams][adultCount]' : '1',
                '_ajax[requestParams][childCount]' : '0',
                '_ajax[requestParams][infantCount]' : '0',
                '_ajax[requestParams][openDateOverview]' : '',
                '_ajax[requestParams][oneway]' : self.oneway}
        response = self.SESSION.post(self.get_full_url().url, data=data)
        return response.content.replace('\\', '')

    def check_for_errors(self, page):
        errors = page.xpath('//span[@class="debugerrors"]/text()')
        if errors:
            raise Exception('Wrong ' + errors[0][1:-1] + '. Please correct your entry.')

    def date_error_checker(self, date):
        lst = date.split('.')[::-1]
        if int(lst[0]) < 2016 or int(lst[0]) > 2017 \
                or int(lst[1]) > 12 or int(lst[1]) < 1 \
                or int(lst[2]) > 31 or int(lst[2]) < 1:
            raise Exception('date out of range')
        return '-'.join(lst)

    def find_data(self):
        """ This func find data in html page."""
        page = html.fromstring(self.get_page())
        self.check_for_errors(page)
        tables = page.xpath('//div[@id="flighttables"][@class="clearfix"]/div')
        tables = tables[::2] if not self.oneway else tables[::3]
        for table in tables:
            row = table.xpath('.//tbody/tr[contains(@class, "flightrow")]')
            print table.xpath('.//div[@class="vacancy_route"]/text()')[0]
            print '-' * 120
            print '{:^20}{:^20}{:^20}{:^20}{:^20}{:^20}'.format('start_end',
                                                                'flight_time',
                                                                'basePlase EUR',
                                                                'comf_plase EUR',
                                                                'prem_plase EUR',
                                                                'flexPrise EUR')
            print '-' * 120
            for data in row:
                start_end = ' - '.join(data.xpath('.//time/text()'))
                flight_time = data.xpath('.//span[contains(@id, "flightDurationFi_")]/text()')[0]
                base_plase = data.xpath('.//label[contains(@id, "priceLabelIdBASEFi_")]'
                                        '/div[@class="lowest"]/span[contains(@id, "price")]/text()')
                base_plase = "-" if not base_plase else ''.join(base_plase)
                comf_plase = data.xpath('.//label[contains(@id, "priceLabelIdCOMFFi_")]'
                                        '/div[@class="lowest"]/span[contains(@id, "price")]/text()')
                comf_plase = "-" if not comf_plase else ''.join(comf_plase)
                prem_plase = data.xpath('.//label[contains(@id, "priceLabelIdPREMFi_")]'
                                        '/div[@class="lowest"]/span[contains(@id, "price")]/text()')
                prem_plase = "-" if not prem_plase else ''.join(prem_plase)
                flex_prise = data.xpath('.//label[contains(@id, "priceLabelIdFLEXFi_")]'
                                        '/div[@class="lowest"]/span[contains(@id, "price")]/text()')
                flex_prise = ' - ' if not flex_prise else ' - '.join(flex_prise)
                print '{:^20}{:^20}{:^20}{:^20}{:^20}{:^20}'.format(start_end, flight_time,
                                                                    base_plase, comf_plase,
                                                                    prem_plase, flex_prise)
            print '-' * 120


if __name__ == '__main__':
    E_1 = Parser()
    E_1.find_data()