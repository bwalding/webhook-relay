# heavily borrowing from: https://github.com/hiroakis/tornado-websocket-example

from tornado import websocket, web, ioloop
import json

clients = {}

class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("index.html")

class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):        
        clients[self.request.uri.split('/subscribe/')[1]] = self

    def on_close(self):
        tenant = self.request.uri.split('/subscribe/')[1]
        if tenant in clients: 
            del clients[tenant]
                    

class ApiHandler(web.RequestHandler):

    @web.asynchronous
    def get(self, *args):
        self.finish()

    @web.asynchronous
    def post(self, *args):    
        tenant = self.request.uri.split('/publish/')[1]
        headers = {}
        for header in self.request.headers:
            headers[header] = self.request.headers[header]        
        payload = {'headers': headers, 'body': self.request.body}
        
        if tenant in clients: 
            clients[tenant].write_message(json.dumps(payload, ensure_ascii=False))
        self.finish()

app = web.Application([
    (r'/', IndexHandler),
    (r'/subscribe/.*', SocketHandler),
    (r'/publish/.*', ApiHandler),
    (r'/(favicon.ico)', web.StaticFileHandler, {'path': '../'}),
    (r'/(rest_api_example.png)', web.StaticFileHandler, {'path': './'}),
])

if __name__ == '__main__':
    app.listen(8888)
    ioloop.IOLoop.instance().start()
