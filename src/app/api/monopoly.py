from fastapi import (APIRouter, Depends, Query, File)
from sqlalchemy.orm import Session
from .. import models
from ..services.auth import get_current_user
from ..database import get_session
from ..services.monopoly import Monopoly, MonopolyParser

router = APIRouter(prefix='/api/v1')


def get_monopoly(session: Session = Depends(get_session)):
    return Monopoly(session=session)


def get_parser_momopoly(session: Session = Depends(get_session)):
    return MonopolyParser(session=session)


@router.get('/monopoly_check')
def check(
        inn: str = Query(..., min_length=10, max_length=12, regex="^[0-9]+$"),
        history: bool = False,
        # user: models.User = Depends(get_current_user),
        monopoly: Monopoly = Depends(get_monopoly)
):
    """
    Метод предназначен для проверки вхождения российской компании в список естественных монополий

    Входные данные:

    - **inn**: регистрационный код ИНН российской компании.
    - **history**: признак использования исторических данных. False - проверяем вхождение на текущий момент, True - проверяем, что когда-либо компания была в списке.  По умолчанию False.

    Выходные данные:

    - status_code 200 - компания находится в списке естественных монополий, status_code 404 - компании нет в списке
    """
    return monopoly.get(inn=inn, history=history)


@router.get('/monopoly_update')
def monopoly_update_data(
        # user: models.User = Depends(get_current_user),
        parser: MonopolyParser = Depends(get_parser_momopoly)
):
    """
    Метод предназначен для обновления списока естестенных монополий с сайта ФАС

    Выходные данные:

    - status_code 200 - обновление прошло успешно, status_code 400 - возникла ошибка при обновлении
    """
    return parser.parser_monopoly()


@router.post("/manual_file_upload/")
def manual_file_upload(
        # user: models.User = Depends(get_current_user),
        parser: MonopolyParser = Depends(get_parser_momopoly),
        file: bytes = File(...)
):
    """
    ## Ручная загрузка списка естестенных монополий
    Загружаем файл EXCEL с фиксированными заголовками. Данные перезаписываются поверх существующих в базе.

    ИНН является ключевым значением по которому проводится проверка, поэтому в случае если в таблице, в поле ИНН
    встретится пустая строка, скрипт завершится с ошибкой **status_code 400** - **"Error parse data"**

    В случае успешного обновления будет получен **status_code 200** и сообщение **Upload success**

    Структура заголовков файла:

    | ИНН  | Реестр   | Раздел  | Номер документа | Регион | Наименование комании | Адрес   | Дата регистрации |
    | ---- | -------- | ------- | --------------- | ------ | -------------------- | ------- | ---------------- |
    | inn  | registry | section | docNumber       | region | companyName          | address | dateFirstReg     |
    """
    return parser.monopoly_upload(file)
