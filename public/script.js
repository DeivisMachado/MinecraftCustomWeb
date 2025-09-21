document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('start-btn');
    let statusInterval = null; // Variável para guardar nosso setInterval

    // Função para atualizar a aparência e função do botão
    const updateButton = (status) => {
        switch (status) {
            case 'ONLINE':
                startBtn.textContent = 'TERMINAR';
                startBtn.className = 'terminar';
                startBtn.disabled = false;
                break;
            case 'STARTING':
                startBtn.textContent = 'INICIANDO...';
                startBtn.className = 'iniciando';
                startBtn.disabled = true;
                break;
            case 'OFFLINE':
            default:
                startBtn.textContent = 'Iniciar Servidor';
                startBtn.className = ''; // Classe padrão (verde)
                startBtn.disabled = false;
                break;
        }
    };

    // Função que consulta o status do servidor
    const pollStatus = () => {
        fetch('/status')
            .then(response => response.json())
            .then(data => {
                console.log('Status atual:', data.status);
                updateButton(data.status);

                // Se o servidor está online ou offline, paramos de verificar
                if (data.status === 'ONLINE' || data.status === 'OFFLINE') {
                    if (statusInterval) {
                        clearInterval(statusInterval);
                        statusInterval = null;
                    }
                }
            })
            .catch(error => {
                console.error('Erro ao verificar status:', error);
                // Se der erro, para de verificar para não sobrecarregar
                if (statusInterval) {
                    clearInterval(statusInterval);
                    statusInterval = null;
                }
            });
    };

    // Event listener principal do botão
    startBtn.addEventListener('click', () => {
        const currentStatus = startBtn.textContent;

        if (currentStatus === 'Iniciar Servidor') {
            // --- Inicia o servidor ---
            fetch('/start-server', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    // Começa a verificar o status
                    updateButton('STARTING');
                    if (!statusInterval) {
                        statusInterval = setInterval(pollStatus, 2000); // Verifica a cada 2 segundos
                    }
                })
                .catch(error => {
                    console.error('Erro ao iniciar o servidor:', error);
                    alert('Erro ao tentar iniciar o servidor.');
                });
        } else if (currentStatus === 'TERMINAR') {
            // --- Para o servidor ---
            fetch('/stop-server', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    // O status será atualizado para OFFLINE pela thread do backend,
                    // então a próxima verificação de status vai atualizar o botão.
                    if (!statusInterval) {
                        statusInterval = setInterval(pollStatus, 2000);
                    }
                })
                .catch(error => {
                    console.error('Erro ao parar o servidor:', error);
                    alert('Erro ao tentar parar o servidor.');
                });
        }
    });

    // Inicia a verificação de status assim que a página carrega,
    // para o caso do servidor já estar rodando.
    pollStatus();
});