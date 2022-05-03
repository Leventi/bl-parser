from sqlalchemy import (Column, Date, Integer, String, MetaData, DateTime, Boolean)
from sqlalchemy.ext.declarative import declarative_base


convention = {
    'all_column_names': lambda constraint, table: '_'.join([
        column.name for column in constraint.columns.values()
    ]),
    'ix': 'ix__%(table_name)s__%(all_column_names)s',
    'uq': 'uq__%(table_name)s__%(all_column_names)s',
    'ck': 'ck__%(table_name)s__%(constraint_name)s',
    'fk': (
        'fk__%(table_name)s__%(all_column_names)s__'
        '%(referred_table_name)s'
    ),
    'pk': 'pk__%(table_name)s'
}

metadata = MetaData(naming_convention=convention)

Base = declarative_base(metadata=metadata)


class Monopoly(Base):
    __tablename__ = 'monopoly'

    id = Column(Integer, primary_key=True)
    inn = Column(String(12), unique=True)
    companyName = Column(String(512))
    registry = Column(String(512))
    section = Column(String(512))
    docNumber = Column(String(13))
    region = Column(String(512))
    address = Column(String(512))
    dateFirstReg = Column(Date)
    lastCheck = Column(DateTime)
    removeDate = Column(DateTime)
    manualUpload = Column(Boolean, default=None)
