"""Models for interaction with database."""

import peewee

db = peewee.SqliteDatabase('VMK_temp.db')

class User(peewee.Model):
    """Model for each registered user (each who tapped on /start)."""

    id = peewee.BigIntegerField(null=False, index=True, unique=True,
                                primary_key=True, help_text="telegram user_id")
    username = peewee.CharField(null=True, unique=True)
    sub_due_date = peewee.DateField(null=True)
    private_ip = peewee.IPField(null=True, unique=True,
                                constraints=[peewee.Check("sub_due_date IS NOT NULL")])
    mac_address = peewee.FixedCharField(null=True, max_length=64)
    public_key = peewee.FixedCharField(null=True, max_length=64)

    class Meta:  # noqa: D106 pylint: disable=missing-class-docstring
        database = db

class QuestionAnswer(peewee.Model):
    """Model represents question-answer pair in FAQ section."""

    id = peewee.AutoField()
    question = peewee.CharField(null=False)
    answer = peewee.TextField(null=True)

    class Meta:  # noqa: D106 pylint: disable=missing-class-docstring
        database = db

if __name__ == "__main__":
    db.connect()
    db.create_tables([User, QuestionAnswer], safe=True)
    db.close()
