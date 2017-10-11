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


db = {'db': "wqy",
      'user': "yong",
      'pwd': "19950105",
      'host': "192.168.4.238",
      'charset': 'utf8'}

only = ['t_fallenark_article', 't_fallenark_title', 'comments_comment', 'fiction_post', 'fiction_category', 'auth_user']

session, base = _conn(db, only)
article = base.classes['t_fallenark_article']
fiction_title = base.classes['t_fallenark_title']
fiction_category = base.classes['fiction_category']
fiction_comment = base.classes['comments_comment']
fiction_post = base.classes['fiction_post']
fiction_user = base.classes['auth_user']


def read_fiction():
    # title_list = list(session.query(fiction_title.title, fiction_title.tid, fiction_title.category).filter(
    #     fiction_title.tid == 31656))
    title_list = list(session.query(fiction_title.title, fiction_title.tid, fiction_title.category))
    print(title_list[0])
    for title_item in title_list[4:]:
        # 文章的属性
        # title_item = title_list[0]
        tid = title_item[1]
        category_list = re.findall(r'\[(.*?)\]', title_item[2])
        if category_list:
            category = category_list[0]
        else:
            category = ''

        title = title_item[0]

        post_list = list(
            session.query(article.tid, article.name, article.uid, article.floor, article.t_time,
                          article.content).filter(
                article.tid == tid).order_by(article.floor))

        # print(post_list[0][5].replace('\n','\n\n'))
        # print(post_list)
        content = []
        create_time = datetime.datetime.today()
        # 整理 正文 和 评论
        comment_list = []

        for post_item in post_list:
            post_content = HanziConv.toSimplified(post_item[5])
            if post_item[3] == 1:
                uid = post_item[2]
                create_time = post_item[4]
                author = post_item[1]
            if post_item[2] == uid:
                content.append('{}\n发表于:{}\t\n'.format(post_content, str(post_item[4])))

            elif len(post_item[-1]) > 300:
                content.append('{}\n{}发表于：{}\t\n'.format(post_content, post_item[1], str(post_item[4])))

                print(post_item)
                print(len(post_content))
            else:
                if len(post_content)>50:
                    name = post_item[1]
                    email = ''
                    url = ''
                    text = post_content
                    comment_create_time = post_item[4]
                    comment_list.append([name, email, url, text, comment_create_time])

        body = '\t\n'.join(content) + '原作者：{}'.format(author)
        body = body.replace('\n', '\n\n')
        # print(body)
        excerpt = body.replace('\n', '').replace('\t', '').replace(' ', '')[:500]

        # create_time =
        print(body)
        print(comment_list)
        print(create_time)
        print(excerpt)
        print(title)
        print(category)
        print(author)

        # 存储category
        category_id = save_category(category)

        # 存储 user

        author_id = save_user(author)
        # print(user_id)
        # 存储post
        post_id = save_post(body, title, create_time, excerpt, author_id, category_id)

        # 存储评论
        save_comment(post_id, comment_list)


def save_category(category):
    # 添加 category
    print('存储 category==================================================')
    category_result = list(session.query(fiction_category.id, fiction_category.name).filter(
        fiction_category.name == category))
    print(category_result)
    if not category_result:
        category_record = fiction_category(name=category)
        try:
            session.merge(category_record)
            session.commit()
            print('category {} 添加成功'.format(category))
        except Exception as e:
            session.rollback()
            print('error:category {} 添加失败'.format(category))
            print(e)
    category_result = list(session.query(fiction_category.id, fiction_category.name).filter(
        fiction_category.name == category))

    # 获得分类id
    category_id = category_result[0][0]
    print(category_id)
    print('存储 category================================================== end')
    return category_id


def save_comment(post_id, comment_list):
    print('start 存储评论 ===========================')
    if comment_list:
        for comment_item in comment_list:
            comment_result = list(session.query(fiction_comment.id, fiction_comment.name, fiction_comment.text,
                                                fiction_comment.post_id).filter(
                fiction_comment.text == comment_item[3], fiction_comment.post_id == post_id,
                fiction_comment.name == comment_item[0]))
            if not comment_result:
                comment_record = fiction_comment(name=comment_item[0],
                                                 post_id=post_id,
                                                 text=comment_item[3],
                                                 email=comment_item[1],
                                                 url=comment_item[2],
                                                 created_time=comment_item[4],
                                                 )
                try:
                    session.merge(comment_record)
                    session.commit()
                    print('comment {} 添加成功'.format(comment_item[3]))
                except Exception as e:
                    session.rollback()
                    print('error:comment {} 添加失败'.format(comment_item[3]))
                    print(e)
            else:
                print('comment exist -----')


    else:
        print('评论列表为空')

    print('end 存储评论 =======================')


def save_post(body, title, create_time, excerpt, author_id, category_id):
    print('开始存储 post ====================')
    post_result = list(session.query(fiction_post.id, fiction_post.title, fiction_post.body).filter(
        fiction_post.title == title, fiction_post.body == body))

    post_record = ''

    if not post_result:
        #     if post_result[0][2] != body:
        #         print("存在相同标题")
        #         post_record = fiction_post(body=body,
        #                                    title=title,
        #                                    created_time=create_time,
        #                                    excerpt=excerpt[:200],
        #                                    modified_time=datetime.datetime.today(),
        #                                    author_id=author_id,
        #                                    category_id=category_id,
        #                                    views=0
        #                                    )
        # else:
        post_record = fiction_post(body=body,
                                   title=title,
                                   created_time=create_time,
                                   excerpt=excerpt[:200],
                                   modified_time=datetime.datetime.today(),
                                   author_id=author_id,
                                   category_id=category_id,
                                   views=0
                                   )
    if post_record:
        try:
            session.merge(post_record)
            session.commit()
            print('post {} 添加成功'.format(title))
        except Exception as e:
            session.rollback()
            print('error:post {} 添加失败'.format(title))
            print(e)
    post_result = list(session.query(fiction_post.id, fiction_post.title, fiction_post.body).filter(
        fiction_post.title == title, fiction_post.body == body))
    post_id = post_result[0][0]
    print('post_id  :{}'.format(post_id))

    print('存储 post ====================end')
    return post_id


def save_user(author):
    # 添加 user
    print('存储 user==================================================')
    category_result = list(session.query(fiction_user.id, fiction_user.username).filter(
        fiction_user.username == author))
    print(category_result)
    if not category_result:
        category_record = fiction_user(username=author,
                                       password='pbkdf2_sha256$30000$hK7rSx9TKYQe$8werTd3reC0cAajnju8Re20l0sxIKE7XDcT5nvtsjLs=',
                                       is_superuser=0,
                                       first_name='',
                                       last_name='',
                                       email='',
                                       date_joined=datetime.datetime.today(),
                                       is_staff=0,
                                       is_active=1)
        try:
            session.merge(category_record)
            session.commit()
            print('user {} 添加成功'.format(author))
        except Exception as e:
            session.rollback()
            print('error:user {} 添加失败'.format(author))
            print(e)
    category_result = list(session.query(fiction_user.id, fiction_user.username).filter(
        fiction_user.username == author))

    # 获得分类id
    user_id = category_result[0][0]
    print(user_id)
    print('存储 category================================================== end')
    # 存储 user
    return user_id


if __name__ == '__main__':
    read_fiction()
