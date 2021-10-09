#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rest_framework

from rest_framework.pagination import (
    remove_query_param, replace_query_param
)

class PageNumberPagination(rest_framework.pagination.PageNumberPagination):

    page_size_query_param = 'size'
    
    def get_next_link(self):
        if not self.page.has_next():
            return None
        url = self.request.get_full_path()
        page_number = self.page.next_page_number()
        return replace_query_param(url, self.page_query_param, page_number)

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        url = self.request.get_full_path()
        page_number = self.page.previous_page_number()
        if page_number == 1:
            return remove_query_param(url, self.page_query_param)
        return replace_query_param(url, self.page_query_param, page_number)
