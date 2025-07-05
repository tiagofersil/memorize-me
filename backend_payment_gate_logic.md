# Lógica de Backend para Gate de Pagamento

## Objetivo

Garantir que apenas usuários com um plano de pagamento ativo possam acessar a funcionalidade de criação de memorial. Caso o usuário não possua um plano ativo, ele deve ser redirecionado para a página de seleção de planos.

## Rota a ser Protegida

A rota principal a ser protegida é aquela que renderiza a página de criação de memorial. No contexto de um aplicativo Flask, isso geralmente seria algo como:

```python
@app.route('/memorial/create')
def create_memorial():
    # ... lógica de verificação de plano ...
    return render_template('create_memorial.html')
```

## Lógica de Verificação

Dentro da função `create_memorial` (ou equivalente), a seguinte lógica deve ser implementada:

1.  **Verificar Autenticação do Usuário:** Certificar-se de que o usuário está logado. Se não estiver, redirecioná-lo para a página de login.

2.  **Consultar Status do Plano:** Acessar o banco de dados ou o sistema de gerenciamento de usuários para verificar se o usuário logado possui um plano ativo. Isso pode envolver:
    *   Verificar um campo `has_active_plan` na tabela de usuários.
    *   Consultar uma tabela `user_subscriptions` para ver se há uma assinatura válida e não expirada para o `user_id` atual.
    *   Integrar com um serviço de pagamento externo (ex: Stripe, Mercado Pago) para verificar o status da assinatura do usuário.

3.  **Redirecionamento Condicional:**
    *   **Se o usuário tiver um plano ativo:** Permitir que a função continue e renderize a página `create_memorial.html`.
    *   **Se o usuário NÃO tiver um plano ativo:** Redirecioná-lo para a página de seleção de planos (`/payments`) e, opcionalmente, exibir uma mensagem flash informando que um plano é necessário para criar um memorial.

## Exemplo de Implementação (Flask/Python)

```python
from flask import Flask, render_template, redirect, url_for, session, flash
# Supondo que você tenha um modelo de usuário e uma forma de verificar planos
# from .models import User, Subscription

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui' # Mude para uma chave secreta real

# Função de exemplo para verificar se o usuário tem um plano ativo
# Em um ambiente real, isso consultaria o banco de dados ou API de pagamento
def user_has_active_plan(user_id):
    # Lógica de exemplo: retorna True se o user_id for par, False se for ímpar
    # Substitua isso pela sua lógica real de consulta ao banco de dados/API
    return user_id % 2 == 0

@app.route('/login')
def login():
    # Lógica de login (apenas para simulação)
    session['user_id'] = 1 # Simula um usuário logado (sem plano)
    # session['user_id'] = 2 # Simula um usuário logado (com plano)
    flash('Você foi logado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html') # Sua página inicial

@app.route('/payments')
def payments():
    return render_template('payments_home.html') # Sua página de seleção de planos

@app.route('/memorial/create')
def create_memorial():
    if 'user_id' not in session: # Verifica se o usuário está logado
        flash('Você precisa estar logado para criar um memorial.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    if not user_has_active_plan(user_id): # Verifica se o usuário tem plano ativo
        flash('Você precisa ter um plano ativo para criar um memorial. Escolha um plano abaixo.', 'warning')
        return redirect(url_for('payments'))

    # Se chegou aqui, o usuário está logado e tem um plano ativo
    return render_template('create_memorial.html')

# Exemplo de rota para processar a compra de um plano
@app.route('/payments/process_purchase', methods=['POST'])
def process_purchase():
    if 'user_id' not in session:
        flash('Você precisa estar logado para comprar um plano.', 'warning')
        return redirect(url_for('login'))
    
    # Lógica para processar o pagamento e ativar o plano do usuário
    # ... (integração com Mercado Pago, atualização do banco de dados)
    
    # Após o sucesso do pagamento, você deve atualizar o status do plano do usuário no seu DB
    # Ex: user = User.query.get(session['user_id'])
    # user.has_active_plan = True
    # db.session.commit()
    
    flash('Seu plano foi ativado com sucesso! Agora você pode criar seu memorial.', 'success')
    return redirect(url_for('create_memorial'))

if __name__ == '__main__':
    app.run(debug=True)
```

## Considerações Adicionais

*   **Mensagens Flash:** Utilize o sistema de mensagens flash do Flask para fornecer feedback claro ao usuário sobre o motivo do redirecionamento.
*   **Segurança:** Sempre valide as informações no backend. Não confie apenas em verificações no frontend, pois elas podem ser facilmente contornadas.
*   **Integração com o Sistema de Pagamento:** A função `user_has_active_plan` e a lógica em `process_purchase` são placeholders. Elas devem ser substituídas pela sua integração real com o Mercado Pago e o seu banco de dados para gerenciar os planos dos usuários.
*   **Sessão:** Certifique-se de que o `user_id` está corretamente armazenado na sessão após o login.
*   **Outras Rotas:** Considere se outras rotas (ex: `/edit_memorial`) também precisam de verificação de plano, dependendo da sua lógica de negócio.

Esta documentação fornece a base para a implementação do gate de pagamento no backend, garantindo que a criação de memoriais seja restrita a usuários pagantes.

