## Como Rodar o Projeto Flask "Meu Memorial Online"

Este guia irá ajudá-lo a configurar e rodar o projeto Flask "Meu Memorial Online" em seu ambiente local.

### Pré-requisitos

Certifique-se de ter o Python 3 e o `pip` (gerenciador de pacotes do Python) instalados em seu sistema.

### 1. Descompactar o Projeto

Primeiro, descompacte o arquivo `meumemorial.zip` em uma pasta de sua preferência.

### 2. Navegar até o Diretório do Projeto

Abra seu terminal ou prompt de comando e navegue até o diretório raiz do projeto `meumemorial`:

```bash
cd /caminho/para/meumemorial
```

### 3. Criar um Ambiente Virtual (Recomendado)

É altamente recomendável criar um ambiente virtual para isolar as dependências do projeto. Isso evita conflitos com outras instalações Python em seu sistema.

```bash
python3 -m venv venv
```

### 4. Ativar o Ambiente Virtual

**No Windows:**

```bash
venv\Scripts\activate
```

**No macOS/Linux:**

```bash
source venv/bin/activate
```

### 5. Instalar as Dependências

Com o ambiente virtual ativado, instale as bibliotecas Python necessárias usando `pip`:

```bash
pip install Flask
```

### 6. Rodar a Aplicação Flask

Para iniciar o servidor de desenvolvimento do Flask, execute o arquivo `manage.py`:

```bash
python manage.py
```

### 7. Acessar o Site

Após executar o comando acima, você verá uma mensagem no terminal indicando que o servidor está rodando. Geralmente, ele estará disponível em `http://127.0.0.1:5000/` ou `http://localhost:5000/`.

Abra seu navegador web e acesse este endereço para ver seu site "Meu Memorial Online" em funcionamento.

### Observações Importantes

*   **Chave Secreta:** No arquivo `meumemorial/meumemorial/app.py`, você encontrará a linha `app.config["SECRET_KEY"] = "your_secret_key_here"`. **É crucial que você altere "your_secret_key_here" para uma string aleatória e segura em um ambiente de produção.**
*   **Funcionalidades:** Este é um projeto base com a estrutura e templates HTML. As funcionalidades de banco de dados, integração com Stripe/MercadoPago, upload de arquivos e lógica de QR Code precisarão ser implementadas. Os arquivos `routes.py` em cada módulo (`accounts`, `memorial`, `payments`) contêm comentários indicando onde a lógica deve ser adicionada.
*   **Estilo:** O arquivo `static/css/style.css` contém um CSS básico. Sinta-se à vontade para modificá-lo para personalizar o design do seu site.

Se tiver alguma dúvida ou precisar de ajuda com a implementação das funcionalidades, por favor, me informe!

