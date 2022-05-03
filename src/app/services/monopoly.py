import re, io
import pylightxl as xl
from fastapi import (HTTPException, status)
from datetime import datetime
from requests import Session as Session_request
from bs4 import BeautifulSoup
from lxml import etree
from .. import tables
from ..settings import settings, LOGGER


class Monopoly:
    """ Класс проверки наличия компании в списке монополий (в нашей базе) """

    def __init__(self, session):
        self.session = session

    def _get(self, inn: str, history: bool):
        """ Проверяем (в нашей базе) наличие компании в списке монополий """
        if history:
            # проверяем была ли компания когла-либо в списке монополий
            return self.session.query(tables.Monopoly) \
                .filter(tables.Monopoly.inn == inn, ) \
                .first()
        else:
            # проверяем сейчас есть в списке монополий
            return self.session.query(tables.Monopoly) \
                .filter(tables.Monopoly.inn == inn) \
                .filter(tables.Monopoly.removeDate == None) \
                .first()

    def get(self, inn: str, history: bool) -> tables.Monopoly:
        """ Основной метод проверки наличие компании в списке монополий """
        company = self._get(inn, history)
        if company is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        else:
            return company


class MonopolyParser:
    """ Класс парсинга данных с сайта ФАС - списка естественных монополий """

    def __init__(self, session):
        self.session = session

    def _get_token_from_cookies(self, cookies: str):
        """ Получаем токен из cookies """
        soup = BeautifulSoup(cookies, 'html.parser')
        el = soup.find("input", {"name": "__RequestVerificationToken"})
        try:
            token = el['value']
        except:
            return None
        return token

    def _get_monopoly_data(self):
        """ Получаем данные с сайта ФАС """
        session_requests = Session_request()
        exception = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Error get data from site',
            headers={'WWW-Authenticate': 'Bearer'},
        )
        headers1 = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'apps.eias.fas.gov.ru',
            'Pragma': 'no-cache',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
        }

        # Получаем cookies и извлекаем токен авторизации
        data = session_requests.get(url=settings.cookies_url_fas, headers=headers1)
        if data.status_code != 200:
            raise exception
        token = self._get_token_from_cookies(data.text)
        if token is None:
            raise exception

        # формируем тело и заголовки запроса для получения списка монополий
        payload = {
            '__RequestVerificationToken': token,
            'RegTypeID': 0,
            'RegPartID': 0,
            'RegionID': 0,
            'OrgName': '',
            'INN': '',
            'OKPO': '',
            'OGRN': '',
        }
        headers2 = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Host': 'apps.eias.fas.gov.ru',
            # 'Origin': 'http://apps.eias.fas.gov.ru',
            'Referer': 'http://apps.eias.fas.gov.ru/FindCem/',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }

        # Получаем таблицу со списком естественных монополий
        data = session_requests.post(url=settings.url_fas, headers=headers2, data=payload)
        if data.status_code != 200:
            raise exception
        return data.text

    def parser_monopoly(self):
        """ Основной метод парсинга данных с сайта ФАС - списка естественных монополий """

        # Фиксируем начало процесса
        start_time = datetime.now()

        exception = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Error parse data',
            headers={'WWW-Authenticate': 'Bearer'},
        )

        # Получаем данные с сайта ФАС
        data = self._get_monopoly_data()

        # Извлекаем табличный список
        htmlparser = etree.HTMLParser()
        tree = etree.fromstring(data, htmlparser)
        all_data_list = tree.xpath('//tbody/tr')

        # Проверяем, что получили данные (в списке должно быть более 1000 записей)
        if len(all_data_list) < 1000:
            LOGGER.info('Resive data not containt >1000 items')
            raise exception

        # Обрабатываем список
        for number, item in enumerate(all_data_list):
            try:
                company_name = item.xpath('.//td[5]/text()')[0]
                registry = item.xpath('.//td[1]/text()')[0]
                section = item.xpath('.//td[2]/text()')[0]
                doc_number = item.xpath('.//td[3]/text()')[0]
                region = item.xpath('.//td[4]/text()')[0]
                address = item.xpath('.//td[7]/text()')[0]
                # order_number = item.xpath('.//td[8]/text()')[0]
                order_date = item.xpath('.//td[9]/text()')[0]
                inn_raw = item.xpath('.//td[6]/nobr/div[contains(text(), "ИНН")]/text()')
            except:
                LOGGER.info('Error parse items - number s%', str(number))
                raise exception

            # Пропускаем строку в таблице, если в поле где должен быть ИНН - пусто
            if len(inn_raw) == 0:
                continue

            # Извлекаем ИНН
            try:
                inn = re.sub(re.compile(r'(^\w+:\s*)'), '', inn_raw[0])
            except:
                LOGGER.info('Error get INN - number s%', str(number))
                raise exception

            # Проверяем что ИНН похож на правильный
            if ((len(inn) == 10) | (len(inn) == 12)) is False:
                LOGGER.info(f'Error len INN != 10 or != 12 {inn}')
                continue

            # Формируем данные для записи в базу
            full_fas_dict = {
                'inn': inn,
                'companyName': company_name,
                'registry': registry,
                'section': section,
                'docNumber': doc_number,
                'region': region,
                'address': address,
                'dateFirstReg': datetime.strptime(order_date, "%d.%m.%Y").date(),
                'lastCheck': datetime.now()
            }
            LOGGER.debug('Parse company: %s ', full_fas_dict)

            # ИНН ранее был в базе ?
            if (self.session.query(tables.Monopoly)
                    .filter(tables.Monopoly.inn == inn)
                    .first()) is None:
                # ИНН новый, добавляем запись в базу
                self.session.add(tables.Monopoly(**full_fas_dict))
                self.session.commit()
            else:
                # ИНН уже есть, обновляем дату последней проверки
                self.session.query(tables.Monopoly) \
                    .filter(tables.Monopoly.inn == inn) \
                    .update({tables.Monopoly.lastCheck: datetime.now()})
                self.session.commit()

        # Для всех записей, которые "пропали" при очередной проверке - фиксируем текущую дату
        self.session.query(tables.Monopoly) \
            .filter(tables.Monopoly.lastCheck < start_time) \
            .filter(tables.Monopoly.removeDate == None) \
            .filter(tables.Monopoly.manualUpload != True) \
            .update({tables.Monopoly.removeDate: datetime.now()})
        self.session.commit()

        return "Update monopoly list successfully"

    def monopoly_upload(self, file):
        """ Метод ручной загрузки списка естественных монополий из файла Excel """

        exception = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Error parse data',
            headers={'WWW-Authenticate': 'Bearer'},
        )

        # Преобразует передаваемый файл из буфера памяти в читаемый файл для дальнейшей обработки
        to_excel = io.BytesIO()
        to_excel.write(file)
        to_excel.seek(0)

        # Считываем данные файла
        excel = xl.readxl(to_excel)

        # Список заголовков базы данных для проверки корректности наименований в файле excel
        db_fields = ['inn', 'companyName', 'registry', 'section', 'docNumber', 'region', 'address', 'dateFirstReg',
                     'manualUpload']

        # Циклом проходим по строкам файла и формируем словарь для записи в базу данных.
        # В случае отсутствия какой либо колонки в файле, структура не изменится поскольку задаётся словарём.
        # На месте отсутствующих значений будет записан null
        # Если отсутствует ИНН выполнение остановится с ошибкой
        excel_header = {}
        for col in excel.ws(excel.ws_names[0]).cols:
            if col[0] in db_fields:
                excel_header[col[0]] = col[0]
            else:
                LOGGER.info('Incorrect headers in excel file')
                raise exception
        excel_header['manualUpload'] = True

        for row in excel.ws(excel.ws_names[0]).rows:
            row.append(True)
            if (row != list(excel_header.values())):

                for i, key in enumerate(excel_header):
                    if key == 'dateFirstReg':
                        excel_header[key] = datetime.strptime(row[i], "%d.%m.%Y").date()
                    else:
                        excel_header[key] = row[i]

                inn = excel_header['inn']

                if excel_header['inn'] != "":
                    # Проверяем что ИНН похож на правильный
                    if ((len(str(inn)) == 10) | (len(str(inn)) == 12)) is False:
                        LOGGER.info(f'Error len INN != 10 or != 12 {inn}')
                        continue

                    if (self.session.query(tables.Monopoly)
                            .filter(tables.Monopoly.inn == str(inn))
                            .first()) is None:
                        self.session.add(tables.Monopoly(**excel_header))
                        self.session.commit()
                    else:
                        self.session.query(tables.Monopoly) \
                            .filter(tables.Monopoly.inn == str(inn)) \
                            .update({**excel_header})
                        self.session.commit()
                else:
                    LOGGER.info('Blank INN field')
                    raise exception

        return HTTPException(status_code=200, detail="Upload success")
