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

from typing import List, Dict

from dimples import Content
from dimples import FileContent, TextContent
from dimples import CustomizedContent

from tvbox.lives import LiveParser
from tvbox import LiveConfig
from tvbox import LiveLoader
from tvbox import LiveScanner

from libs.utils import Logging
from libs.utils import Config

from .service import Request
from .service import BaseService


class LiveStreamService(BaseService, Logging):

    # list foot
    LIST_DESC = '* Here are the live stream sources collected from the internet;\n' \
                '* All live stream sources are contributed by the netizens with a spirit of sharing;\n' \
                '* Before presenting them to you, the service bot scans all sources to verify their availability.'

    def __init__(self, config: Config):
        super().__init__()
        index_uri = config.get_string(section='tvbox', option='index')
        assert index_uri is not None and len(index_uri) > 0, 'failed to get index url: %s' % config
        info = {
            'tvbox': {
                'sources': [
                    index_uri,
                ],
            }
        }
        self.__loader = LiveLoader(config=LiveConfig(info=info),
                                   parser=LiveParser(),
                                   scanner=LiveScanner())

    @property
    def loader(self) -> LiveLoader:
        return self.__loader

    def clear_caches(self):
        self.__loader.clear_caches()

    async def get_lives(self) -> List[Dict]:
        live_set = await self.__loader.get_live_set()
        return live_set.lives

    # Override
    async def _process_file_content(self, content: FileContent, request: Request):
        self.warning(msg='TODO: process file content from "%s"' % request.identifier)

    # Override
    async def _process_text_content(self, content: TextContent, request: Request):
        await self._request_lives(content=content, request=request)

    # Override
    async def _process_customized_content(self, content: CustomizedContent, request: Request):
        # app = content.application
        app = content.get_str(key='app')
        mod = content.module
        act = content.action
        if app == 'chat.dim.tvbox':
            if mod == 'lives' and act == 'request':
                return await self._request_lives(content=content, request=request)
        # error
        sender = request.envelope.sender
        self.error(msg='unknown customized content: app="%s" mod="%s" act="%s", sender: %s' % (app, mod, act, sender))

    async def _request_lives(self, content: Content, request: Request):
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
        command = keywords.strip().lower()
        # TV command
        if command == 'live stream sources':
            self.clear_caches()
            array = await self.get_lives()
            await self._respond_live_urls(lives=array, request=request)
        else:
            self.error(msg='ignore request "%s" from %s' % (keywords, request.identifier))

    async def _respond_live_urls(self, lives: List[Dict], request: Request):
        count = len(lives)
        text = 'Live Stream Sources:\n'
        text += '\n----\n'
        for item in lives:
            url = item.get('url')
            text += '- [%s](%s#lives.txt "LIVE")\n' % (url, url)
        text += '\n----\n'
        text += 'Total %d source(s).' % count
        # search tag
        content = request.content
        tag = content.get('tag')
        title = content.get('title')
        hidden = content.get('hidden')
        keywords = content.get('keywords')
        self.info(msg='respond %d sources with tag %s to %s' % (count, tag, request.identifier))
        return await self.respond_text(text=text, request=request, extra={
            'format': 'markdown',
            'muted': hidden,
            'hidden': hidden,

            'app': 'chat.dim.tvbox',
            'mod': 'lives',
            'act': 'respond',
            'expires': 600,

            'tag': tag,
            'title': title,
            'keywords': keywords,

            'lives': lives,
            'description': self.LIST_DESC,
        })
