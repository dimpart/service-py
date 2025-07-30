# -*- coding: utf-8 -*-
# ==============================================================================
# MIT License
#
# Copyright (c) 2024 Albert Moky
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================

import threading
import time
from typing import Optional, Tuple, Dict

from dimples import Content
from dimples import FileContent, TextContent
from dimples import CustomizedContent
from dimples.utils import SharedCacheManager
from dimples.database import Storage

from tvbox.utils import json_decode

from libs.utils import Logging
from libs.utils import Config

from .service import Request
from .service import BaseService


class WebMaster(Logging):

    MEM_CACHE_EXPIRES = 600  # seconds
    MEM_CACHE_REFRESH = 32   # seconds

    def __init__(self, config: Config):
        self.__config = config
        man = SharedCacheManager()
        self.__cache = man.get_pool(name='web_pages')  # path => text
        self.__lock = threading.Lock()

    @property  # protected
    def config(self) -> Config:
        return self.__config

    @property  # protected
    def indexes(self) -> Optional[str]:
        config = self.config
        return config.get_string(section='sites', option='indexes')

    async def _load_file(self, path: str) -> Optional[str]:
        now = time.time()
        cache_pool = self.__cache
        #
        #  1. check memory cache
        #
        value, holder = cache_pool.fetch(key=path, now=now)
        if value is not None:
            # got it from cache
            return value
        elif holder is None:
            # holder not exists, means it is the first querying
            pass
        elif holder.is_alive(now=now):
            # holder is not expired yet,
            # means the value is actually empty,
            # no need to check it again.
            return None
        #
        #  2. lock for querying
        #
        with self.__lock:
            # locked, check again to make sure the cache not exists.
            # (maybe the cache was updated by other threads while waiting the lock)
            value, holder = cache_pool.fetch(key=path, now=now)
            if value is not None:
                return value
            elif holder is None:
                pass
            elif holder.is_alive(now=now):
                return None
            else:
                # holder exists, renew the expired time for other threads
                holder.renewal(duration=self.MEM_CACHE_REFRESH, now=now)
            # check local storage
            value = await Storage.read_text(path=path)
            # update memory cache
            cache_pool.update(key=path, value=value, life_span=self.MEM_CACHE_EXPIRES, now=now)
        #
        #  3. OK, return cached value
        #
        return value

    async def _get_path(self, title: str) -> Optional[str]:
        index_path = self.indexes
        if index_path is None:
            self.error(msg='failed to get indexes for webmaster')
            return None
        # get indexes
        js = await self._load_file(path=index_path)
        if js is None:
            self.error(msg='indexes not found: %s' % index_path)
            return None
        info = json_decode(string=js)
        if info is None:
            self.error(msg='indexes error: %s' % js)
            return None
        assert isinstance(info, Dict), 'indexes error: %s' % info
        return info.get(title)

    async def get_format(self, title: str) -> Optional[str]:
        path = await self._get_path(title=title)
        if path is None:
            self.warning(msg='page not found: "%s"' % title)
        elif path.endswith(r'.md'):
            return 'markdown'
        elif path.endswith(r'.html'):
            return 'html'
        else:
            self.error(msg='unknown format: "%s" -> %s' % (title, path))

    async def get_page(self, title: str) -> Optional[str]:
        path = await self._get_path(title=title)
        if path is None:
            self.warning(msg='page not found: "%s"' % title)
        else:
            return await self._load_file(path=path)


class WebPageService(BaseService, Logging):

    def __init__(self, config: Config):
        super().__init__()
        self.__master = WebMaster(config=config)

    @property
    def master(self) -> WebMaster:
        return self.__master

    # private
    async def _get_page_content(self, title: str) -> Tuple[Optional[str], Optional[str]]:
        # load page content with title
        master = self.master
        text_content = await master.get_page(title=title)
        text_format = await master.get_format(title=title)
        return text_content, text_format

    # Override
    async def _process_file_content(self, content: FileContent, request: Request):
        self.warning(msg='TODO: process file content from "%s"' % request.identifier)

    # Override
    async def _process_text_content(self, content: TextContent, request: Request):
        await self._request_homepage(content=content, request=request)

    # Override
    async def _process_customized_content(self, content: CustomizedContent, request: Request):
        app = content.application
        mod = content.module
        act = content.action
        if app == 'chat.dim.sites':
            if mod == 'homepage' and act == 'request':
                return await self._request_homepage(content=content, request=request)
        # error
        sender = request.envelope.sender
        self.error(msg='unknown customized content: app="%s" mod="%s" act="%s", sender: %s' % (app, mod, act, sender))

    async def _request_homepage(self, content: Content, request: Request):
        # get keywords
        keywords = content.get_str(key='keywords')
        if keywords is None or len(keywords) == 0:
            keywords = content.get_str(key='title')
            if keywords is None or len(keywords) == 0:
                # keywords = await request.get_text(facebook=self.facebook)
                keywords = content.get_str(key='text')
                if keywords is None:
                    self.error(msg='text content error: %s' % content)
                    return
        title = keywords.strip().lower()
        # load page content with title
        text, fmt = await self._get_page_content(title=title)
        if text is None:
            self.warning(msg='page content not found: "%s"' % keywords)
        else:
            self.info(msg='loaded %d bytes for page: "%s"' % (len(text), keywords))
        await self._respond_homepage(title=keywords, text=text, text_format=fmt, request=request)

    async def _respond_homepage(self, title: str, text: Optional[str], text_format: Optional[str], request: Request):
        if text is None:
            text = '## 404 Not Found\n' \
                   'The resource **"%s"** not exists.' % title.strip()
            text_format = 'markdown'
        elif text_format is None:
            text_format = 'markdown'
        # search tag
        content = request.content
        tag = content.get('tag')
        title = content.get('title')
        hidden = content.get('hidden')
        keywords = content.get('keywords')
        self.info(msg='respond %d bytes with tag %s to %s' % (len(text), tag, request.identifier))
        return await self.respond_text(text=text, request=request, extra={
            'format': text_format,
            'muted': hidden,
            'hidden': hidden,

            'app': 'chat.dim.sites',
            'mod': 'homepage',
            'act': 'respond',
            'expires': 600,

            'tag': tag,
            'title': title,
            'keywords': keywords,
        })
