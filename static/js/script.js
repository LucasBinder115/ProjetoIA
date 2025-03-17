$(document).ready(function() {
    $('.formato-form').on('submit', function(e) {
        e.preventDefault(); // Prevent default form submission

        var formData = new FormData(this);
        $.ajax({
            url: '/gerar_ebook',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                var taskId = response.task_id;
                $('#status').text('Gerando seu ebook... Aguarde!').show();
                checkTaskStatus(taskId);
            },
            error: function(xhr) {
                $('#status').text('Erro: ' + xhr.responseJSON.error).show();
            }
        });
    });

    function checkTaskStatus(taskId) {
        $.get('/status/' + taskId, function(data) {
            if (data.status === 'SUCCESS') {
                $('#status').html('Pronto! <a href="' + data.download_url + '" class="btn btn-success btn-sm">Baixar Ebook</a>');
            } else if (data.status === 'FAILURE') {
                $('#status').text('Erro ao gerar o ebook. Tente novamente.');
            } else {
                setTimeout(function() { checkTaskStatus(taskId); }, 2000); // Check every 2 seconds
            }
        });
    }
});