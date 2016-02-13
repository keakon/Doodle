# -*- coding: utf-8 -*-

from doodle.config import CONFIG

from .base_handler import NotFoundHandler, StaticFileHandler
from .admin.article import CreateArticleHandler, CreateArticleRedirectHandler, EditArticleHandler
from .admin.category import CreateCategoryHandler
from .admin.tag import CreateTagHandler
from .web.article import ArticleHandler, ArticleIDHandler
from .web.category import CategoryArticlesHandler
from .web.comment import CreateCommentHandler, ArticleCommentsHandler
from .web.feed import FeedHandler
from .web.home import HomeHandler
from .web.search import SearchHandler
from .web.tag import TagArticlesHandler
from .web.user import LoginHandler, LogoutHandler, ProfileHandler


BLOG_HOME_RELATIVE_PATH = CONFIG.BLOG_HOME_RELATIVE_PATH
BLOG_ADMIN_RELATIVE_PATH = CONFIG.BLOG_ADMIN_RELATIVE_PATH
STATIC_PATH = CONFIG.STATIC_PATH

handlers = [
    (BLOG_HOME_RELATIVE_PATH, HomeHandler),
    # (BLOG_HOME_RELATIVE_PATH + r'(?:page/(\d+))?', HomeHandler),
	(BLOG_HOME_RELATIVE_PATH + r'((\d{4}/\d{2}/\d{2}/).+)', ArticleHandler),
    (BLOG_HOME_RELATIVE_PATH + r'article/(\d+)', ArticleIDHandler),
    (BLOG_HOME_RELATIVE_PATH + r'comment/(\d+)', CreateCommentHandler),
    (BLOG_HOME_RELATIVE_PATH + r'article/(\d+)/comments/(asc|desc)/(\d+)', ArticleCommentsHandler),
    (BLOG_HOME_RELATIVE_PATH + r'category/(.+)', CategoryArticlesHandler),
    (BLOG_HOME_RELATIVE_PATH + r'tag/(.+)', TagArticlesHandler),
    (BLOG_HOME_RELATIVE_PATH + 'search', SearchHandler),
    (BLOG_HOME_RELATIVE_PATH + 'feed', FeedHandler),

    (BLOG_ADMIN_RELATIVE_PATH, CreateArticleRedirectHandler),
    (BLOG_ADMIN_RELATIVE_PATH + 'article/new', CreateArticleHandler),
    (BLOG_ADMIN_RELATIVE_PATH + r'article/(\d+)/edit', EditArticleHandler),
    (BLOG_ADMIN_RELATIVE_PATH + 'category/new', CreateCategoryHandler),
    (BLOG_ADMIN_RELATIVE_PATH + 'tag/new', CreateTagHandler),

    (CONFIG.LOGIN_URL, LoginHandler),
    (BLOG_HOME_RELATIVE_PATH + 'logout', LogoutHandler),
    (BLOG_HOME_RELATIVE_PATH + 'profile', ProfileHandler),

    (BLOG_HOME_RELATIVE_PATH + r'(robots\.txt|favicon\.ico)', StaticFileHandler, {'path': STATIC_PATH}),
    (BLOG_HOME_RELATIVE_PATH + r'static/(.*)', StaticFileHandler, {'path': STATIC_PATH}),

    (BLOG_HOME_RELATIVE_PATH + r'.*', NotFoundHandler)
]
