"""Models for interaction with database."""

import peewee

db = peewee.SqliteDatabase('VMK_temp.db')

class User(peewee.Model):
    """Model for each registered user (each who tapped on /start)."""

    id = peewee.BigIntegerField(null=False, index=True, unique=True,
                                primary_key=True, help_text="telegram user_id")
    username = peewee.CharField(null=True, unique=True)
    sub_due_date = peewee.DateField(null=True)
    private_ip = peewee.IPField(null=True, unique=True)
    mac_address = peewee.FixedCharField(null=True)
    lang = peewee.FixedCharField(max_length=2, null=False, default="ru")

    class Meta:  # pylint: disable = too-few-public-methods, missing-class-docstring
        # noqa: D106  # Disable error with docstrings.
        database = db

class QuestionAnswer(peewee.Model):
    """FAQ data."""

    id = peewee.PrimaryKeyField()
    question = peewee.CharField(null=False)
    answer = peewee.TextField(null=True)

    class Meta:  # pylint: disable = too-few-public-methods, missing-class-docstring
        # noqa: D106  # Disable error with docstrings.
        database = db

if __name__ == "__main__":
    db.connect()
    db.create_tables([User, QuestionAnswer], safe=True)
    db.close()
