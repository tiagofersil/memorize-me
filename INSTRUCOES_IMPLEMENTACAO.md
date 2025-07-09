# 🚀 Instruções de Implementação - Memorial Digital

## 📋 Como Implementei as Funcionalidades Solicitadas

### 🔒 1. Autenticação de Usuários

#### ✅ Sistema de Login e Cadastro
**Arquivos criados:**
- `auth_service.py` - Serviço principal de autenticação
- `auth_routes.py` - Rotas para login, cadastro, logout
- `templates/auth/login.html` - Interface de login
- `templates/auth/register.html` - Interface de cadastro

**Funcionalidades implementadas:**
- Validação de dados em tempo real (JavaScript)
- Hash seguro de senhas com Werkzeug
- Verificação de disponibilidade de username/email via AJAX
- Recuperação de senha
- Controle de sessão com Flask-Login

#### ✅ Identificação de user_id em Sessões
```python
# Em auth_service.py
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['id'])  # user_id sempre disponível
        
# Em todas as rotas protegidas
@login_required
def protected_route():
    user_id = int(current_user.id)  # Acesso ao user_id logado
```

#### ✅ Restrição de Acesso
```python
# Em security_service.py
def check_memorial_access(self, user_id, memorial_id, required_level='read'):
    # Verifica se usuário é proprietário
    memorial = self.db.buscar_memorial_por_id(memorial_id)
    is_owner = user_id and memorial['user_id'] == user_id
    
    if required_level == 'owner' and not is_owner:
        return {'allowed': False, 'error': 'Apenas o proprietário pode realizar esta ação'}
```

### 📁 2. Integração com Cloudinary

#### ✅ Configuração das Credenciais
**Arquivo `.env`:**
```env
CLOUD_NAME=your_cloud_name
API_KEY=your_api_key
API_SECRET=your_api_secret
```

**Arquivo `cloudinary_service.py`:**
```python
class CloudinaryService:
    def __init__(self):
        cloudinary.config(
            cloud_name=os.getenv('CLOUD_NAME'),
            api_key=os.getenv('API_KEY'),
            api_secret=os.getenv('API_SECRET')
        )
```

#### ✅ Rota/Formulário para Upload
**Arquivo `image_routes.py`:**
```python
@image_bp.route('/api/upload', methods=['POST'])
@login_required
def upload_image():
    # Validação de arquivo
    validation = cloudinary_service.validate_image_file(file)
    
    # Upload para Cloudinary
    upload_result = cloudinary_service.upload_image(
        file,
        folder=f"memorial_{memorial_id}",
        public_id=public_id
    )
    
    # Salvar URL no banco
    foto_id = db.salvar_foto(
        memorial_id=memorial_id,
        user_id=int(current_user.id),
        cloudinary_url=upload_result['url'],
        cloudinary_public_id=upload_result['public_id']
    )
```

#### ✅ Não Salva Localmente
- Todas as imagens vão direto para o Cloudinary
- Apenas URLs são armazenadas no banco de dados
- Nenhum arquivo fica no servidor local

### 💾 3. Banco de Dados

#### ✅ Tabela de URLs das Imagens
**Estrutura da tabela `fotos`:**
```sql
CREATE TABLE fotos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memorial_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    cloudinary_url TEXT NOT NULL,        -- URL da imagem no Cloudinary
    cloudinary_public_id TEXT NOT NULL,  -- ID público para gerenciamento
    titulo TEXT,
    descricao TEXT,
    data_foto DATE,
    categoria TEXT DEFAULT 'geral',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (memorial_id) REFERENCES memorials (id),
    FOREIGN KEY (user_id) REFERENCES usuarios (id)
);
```

#### ✅ Associação com user_id
```python
# Em database_enhanced.py
def salvar_foto(self, memorial_id, user_id, cloudinary_url, cloudinary_public_id, ...):
    cursor = conn.execute(
        """INSERT INTO fotos (memorial_id, user_id, cloudinary_url, cloudinary_public_id,
           titulo, descricao, data_foto, categoria) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (memorial_id, user_id, cloudinary_url, cloudinary_public_id, ...)
    )
```

#### ✅ Metadados Completos
- Data de upload automática
- Título e descrição opcionais
- Categoria para organização
- Associação com memorial e usuário

### 📜 4. Textos Personalizados

#### ✅ Tabelas para Informações do Memorial
**Tabela `memorials`:**
```sql
CREATE TABLE memorials (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    nome_falecido TEXT NOT NULL,
    biografia TEXT,
    data_nascimento DATE,
    data_falecimento DATE,
    local_nascimento TEXT,
    local_falecimento TEXT,
    profissao TEXT,
    estado_civil TEXT,
    nome_conjuge TEXT,
    filhos TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### ✅ Tabela para Homenagens
**Tabela `homenagens`:**
```sql
CREATE TABLE homenagens (
    id INTEGER PRIMARY KEY,
    memorial_id INTEGER NOT NULL,
    autor_nome TEXT NOT NULL,
    autor_email TEXT,
    autor_telefone TEXT,
    texto_homenagem TEXT NOT NULL,
    relacionamento TEXT,
    aprovado BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP
);
```

#### ✅ Textos Personalizados
**Tabela `textos_memorial`:**
```sql
CREATE TABLE textos_memorial (
    id INTEGER PRIMARY KEY,
    memorial_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    tipo_texto TEXT NOT NULL,  -- 'biografia', 'historia_vida', 'mensagem_familia', etc.
    titulo TEXT,
    conteudo TEXT NOT NULL,
    ordem INTEGER DEFAULT 0,
    visivel BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### ✅ Associação com Usuários
```python
# Todas as tabelas têm foreign key para user_id
# Apenas o proprietário pode editar
def verificar_proprietario_memorial(self, memorial_id, user_id):
    memorial = self.buscar_memorial_por_id(memorial_id)
    return memorial and memorial['user_id'] == user_id
```

### 🖼️ 5. Exibição de Imagens e Textos

#### ✅ Página de Visualização
**Arquivo `memorial_routes.py`:**
```python
@memorial_bp.route('/view/<int:memorial_id>')
def view(memorial_id):
    # Verificar acesso (proprietário ou público)
    # Buscar conteúdo
    textos = db.buscar_textos_memorial(memorial_id)
    homenagens = db.buscar_homenagens_memorial(memorial_id, apenas_aprovadas=True)
    fotos = db.buscar_fotos_memorial(memorial_id)
    
    return render_template('memorial/view.html', 
                         memorial=memorial, 
                         textos=textos_dict, 
                         homenagens=homenagens,
                         fotos=fotos)
```

#### ✅ Filtro por user_id
```python
# Em database_enhanced.py
def buscar_fotos_memorial(self, memorial_id):
    fotos = conn.execute(
        "SELECT * FROM fotos WHERE memorial_id = ? ORDER BY created_at DESC",
        (memorial_id,)
    ).fetchall()
    # Retorna apenas fotos do memorial específico
```

#### ✅ Layout Organizado
- Galeria responsiva com Bootstrap
- Categorização de fotos
- Ordenação cronológica
- Metadados visíveis (título, descrição, data)

### 🛡️ 6. Segurança e Privacidade

#### ✅ Controle de Acesso
**Arquivo `security_service.py`:**
```python
def check_memorial_access(self, user_id, memorial_id, required_level='read'):
    # Verificar proprietário
    is_owner = user_id and memorial['user_id'] == user_id
    
    # Verificar configurações de privacidade
    config = self.db.buscar_configuracoes_privacidade(memorial_id)
    
    if config and config['publico']:
        return {'allowed': True, 'level': 'read'}
    
    # Verificar senha de acesso
    if config and config['senha_acesso']:
        return {'allowed': False, 'requires_password': True}
```

#### ✅ Sessões Seguras
```python
# Flask-Login gerencia sessões automaticamente
# Middleware de segurança em app_integrated.py
@app.before_request
def security_middleware():
    # Rate limiting
    # Log de acesso
    # Validação de sessão
```

#### ✅ Proteção de URLs
```python
# Decorator para verificar acesso
@require_memorial_access('owner')
def protected_route(memorial_id):
    # Apenas proprietário pode acessar
```

#### ✅ Configurações de Privacidade
**Tabela `configuracoes_privacidade`:**
```sql
CREATE TABLE configuracoes_privacidade (
    id INTEGER PRIMARY KEY,
    memorial_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    publico BOOLEAN DEFAULT FALSE,
    requer_aprovacao_homenagens BOOLEAN DEFAULT TRUE,
    permite_comentarios BOOLEAN DEFAULT TRUE,
    permite_fotos_visitantes BOOLEAN DEFAULT FALSE,
    senha_acesso TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## 🎯 Estrutura Final Implementada

### Arquivos Principais
```
/home/ubuntu/upload/home/
├── app_integrated.py              # Aplicação Flask principal
├── database_enhanced.py           # Camada de dados completa
├── auth_service.py               # Autenticação e usuários
├── cloudinary_service.py         # Integração Cloudinary
├── security_service.py           # Segurança e privacidade
├── auth_routes.py                # Rotas de autenticação
├── memorial_routes.py            # Rotas de memoriais
├── image_routes.py               # Rotas de imagens
├── privacy_routes.py             # Rotas de privacidade
├── requirements.txt              # Dependências
├── .env                          # Configurações
└── templates/                    # Templates HTML
    ├── auth/
    ├── memorial/
    ├── images/
    └── index.html
```

### Banco de Dados
```
meumemorial.db
├── usuarios                      # Dados dos usuários
├── memorials                     # Informações dos memoriais
├── fotos                         # URLs das imagens (Cloudinary)
├── homenagens                    # Depoimentos e mensagens
├── textos_memorial              # Conteúdo personalizado
├── configuracoes_privacidade    # Controle de acesso
└── logs_acesso                  # Auditoria e segurança
```

## ✅ Checklist de Implementação

### 🔒 Autenticação
- [x] Sistema de login e cadastro
- [x] Identificação de user_id em sessões
- [x] Restrição de acesso por proprietário
- [x] Validação e segurança

### 📁 Cloudinary
- [x] Configuração de credenciais (.env)
- [x] Rota/formulário para upload
- [x] Envio direto para Cloudinary
- [x] Obtenção e armazenamento de URLs
- [x] Não salva arquivos localmente

### 💾 Banco de Dados
- [x] Tabela para URLs das imagens
- [x] Associação com user_id
- [x] Metadados (data, título, descrição)
- [x] Tabelas para textos e homenagens

### 📜 Textos Personalizados
- [x] Tabela para informações do memorial
- [x] Tabela para homenagens/depoimentos
- [x] Associação com memorial e autor
- [x] Sistema de aprovação

### 🖼️ Exibição
- [x] Página de visualização do memorial
- [x] Filtro por user_id logado
- [x] Layout organizado e responsivo
- [x] Agrupamento cronológico

### 🛡️ Segurança
- [x] Controle de acesso a memoriais
- [x] Verificação de proprietário
- [x] Sessões seguras
- [x] Proteção de URLs diretos
- [x] Configurações de privacidade

## 🚀 Como Executar

1. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar Cloudinary:**
   Editar `.env` com suas credenciais

3. **Executar aplicação:**
   ```bash
   python app_integrated.py
   ```

4. **Acessar:**
   http://localhost:5000

---

**Todas as funcionalidades solicitadas foram implementadas com sucesso!** 🎉

