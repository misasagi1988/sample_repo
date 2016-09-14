# coding: utf-8
import sys
sys.path.append("..")
import os, logging
import argparse
from utils import config
from utils.util_proc import Dict
from utils.util_proc import Sample_Info
from utils.util_proc import cal_hash
from utils.log_handler import Logger
from utils.db import MYSQL_Handle

log_path = config.log
with open(log_path, "w"):
    print "clear main log"
logger = Logger(log_path)

class Sample_Repo(object):
    '''
    sample repository class
    '''
    def __init__(self):
        '''
        init function
        '''
        if not os.path.exists(config.sample_folder):
            logger.debug("sample path %s not exist, exit" %config.sample_folder)
            sys.exit()
        if not os.path.exists(config.result_folder):
            logger.debug("sample scan result path %s not exist, exit" %config.result_folder)
            sys.exit()
        self.sql_handler = MYSQL_Handle(config.db_info, logger)

    def get_one_sample_info(self, sampleset_name, sample_name, full_name):
        '''
        get only one sample info from api log and report xml, store into db
        :param sampleset_name: sample set name
        :param sample_name: sample name
        :param full_name: sample full path
        :return: None
        '''
        try:
            logger.info("start check file %s in set %s" %(sample_name, sampleset_name))
            s = Sample_Info(sampleset_name, sample_name, logger)
            s.get_sample_api_info()
            sample_info = s.get_info_dict()
            if sample_info.sha1 is None:
                sample_info.sha1 = cal_hash(full_name)
            query_str = 'select * from %s where sha1=?' %config.tb_name
            select_res = self.sql_handler.queryOne(query_str, sample_info.sha1)
            if select_res is not None:
                logger.debug("query res %s" %select_res)
                logger.debug("sample %s exists, continue" %sample_info.sha1)                
                return
            self.sql_handler.insert(config.tb_name, **sample_info)
            self.sql_handler.commit()
        except Exception, e:
            logger.debug("exception, %s, continue." % e)

    def check_folder(self):
        '''
        get sample info in folder defined in config, call get_one_sample_info function cyclically
        :return: None
        '''
        for root, dirs, files in os.walk(config.sample_folder):
            for filename in files:
                sampleset_name = os.path.basename(root)
                self.get_one_sample_info(sampleset_name, filename, os.path.join(root, filename))
            

    def create_table(self):
        '''
        create table if table not exists
        :return: None
        '''
        sql_str = "SHOW TABLES LIKE '%s'" %config.tb_name
        res = self.sql_handler.update(sql_str)
        if not res:
            logger.info("table not exists, create table %s." %config.tb_name)
            create_str = "create table %s (sha1 varchar(40) primary key, md5 varchar(32), crc32 varchar(8), sample_path varchar(1000), vsdt_type varchar(20), file_type varchar(100), signature varchar(100), detection varchar(20), comment varchar(255))" %config.tb_name
            self.sql_handler.update(create_str)

    def run(self):
        '''
        run function, call function above to get information needed
        :return: None
        '''
        self.create_table()
        self.check_folder()

if __name__ == "__main__":
    d = Sample_Repo()
    d.run()





