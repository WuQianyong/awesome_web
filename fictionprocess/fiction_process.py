#!/usr/bin/env Python3
# -*- coding: utf-8 -*-
# 
# Name   : fiction_process
# Fatures:
# Author : qianyong
# Time   : 2017/10/10 16:40
# Version: V0.0.1
#

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import re
import datetime
from hanziconv import HanziConv


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
    session_factory = sessionmaker(bind=engine, autocommit=False,
                                   autoflush=False)

    if only is None:
        base = automap_base()
        base.prepare(engine, reflect=True)
    else:
        metadata = MetaData()
        metadata.reflect(engine, only=only)
        base = automap_base(metadata=metadata)
        base.prepare()

    # 创建数据会话
    session = scoped_session(session_factory)

    # session = Session(engine)
    # session = Session()

    return session, base


def read_fiction():
    db = {'db': "wqy",
          'user': "yong",
          'pwd': "19950105",
          'host': "192.168.4.238",
          'charset': 'utf8'}

    only = ['t_fallenark_article', 't_fallenark_title','comments_comment','fiction_post','fiction_category']

    session, base = _conn(db, only)
    article = base.classes['t_fallenark_article']
    title = base.classes['t_fallenark_title']

    title_list = list(session.query(title.title, title.tid, title.category))
    print(title_list[0])

    # 文章的属性
    title_item = title_list[0]
    tid = title_item[1]
    category_list  = re.findall(r'\[(.*?)\]',title_item[2])
    if category_list:
        category = category_list[0]
    else:
        category = ''

    title = title_item[0]


    post_list = list(
        session.query(article.tid, article.name, article.uid, article.floor, article.t_time,article.content).filter(
            article.tid == tid).order_by(article.floor))
    # print(post_list)
    content = []
    create_time = datetime.datetime.today()
    # 整理 正文 和 评论
    comment_list = []
    for post_item in post_list:
        if post_item[3] == 1:
            uid = post_item[2]
            create_time = post_item[4]
            author =post_item[1]
        if post_item[2] == uid:
            content.append('{}\n发表于:{}\t\n'.format( post_item[-1],str(post_item[4])))

        elif len(post_item[-1]) > 300:
                content.append('{}\n{}发表于：{}\t\n'.format(post_item[-1],post_item[1], str(post_item[4])))

                print(post_item)
                print(len(post_item[-1]))
        else:
            name = post_item[1]
            email = ''
            url = ''
            text = post_item[-1]
            comment_create_time = post_item[4]
            comment_list.append([name,email,url,text,comment_create_time])

    body = HanziConv.toSimplified('\t\n'.join(content) + '原作者：{}'.format(author).replace('\n','\n\n'))
    excerpt = body.replace('\n','').replace('\t','').replace(' ','')[:500]

    # create_time =
    print(body)
    print(comment_list)
    print(create_time)
    print(excerpt)
    print(title)
    print(category)
    # print(author)




if __name__ == '__main__':
    read_fiction()
