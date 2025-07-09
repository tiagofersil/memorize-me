# Memorial Digital - Sistema Completo

## 📋 Descrição

Sistema completo de memorial digital que permite criar, gerenciar e compartilhar memoriais online com funcionalidades avançadas de segurança, upload de imagens via Cloudinary, sistema de autenticação robusto e controle granular de privacidade.

## ✨ Funcionalidades Implementadas

### 🔒 1. Autenticação de Usuários
- ✅ Sistema de login e cadastro completo
- ✅ Validação de dados em tempo real
- ✅ Controle de sessão com Flask-Login
- ✅ Recuperação de senha
- ✅ Perfil de usuário editável

### 📁 2. Integração com Cloudinary
- ✅ Upload de imagens direto para Cloudinary
- ✅ URLs otimizadas e responsivas
- ✅ Thumbnails automáticos
- ✅ Validação de arquivos
- ✅ Organização por pastas

### 💾 3. Banco de Dados Estruturado
- ✅ Tabela `usuarios` - dados dos usuários
- ✅ Tabela `memorials` - informações dos memoriais
- ✅ Tabela `fotos` - URLs e metadados das imagens
- ✅ Tabela `homenagens` - depoimentos e mensagens
- ✅ Tabela `textos_memorial` - conteúdo personalizado
- ✅ Tabela `configuracoes_privacidade` - controle de acesso
- ✅ Tabela `logs_acesso` - auditoria e segurança

### 📜 4. Textos Personalizados
- ✅ Biografias detalhadas
- ✅ Histórias de vida
- ✅ Mensagens da família
- ✅ Valores e princípios
- ✅ Editor de texto rico
- ✅ Organização por categorias

### 🖼️ 5. Galeria de Imagens
- ✅ Upload múltiplo com drag & drop
- ✅ Categorização de fotos
- ✅ Metadados (título, descrição, data)
- ✅ Visualização em galeria
- ✅ Edição de informações
- ✅ Exclusão segura

### 🛡️ 6. Segurança e Privacidade
- ✅ Controle de acesso granular
- ✅ Memoriais públicos/privados
- ✅ Proteção por senha
- ✅ Aprovação de homenagens
- ✅ Rate limiting
- ✅ Logs de auditoria
- ✅ Validação de entrada
- ✅ Headers de segurança

## 🏗️ Arquitetura

### Backend (Flask)
```
app_integrated.py          # Aplicação principal
├── auth_service.py        # Serviço de autenticação
├── cloudinary_service.py  # Integração Cloudinary
├── database_enhanced.py   # Camada de dados
├── security_service.py    # Serviços de segurança
├── auth_routes.py         # Rotas de autenticação
├── memorial_routes.py     # Rotas de memoriais
├── image_routes.py        # Rotas de imagens
└── privacy_routes.py      # Rotas de privacidade
```

### Frontend (Templates)
```
templates/
├── auth/
│   ├── login.html         # Página de login
│   └── register.html      # Página de cadastro
├── memorial/
│   └── dashboard.html     # Dashboard do usuário
├── images/
│   └── upload.html        # Upload de imagens
└── index.html             # Página inicial
```

### Banco de Dados (SQLite)
```sql
-- Estrutura principal
usuarios                   # Dados dos usuários
memorials                  # Informações dos memoriais
fotos                      # URLs das imagens (Cloudinary)
homenagens                 # Depoimentos e mensagens
textos_memorial           # Conteúdo personalizado
configuracoes_privacidade # Controle de acesso
logs_acesso               # Auditoria e segurança
```

## 🚀 Instalação e Configuração

### 1. Dependências
```bash
pip install -r requirements.txt
```

### 2. Configuração do Cloudinary
Edite o arquivo `.env`:
```env
CLOUD_NAME=seu_cloud_name
API_KEY=sua_api_key
API_SECRET=seu_api_secret
SECRET_KEY=sua_chave_secreta_flask
```

### 3. Executar Aplicação
```bash
python app_integrated.py
```

A aplicação estará disponível em: `http://localhost:5000`

## 📊 Estrutura do Banco de Dados

### Tabela `usuarios`
```sql
id INTEGER PRIMARY KEY
username TEXT UNIQUE NOT NULL
email TEXT UNIQUE NOT NULL
password_hash TEXT NOT NULL
nome_completo TEXT
telefone TEXT
created_at TIMESTAMP
updated_at TIMESTAMP
```

### Tabela `memorials`
```sql
id INTEGER PRIMARY KEY
user_id INTEGER NOT NULL
nome_falecido TEXT NOT NULL
biografia TEXT
data_nascimento DATE
data_falecimento DATE
local_nascimento TEXT
local_falecimento TEXT
profissao TEXT
estado_civil TEXT
nome_conjuge TEXT
filhos TEXT
created_at TIMESTAMP
updated_at TIMESTAMP
```

### Tabela `fotos`
```sql
id INTEGER PRIMARY KEY
memorial_id INTEGER NOT NULL
user_id INTEGER NOT NULL
cloudinary_url TEXT NOT NULL
cloudinary_public_id TEXT NOT NULL
titulo TEXT
descricao TEXT
data_foto DATE
categoria TEXT DEFAULT 'geral'
created_at TIMESTAMP
```

### Tabela `homenagens`
```sql
id INTEGER PRIMARY KEY
memorial_id INTEGER NOT NULL
autor_nome TEXT NOT NULL
autor_email TEXT
autor_telefone TEXT
texto_homenagem TEXT NOT NULL
relacionamento TEXT
aprovado BOOLEAN DEFAULT FALSE
created_at TIMESTAMP
```

## 🔐 Recursos de Segurança

### Autenticação
- Hash seguro de senhas (Werkzeug)
- Validação de força de senha
- Controle de sessão
- Rate limiting para login

### Autorização
- Verificação de proprietário
- Controle de acesso granular
- Middleware de segurança
- Logs de auditoria

### Privacidade
- Memoriais públicos/privados
- Proteção por senha
- Aprovação de conteúdo
- Configurações personalizáveis

### Proteção de Dados
- Validação de entrada
- Sanitização de dados
- Headers de segurança HTTP
- CORS configurado

## 🎯 Funcionalidades por Usuário

### Proprietário do Memorial
- ✅ Criar e editar memoriais
- ✅ Upload e gerenciamento de fotos
- ✅ Escrever textos personalizados
- ✅ Configurar privacidade
- ✅ Aprovar homenagens
- ✅ Ver logs de acesso
- ✅ Exportar dados

### Visitantes (se permitido)
- ✅ Visualizar memorial público
- ✅ Ver galeria de fotos
- ✅ Ler textos e biografia
- ✅ Deixar homenagens
- ✅ Acessar com senha (se configurado)

## 📱 Responsividade

- ✅ Design responsivo com Bootstrap 5
- ✅ Otimizado para desktop, tablet e mobile
- ✅ Imagens adaptáveis via Cloudinary
- ✅ Interface touch-friendly

## 🔧 APIs Disponíveis

### Autenticação
- `POST /auth/login` - Login de usuário
- `POST /auth/register` - Cadastro de usuário
- `GET /auth/logout` - Logout
- `POST /auth/api/check_username` - Verificar disponibilidade
- `POST /auth/api/check_email` - Verificar email

### Memoriais
- `GET /memorial/dashboard` - Dashboard do usuário
- `POST /memorial/create` - Criar memorial
- `GET /memorial/edit/<id>` - Editar memorial
- `GET /memorial/view/<id>` - Visualizar memorial
- `POST /memorial/api/save_text` - Salvar texto
- `POST /memorial/api/add_tribute` - Adicionar homenagem

### Imagens
- `POST /images/api/upload` - Upload de imagem
- `DELETE /images/api/delete/<id>` - Deletar imagem
- `GET /images/gallery/<memorial_id>` - Galeria pública
- `GET /images/api/gallery/<memorial_id>` - API da galeria

### Privacidade
- `GET /privacy/settings/<memorial_id>` - Configurações
- `POST /privacy/api/update_settings` - Atualizar configurações
- `POST /privacy/api/check_password` - Verificar senha de acesso

## 🚦 Status do Projeto

### ✅ Concluído
- Sistema de autenticação completo
- Integração com Cloudinary funcionando
- Banco de dados estruturado
- Upload e gerenciamento de imagens
- Sistema de textos personalizados
- Controle de privacidade e segurança
- Interface responsiva
- APIs RESTful

### 🔄 Melhorias Futuras
- Sistema de notificações
- Integração com redes sociais
- Backup automático
- Temas personalizáveis
- Aplicativo mobile
- Sistema de pagamentos

## 📞 Suporte

Para dúvidas ou suporte técnico, consulte a documentação ou entre em contato através dos canais oficiais.

---

**Memorial Digital** - Preservando memórias com amor e tecnologia. 💙

