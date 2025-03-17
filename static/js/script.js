$(document).ready(function() {
    $('.formato-form').on('submit', function(e) {
        e.preventDefault(); // Impede o envio padrão do formulário

        var formData = new FormData(this);
        $('#status-message').text('Gerando seu ebook... Aguarde!').show();
        $('#download-link').hide(); // Esconde o botão de download até estar pronto

        $.ajax({
            url: '/gerar_ebook',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                var taskId = response.task_id;
                checkTaskStatus(taskId);
            },
            error: function(xhr) {
                $('#status-message')
                    .text('Erro: ' + (xhr.responseJSON ? xhr.responseJSON.error : 'Falha ao gerar o ebook'))
                    .addClass('text-danger');
            }
        });
    });

    function checkTaskStatus(taskId) {
        $.get('/status/' + taskId, function(data) {
            if (data.status === 'SUCCESS') {
                // Opção 1: Botão de Download (descomente esta se preferir)
                $('#status-message')
                    .text('Ebook gerado com sucesso!')
                    .addClass('text-success')
                    .removeClass('text-danger');
                $('#download-link')
                    .attr('href', data.download_url)
                    .show(); // Mostra o botão com o link

                // Opção 2: Redirecionamento Automático (descomente esta se preferir, comente a Opção 1)
                /*
                $('#status-message')
                    .text('Ebook gerado com sucesso! Redirecionando...')
                    .addClass('text-success')
                    .removeClass('text-danger');
                window.location.href = data.download_url; // Abre o PDF no navegador
                */
            } else if (data.status === 'FAILURE') {
                $('#status-message')
                    .text('Erro ao gerar o ebook: ' + (data.error || 'Tente novamente.'))
                    .addClass('text-danger');
                $('#download-link').hide();
            } else {
                $('#status-message')
                    .text('Gerando seu ebook... Aguarde! (' + data.status + ')');
                setTimeout(function() { checkTaskStatus(taskId); }, 2000); // Verifica a cada 2 segundos
            }
        }).fail(function() {
            $('#status-message')
                .text('Erro ao verificar o status. Tente novamente.')
                .addClass('text-danger');
            $('#download-link').hide();
        });
    }
});