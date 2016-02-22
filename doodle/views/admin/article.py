# -*- coding: utf-8 -*-

from datetime import datetime
import logging
import time

from tornado.web import HTTPError

from doodle.core.models.article import Article
from doodle.core.models.category import Category
from doodle.core.models.tag import Tag
from doodle.common.errors import IntegrityError
from doodle.common.time_format import datetime_to_timestamp, formatted_date_for_url, parse_time
from doodle.common.url import replace_special_characters_for_url
from doodle.common.content_format import ContentFormatFlag
from doodle.config import CONFIG

from ..base_handler import AdminHandler


class CreateArticleHandler(AdminHandler):
    def get(self):
        categories = Category.get_all_names_with_paths()
        tags = Tag.get_all()

        self.render('admin/create_article.html', {
            'title': '发表新文章',
            'page': 'create_article',
            'categories': categories,
            'tags': sorted(tags)
        })

    def post(self):
        title = self.get_argument('title', None)
        if not title:
            self.finish('发表失败，标题不能为空')
            return

        pub_time = self.get_argument('pub_time', None)
        if pub_time:
            pub_time = parse_time(pub_time)
        if not pub_time:
            pub_time = datetime.utcnow()
        pub_timestamp = datetime_to_timestamp(pub_time)

        mod_time = self.get_argument('mod_time', None)
        if mod_time:
            mod_time = parse_time(mod_time)
        if not mod_time:
            mod_timestamp = pub_timestamp
        else:
            mod_timestamp = datetime_to_timestamp(mod_time)

        url = self.get_argument('url', None)
        # todo: check url pattern
        if not url:
            formatted_date = formatted_date_for_url(pub_time)
            if CONFIG.REPLACE_SPECIAL_CHARACTERS_FOR_URL:
                url = formatted_date + replace_special_characters_for_url(title)
            else:
                url = formatted_date + title
        if Article.exist_url(url):
            self.finish('发表失败，同链接的文章已存在')
            return

        public = self.get_argument('public', None) == 'on'
        bbcode = self.get_argument('bbcode', None) == 'on'
        html = self.get_argument('html', None) == 'on'
        format = bbcode * ContentFormatFlag.BBCODE + html * ContentFormatFlag.HTML
        content = self.get_argument('content').replace('\r\n', '\n').replace('\r', '\n')

        category_name = self.get_argument('category', None)
        if category_name:
            if not Category.exists(category_name):
                self.finish('发表失败，分类不存在')
                return

        tag_names = self.get_arguments('tags')
        if tag_names:
            tag_names = set(tag_names)
            tag_names.discard('')

        keywords = self.get_argument('keywords', None)
        if keywords:
            keywords = keywords.lower()

        article = Article(
            title=title,
            url=url,
            content=content,
            format=format,
            category=category_name or None,
            tags=sorted(tag_names) if tag_names else None,
            keywords=keywords,
            public=public,
            pub_time=pub_timestamp,
            mod_time=mod_timestamp
        )
        try:
            article.save(inserting=True)
        except IntegrityError:
            quoted_url = article.quoted_url()
            self.finish('发表失败，已有<a href="%s%s">相同链接的文章</a>存在' % (CONFIG.BLOG_HOME_RELATIVE_PATH, quoted_url))
        except Exception:
            logging.exception('failed to save new article')
            self.finish('发表失败')
        else:
            quoted_url = article.quoted_url()
            self.finish('发表成功，查看<a href="%s%s">发表后的文章</a>' % (CONFIG.BLOG_HOME_RELATIVE_PATH, quoted_url))


class CreateArticleRedirectHandler(AdminHandler):
    def get(self):
        self.redirect('/admin/article/new', True)


class EditArticleHandler(AdminHandler):
    def get(self, article_id):
        article_id = int(article_id)
        if not article_id:
            raise HTTPError(404)

        article = Article.get_by_id(article_id)
        if not article:
            raise HTTPError(404)

        categories = Category.get_all_names_with_paths()
        tags = Tag.get_all()

        self.render('admin/edit_article.html', {
            'title': u'编辑《%s》' % article.title,
            'page': 'edit_article',
            'article': article,
            'categories': categories,
            'tags': sorted(tags)
        })

    def post(self, article_id):
        article_id = int(article_id)
        if not article_id:
            raise HTTPError(404)

        article = Article.get_by_id(article_id)
        if not article:
            raise HTTPError(404)

        title = self.get_argument('title', None)
        if title:
            article.title = title

        now = None
        pub_time = self.get_argument('pub_time', None)
        if pub_time:
            pub_time = parse_time(pub_time)
        if pub_time:
            pub_timestamp = datetime_to_timestamp(pub_time)
        else:
            pub_time = datetime.utcnow()
            pub_timestamp = now = datetime_to_timestamp(pub_time)
        article.pub_time = pub_timestamp

        mod_time = self.get_argument('mod_time', None)
        if mod_time:
            mod_time = parse_time(mod_time)
        if mod_time:
            mod_timestamp = datetime_to_timestamp(mod_time)
        else:
            mod_timestamp = now
        article.mod_time = mod_timestamp

        url = self.get_argument('url', None)
        # todo: check url pattern
        if not url:
            formatted_date = formatted_date_for_url(pub_time)
            if CONFIG.REPLACE_SPECIAL_CHARACTERS_FOR_URL:
                url = formatted_date + replace_special_characters_for_url(article.title)
            else:
                url = formatted_date + article.title
        if article.url != url:
            if Article.exist_url(url):
                self.finish('编辑失败，同链接的文章已存在')
                return
            else:
                article.url = url

        article.public = self.get_argument('public', None) == 'on'
        bbcode = self.get_argument('bbcode', None) == 'on'
        html = self.get_argument('html', None) == 'on'
        article.format = bbcode * ContentFormatFlag.BBCODE + html * ContentFormatFlag.HTML
        article.content = self.get_argument('content').replace('\r\n', '\n').replace('\r', '\n')

        category_name = self.get_argument('category', None)
        if category_name:
            if not Category.exists(category_name):
                self.finish('发表失败，分类不存在')
                return
        article.category = category_name or None

        tag_names = self.get_arguments('tags')
        if tag_names:
            tag_names = set(tag_names)
            tag_names.discard('')
        article.tags = sorted(tag_names) if tag_names else None

        keywords = self.get_argument('keywords', None)
        if keywords:
            keywords = keywords.lower()
        article.keywords = keywords

        try:
            article.save()
        except IntegrityError:
            quoted_url = article.quoted_url()
            self.finish('编辑失败，已有<a href="%s%s">相同链接的文章</a>存在' % (CONFIG.BLOG_HOME_RELATIVE_PATH, quoted_url))
        except Exception:
            logging.exception('failed to save modified article')
            self.finish('编辑失败')
        else:
            quoted_url = article.quoted_url()
            # 增加时间戳，已避免缓存造成影响，打开后会被 history.replaceState 去掉 query 部分
            self.finish('编辑成功，查看<a href="%s%s?t=%d">更新后的文章</a>' % (CONFIG.BLOG_HOME_RELATIVE_PATH, quoted_url, int(time.time())))
