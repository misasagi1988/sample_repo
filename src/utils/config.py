# coding: utf-8
import os

work_dir = os.path.dirname(os.path.dirname(os.path.abspath(".")))

log = os.path.join(work_dir, "log", "main.log")

sample_folder = unicode(r"\\10.5.36.218\sharewrite\share\Samples\RAT", "utf-8")
result_folder = unicode(r"\\10.5.37.16\Result\seg6.0.1208_repack.vbox213.xp", "utf-8")

db_info = {
    "host": "127.0.0.1",
    "port": 3306,
    "name": "sample_info",
    "user": "root",
    "pwd": "mac8.6",
    "charset": "utf8"
}

tb_name = "sample_info"
fields = ("sample_path", "vsdt_type", "crc32", "md5", "sha1",  "file_type", "signature", "detection", "comment")
values = (None,)*9

