# coding: utf-8
import sys
import MySQLdb
import MySQLdb.cursors
from log_handler import Logger
from util_proc import Dict

class MYSQL_Handle(object):
    '''
    mysql module api
    '''
    def __init__(self, sql_dict, logger):
        '''
        init function
        :param sql_dict: sql dict
        :param logger: logger handle
        '''
        db_host = sql_dict["host"]
        db_port = sql_dict["port"]
        db_name = sql_dict["name"]
        db_user = sql_dict["user"]
        db_pwd = sql_dict["pwd"]
        db_charset = sql_dict["charset"]
        self.logger = logger

        try:
            self.conn = MySQLdb.connect(host = db_host, user = db_user, passwd = db_pwd, db = db_name, port = db_port)
            self.conn.set_character_set(db_charset)
            self.cur = self.conn.cursor()
        except MySQLdb.Error, e:
            self.logger.error("mysql db connection error, %s" %e)
            sys.exit()

    def execute(self, sql, *args):
        '''
        execute non query sql(add, update, delete)
        :param sql: sql statement
        :return: execute number
        '''
        try:
            ret = self.cur.execute(sql, args)
            return ret
        except MySQLdb.Error, e:
            self.logger.error("mysql execute error: %s\nsql: %s" % (e.args[1], sql))
            sys.exit(1)

    def commit(self):
        '''
        commit data to database
        when add, update or delete data, execute commit to update database
        :return: None
        '''
        try:
            self.conn.commit()
        except MySQLdb.Error, e:
            self.logger.error("mysql commit error: %s\n" % e.args[1])
            sys.exit(1)

    def insert(self, table, **kw):
        '''
        insert into table
        :param table: table name
        :param kw: dict format
        :return: line count
        '''
        cols, args = zip(*kw.iteritems())
        sql = 'insert into `%s` (%s) values (%s)' % (table, ','.join(['`%s`' % col for col in cols]), ','.join(['?' for i in range(len(cols))]))
        sql = sql.replace('?', '%s')
        num = self.execute(sql, *args)
        return num

    def update(self, sql, *args):
        '''
        update table
        :param sql: sql statement
        :param args: parameters
        :return: line count
        '''
        sql = sql.replace('?', '%s')
        num = self.execute(sql, *args)
        return num

    def query(self, sql, first, *args):
        '''
        query table
        :param sql: sql statement
        :param first: query one or all
        :param args: parameters
        :return: query content in Dict format
        '''
        sql = sql.replace('?', '%s')
        try:
            self.cur.execute(sql, args)
            if self.cur.description:
                names = [x[0] for x in self.cur.description]
            if first:
                values = self.cur.fetchone()
                if not values:
                    return None
                return Dict(names, values)
            return [Dict(names, x) for x in self.cur.fetchall()]
        except MySQLdb.Error, e:
            self.logger.error("mysql query error: %s\nsql: %s\n" % (e.args[1], sql))
            sys.exit(1)

    def queryAll(self, sql, *args):
        '''
        query table
        :param sql: sql statement
        :param args: query all
        :return: query content in Dict format
        '''
        return self.query(sql, False, *args)

    def queryOne(self, sql, *args):
        '''
        query table
        :param sql: sql statement
        :param args: query one
        :return: query content in Dict format
        '''
        return self.query(sql, True, *args)

    def close(self):
        '''
        close cursor and connection
        :return: None
        '''
        try:
            self.cur.close()
            self.conn.close()
        except Exception, e:
            pass

    def __del__(self):
        '''
        close everything
        :return: None
        '''
        self.close()

if __name__ == "__main__":
    info_dict = {}
    info_dict["host"] = "127.0.0.1"
    info_dict["port"] = 3306
    info_dict["user"] = "root"
    info_dict["pwd"] = r"mac8.6"
    info_dict["name"] = "sample_info"
    info_dict["charset"] = "utf8"
    mysql = MYSQL_Handle(info_dict, Logger(r"test.log"))
    query_str = 'select * from sample_info where sha1=?'
    sample_sha1 = 'DA39A3EE5E6B4B0D3255BFEF95601890AFD80709'
    select_res = mysql.queryOne(query_str, sample_sha1)
    print select_res

