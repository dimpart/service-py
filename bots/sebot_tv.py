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

import sys

from dimples.utils import SysArgvParser
from dimples.utils import init_logger
from dimples.utils import Log, LogLevel
from dimples.utils import Runner
from dimples.utils import Path

path = Path.abs(path=__file__)
path = Path.dir(path=path)
path = Path.dir(path=path)
Path.add(path=path)

from libs.client import ClientProcessor, Service
from engine import LiveStreamService

from bots.shared import GlobalVariable
from bots.shared import create_config, start_bot
from bots.shared import show_help


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
#  show logs
#
LOG_LEVEL = LogLevel.DEVELOP

BOT_NAME = 'tvbox'

APP_NAME = 'ChatBot: TV Box'

DEFAULT_CONFIG = '/etc/dim/bots.ini'


async def async_main():
    #
    #  parse cmd parameters
    #
    sys_argv = SysArgvParser.parse(shortopts='hf:ld:',
                                   longopts=['help', 'config=', 'log-location', 'log-dir='])
    if sys_argv is None:
        show_help(app_name=APP_NAME, cmd=sys.argv[0], default_config=DEFAULT_CONFIG)
        sys.exit(1)
    #
    #  init logger
    #
    show_location = sys_argv.has_opt(opt='log-location')
    log_directory = sys_argv.get_opt(opt='log-dir')
    init_logger(name=BOT_NAME, level=LOG_LEVEL, show_location=show_location, directory=log_directory)
    #
    #  create config
    #
    config = await create_config(sys_argv=sys_argv, default_config=DEFAULT_CONFIG)
    if config is None:
        show_help(app_name=APP_NAME, cmd=sys.argv[0], default_config=DEFAULT_CONFIG)
        sys.exit(1)
    #
    #  Create & start the bot
    #
    client = await start_bot(ans_name=BOT_NAME, section='tvbox', processor_class=BotMessageProcessor)
    Log.warning(msg='bot stopped: %s' % client)


def main():
    Runner.sync_run(main=async_main())


if __name__ == '__main__':
    main()
