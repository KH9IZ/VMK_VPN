"""Handle timeouts and remove old user from server."""

import logging
import datetime
from datetime import date, timedelta
from wg import WireGuardConfig
from models import User

logger = logging.getLogger("TimeoutsHandlers")

def clear_db(key_remover = WireGuardConfig.remove) -> tuple[set[User], set[User], set[User]]:
    # pylint: disable=not-an-iterable
    """Remove old user from database. Remove their keys from server.

    :return: Tuple where 1st set of Users are users that have
    3 remaining days of subscribing. The second one are users that
    have 1 day remaining. And the last one are users which configs are out.
    """
    result = (set(), set(), set())
    for user in User.select().where(~User.sub_due_date.is_null() & ~User.public_key.is_null()):
        sub_due_date: date = user.sub_due_date
        now: date = datetime.date.today()
        if now < sub_due_date:
            time_left: timedelta = sub_due_date - now
            match time_left.days:
                case 2|3:
                    result[0].add(user)
                case 1:
                    result[1].add(user)
        else:
            key_remover(str(user.public_key))
            user.sub_due_date = None
            logger.info("User subscribtion run out: %s; update database: %d", str(user.id), user.save())
            result[2].add(user)
    return result