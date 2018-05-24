#encoding: utf-8

import MySQLdb

import gconf

def execute_sql_v1(sql, args, is_fetch):
    rt_cnt = 0
    rt_list = []
    conn = MySQLdb.connect(host=gconf.MYSQL_HOST, \
                        port=gconf.MYSQL_PORT, \
                        user=gconf.MYSQL_USER, \
                        passwd=gconf.MYSQL_PASSWD, \
                        db=gconf.MYSQL_DB, \
                        charset=gconf.MYSQL_CHARSET)
    cursor = conn.cursor()
    rt_cnt = cursor.execute(sql, args)
    if is_fetch:
        rt_list = cursor.fetchall()
    else:
        conn.commit()
    cursor.close()
    conn.close()
    return rt_cnt, rt_list

def execute_sql(sql, args, is_fetch):
    conn = MySQLConnection(host=gconf.MYSQL_HOST, \
                        port=gconf.MYSQL_PORT, \
                        user=gconf.MYSQL_USER, \
                        passwd=gconf.MYSQL_PASSWD, \
                        db=gconf.MYSQL_DB
                        )
    rt_cnt, rt_list = conn.execute_sql(sql, args, is_fetch)
    conn.close()
    return rt_cnt, rt_list


class MySQLConnection(object):

    def __init__(self, host, port, user, passwd, db):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.db = db
        self.conn = None
        self.cursor = None

    def _connect(self):
        if self.conn is None:
            self.conn = MySQLdb.connect(host=self.host, \
                                port=self.port, \
                                user=self.user, \
                                passwd=self.passwd, \
                                db=self.db, \
                                charset='utf8')
        if self.cursor is None:
            self.cursor = self.conn.cursor()


    def execute_sql(self, sql, args=(), is_fetch=True):
        rt_cnt = 0
        rt_list = []
        self._connect()
        rt_cnt = self.cursor.execute(sql, args)
        if is_fetch:
            rt_list = self.cursor.fetchall()

        return rt_cnt, rt_list

    def commit(self):
        if self.conn is not None:
            self.conn.commit()


    def execute_update_sql(self, sql, args=()):
        self._connect()
        self.cursor.execute(sql, args)


    def execute_fetch_sql(self, sql, args=()):
        self._connect()
        self.cursor.execute(sql, args)
        return self.cursor.fetchall()

    def close(self):
        if self.cursor is not None:
            self.cursor.close()
            self.cursor = None

        if self.conn is not None:
            self.commit()
            self.conn.close()
            self.conn = None






if __name__ == '__main__':
    pass
