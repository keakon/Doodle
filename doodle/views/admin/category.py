# -*- coding: utf-8 -*-

from doodle.core.models.category import Category
from doodle.common.errors import IntegrityError

from ..base_handler import AdminHandler


class CreateCategoryHandler(AdminHandler):
    def get(self):
        self.render('admin/create_category.html', {
            'title': '添加新分类',
            'page': 'create_category'
        })

    def post(self):
        path = self.get_argument('path', None)
        if not path:
            self.finish('添加失败，分类不能为空')
            return

        try:
            Category.add(path)
        except IntegrityError as e:
            self.finish('添加失败，分类名“%s”已存在于路径“%s”中' % (e.category_name, e.category_parent_path))
        else:
            self.finish('添加成功')
