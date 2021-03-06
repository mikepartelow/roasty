from peewee import *

_db = Proxy()
def init_db(path_to_db):
    _db.initialize(SqliteDatabase(path_to_db))
    return _db

def as_time(seconds):
    return "{}:{:02d}".format(seconds/60, seconds%60)

class BaseModel(Model):
    id      = PrimaryKeyField(db_column='z_pk')

    class Meta:
        database = _db

class Country(BaseModel):
    name    = CharField(db_column='zname')

    class Meta:
        db_table = 'zcountry'

class Bean(BaseModel):
    country     = ForeignKeyField(Country, db_column='zcountry')
    marketname  = CharField(db_column='zmarketname')
    estate      = CharField(db_column='zestate')
    variety     = CharField(db_column='zvariety')
    inventory   = DecimalField(db_column='zinventory')

    class Meta:
        db_table = 'zbean'

    @property
    def name(self):
        name = u"{} {} {} {}".format(self.country.name,
                                     self.marketname if self.marketname else '',
                                     self.estate if self.estate else '',
                                     self.variety if self.variety else '')

        return ' '.join(name.split())

class Roast(BaseModel):
    timestamp           = TimestampField(db_column='zdate')
    duration            = IntegerField(db_column='zduration')
    first_crack         = IntegerField(db_column='zfirstcrack')
    first_crack_end     = IntegerField(db_column='zfirstcrackend')
    rating              = IntegerField(db_column='zrating')

    @property
    def duration_as_time(self):
        return as_time(self.duration)

    @property
    def first_crack_as_time(self):
        return as_time(self.first_crack)

    @property
    def first_crack_end_as_time(self):
        return as_time(self.first_crack_end)

    @property
    def items(self):
        return RoastedItem.select().join(Roast).where(Roast.id==self.id)

    @property
    def beans(self):
        return map(lambda i: i.bean, self.items)

    class Meta:
        db_table = 'zroast'

class RoastedItem(BaseModel):
    bean        = ForeignKeyField(Bean, db_column='zbean')
    roast       = ForeignKeyField(Roast, db_column='zroast')

    class Meta:
        db_table = 'zroasteditem'

# db.connect()

# for bean in sorted(Bean.select(), key=lambda b: b.name):
#     print(u"{} : {}g".format(bean.name, int(bean.inventory)))