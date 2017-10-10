#!/usr/bin/env Python3
# -*- coding: utf-8 -*-
# 
# Name   : sync_es_to_mysql
#
# Fatures: 将 es 的数据同步到 mysql
#
# Author : qianyong
#
# Time   : 2017-06-05 17:19
# Version: V0.0.1
#

import sys, os
from elasticsearch import Elasticsearch
from sqlalchemy import *
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime, time


def get_susong(es):
    """
    从 elasticserrch 获取新的 公司
    :param es: 
    :return: 
    """
    # res = es.get(index="rk_corp",id='01fae5e48365571dd736aa4f360079d5')
    res = es.search(index="rk_susong", doc_type='susong', body={"query": {"match_all": {}}}, size=10000)

    for susong_item in res['hits']['hits']:
        yield susong_item["_source"]


def _conn(db, only=None):
    """
    链接单个数据库
    :param db:
    :param only:
    :return:
    """
    # print(db)
    engine_str = 'mysql+pymysql://{}:{}@{}/{}?charset={}'.format(db.get('user'),
                                                                 db.get('pwd'),
                                                                 db.get('host'),
                                                                 db.get('db'),
                                                                 db.get('charset'))

    engine = create_engine(engine_str)
    if only is None:
        base = automap_base()
        base.prepare(engine, reflect=True)
    else:
        metadata = MetaData()
        metadata.reflect(engine, only=only)
        base = automap_base(metadata=metadata)
        base.prepare()

    # 创建数据会话
    session = Session(engine)

    return session, base


if __name__ == '__main__':

    es_param = {
        "host": "http://54.223.109.46:9200",
        "user": "root",
        "password": "2I*EMXHnyrFt7L8l"}
    mysql_param = {
        "host": "115.28.93.101:3306",
        "user": "zhongtai",
        "pwd": "CQC$zRp1nMSu94nT",
        "db": "hsh_zt",
        "charset": "utf8"
    }

    es = Elasticsearch([es_param.get('host')], http_auth=(es_param.get('user'), es_param.get('password')),
                       verify_certs=True)

    session, base = _conn(mysql_param, ['crm_user_title_susong', 'crm_user_title'])
    title = base.classes['crm_user_title']
    susong = base.classes['crm_user_title_susong']
    # title_id = session.query(title.title_id).filter(title.company_name ==)

    i = 0
    # 链接mysql
    for susong_item in get_susong(es):
        i += 1
        print('\n{} ==== 准备导入数据 {}'.format(i, susong_item))
        # print(type(susong_item))
        company_name = susong_item.get('companyName')
        title_id_list = session.query(title.title_id).filter(title.company_name == company_name)
        if len(list(title_id_list)) == 1:
            try:
                title_id = list(title_id_list)[0][0]
                if susong_item.get('publishTime'):
                    dateArray = datetime.datetime.utcfromtimestamp(int(susong_item.get('publishTime')) / 1000)
                    publist_time = dateArray.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    publist_time = '1970-01-01 01:00:00'
                print('--------- title_id: {}   publish_time: {} '.format(title_id, publist_time))
                #  判断记录是否存在
                id_list = session.query(susong.id).filter(susong.title == susong_item.get('title'),
                                                          susong.number == susong_item.get('caseNumber')
                                                          )
                if len(list(id_list)) > 1:
                    print('[ERROR] 存在重复数据:-->id: {} , {}'.format(list(id_list), susong_item))
                    continue
                elif len(list(id_list)) == 1:

                    id = id_list[0][0]
                    print('---------- 更新id :{}'.format(id))
                    record = susong(
                        id=id,
                        title_id=title_id,
                        title=susong_item.get('title'),
                        publish_date=publist_time,
                        number=susong_item.get('caseNumber'),
                        created=func.now(),
                        updated=func.now()
                    )
                else:
                    record = susong(
                        title_id=title_id,
                        title=susong_item.get('title'),
                        publish_date=publist_time,
                        number=susong_item.get('caseNumber'),
                        created=func.now(),
                        updated=func.now()
                    )
            except Exception as e:
                print('[ERROR] 发生错误,错误原因是:{}'.format(e))
                continue

            try:
                session.merge(record)
                session.commit()
                print('---------------> 数据导入成功')
            except Exception as e:
                print('[ERROR] 发生错误,错误原因是:{}'.format(e))
                session.rollback()

        else:
            print('[WARNING]: {} 在 title 表中可能不止一条记录'.format(company_name))
    session.close()
