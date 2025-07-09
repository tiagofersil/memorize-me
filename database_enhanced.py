import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

class DatabaseEnhanced:
    def __init__(self, db_path='meumemorial.db'):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Inicializa o banco de dados com as tabelas necessárias para o sistema completo"""
        conn = self.get_connection()
        
        # Tabela de usuários
        conn.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                nome_completo TEXT,
                telefone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de memoriais
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memorials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                profile_photo_path TEXT,
                cover_photo_path TEXT,
                family_message TEXT,
                timeline_events TEXT,
                music_embed_url TEXT,
                featured_testimonials TEXT,
                burial_location TEXT,
                donation_link TEXT,
                quotes_values TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE
            )
        """)
        
        # Tabela de fotos (integração com Cloudinary)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS fotos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memorial_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                cloudinary_url TEXT NOT NULL,
                cloudinary_public_id TEXT NOT NULL,
                titulo TEXT,
                descricao TEXT,
                data_foto DATE,
                categoria TEXT DEFAULT 'geral',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memorial_id) REFERENCES memorials (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE
            )
        """)
        
        # Tabela de homenagens/depoimentos
        conn.execute("""
            CREATE TABLE IF NOT EXISTS homenagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memorial_id INTEGER NOT NULL,
                autor_nome TEXT NOT NULL,
                autor_email TEXT,
                autor_telefone TEXT,
                texto_homenagem TEXT NOT NULL,
                relacionamento TEXT,
                aprovado BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memorial_id) REFERENCES memorials (id) ON DELETE CASCADE
            )
        """)
        
        # Tabela de textos personalizados do memorial
        conn.execute("""
            CREATE TABLE IF NOT EXISTS textos_memorial (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memorial_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                tipo_texto TEXT NOT NULL, -- 'biografia', 'historia_vida', 'mensagem_familia', etc.
                titulo TEXT,
                conteudo TEXT NOT NULL,
                ordem INTEGER DEFAULT 0,
                visivel BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memorial_id) REFERENCES memorials (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE
            )
        """)
        
        # Tabela de sessões de usuário (para controle de acesso)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessoes_usuario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE
            )
        """)
        
        # Tabela de configurações de privacidade
        conn.execute("""
            CREATE TABLE IF NOT EXISTS configuracoes_privacidade (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memorial_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                publico BOOLEAN DEFAULT FALSE,
                requer_aprovacao_homenagens BOOLEAN DEFAULT TRUE,
                permite_comentarios BOOLEAN DEFAULT TRUE,
                permite_fotos_visitantes BOOLEAN DEFAULT FALSE,
                senha_acesso TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memorial_id) REFERENCES memorials (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE
            )
        """)
        
        # Tabela de logs de acesso (para segurança)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS logs_acesso (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                memorial_id INTEGER,
                acao TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                detalhes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE SET NULL,
                FOREIGN KEY (memorial_id) REFERENCES memorials (id) ON DELETE SET NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    # Métodos para usuários
    def criar_usuario(self, username, email, password, nome_completo=None, telefone=None):
        """Cria um novo usuário"""
        conn = self.get_connection()
        password_hash = generate_password_hash(password)
        
        try:
            cursor = conn.execute(
                "INSERT INTO usuarios (username, email, password_hash, nome_completo, telefone) VALUES (?, ?, ?, ?, ?)",
                (username, email, password_hash, nome_completo, telefone)
            )
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def buscar_usuario_por_username(self, username):
        """Busca usuário pelo nome de usuário"""
        conn = self.get_connection()
        user = conn.execute(
            "SELECT * FROM usuarios WHERE username = ?", (username,)
        ).fetchone()
        conn.close()
        return user
    
    def buscar_usuario_por_email(self, email):
        """Busca usuário pelo email"""
        conn = self.get_connection()
        user = conn.execute(
            "SELECT * FROM usuarios WHERE email = ?", (email,)
        ).fetchone()
        conn.close()
        return user
    
    def buscar_usuario_por_id(self, user_id):
        """Busca usuário pelo ID"""
        conn = self.get_connection()
        user = conn.execute(
            "SELECT * FROM usuarios WHERE id = ?", (user_id,)
        ).fetchone()
        conn.close()
        return user
    
    def verificar_senha(self, user, password):
        """Verifica se a senha está correta"""
        return check_password_hash(user["password_hash"], password)
    
    # Métodos para memoriais
    def criar_memorial(self, user_id, nome_falecido, biografia=None, data_nascimento=None, 
                      data_falecimento=None, local_nascimento=None, local_falecimento=None,
                      profissao=None, estado_civil=None, nome_conjuge=None, filhos=None):
        """Cria um novo memorial"""
        conn = self.get_connection()
        cursor = conn.execute(
            """INSERT INTO memorials (user_id, nome_falecido, biografia, data_nascimento, 
               data_falecimento, local_nascimento, local_falecimento, profissao, 
               estado_civil, nome_conjuge, filhos) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, nome_falecido, biografia, data_nascimento, data_falecimento,
             local_nascimento, local_falecimento, profissao, estado_civil, nome_conjuge, filhos)
        )
        memorial_id = cursor.lastrowid
        
        # Criar configurações de privacidade padrão
        conn.execute(
            "INSERT INTO configuracoes_privacidade (memorial_id, user_id) VALUES (?, ?)",
            (memorial_id, user_id)
        )
        
        conn.commit()
        conn.close()
        return memorial_id
    
    def atualizar_memorial(self, memorial_id, user_id, **kwargs):
        """Atualiza um memorial existente"""
        conn = self.get_connection()
        
        # Verificar se o usuário é proprietário
        if not self.verificar_proprietario_memorial(memorial_id, user_id):
            conn.close()
            return False
        
        # Construir query dinamicamente
        campos = []
        valores = []
        for campo, valor in kwargs.items():
            if campo in ['nome_falecido', 'biografia', 'data_nascimento', 'data_falecimento',
                        'local_nascimento', 'local_falecimento', 'profissao', 'estado_civil',
                        'nome_conjuge', 'filhos', 'profile_photo_path', 'cover_photo_path',
                        'family_message', 'timeline_events', 'music_embed_url', 
                        'featured_testimonials', 'burial_location', 'donation_link', 'quotes_values']:
                campos.append(f"{campo} = ?")
                valores.append(valor)
        
        if campos:
            campos.append("updated_at = CURRENT_TIMESTAMP")
            valores.append(memorial_id)
            
            query = f"UPDATE memorials SET {', '.join(campos)} WHERE id = ?"
            conn.execute(query, valores)
            conn.commit()
        
        conn.close()
        return True
    
    def buscar_memoriais_usuario(self, user_id):
        """Busca todos os memoriais de um usuário"""
        conn = self.get_connection()
        memorials = conn.execute(
            "SELECT * FROM memorials WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        ).fetchall()
        conn.close()
        return memorials
    
    def buscar_memorial_por_id(self, memorial_id):
        """Busca memorial pelo ID"""
        conn = self.get_connection()
        memorial = conn.execute(
            "SELECT * FROM memorials WHERE id = ?", (memorial_id,)
        ).fetchone()
        conn.close()
        return memorial
    
    def verificar_proprietario_memorial(self, memorial_id, user_id):
        """Verifica se o usuário é proprietário do memorial"""
        memorial = self.buscar_memorial_por_id(memorial_id)
        return memorial and memorial['user_id'] == user_id
    
    # Métodos para fotos (Cloudinary)
    def salvar_foto(self, memorial_id, user_id, cloudinary_url, cloudinary_public_id, 
                   titulo=None, descricao=None, data_foto=None, categoria='geral'):
        """Salva informações da foto no banco de dados"""
        conn = self.get_connection()
        cursor = conn.execute(
            """INSERT INTO fotos (memorial_id, user_id, cloudinary_url, cloudinary_public_id,
               titulo, descricao, data_foto, categoria) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (memorial_id, user_id, cloudinary_url, cloudinary_public_id, titulo, descricao, data_foto, categoria)
        )
        foto_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return foto_id
    
    def buscar_fotos_memorial(self, memorial_id):
        """Busca todas as fotos de um memorial"""
        conn = self.get_connection()
        fotos = conn.execute(
            "SELECT * FROM fotos WHERE memorial_id = ? ORDER BY created_at DESC",
            (memorial_id,)
        ).fetchall()
        conn.close()
        return fotos
    
    def buscar_foto_por_id(self, foto_id):
        """Busca foto pelo ID"""
        conn = self.get_connection()
        foto = conn.execute(
            "SELECT * FROM fotos WHERE id = ?", (foto_id,)
        ).fetchone()
        conn.close()
        return foto
    
    def deletar_foto(self, foto_id, user_id):
        """Deleta uma foto (apenas se o usuário for o proprietário)"""
        conn = self.get_connection()
        # Verificar se o usuário é proprietário da foto
        foto = conn.execute(
            "SELECT * FROM fotos WHERE id = ? AND user_id = ?", (foto_id, user_id)
        ).fetchone()
        
        if foto:
            conn.execute("DELETE FROM fotos WHERE id = ?", (foto_id,))
            conn.commit()
            conn.close()
            return foto['cloudinary_public_id']  # Retorna o public_id para deletar do Cloudinary
        
        conn.close()
        return None
    
    # Métodos para homenagens
    def criar_homenagem(self, memorial_id, autor_nome, texto_homenagem, autor_email=None, 
                       autor_telefone=None, relacionamento=None):
        """Cria uma nova homenagem"""
        conn = self.get_connection()
        cursor = conn.execute(
            """INSERT INTO homenagens (memorial_id, autor_nome, autor_email, autor_telefone,
               texto_homenagem, relacionamento) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (memorial_id, autor_nome, autor_email, autor_telefone, texto_homenagem, relacionamento)
        )
        homenagem_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return homenagem_id
    
    def buscar_homenagens_memorial(self, memorial_id, apenas_aprovadas=True):
        """Busca homenagens de um memorial"""
        conn = self.get_connection()
        if apenas_aprovadas:
            homenagens = conn.execute(
                "SELECT * FROM homenagens WHERE memorial_id = ? AND aprovado = 1 ORDER BY created_at DESC",
                (memorial_id,)
            ).fetchall()
        else:
            homenagens = conn.execute(
                "SELECT * FROM homenagens WHERE memorial_id = ? ORDER BY created_at DESC",
                (memorial_id,)
            ).fetchall()
        conn.close()
        return homenagens
    
    def aprovar_homenagem(self, homenagem_id, user_id):
        """Aprova uma homenagem (apenas proprietário do memorial)"""
        conn = self.get_connection()
        # Verificar se o usuário é proprietário do memorial
        homenagem = conn.execute(
            """SELECT h.*, m.user_id as memorial_owner 
               FROM homenagens h 
               JOIN memorials m ON h.memorial_id = m.id 
               WHERE h.id = ?""", (homenagem_id,)
        ).fetchone()
        
        if homenagem and homenagem['memorial_owner'] == user_id:
            conn.execute(
                "UPDATE homenagens SET aprovado = 1 WHERE id = ?", (homenagem_id,)
            )
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False
    
    # Métodos para textos personalizados
    def salvar_texto_memorial(self, memorial_id, user_id, tipo_texto, conteudo, titulo=None, ordem=0):
        """Salva ou atualiza um texto personalizado do memorial"""
        conn = self.get_connection()
        
        # Verificar se já existe um texto deste tipo para este memorial
        texto_existente = conn.execute(
            "SELECT id FROM textos_memorial WHERE memorial_id = ? AND tipo_texto = ?",
            (memorial_id, tipo_texto)
        ).fetchone()
        
        if texto_existente:
            # Atualizar texto existente
            conn.execute(
                """UPDATE textos_memorial SET conteudo = ?, titulo = ?, ordem = ?, 
                   updated_at = CURRENT_TIMESTAMP WHERE id = ?""",
                (conteudo, titulo, ordem, texto_existente['id'])
            )
            texto_id = texto_existente['id']
        else:
            # Criar novo texto
            cursor = conn.execute(
                """INSERT INTO textos_memorial (memorial_id, user_id, tipo_texto, titulo, 
                   conteudo, ordem) VALUES (?, ?, ?, ?, ?, ?)""",
                (memorial_id, user_id, tipo_texto, titulo, conteudo, ordem)
            )
            texto_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return texto_id
    
    def buscar_textos_memorial(self, memorial_id):
        """Busca todos os textos de um memorial"""
        conn = self.get_connection()
        textos = conn.execute(
            "SELECT * FROM textos_memorial WHERE memorial_id = ? AND visivel = 1 ORDER BY ordem, created_at",
            (memorial_id,)
        ).fetchall()
        conn.close()
        return textos
    
    # Métodos para segurança e logs
    def registrar_log_acesso(self, user_id, memorial_id, acao, ip_address=None, user_agent=None, detalhes=None):
        """Registra um log de acesso"""
        conn = self.get_connection()
        conn.execute(
            """INSERT INTO logs_acesso (user_id, memorial_id, acao, ip_address, user_agent, detalhes)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, memorial_id, acao, ip_address, user_agent, detalhes)
        )
        conn.commit()
        conn.close()
    
    def buscar_configuracoes_privacidade(self, memorial_id):
        """Busca configurações de privacidade de um memorial"""
        conn = self.get_connection()
        config = conn.execute(
            "SELECT * FROM configuracoes_privacidade WHERE memorial_id = ?", (memorial_id,)
        ).fetchone()
        conn.close()
        return config
    
    def atualizar_configuracoes_privacidade(self, memorial_id, user_id, **kwargs):
        """Atualiza configurações de privacidade"""
        conn = self.get_connection()
        
        # Verificar se o usuário é proprietário
        if not self.verificar_proprietario_memorial(memorial_id, user_id):
            conn.close()
            return False
        
        # Construir query dinamicamente
        campos = []
        valores = []
        for campo, valor in kwargs.items():
            if campo in ['publico', 'requer_aprovacao_homenagens', 'permite_comentarios', 
                        'permite_fotos_visitantes', 'senha_acesso']:
                campos.append(f"{campo} = ?")
                valores.append(valor)
        
        if campos:
            campos.append("updated_at = CURRENT_TIMESTAMP")
            valores.append(memorial_id)
            
            query = f"UPDATE configuracoes_privacidade SET {', '.join(campos)} WHERE memorial_id = ?"
            conn.execute(query, valores)
            conn.commit()
        
        conn.close()
        return True



    def save_user_address(self, user_id, address_data):
        """Salva o endereço do usuário para envio da placa QR Code"""
        try:
            cursor = self.conn.cursor()
            
            # Criar tabela se não existir
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_addresses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    street TEXT NOT NULL,
                    number TEXT NOT NULL,
                    complement TEXT,
                    neighborhood TEXT NOT NULL,
                    city TEXT NOT NULL,
                    state TEXT NOT NULL,
                    zip_code TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES usuarios (id)
                )
            ''')
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_addresses 
                (user_id, street, number, complement, neighborhood, city, state, zip_code, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ''', (
                user_id,
                address_data['street'],
                address_data['number'],
                address_data.get('complement', ''),
                address_data['neighborhood'],
                address_data['city'],
                address_data['state'],
                address_data['zip_code']
            ))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Erro ao salvar endereço: {e}")
            return None

    def get_user_address(self, user_id):
        """Busca o endereço do usuário"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM user_addresses 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            ''', (user_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Erro ao buscar endereço: {e}")
            return None

