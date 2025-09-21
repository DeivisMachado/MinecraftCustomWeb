document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('start-btn');

    if (startBtn) {
        startBtn.addEventListener('click', () => {
            console.log('Botão clicado. Enviando requisição para /start-server...');

            // Desabilita o botão para evitar múltiplos cliques
            startBtn.disabled = true;
            startBtn.textContent = 'Iniciando...';

            fetch('/start-server', {
                method: 'POST',
            })
            .then(response => response.json())
            .then(data => {
                console.log('Resposta do servidor:', data);
                alert(data.message || 'Comando enviado!');
                // Você pode optar por reabilitar o botão ou não
                // startBtn.disabled = false;
                // startBtn.textContent = 'Iniciar Servidor';
            })
            .catch(error => {
                console.error('Erro ao enviar requisição:', error);
                alert('Ocorreu um erro ao tentar iniciar o servidor. Veja o console para detalhes.');
                // Reabilita o botão em caso de erro
                startBtn.disabled = false;
                startBtn.textContent = 'Iniciar Servidor';
            });
        });
    }
});
