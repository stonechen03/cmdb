#!/usr/bin/env python
# coding:utf-8
__author__ = 'stone'
__date__ = '2017/11/28'

from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import smtplib

from conf import conf

log = logging.getLogger('django')


class Mail(object):
    """
    批量发送邮件
    """

    def __init__(self, subject, text, receivers=None):
        self.subject = subject
        self.text = text
        self.file = None
        self.receivers = receivers

        self.host = conf.EMAIL_HOST
        self.port = conf.EMAIL_PORT
        self.timeout = conf.EMAIL_TIMEOUT
        self.user = conf.EMAIL_HOST_USER
        self.passwd = conf.EMAIL_HOST_PASSWORD
        self.form = conf.EMAIL_FORM_USER
        self.ssl = conf.EMAIL_USE_SSL
        if self.ssl:
            self.smtpObj = smtplib.SMTP_SSL()
        else:
            self.smtpObj = smtplib.SMTP()

        self.message = MIMEMultipart()
        self.message.attach(MIMEText(self.text, 'plain', 'utf-8'))
        self.message['Subject'] = Header(self.subject)
        self.message['From'] = self.form

        if isinstance(self.receivers, list):
            self.message['To'] = ','.join(self.receivers)
        else:
            raise TypeError

    def send_file(self):
        """发送附件
        :return:
        """

        if self.file is not None and isinstance(self.file, list):
            for filename in self.file:
                if filename != '':
                    with open(filename, 'rb') as f:
                        mime = MIMEBase('text', 'txt', filename=filename)
                        mime.add_header('Content-Disposition', 'attachment', filename=filename.split('/')[-1])
                        mime.set_payload(f.read())
                        encoders.encode_base64(mime)
                        self.message.attach(mime)

    def send_mail(self):
        """
        发送正文
        :return:
        """

        try:
            self.smtpObj.timeout = self.timeout
            self.smtpObj.connect(self.host, self.port)
            self.smtpObj.login(self.user, self.passwd)
            log.debug('send mail: {}:{}  user:{}, passwd:{}'.format(self.host, self.port, self.user, self.passwd))
            self.smtpObj.sendmail(self.user, self.receivers, self.message.as_string())
            self.smtpObj.quit()
            self.smtpObj.close()
            return True
        except smtplib.SMTPException as e:
            self.smtpObj.quit()
            self.smtpObj.close()
            log.error(e)
            return False
