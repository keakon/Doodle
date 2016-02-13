# -*- coding: utf-8 -*-

from doodle.core.models.tag import Tag

from ..base_handler import AdminHandler


class CreateTagHandler(AdminHandler):
    def get(self):
        self.render('admin/create_tag.html', {
            'title': '添加新标签',
            'page': 'create_tag'
        })

    def post(self):
        name = self.get_argument('name', None)
        if not name:
            self.finish('添加失败，标签名不能为空')
            return

        Tag.add(name)
        self.finish('添加成功')
