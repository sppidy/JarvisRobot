import threading

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import UnicodeText

from jarvis.modules.sql import BASE
from jarvis.modules.sql import SESSION


class APPROVE(BASE):
    __tablename__ = "approved_users"

    user_id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, primary_key=True)

    def __init__(self, user_id, chat_id):
        self.user_id = user_id
        self.chat_id = chat_id

    def __repr__(self):
        return "approved_status for {} in {}".format(self.user_id,
                                                     self.chat_id)


APPROVE.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.RLock()

APPROVED_USERS = []


def is_approved(user_id, chat_id):
    return user_id and chat_id in APPROVED_USERS


def set_APPROVE(user_id, chat_id):
    with INSERTION_LOCK:
        curr = SESSION.query(APPROVE).get(user_id, chat_id)
        if not curr:
            curr = APPROVE(user_id, chat_id)
        else:
            curr.is_approved = True
        SESSION.add(curr)
        SESSION.commit()


def rm_APPROVE(user_id, chat_id):
    with INSERTION_LOCK:
        curr = SESSION.query(APPROVE).get(user_id, chat_id)
        if curr:
            if user_id and chat_id in APPROVED_USERS:
                del APPROVED_USERS[user_id, chat_id]
            SESSION.delete(curr)
            SESSION.commit()
            return True
        SESSION.close()
        return False


def toggle_APPROVE(user_id, chat_id):
    with INSERTION_LOCK:
        curr = SESSION.query(APPROVE).get(user_id, chat_id)
        if not curr:
            curr = APPROVE(user_id, chat_id)
        elif curr.is_approved:
            curr.is_approved = False
        elif not curr.is_approved:
            curr.is_approved = True
        SESSION.add(curr)
        SESSION.commit()


def __load_APPROVE_users():
    global APPROVED_USERS
    try:
        all_APPROVE = SESSION.query(APPROVE).all()
        APPROVED_USERS = {
            user.user_id + " " + user.chat_id
            for user in all_APPROVE if user.is_approved
        }
    finally:
        SESSION.close()


__load_APPROVE_users()
