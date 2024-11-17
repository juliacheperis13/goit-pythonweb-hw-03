from http.server import HTTPServer, BaseHTTPRequestHandler
import pathlib
import urllib.parse
import mimetypes
import os
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader


class StorageManager:
    def __init__(self, file_path="./storage/data.json"):
        self.file_path = file_path
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def save_entry(self, data):
        timestamp = datetime.now().isoformat()
        all_data = self.load_all_data()
        all_data[timestamp] = data
        with open(self.file_path, "w", encoding="utf-8") as json_file:
            json.dump(all_data, json_file, ensure_ascii=False, indent=4)

    def load_all_data(self):
        if not os.path.exists(self.file_path):
            return {}
        with open(self.file_path, "r", encoding="utf-8") as json_file:
            return json.load(json_file)


class HttpHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.storage_manager = StorageManager()
        super().__init__(*args, **kwargs)

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("index.html")
        elif pr_url.path == "/message":
            self.send_html_file("message.html")
        elif pr_url.path == "/read":
            all_data = self.storage_manager.load_all_data()
            self.render_template("read.html", all_data)
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("error.html", 404)

    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {
            key: value for key, value in [el.split("=") for el in data_parse.split("&")]
        }

        self.storage_manager.save_entry(data_dict)
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())

    def render_template(self, url, data, status=200):
        env = Environment(loader=FileSystemLoader("./templates/"))
        template = env.get_template(url)
        file = template.render(data=data)
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(file.encode())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ("", 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == "__main__":
    run()
