# -*- coding: utf-8 -*-

from doodle.common.time_format import iso_time_format, iso_time_now, timestamp_to_datetime
from doodle.core.models.article import Article

from ..base_handler import UserHandler


class FeedHandler(UserHandler):
    def get(self):
        self.set_content_type('atom')
        # todo: handler subscribers

        articles = Article.get_articles_for_feed()
        if articles:
            last_updated = iso_time_format(timestamp_to_datetime(articles[0].mod_time))
        else:
            last_updated = iso_time_now()

        self.render('web/feed.xml', {
            'articles': articles,
            'last_updated': last_updated
        })
