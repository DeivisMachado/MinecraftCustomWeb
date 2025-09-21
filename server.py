import http.server
import socketserver
import subprocess
import json
import threading
import time

# --- Configuração ---
PORT = 8000
MINECRAFT_COMMAND = "./run.sh nogui"
SERVER_DIR = "." # Diretório do servidor, agora que está tudo na mesma pasta
SERVER_ONLINE_MESSAGE = "Done" # Texto que indica que o servidor está online

# --- Estado Global do Servidor (simplificado) ---
SERVER_STATE = {
    "process": None,
    "status": "OFFLINE",  # OFFLINE, STARTING, ONLINE
    "thread": None
}

def watch_server_output():
    """
    Esta função roda em uma thread para monitorar a saída do console do servidor.
    """
    # Garante que estamos usando o processo correto que está no estado global
    process = SERVER_STATE["process"]
    if not process:
        return

    print("Thread de monitoramento iniciada.")
    # Lê a saída do processo linha por linha
    for line in iter(process.stdout.readline, b''):
        line_str = line.decode('utf-8').strip()
        if line_str: # Mostra o output do servidor no console do nosso script
            print(f"[Minecraft Server]: {line_str}")

        # Verifica se a mensagem de "servidor online" apareceu
        if SERVER_ONLINE_MESSAGE in line_str and SERVER_STATE["status"] == "STARTING":
            print("--- SERVIDOR DETECTADO COMO ONLINE ---")
            SERVER_STATE["status"] = "ONLINE"

    # Quando o loop termina, o processo foi encerrado
    process.wait()
    print("--- SERVIDOR DETECTADO COMO OFFLINE ---")
    SERVER_STATE["status"] = "OFFLINE"
    SERVER_STATE["process"] = None
    SERVER_STATE["thread"] = None
    print("Thread de monitoramento finalizada.")


class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    # Sirva arquivos da pasta 'public' por padrão
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="public", **kwargs)

    def do_GET(self):
        # Endpoint para verificar o status
        if self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': SERVER_STATE['status']}).encode('utf-8'))
        else:
            # Comportamento padrão para servir arquivos (index.html, css, js)
            super().do_GET()

    def do_POST(self):
        # Endpoint para iniciar o servidor
        if self.path == '/start-server':
            if SERVER_STATE['process'] is not None:
                self.send_response(409) # Conflict
                self.end_headers()
                self.wfile.write(json.dumps({'message': 'Servidor já está em execução ou iniciando.'}).encode('utf-8'))
                return

            try:
                print(f"Iniciando o servidor com o comando: {MINECRAFT_COMMAND}")
                # Inicia o processo do servidor
                proc = subprocess.Popen(
                    MINECRAFT_COMMAND,
                    cwd=SERVER_DIR,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    stderr=subprocess.STDOUT
                )
                # Atualiza o estado global
                SERVER_STATE['process'] = proc
                SERVER_STATE['status'] = "STARTING"

                # Inicia a thread para monitorar o output do servidor
                thread = threading.Thread(target=watch_server_output)
                SERVER_STATE['thread'] = thread
                thread.start()

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'message': 'Comando para iniciar o servidor enviado.'}).encode('utf-8'))

            except Exception as e:
                print(f"Erro ao iniciar o servidor: {e}")
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({'message': f'Erro: {e}'}).encode('utf-8'))

        # Endpoint para parar o servidor
        elif self.path == '/stop-server':
            proc = SERVER_STATE.get('process')
            if proc is None:
                self.send_response(409) # Conflict
                self.end_headers()
                self.wfile.write(json.dumps({'message': 'Servidor não está em execução.'}).encode('utf-8'))
                return

            try:
                print("Enviando comando 'stop' para o servidor Minecraft...")
                proc.stdin.write(b'stop\n')
                proc.stdin.flush()

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'message': 'Comando para parar o servidor enviado.'}).encode('utf-8'))
            except Exception as e:
                print(f"Erro ao parar o servidor: {e}")
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({'message': f'Erro: {e}'}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

# --- Início do Servidor ---
with socketserver.TCPServer(('', PORT), MyHttpRequestHandler) as httpd:
    print(f"Servidor web iniciado na porta {PORT}")
    httpd.serve_forever()