# Integração Mercado Pago Checkout Pro

## Visão Geral

Esta integração permite que os usuários realizem pagamentos diretamente no seu site usando o Mercado Pago Checkout Pro e, após a aprovação do pagamento, preencham seus dados de endereço para o envio da placa QR Code personalizada.

## Arquivos Criados/Modificados

### 1. Backend - Rotas de Pagamento
- **`payments/payment_routes.py`** - Blueprint com todas as rotas de pagamento
- **`payments/__init__.py`** - Inicialização do módulo de pagamentos

### 2. Templates
- **`templates/payment/select_plan.html`** - Página de seleção de planos
- **`templates/payment/address_form.html`** - Formulário de endereço
- **`templates/payment/success.html`** - Página de sucesso do pagamento
- **`templates/payment/failure.html`** - Página de falha do pagamento
- **`templates/payment/pending.html`** - Página de pagamento pendente

### 3. Configurações
- **`.env`** - Arquivo de variáveis de ambiente
- **`app_integrated.py`** - Adicionado registro do blueprint de pagamento
- **`database_enhanced.py`** - Adicionados métodos para salvar/buscar endereços
- **`templates/layout.html`** - Adicionado link "Planos" no menu

## Fluxo de Pagamento

### 1. Seleção de Plano (`/payment/select_plan`)
- Usuário visualiza os planos disponíveis
- Cada plano tem design profissional com recursos listados
- Botão "Escolher Plano" inicia o processo de pagamento

### 2. Criação da Preferência (`/payment/create_preference`)
- Cria preferência no Mercado Pago com dados do plano selecionado
- Redireciona para o Checkout Pro do Mercado Pago
- Salva informações na sessão para uso posterior

### 3. Retorno do Pagamento
- **Sucesso** (`/payment/success`) - Mostra página de confirmação e redireciona para formulário de endereço
- **Falha** (`/payment/failure`) - Mostra página de erro com opções de tentar novamente
- **Pendente** (`/payment/pending`) - Mostra página de aguardo

### 4. Coleta de Endereço (`/payment/address_form`)
- Formulário responsivo com validação JavaScript
- Máscara automática para CEP
- Validação de campos obrigatórios
- Design consistente com o resto do site

### 5. Processamento do Endereço (`/payment/submit_address`)
- Salva endereço no banco de dados
- Limpa dados da sessão
- Redireciona para página inicial com mensagem de sucesso

## Configuração Necessária

### 1. Variáveis de Ambiente (.env)
```env
# Mercado Pago
MERCADOPAGO_ACCESS_TOKEN=seu_access_token_aqui

# URL base para webhooks
BASE_URL=http://localhost:5000
```

### 2. Obter Credenciais do Mercado Pago
1. Acesse https://www.mercadopago.com.br/developers
2. Crie uma aplicação
3. Copie o Access Token (use o de teste para desenvolvimento)
4. Configure o Access Token no arquivo .env

### 3. Configurar Webhooks (Opcional)
- URL do webhook: `{BASE_URL}/payment/webhook`
- Eventos: `payment`

## Planos Disponíveis

### Planos Pessoa
- **Básico** - R$ 29,00
- **Premium** - R$ 59,00 (Destacado como "Mais Popular")
- **Família** - R$ 99,00

### Planos Pet
- **Pet Básico** - R$ 19,90
- **Pet Premium** - R$ 29,90

## Recursos Implementados

### Design e UX
- ✅ Layout responsivo e profissional
- ✅ Consistência visual com o resto do site
- ✅ Animações e micro-interações
- ✅ Feedback visual para estados de loading/erro
- ✅ Máscaras de entrada para CEP
- ✅ Validação em tempo real

### Funcionalidades
- ✅ Integração completa com Mercado Pago Checkout Pro
- ✅ Múltiplos planos de pagamento
- ✅ Coleta de endereço pós-pagamento
- ✅ Armazenamento seguro de dados
- ✅ Tratamento de erros e estados pendentes
- ✅ Webhook para notificações (estrutura básica)

### Segurança
- ✅ Validação de sessão para acesso ao formulário de endereço
- ✅ Sanitização de dados de entrada
- ✅ Uso de HTTPS recomendado para produção

## Como Usar

### 1. Para Desenvolvedores
```bash
# 1. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais

# 2. Execute a aplicação
python3 app_integrated.py

# 3. Acesse http://localhost:5000/payment/select_plan
```

### 2. Para Usuários
1. Acesse a página "Planos" no menu
2. Escolha o plano desejado
3. Complete o pagamento no Mercado Pago
4. Preencha o endereço de entrega
5. Aguarde o envio da placa QR Code

## Próximos Passos Recomendados

### 1. Produção
- [ ] Configurar SSL/HTTPS
- [ ] Usar Access Token de produção
- [ ] Configurar domínio real no BASE_URL
- [ ] Implementar logs de auditoria

### 2. Melhorias Futuras
- [ ] Integração com API dos Correios para cálculo de frete
- [ ] Sistema de rastreamento de pedidos
- [ ] Notificações por email/SMS
- [ ] Dashboard administrativo para gerenciar pedidos
- [ ] Integração com sistema de estoque

### 3. Monitoramento
- [ ] Implementar métricas de conversão
- [ ] Logs de transações
- [ ] Alertas para falhas de pagamento
- [ ] Relatórios de vendas

## Suporte

Para dúvidas sobre a integração:
- Documentação oficial: https://www.mercadopago.com.br/developers
- Suporte técnico: Através do painel do desenvolvedor do Mercado Pago

## Observações Importantes

1. **Teste sempre em ambiente de desenvolvimento** antes de colocar em produção
2. **Use credenciais de teste** durante o desenvolvimento
3. **Configure webhooks** para receber notificações automáticas de pagamento
4. **Implemente logs** para facilitar debugging
5. **Mantenha as credenciais seguras** e nunca as commite no código

---

**Integração criada com sucesso!** 🎉

A solução está pronta para uso e mantém a consistência visual com o restante do seu site, oferecendo uma experiência de pagamento profissional e intuitiva para seus usuários.

