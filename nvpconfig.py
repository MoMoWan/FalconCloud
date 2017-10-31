import logging
import tornado.escape
import tornado.ioloop
import tornado.web
import os
import uuid
from tornado.concurrent import Future
from tornado import gen
from tornado.options import define, options, parse_command_line
import globals
import subprocess
import platform
import handlers
define("port", default=8888, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")

def main():
    parse_command_line()
    root_dir = os.path.dirname(os.path.abspath(__file__))
    globals.BIN_DIRECTORY = os.path.join(root_dir, "bin")
    print("bin directory = {}".format(globals.BIN_DIRECTORY))
    app = tornado.web.Application(
        [
            (r"/jedi/nvpconfig", handlers.NvpConfigHandler),
            (r"/jedi/fim", handlers.MfgBundleHandler),
            (r"/phx/ledm", handlers.LedmHandler),
            ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        )
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
