from __future__ import print_function

import os.path
import shutil
import tornado.ioloop
import tornado.web
import tornado.process
import tornado.escape
from tornado import gen
import tempfile

tmpdir = "/tmp"

class InvalidRequest(Exception):
    def __init__(self, err):
        self.message = err

def parse_request(request, format):
    """Decode a JSON request based on the \
given format. It will only extract what is required \
from the data object and leave the rest."""
    result = {}
    req = tornado.escape.json_decode(request)
    if not "text" in req or not "lang" in req:
        raise InvalidRequest("Invalid request object")

    result["text"] = req["text"]
    result["lang"] = req["lang"]
    return result

def mktmpdir(prefix="js-svc_"):
    """Attempt to make a temporary directory in /tmp
If it fails it raises an EnvironmentError."""
    return tempfile.mkdtemp(prefix=prefix)

class ServiceHandler(tornado.web.RequestHandler):
    def get(self):
        self.write_error(405)
    def put(self):
        self.write_error(405)
    def head(self):
        self.write_error(405)
    def delete(self):
        self.write_error(405)
    def trace(self):
        self.write_error(405)
    def patch(self):
        self.write_error(405,)
    @gen.coroutine
    def post(self):        
        tmpdir = mktmpdir()
        dat = parse_request(self.request.body)

        with open(os.path.join(tmpdir, "input"), "wb") as f:
            f.write(tornado.escape.json_encode(dat))
        proc = tornado.process.Subprocess(["convert-to-js.py", tmpdir + "/input", tmpdir + "/output"])

        resp = {
            "text": "",
            "success": True,
            "output": ""
        }

        try:
            yield proc.wait_for_exit()
        except:
            resp["success"] = False

        with open(os.path.join(tmpdir, "output"), "rb") as f:
            resp["text"] = f.read()

        shutil.rmtree(tmpdir)

        self.write(resp)
        self.finish()

if __name__ == "__main__":
    app = tornado.web.Application([
        (r"/", ServiceHandler)
    ])
    app.listen(80)
    tornado.ioloop.IOLoop.current().start()

        
        
