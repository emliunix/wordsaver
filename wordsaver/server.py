# -*- coding: utf-8 -*-

import tornado
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, RedirectHandler, StaticFileHandler
from tornado import netutil
from tornado.httpserver import HTTPServer
import wordsaver.dbop as dbop
import json
import os
import datetime
import dateutil

def exceptwrapper(meth):
    def f(self, *args, **kwargs):
        try:
            meth(self, *args, **kwargs)
        except StandardError as err:
            self.set_status(400)
            self.write({"status": "err", "message": str(err)})
    return f

class WordsHandler(RequestHandler):
    @exceptwrapper
    def get(self):
        words = dbop.getallword()
        # words = [w.todict() for w in words]
        self.write({"status": "ok", "result": words})

    @exceptwrapper
    def post(self):
        contenttype = self.request.headers["Content-Type"]
        if contenttype and not contenttype.find("application/json") == -1:
            jobj = json.loads(self.request.body.decode("UTF-8"))
            word = jobj["word"]
            date = jobj["date"]
            datetime.datetime.now().second()
            w = dbop.addword(word)
            if w:
                self.write({"status": "ok", "result": w})
                # try to fetch data from bing
                try:
                    dbop.refreshworddetail(w["wid"])
                except StandardError:
                    pass
            else:
                raise StandardError("Add word error")
        else:
            raise StandardError("Content-Type is not \"applicaton/json\"")


class WordHandler(RequestHandler):
    @exceptwrapper
    def get(self, wid):
        wid = int(wid)
        if "yes" == self.get_query_argument("refresh", "no"):
            if not dbop.refreshworddetail(wid):
                raise StandardError("err")
        w = dbop.getword(wid)
        # w = w.todict()
        if w:
            detail = dbop.getworddetail(wid)
            if detail:
                w.update(detail)
            self.write({"status": "ok", "result": w})
        else:
            raise StandardError("get word failed")

    @exceptwrapper
    def delete(self, wid):
        wid = int(wid)
        if dbop.delword(wid):
            self.write({"status": "ok"})
        else:
            raise StandardError("delete word failed")

staticfilepath = os.path.join(os.path.dirname(__file__), "static")

def run():
    app = Application([
        (r"/", RedirectHandler, {"url": "/s/index.html"}),
        (r"/s/(.*)", StaticFileHandler, {"path": staticfilepath}),
        (r"/word", WordsHandler),
        (r'/word/(.*)', WordHandler)
    ], debug=False)

    server = HTTPServer(app)
    # mode 438 means 0o666
    socket = netutil.bind_unix_socket("/var/wordsaver/socket", mode=438)
    tornado.process.fork_processes(0)
    server.add_sockets([socket])
    # server.start(0)
    IOLoop.current().start()
