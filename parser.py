#-*- coding: utf-8 -*-;

"""
parser modul
"""

import requests
from lxml import html


class Parser(object):

    '''
    parser
    '''

    def __init__(self, departure, destination, outbound_date, return_date=''):

        self.departure = departure
        self.destination = destination
        self.outbound_date = outbound_date
        self.return_date = return_date

    def get_page(self):

        """
        get html file
        """

        self.outbound_date = '-'.join(self.outbound_date.split('.')[::-1])

        if self.return_date == '':
            self.return_date = self.outbound_date
        else: self.return_date = '-'.join(self.return_date.split('.')[::-1])

        session = requests.session()

        url = 'http://www.flyniki.com/en/booking/flight/vacancy.php?' \
              'departure={}' \
              '&destination={}' \
              '&outbound_date={}' \
              '&return_date={}' \
              '&oneway=1' \
              '&openDateOverview=0' \
              '&adultCount=1' \
              '&childCount=0' \
              '&infantCount=0'.format(self.departure, self.destination,
                                      self.outbound_date, self.return_date)
        response = session.head(url)
        response_2 = session.get(response.url)
        url_sesid = 'http://www.flyniki.com/static/site/loader/' \
                    'nl,js:nzf,jquery%7Cjquery.flightdatepickers,jquery%7Cjquery.fancybox.js'
        response_3 = session.head(url_sesid)

        data = {'_ajax[templates][]' : ['main', 'priceoverview', 'infos', 'flightinfo'],
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
                '_ajax[requestParams][oneway]' : 'on'}

        response_3 = session.post(response_2.url, data=data)
        return response_3.content.replace('\\', '')

    def find_data(self):

        """
        this func find data in page
        """

        page = html.fromstring(self.get_page())
        row = page.xpath('//tbody/tr[contains(@class, "flightrow")]')

        print page.xpath('//div[@class="vacancy_route"]/text()')[0]
        print '-------------------------------------------------------' \
              '---------------------------------------------------------------'
        print '{:^20}{:^20}{:^20}{:^20}{:^20}{:^20}'.format('start_end', 'flight_time',
                                                            'basePlase EUR', 'comf_plase EUR',
                                                            'prem_plase EUR', 'flexPrise EUR')
        print '-------------------------------------------------------' \
              '---------------------------------------------------------------'

        for data in row:

            start_end = ' - '.join(data.xpath('.//time/text()'))
            flight_time = data.xpath('.//span[contains(@id, "flightDurationFi_")]/text()')[0]
            base_plase = data.xpath('.//label[contains(@id, "priceLabelIdBASEFi_")]'
                                    '/div[@class="lowest"]/span[contains(@id, "price")]/text()')
            if base_plase == []:
                base_plase = "-"
            else: base_plase = ''.join(base_plase)

            comf_plase = data.xpath('.//label[contains(@id, "priceLabelIdCOMFFi_")]'
                                    '/div[@class="lowest"]/span[contains(@id, "price")]/text()')
            if comf_plase == []:
                comf_plase = "-"
            else: comf_plase = ''.join(comf_plase)

            prem_plase = data.xpath('.//label[contains(@id, "priceLabelIdPREMFi_")]'
                                    '/div[@class="lowest"]/span[contains(@id, "price")]/text()')
            if prem_plase == []:
                prem_plase = "-"
            else: prem_plase = ''.join(prem_plase)

            flex_prise = data.xpath('.//label[contains(@id, "priceLabelIdFLEXFi_")]'
                                    '/div[@class="lowest"]/span[contains(@id, "price")]/text()')
            if flex_prise == []:
                flex_prise = ' - '
            elif len(flex_prise) == 2:
                flex_prise = ' - '.join(flex_prise)
            else: flex_prise = ''.join(flex_prise)

            print '{:^20}{:^20}{:^20}{:^20}{:^20}{:^20}'.format(start_end, flight_time,
                                                                base_plase, comf_plase,
                                                                prem_plase, flex_prise)

        print '---------------------------------------------------------' \
              '-------------------------------------------------------------'



if __name__ == '__main__':
    E_1 = Parser('dme', 'prg', '28.11.2016')
    E_2 = Parser('dxb', 'prg', '2016-11-27', '2016-11-30')
    E_1.find_data()
    E_2.find_data()
