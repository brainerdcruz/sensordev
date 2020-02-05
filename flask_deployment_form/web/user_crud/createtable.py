# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 09:15:24 2019

@author: Dynaslope
"""

import analysis.querydb as qdb

def create_tilt_table(logger_name = ''):
    query = ("CREATE TABLE `tilt_{}` ( "
                 "`data_id` int(10) unsigned NOT NULL AUTO_INCREMENT, "
                 "`ts` timestamp NULL DEFAULT NULL, "
                 "`node_id` int(11) unsigned DEFAULT NULL, "
                 "`type_num` int(11) unsigned DEFAULT NULL, "
                 "`xval` int(6) DEFAULT NULL, "
                 "`yval` int(6) DEFAULT NULL, "
                 "`zval` int(6) DEFAULT NULL, "
                 "`batt` float DEFAULT NULL, "
                 "`is_live` tinyint(4) DEFAULT '1', "
                 "PRIMARY KEY (`data_id`), "
                 "UNIQUE KEY `unique1` (`ts`,`node_id`,`type_num`)"
                 ") ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;".format(logger_name))
    print (query)
    qdb.execute_query(query)

def create_soms_table(logger_name = ''):
    query = ("CREATE TABLE `soms_{}` ( "
                 "`data_id` int(11) NOT NULL AUTO_INCREMENT, "
                 "`ts` timestamp NULL DEFAULT NULL, " 
                 "`node_id` int(11) DEFAULT NULL, "
                 "`type_num` int(11) DEFAULT NULL, "
                 "`mval1` int(11) DEFAULT NULL, "
                 "`mval2` int(11) DEFAULT NULL, "
                 "PRIMARY KEY (`data_id`), "
                 "UNIQUE KEY `unique1` (`ts`,`node_id`,`type_num`) "
                 ") ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;".format(logger_name))
    print (query)
    qdb.execute_query(query)

def create_rain_table(logger_name = ''):
    query = ("CREATE TABLE `rain_{}` (" 
             "`data_id` int(10) unsigned NOT NULL AUTO_INCREMENT, "
             "`ts` timestamp NULL DEFAULT NULL, "
             "`rain` float DEFAULT NULL, "
             "`temperature` float DEFAULT NULL, "
             "`humidity` float DEFAULT NULL, "
             "`battery1` float DEFAULT NULL, "
             "`battery2` float DEFAULT NULL, "
             "`csq` tinyint(3) DEFAULT NULL, "
             "PRIMARY KEY (`data_id`), "
             "UNIQUE KEY `unique1` (`ts`) "
             ") ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;".format(logger_name))
    print (query)
    qdb.execute_query(query)

def create_piezo_table(logger_name = ''):
    query = ("CREATE TABLE `piezo_{}` ("
                 "`data_id` int(10) unsigned NOT NULL AUTO_INCREMENT,"
                 "`ts` timestamp NULL DEFAULT NULL, "
                 "`frequency_shift` decimal(6,2) unsigned DEFAULT NULL, "
                 "`temperature` float DEFAULT NULL, "
                 "PRIMARY KEY (`data_id`), UNIQUE KEY `unique1` (`ts`) "
                 ") ENGINE=InnoDB DEFAULT CHARSET=utf8;".format(logger_name))
    print (query)
    qdb.execute_query(query)