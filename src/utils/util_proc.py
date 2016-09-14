# coding: utf-8
import os, re, glob, sys
import hashlib
import config
import xml.etree.ElementTree

def cal_hash(filename, block_size=64 * 1024):
    '''
    call hash for file
    :param filename: full file path
    :param block_size: max size to read once
    :return: sha1 value
    '''
    with open(filename, "rb") as fp:
        sha1 = hashlib.sha1()
        while True:
            data = fp.read(block_size)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest().upper()


class Dict(dict):
    '''
    Simple dict but support access as x.y style.
    '''
    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value


class Sample_Info(object):
    '''
    sample info store class
    '''
    def __init__(self, sampleset_name, sample_name, logger):
        '''
        init function
        :param sampleset_name: sample set name
        :param sample_name: sample name
        :param logger: logger
        '''
        self.logger = logger
        self.sampleset_name = sampleset_name
        self.sample_name = sample_name
        t = re.compile("\[.*\]")
        tmp_path = t.sub("*", sample_name)
        tmp_path = glob.glob(os.path.join(config.result_folder,self.sampleset_name, "All", tmp_path + '.?[0-9A-Z]*'))[0]
        self.api_path = os.path.join(tmp_path, "api.log")
        self.logger.debug("api log path: %s"%(self.api_path))
        self.report_path = os.path.join(tmp_path, self.sample_name + ".report.xml")
        self.logger.debug("report xml path: %s"%(self.report_path))
        self.sample_info = Dict(names = config.fields, values = config.values)

    def get_info_dict(self):
        '''
        get sample info Dict
        :return: Dict
        '''
        return self.sample_info

    def set_sample_info(self, key, value):
        '''
        set sample info key and value
        :param key: key to be set
        :param value: value
        :return: None
        '''
        self.sample_info[key] = value

    def read_xml(self):
        '''
        read report xml
        :return: xml structure
        '''
        try:
            xmltree = xml.etree.ElementTree.parse(self.report_path)
            return xmltree
        except Exception, e:
            self.logger.debug("error occurred: %s" % e)
            return None

    def get_sample_detection_info(self):
        '''
        read report xml to get detection info
        :return: detection string
        '''
        xmltree = self.read_xml()
        if xmltree is None:
            return ""
        root = xmltree.getroot()
        sumarry_info = root.findall("sample/attribute")
        decision = ""
        for i in sumarry_info:
            is_decision = False
            is_score = False
            for j in i.iter():
                if "name" == j.tag and "Decision" == j.text:
                    is_decision = True
                if is_decision == True and "value" == j.tag:
                    decision = j.text
                    break
        return decision

    def get_sample_api_info(self):
        '''
        read api log to get sample file info
        :return: None
        '''
        reg_ptn = re.compile("FileInfo: .*,(VSDT.*)")
        try:
            with open(self.api_path) as pf:
                for line in pf.readlines():
                    res = re.search(reg_ptn, line)
                    if res:
                        info = res.group(1).split(",", 5)
                        info.insert(0, os.path.join(self.sampleset_name, self.sample_name))
                        len_info = len(info)
                        len_dict = len(config.fields)
                        info.extend([""]*(len_dict - len_info))
                        for i in range(0,len(config.fields)):
                            self.set_sample_info(config.fields[i], info[i].strip())
                        self.set_sample_info("detection", self.get_sample_detection_info())
                        self.logger.debug("sample file info: %s" %self.sample_info)
                        break
        except Exception, e:
            self.logger.debug("error occurred, %s" %e)


