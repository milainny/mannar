from tornado import websocket, web, ioloop, options
from tornado.options import options, define
import os
import json
import base64
import main as ma

define(name='port', default=5000, help='.', type=int)

class ImgHandler(websocket.WebSocketHandler):
  clients = []

  def open(self):
      ImgHandler.clients.append(self)
      print('client connected')

  def on_close(self):
      ImgHandler.clients.remove(self)
      print('client removed')

  def on_message(self, message):
    print('aquii')
    message_ = json.loads(message)
    if message_['data'] is not None:
      data = message_['data']
      data = data.split(';base64')[1].encode('utf-8')
      data = base64.b64decode(data)
      print(message_['file_name'])
      with open(os.path.join('./', "automataImg.jpg"), 'wb') as file:
        file.write(data)
      r = ma.main("automataImg.jpg")
      self.write_message(r)

  def check_origin(self, origin):
      return True

if __name__ == '__main__':
    application = web.Application(
        handlers=[
            (r'/img', ImgHandler)
        ],
        template_path=os.path.join(os.path.dirname(__file__), 'template'),
        static_path=os.path.join(os.path.dirname(__file__), 'static'),
        debug=True,
        autoreload=True
    )
    application.listen(options.port)
    ioloop.IOLoop.current().start()
