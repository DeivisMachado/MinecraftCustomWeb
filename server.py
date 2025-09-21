
import http.server
import socketserver
import subprocess
import json
from functools import partial

# O comando para iniciar o servidor Minecraft.
# Ele será executado no diretório onde o server.py está.
MINECRAFT_COMMAND = "/usr/bin/java @user_jvm_args.txt @libraries/net/neoforged/neoforge/21.1.185/unix_args.txt nogui"

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="public", **kwargs)

    def do_POST(self):
        if self.path == "/start-server":
            try:
                print(f"Recebido comando para iniciar o servidor. Executando: {MINECRAFT_COMMAND}")
                # Usamos Popen para não bloquear o servidor web.
                # O servidor Minecraft vai rodar como um processo separado.
                subprocess.Popen(MINECRAFT_COMMAND, shell=True, cwd="ext/neoforgeserver") # Define o diretório de trabalho para o servidor

                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"message": "Comando para iniciar o servidor foi enviado com sucesso!"}).encode('utf-8'))
            except FileNotFoundError:
                print("Erro: O comando java não foi encontrado. Verifique se o Java está instalado e no PATH.")
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"message": "Erro: Java não encontrado."}).encode('utf-8'))
            except Exception as e:
                print(f"Um erro ocorreu ao tentar iniciar o servidor: {e}")
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"message": f"Erro interno do servidor: {e}"}).encode('utf-8'))
            return

        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Not Found")

PORT = 8000
Handler = MyHttpRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Servidor web iniciado na porta {PORT}. Sirva a pasta 'public'.")
    print(f"Acesse http://localhost:{PORT}")
    httpd.serve_forever()
