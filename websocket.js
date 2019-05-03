
$(document).ready( function() {

    socket = new WebSocket('ws://localhost:5000/img')

    /*
    * Funções websocket
    */
    socket.onopen = function(event) {
        document.getElementById('server-status').innerHTML = 'Conectado'
    }

    socket.onerror = function(error) {
        document.getElementById("server-status").innerHTML = 'Erro ao realizar conexão'
    };

    socket.onmessage = function (evt) {
        alert(evt.data);
    };

    var data = null
    var file_name = null

    $(document).on('change', '#file-input', function (e) {
        var img = e.target.files[0];
        file_name = img.name;

        var file_reader = new FileReader();

        file_reader.onload = function (e) {
            data = e.target.result;
        };

        file_reader.readAsDataURL(img);

    });

    $(document).on('click', '#btn-file', function () {
        if (file_name == null){
            alert("É necessário primeiro selecionar um arquivo de imagem");
        } else {
          var message = {
              'file_name': file_name,
              'data': data
          };

          socket.send(JSON.stringify(message));

        }
    })

    socket.onmessage = function (evt) {
        if (evt.data == "0"){
          aler
          window.location.href = "./result.html";
        }
    };
})
