from peewee import AutoField, CharField, BooleanField, DateTimeField, ForeignKeyField
from app.database import BaseModel
from app.models.user import User

class Url(BaseModel):
    id = AutoField()
    user = ForeignKeyField(User, backref='urls')

    short_code = CharField(unique=True)
    original_url = CharField()

    title = CharField(null=True)

    is_active = BooleanField(default=True)

    created_at = DateTimeField(null=True)
    updated_at = DateTimeField(null=True)
