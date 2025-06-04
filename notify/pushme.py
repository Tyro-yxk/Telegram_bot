import os

import requests


def get_push_key():
    push_key = os.environ.get('PUSH_KEY')
    push_url = os.environ.get('PUSH_URL', 'https://push.i-i.me')
    if not push_key:
        print('❌未添加PUSH_KEY变量')
        raise EnvironmentError('❌未添加PUSH_KEY变量')
    return push_key, push_url


def send(title='title', content='content', type='text'):
    """
   :param title: 标题
   :param content: 内容
   :param type: 类型
   :return:
   """
    push_key, push_url = get_push_key()

    re = requests.post(push_url, data={
        "push_key": push_key,
        "title": title,
        "content": content,
        "type": type,
    })
    print(re.text)
    return re


if __name__ == '__main__':
    send('title', 'content', 'text')
