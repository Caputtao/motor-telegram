<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            padding: 20px; 
            background-color: #f9f9f9;
        }
        .container { 
            max-width: 500px; 
            margin: auto; 
            background: white; 
            padding: 20px; 
            border-radius: 8px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
        }
        h3 { color: #14412A; margin-top: 0; }
        input { 
            width: 100%; 
            padding: 12px; 
            margin: 10px 0 20px 0; 
            box-sizing: border-box; 
            border: 1px solid #ccc; 
            border-radius: 4px;
        }
        button { 
            width: 100%; 
            padding: 12px; 
            background-color: #14412A; 
            color: white; 
            border: none; 
            font-weight: bold; 
            font-size: 16px;
            border-radius: 4px; 
            cursor: pointer; 
        }
        button:hover { background-color: #0f301e; }
        #resultado { 
            margin-top: 20px; 
            white-space: pre-wrap; 
            background: #f1f1f1; 
            padding: 15px; 
            border-radius: 4px;
            font-size: 13px;
            color: #333;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h3>Consulta Rápida de Dados</h3>
        <label for="cpfInput">CPF do Cliente:</label>
        <input type="text" id="cpfInput" placeholder="Digite apenas os números...">
        <button onclick="buscarDados()">Buscar Cliente</button>
        
        <div id="resultado"></div>
    </div>

    <script>
        async function buscarDados() {
            const cpf = document.getElementById('cpfInput').value.replace(/\D/g, '');
            const divResultado = document.getElementById('resultado');
            
            if (cpf.length !== 11) {
                alert("Por favor, digite um CPF válido.");
                return;
            }

            divResultado.style.display = "block";
            divResultado.innerText = "Conectando ao banco de dados... aguarde.";
            
            try {
                // URL do servidor Python Render
                const url = `https://SEU-SERVIDOR-PYTHON.onrender.com/consultar/${cpf}`;
                const response = await fetch(url);
                const data = await response.json();
                
                if(data.sucesso) {
                    // Joga o texto copiado da página direto na tela
                    divResultado.innerText = data.dados;
                } else {
                    divResultado.innerText = "Erro: " + data.erro;
                }
            } catch (error) {
                divResultado.innerText = "Falha de comunicação com o sistema central.";
            }
        }
    </script>
</body>
</html>
