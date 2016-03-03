# -*- coding: utf-8 -*-

from datetime import timedelta
import os
import os.path
import re


class ConfigMeta(type):
    def __init__(cls, name, bases, dct):
        super(ConfigMeta, cls).__init__(name, bases, dct)
        if bases[0] == object:
            cls.update_default_config()
        else:
            cls.update_sub_config()


class Config(object):
    __metaclass__ = ConfigMeta

    # application config
    DEBUG_MODE = True  # 开发时可设为 True，修改源码后会自动重启
    TEST = False  # 测试时设为 True，否则不能运行
    GZIP = True  # 生产环境应该设为 False，让 nginx 去 gzip，否则会丢失 ETag
    IPV4_ONLY = True  # 是否需要支持 IPv6
    XHEADERS = False  # 生产环境会在 nginx 传一些 X 开头的 header，此时建议开启
    ENABLE_HTTPS = False  # 支持 HTTPS，登录时会跳到 HTTPS 的登录界面，登录所用的 cookie 仅在 HTTPS 下可用，管理后台仅在 HTTPS 下可访问
    PORT = 8080  # 默认运行的端口
    MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 10  # 退出时如果还有没处理完的 callbacks，最长会等待多少秒
    COOKIE_SECRET = ''  # cookie 的密钥，可以用 os.urandom(32) 生成
    XSRF_COOKIES = False  # POST 请求需要验证 xsrf，暂时不支持

    # blog config
    BLOG_TITLE = u''  # 博客标题
    BLOG_SUB_TITLE = u''  # 博客副标题
    BLOG_DESCRIPTION = u''  # 用于 feed 的博客描述
    BLOG_AUTHOR = u''  # 博客作者
    LANGUAGE = 'zh-CN'  # 博客文章采用的主要语言
    MAJOR_DOMAIN = 'localhost'  # 主要域名

    OUTPUT_FULLTEXT_FOR_FEED = True  # Feed 中是否全文输出
    SORT_FEED_BY_UPDATE_TIME = False  # True: 按发布时间输出 feed，False: 按更新时间输出 feed

    ADMIN_USER_ID = 1  # 管理员 ID

    SOCIAL_MEDIAS = []  # 社交媒体链接
    NAV_LINKS = []  # 导航栏链接，为了避免多次转义，如果网址包含中文或特殊字符，请在这里写百分号转义过的网址

    # path config
    PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    TEMPLATE_PATH = os.path.join(PROJECT_PATH, 'templates')
    STATIC_PATH = os.path.join(PROJECT_PATH, 'static')

    BLOG_HOME_RELATIVE_PATH = '/'  # 博客首页相对路径，可以改为'/blog/'等子目录
    BLOG_ADMIN_RELATIVE_PATH = BLOG_HOME_RELATIVE_PATH + 'admin/'  # 博客管理相对路径
    LOGIN_URL = BLOG_HOME_RELATIVE_PATH + 'login'  # 登录地址

    MAJOR_SCHEME = 'https' if ENABLE_HTTPS else 'http'
    if PORT in (80, 443):  # 生产环境可以直接写死，一般不暴露其他端口
        MAJOR_HOST_URL = '%s://%s' % (MAJOR_SCHEME, MAJOR_DOMAIN)
    else:
        MAJOR_HOST_URL = '%s://%s:%d' % (MAJOR_SCHEME, MAJOR_DOMAIN, PORT)
    BLOG_FEED_URL = MAJOR_HOST_URL + '/feed'
    BLOG_HOME_FULL_URL = MAJOR_HOST_URL + BLOG_HOME_RELATIVE_PATH  # 博客首页完整链接

    # redis config
    REDIS_MAIN_DB = {'host': 'localhost', 'port': 6379, 'db': 0}  # 存储数据的 Redis 服务器地址
    REDIS_CACHE_DB = {'host': 'localhost', 'port': 6379, 'db': 1}  # 缓存的 Redis 服务器地址

    # 3rd services config
    GOOGLE_ANALYTICS_ID = ''  # Google Analytics web property ID，没有就留空，可在 https://www.google.com/analytics/ 申请
    GOOGLE_CSE_ID = ''  # Google自定义搜索引擎ID，没有就留空，可在 http://www.google.com/cse/manage/create 申请

    # email config
    MAILGUN_API_BASE_URL = ''  # Mailgun API Base URL，可在 https://mailgun.com/ 申请
    MAILGUN_API_KEY = ''  # Mailgun API Key
    EMAIL_SENDER = ''  # 发件人邮件地址
    ADMIN_EMAIL = ''  # 管理员邮件地址

    # auth config
    AUTH_RANDOM_BYTES = 10  # 登录时使用的随机数位数，建议加 2 后能被 3 整除
    AUTH_STATE_LENGTH = 24  # == (10 + 8) / 3 * 4，base 64 编码后的长度，8 是 double 类型的时间戳长度
    AUTH_EXPIRE_TIME = 300  # 登录验证的有效时间
    GOOGLE_OAUTH2_CLIENT_ID = ''  # Google OAuth 2 Client ID，可在 https://console.developers.google.com/ 申请
    GOOGLE_OAUTH2_CLIENT_SECRET = ''  # Google OAuth 2 Client secret
    GOOGLE_OAUTH2_REDIRECT_URI = MAJOR_HOST_URL + LOGIN_URL  # Google OAuth 2 Redirect URI，如果启用了 HTTPS，应该设置成 HTTPS 的登录地址

    # paging config
    DEFAULT_PAGE_SIZE = 10

    ARTICLES_PER_PAGE = DEFAULT_PAGE_SIZE  # 每页的文章数
    ARTICLES_FOR_FEED = DEFAULT_PAGE_SIZE  # Feed 输出的文章数，非正数时输出所有文章

    SEARCH_PAGE_SIZE = 20  # 搜索展示的每页文章数
    MAX_SEARCH_COUNT = 10000  # 最多搜索的文章数

    COMMENTS_PER_PAGE = DEFAULT_PAGE_SIZE  # 每页的评论数
    LATEST_COMMENTS_FOR_SIDEBAR = 5  # 侧边栏显示的最新评论数
    LATEST_COMMENTS_LENGTH = 20  # 侧边栏显示的最新评论截取的长度

    # cache config
    DEFAULT_CACHE_TIME = 300
    CATEGORY_ARTICLES_CACHE_TIME = 1800  # 分类文章缓存时间
    SIDEBAR_BAR_CACHE_TIME = 1800  # 侧边栏缓存时间

    # edit config
    SUMMARY_DELIMETER = re.compile(r'\r?\n\r?\n\[cut1\]\r?\n')  # 分隔摘要和文章内容的标记，分隔符之前的作成摘要，分隔符前后的都作为文章内容
    SUMMARY_DELIMETER2 = re.compile(r'\r?\n\r?\n\[cut2\]\r?\n')  # 分隔摘要和文章内容的标记，分隔符之前的作成摘要，之后的为文章内容
    # 一篇文章中同时出现2种分隔符时，以第一种优先；同时出现多次分隔符时，以最先出现的优先。

    # time config
    LOCAL_TIME_DELTA = timedelta(hours=8)  # 本地时区偏差
    DATE_FORMAT = '%Y-%m-%d'  # 日期格式
    SECOND_FORMAT = '%Y-%m-%d %H:%M:%S'  # 时间格式（精确到秒）
    MINUTE_FORMAT = '%Y-%m-%d %H:%M'  # 时间格式（精确到分）

    REPLACE_SPECIAL_CHARACTERS_FOR_URL = True  # 在自动生成URL时，是否将空格、引号、尖括号、&、#、%替换成“-”，在写英文标题时可能会需要
    if REPLACE_SPECIAL_CHARACTERS_FOR_URL:
        URL_SPECIAL_CHARACTERS = re.compile(r'[\s\"\'&#<>%]+')
        URL_REPLACE_CHARACTER = ''

    # static file config
    JQUERY_VERSION = '1.8.3'  # todo: upgrade

    @classmethod
    def update_default_config(cls):
        cls.update_from_env()

    @classmethod
    def update_sub_config(cls):
        cls.update_paths()

    @classmethod
    def update_from_env(cls):
        REDIS_HOST = os.getenv('REDIS_HOST')
        if REDIS_HOST:
            cls.REDIS_MAIN_DB['host'] = cls.REDIS_CACHE_DB['host'] = REDIS_HOST

    @classmethod
    def update_paths(cls):
        cls.BLOG_FEED_URL = cls.MAJOR_HOST_URL + '/feed'
        cls.BLOG_HOME_FULL_URL = cls.MAJOR_HOST_URL + cls.BLOG_HOME_RELATIVE_PATH
        cls.GOOGLE_OAUTH2_REDIRECT_URI = cls.MAJOR_HOST_URL + cls.LOGIN_URL
