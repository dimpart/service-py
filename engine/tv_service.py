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

from dimples import FileContent, TextContent
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
        text = content.text
        if text is None or len(text) == 0:
            self.error(msg='text content error: %s' % content)
            return
        else:
            keyword = text.strip().lower()
        # process
        if keyword == 'live stream sources':
            self.clear_caches()
            array = await self.get_lives()
            await self._respond_live_urls(lives=array, request=request)
        else:
            self.error(msg='ignore request "%s" from %s' % (text, request.identifier))

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
        tag = request.content.get('tag')
        title = request.content.get('title')
        hidden = request.content.get('hidden')
        cid = request.identifier
        self.info(msg='respond %d sources with tag %s to %s' % (count, tag, cid))
        return await self.respond_markdown(text=text, request=request, muted='yes', extra={
            'hidden': hidden,

            'app': 'chat.dim.tvbox',
            'mod': 'lives',
            'act': 'respond',
            'expires': 600,

            'tag': tag,
            'title': title,
            'lives': lives,
            'description': self.LIST_DESC,
        })
