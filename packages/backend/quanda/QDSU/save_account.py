# coding:utf-8
#
# The MIT License (MIT)
#
from pymongo import DESCENDING, ASCENDING
from quanda.QDUtil import DATABASE
"""对于账户的增删改查(QAACCOUNT/QAUSER/QAPORTFOLIO)
"""


def save_account(message, collection=DATABASE.account):
    """save account

    Arguments:
        message {[type]} -- [description]

    Keyword Arguments:
        collection {[type]} -- [description] (default: {DATABASE})
    """
    try:
        collection.create_index(
            [("account_cookie", ASCENDING), ("user_cookie", ASCENDING), ("portfolio_cookie", ASCENDING)], unique=True)
    except:
        pass
    collection.update_one(
        {'account_cookie': message['account_cookie'], 'portfolio_cookie':
            message['portfolio_cookie'], 'user_cookie': message['user_cookie']},
        {'$set': message},
        upsert=True
    )


def update_account(mes, collection=DATABASE.account):
    """update the account with account message

    Arguments:
        mes {[type]} -- [description]

    Keyword Arguments:
        collection {[type]} -- [description] (default: {DATABASE})
    """

    collection.find_one_and_update({'account_cookie': mes['account_cookie']})


def save_riskanalysis(message, collection=DATABASE.risk):
    # print(message)

    try:
        collection.create_index(
            [("account_cookie", ASCENDING), ("user_cookie", ASCENDING), ("portfolio_cookie", ASCENDING)], unique=True)
    except:
        pass
        
    collection.update_one(
        {'account_cookie': message['account_cookie'], 'portfolio_cookie':
            message['portfolio_cookie'], 'user_cookie': message['user_cookie']},
        {'$set': message},
        upsert=True
    )

