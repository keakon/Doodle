# -*- coding: utf-8 -*-

from cgi import escape

from tornado.gen import coroutine
from tornado.web import HTTPError

from doodle.common.content_format import ContentFormatFlag
from doodle.common.email_client import send_email
from doodle.common.time_format import formatted_time, timestamp_to_datetime
from doodle.config import CONFIG
from doodle.core.models.article import Article
from doodle.core.models.comment import Comment
from doodle.core.models.fragment_cache import FragmentCache
from doodle.core.models.user import User

from ..base_handler import UserHandler, authorized


class ArticleCommentsHandler(UserHandler):
    def get(self, article_id, order, page):
        article_id = int(article_id)
        if not article_id:
            raise HTTPError(404)

        article = Article.get_by_id(article_id)
        if not article:
            raise HTTPError(404)
        if not article.public:
            self.set_cache(is_public=False)
            if not self.is_admin:
                raise HTTPError(404)

        page = int(page)

        comments_list = []
        comments, has_next_page = Comment.get_comments_of_article(article_id, order == 'asc', page)
        if comments:
            user_ids = {comment.user_id for comment in comments}
            users = User.get_by_ids(user_ids, filter_empty=True)
            if users:
                user_dict = {user.id: user for user in users}
            else:
                user_dict = {}
            for comment in comments:
                user = user_dict.get(comment.user_id)
                if user:
                    user_name = user.name
                    user_site = escape(user.site) if user.site else ''
                else:
                    user_name = u'匿名用户'
                    user_site = ''
                comments_list.append({
                    'user_name': user_name,
                    'url': user_site,
                    'img': user.get_avatar(),
                    'ua': comment.ua,
                    'time': formatted_time(timestamp_to_datetime(comment.time)),
                    'id': comment.id,
                    'content': comment.html_content()
                })

        output = {'comments': comments_list}
        if has_next_page:
            output['next_page'] = page + 1
        self.write_json(output)


class CreateCommentHandler(UserHandler):
    @authorized()
    @coroutine
    def post(self, article_id):
        article_id = int(article_id)
        if not article_id:
            raise HTTPError(404)

        current_user = self.current_user
        if self.current_user.banned:
            raise HTTPError(403)

        article = Article.get_by_id(article_id)
        if not (article and (article.public or self.is_admin)):
            raise HTTPError(404)

        content = self.get_argument('comment', None)
        if not content:
            raise HTTPError(400)
        content = content.strip().replace('\r\n', '\n').replace('\r', '\n')
        if not content:
            raise HTTPError(400)

        if self.get_argument('bbcode', None) == 'on':
            format = ContentFormatFlag.BBCODE
        else:
            format = ContentFormatFlag.PLAIN

        ua = []
        browser, platform, os, os_version, vendor = self.ua_details
        if platform:
            if platform in ('iPhone', 'iPod Touch', 'iPad', 'Android'):
                ua.append(platform)
            elif self.is_mobile:
                ua.append('mobile')
        else:
            if self.is_mobile:
                ua.append('mobile')
            elif os and os in ('Windows', 'Mac OS', 'Linux', 'FreeBSD'):
                ua.append(os)
        if browser:
            if browser == 'Internet Explorer':
                ua.append('IE')
            elif browser in ('Firefox', 'Chrome', 'Safari', 'Opera'):
                ua.append(browser)
            elif browser == 'Mobile Safari':
                ua.append('Safari')
            elif browser in ('Opera Mini', 'Opera Mobile'):
                ua.append('Opera')

        # todo: check last comment

        current_user_id = self.current_user_id
        comment = Comment(
            article_id=article_id,
            user_id=current_user_id,
            content=content,
            format=format,
            ua=ua,
            public=True
        )
        comment.save(inserting=True)

        self.write_json({
            'comment': {
                'user_name': current_user.name,
                'url': current_user.site,
                'img': current_user.get_avatar(),
                'ua': comment.ua,
                'time': formatted_time(timestamp_to_datetime(comment.time)),
                'id': comment.id,
                'content': comment.html_content()
            }
        })

        FragmentCache.delete('sidebar')

        if CONFIG.MAILGUN_API_KEY:
            url = html_content = html_body = title = ''

            if CONFIG.ADMIN_EMAIL and not self.is_admin:
                url = u'%s%s#comment-id-%d' % (CONFIG.BLOG_HOME_FULL_URL, article.quoted_url(), comment.id)
                html_content = comment.html_content_with_full_url(url)
                html_body = u'%s 在 <a href="%s">%s</a> 评论道:<br/>%s' % (escape(current_user.name), url, article.title, html_content)
                title = u'Re: ' + article.title
                yield send_email(to=CONFIG.ADMIN_EMAIL, subject=title, html=html_body)

            if format != ContentFormatFlag.PLAIN:
                if not html_content:
                    url = u'%s%s#comment-id-%d' % (CONFIG.BLOG_HOME_FULL_URL, article.quoted_url(), comment.id)
                    html_content = comment.html_content_with_full_url(url)
                comment_ids = set(int(comment_id) for comment_id in Comment.REPLY_LINK_PATTERN.findall(html_content))
                if comment_ids:
                    comments = Comment.get_by_ids(comment_ids)
                    if comments:
                        user_ids = {comment.user_id for comment in comments}
                        user_ids.discard(CONFIG.ADMIN_USER_ID)  # already sent to admin
                        if user_ids:
                            users = User.get_by_ids(user_ids)
                            if users:
                                if not html_body:
                                    html_body = u'%s 在 <a href="%s">%s</a> 评论道:<br/>%s<hr/>您收到这封邮件是因为有人回复了您的评论。您可前往原文回复，请勿直接回复该邮件。' % (escape(current_user.name), url, article.title, html_content)
                                    title = u'Re: ' + article.title
                                else:
                                    html_body += u'<hr/>您收到这封邮件是因为有人回复了您的评论。您可前往原文回复，请勿直接回复该邮件。'

                                for user in users:
                                    yield send_email(to=user.email, subject=title, html=html_body)
