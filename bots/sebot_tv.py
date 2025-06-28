#! /usr/bin/env python3
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

"""
    Service Bot: TV Box
    ~~~~~~~~~~~~~~~~~~~

    Chat bot as service
"""

from dimples.utils import Path

path = Path.abs(path=__file__)
path = Path.dir(path=path)
path = Path.dir(path=path)
Path.add(path=path)

from libs.utils import Log, Runner
from libs.client import ClientProcessor, Service
from engine import LiveStreamService

from bots.shared import GlobalVariable
from bots.shared import create_config, start_bot


class BotMessageProcessor(ClientProcessor):

    # Override
    def _create_service(self) -> Service:
        shared = GlobalVariable()
        config = shared.config
        # create & run service
        service = LiveStreamService(config=config)
        # Runner.thread_run(runner=service)
        thr = Runner.async_thread(coro=service.run())
        thr.start()
        return service


#
# show logs
#
Log.LEVEL = Log.DEVELOP


DEFAULT_CONFIG = '/etc/dim/bots.ini'


async def async_main():
    # create global variable
    shared = GlobalVariable()
    config = await create_config(app_name='ChatBot: TV Box', default_config=DEFAULT_CONFIG)
    await shared.prepare(config=config)
    #
    #  Create & start the bot
    #
    client = await start_bot(ans_name='tvbox', section='tvbox', processor_class=BotMessageProcessor)
    Log.warning(msg='bot stopped: %s' % client)


def main():
    Runner.sync_run(main=async_main())


if __name__ == '__main__':
    main()
