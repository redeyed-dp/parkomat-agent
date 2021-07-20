from peewee import SqliteDatabase, Model, DateTimeField, IntegerField, CharField, TextField

db = SqliteDatabase('monitoring.db')

class HealthCache(Model):
    time = DateTimeField()
    internet = IntegerField()
    vpn = IntegerField()
    uptime = IntegerField()
    usb = CharField()
    cpu = IntegerField()
    ram = IntegerField()
    hdd = IntegerField()
    api = TextField()
    log = TextField()

    class Meta:
        database = db

    @classmethod
    def notEmpty(self):
        if self.select().count() > 0:
            return True
        return False