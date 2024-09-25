import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import io
from kgqan.kgqan import KGQAn
from kgqan.logger import logger

hostName = "0.0.0.0"
serverPort = 8898

max_Vs = 1
max_Es = 21
max_answers = 41
limit_VQuery = 400
limit_EQuery = 25

class MyServer(BaseHTTPRequestHandler):
    def do_POST(self):
        print("In post ")
        print(self.request)
        try:
            content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
            post_data = self.rfile.read(content_length)  # <--- Gets the data itself
            print("Before parsing ", post_data)
            # fix_bytes_value = post_data.replace(b"'", b'"')
            data = json.load(io.BytesIO(post_data))
            print("After parsing ", data)
        except:
            self.send_error(500, "Failed to parse data from request")

        try:
            MyKGQAn = KGQAn(n_max_answers=max_answers, n_max_Vs=max_Vs, n_max_Es=max_Es,
                            n_limit_VQuery=limit_VQuery, n_limit_EQuery=limit_EQuery)

            answers, _, _, _, _, _, sparqls = MyKGQAn.ask(question_text=data['question'], knowledge_graph=data['knowledge_graph'])
            result = json.dumps(sparqls)
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(bytes(result, "utf-8"))
        except Exception as e:
            print("Error from : ", e)
            print("Stack trace")
            traceback.print_exc()
            self.send_error(500, "Failed to get the answer to the question")

def main():
    webServer = HTTPServer((hostName, serverPort), MyServer)
    logger.log_info("Server started http://%s:%s" % (hostName, serverPort))
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")

if __name__ == "__main__":
    main()

