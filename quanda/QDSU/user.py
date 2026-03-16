# coding=utf-8
#
# The MIT License (MIT)
#
from quanda.QDUtil.QALogs import QA_util_log_info
#from quanda.QDARP.QAUser import QA_User
from quanda.QDUtil.QASetting import DATABASE


def QA_user_sign_in(username, password):
    """用户登陆
    不使用 QAUSER库
    只返回 TRUE/FALSE
    """
    #user = QA_User(name= name, password=password)
    cursor = DATABASE.user.find_one(
        {'username': username, 'password': password})
    if cursor is None:
        QA_util_log_info('SOMETHING WRONG')
        return False
    else:
        return True


def QA_user_sign_up(name, password, client):
    """只做check! 具体逻辑需要在自己的函数中实现

    参见:QAWEBSERVER中的实现
    
    Arguments:
        name {[type]} -- [description]
        password {[type]} -- [description]
        client {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """

    coll = client.user
    if (coll.count_documents({'username': name}) > 0):
        print(name)
        QA_util_log_info('user name is already exist')
        return False
    else:
        return True
