# coding=utf-8
#
# The MIT License (MIT)
#
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib


def QA_util_send_mail(msg, title, from_user, from_password, to_addr, smtp):
    
    """
    explanation:
        邮件发送	

    params:
        * msg ->:
            meaning: 邮件内容
            type: str
            optional: [null]
        * title ->:
            meaning: 标题
            type: str
            optional: [null]
        * from_user ->:
            meaning: 来自用户
            type: str
            optional: [null]
        * from_password ->:
            meaning: 密码
            type: null
            optional: [null]
        * to_addr ->:
            meaning: 邮件发送地址
            type: null
            optional: [null]
        * smtp ->:
            meaning: smtp地址
            type: null
            optional: [null]

    return:
        None
	
    demonstrate:
        Not described
	
    output:
        Not described
    """
    msg = MIMEText(msg, 'plain', 'utf-8')
    msg['Subject'] = Header(title, 'utf-8').encode()

    server = smtplib.SMTP(smtp, 25)  # SMTP协议默认端口是25
    server.set_debuglevel(1)
    server.login(from_user, from_password)
    server.sendmail(from_user, [to_addr], msg.as_string())



