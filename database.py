import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_path='meumemorial.db'):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        conn = self.get_connection()
        
        # Tabela de usuários
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de memoriais
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memorials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                text_content TEXT,
                biography TEXT,
                family_message TEXT,
                birth_date TEXT,
                death_date TEXT,
                profile_photo_path TEXT,
                qr_code_path TEXT,
                generated INTEGER DEFAULT 0, -- 0 para não gerado, 1 para gerado
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Adicionar a coluna 'generated' se ela não existir (para compatibilidade com DBs existentes)
        try:
            conn.execute("ALTER TABLE memorials ADD COLUMN generated INTEGER DEFAULT 0")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                raise
        
        # Adicionar a coluna 'profile_photo_path' se ela não existir (para compatibilidade com DBs existentes)
        try:
            conn.execute("ALTER TABLE memorials ADD COLUMN profile_photo_path TEXT")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                raise
        
        # Adicionar a coluna 'cover_photo_path' se ela não existir (para compatibilidade com DBs existentes)
        try:
            conn.execute("ALTER TABLE memorials ADD COLUMN cover_photo_path TEXT")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                raise

        # Adicionar novos campos para as funcionalidades expandidas
        try:
            conn.execute("ALTER TABLE memorials ADD COLUMN timeline_events TEXT")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                raise
        
        try:
            conn.execute("ALTER TABLE memorials ADD COLUMN music_embed_url TEXT")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                raise
        
        try:
            conn.execute("ALTER TABLE memorials ADD COLUMN featured_testimonials TEXT")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                raise
        
        try:
            conn.execute("ALTER TABLE memorials ADD COLUMN burial_location TEXT")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                raise
        
        try:
            conn.execute("ALTER TABLE memorials ADD COLUMN donation_link TEXT")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                raise
        
        try:
            conn.execute("ALTER TABLE memorials ADD COLUMN quotes_values TEXT")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                raise

        # Tabela de fotos dos memoriais
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memorial_photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memorial_id INTEGER NOT NULL,
                photo_path TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memorial_id) REFERENCES memorials (id)
            )
        """)
        
        # Tabela de comentários dos memoriais
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memorial_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memorial_id INTEGER NOT NULL,
                author_name TEXT NOT NULL,
                comment_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memorial_id) REFERENCES memorials (id)
            )
        """)
        
        # Tabela de questões dos memoriais
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memorial_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memorial_id INTEGER NOT NULL,
                question_key TEXT NOT NULL,
                question_text TEXT NOT NULL,
                answer TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memorial_id) REFERENCES memorials (id)
            )
        """)
        
        # Tabela de pagamentos
        conn.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                memorial_id INTEGER,
                amount DECIMAL(10,2) NOT NULL,
                plan_type TEXT,
                mercadopago_payment_id TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (memorial_id) REFERENCES memorials (id)
            )
        """)
        
        # Nova tabela para planos ativos dos usuários
        # 'credits_available' agora armazena os créditos comprados para aquele tipo de plano
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                plan_type TEXT NOT NULL,
                credits_available INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                payment_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (payment_id) REFERENCES payments (id),
                UNIQUE(user_id, plan_type) -- Garante um único registro por user_id e plan_type
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_user(self, username, email, password):
        """Cria um novo usuário"""
        conn = self.get_connection()
        password_hash = generate_password_hash(password)
        
        try:
            conn.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_user_by_username(self, username):
        """Busca usuário pelo nome de usuário"""
        conn = self.get_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()
        return user
    
    def get_user_by_email(self, email):
        """Busca usuário pelo email"""
        conn = self.get_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        conn.close()
        return user
    
    def verify_password(self, user, password):
        """Verifica se a senha está correta"""
        return check_password_hash(user["password_hash"], password)
    
    def create_memorial(self, user_id, name, biography=None, family_message=None, birth_date=None, death_date=None, profile_photo_path=None, cover_photo_path=None, timeline_events=None, music_embed_url=None, featured_testimonials=None, burial_location=None, donation_link=None, quotes_values=None):
        """Cria um novo memorial"""
        conn = self.get_connection()
        cursor = conn.execute(
            "INSERT INTO memorials (user_id, name, text_content, biography, family_message, birth_date, death_date, profile_photo_path, cover_photo_path, timeline_events, music_embed_url, featured_testimonials, burial_location, donation_link, quotes_values) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, name, biography or "", biography, family_message, birth_date, death_date, profile_photo_path, cover_photo_path, timeline_events, music_embed_url, featured_testimonials, burial_location, donation_link, quotes_values)
        )
        memorial_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return memorial_id
    
    def get_user_memorials(self, user_id):
        """Busca todos os memoriais de um usuário"""
        conn = self.get_connection()
        memorials_raw = conn.execute(
            "SELECT * FROM memorials WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        ).fetchall()
        conn.close()
        
        # Converter created_at para datetime se for string
        memorials = []
        for memorial in memorials_raw:
            memorial_dict = dict(memorial)
            if memorial_dict['created_at'] and isinstance(memorial_dict['created_at'], str):
                try:
                    memorial_dict['created_at'] = datetime.strptime(memorial_dict['created_at'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    # Se não conseguir converter, manter como string
                    pass
            memorials.append(type('Memorial', (), memorial_dict)())
        
        return memorials
    
    def get_memorial_by_id(self, memorial_id):
        """Busca memorial pelo ID"""
        conn = self.get_connection()
        memorial = conn.execute(
            "SELECT * FROM memorials WHERE id = ?", (memorial_id,)
        ).fetchone()
        conn.close()
        return memorial
    
    def add_memorial_photo(self, memorial_id, photo_path):
        """Adiciona uma foto ao memorial"""
        conn = self.get_connection()
        conn.execute(
            "INSERT INTO memorial_photos (memorial_id, photo_path) VALUES (?, ?)",
            (memorial_id, photo_path)
        )
        conn.commit()
        conn.close()
    
    def get_memorial_photos(self, memorial_id):
        """Busca todas as fotos de um memorial"""
        conn = self.get_connection()
        photos = conn.execute(
            "SELECT * FROM memorial_photos WHERE memorial_id = ?",
            (memorial_id,)
        ).fetchall()
        conn.close()
        return photos
    
    def get_memorial_photo_by_id(self, photo_id):
        """Busca uma foto pelo ID"""
        conn = self.get_connection()
        photo = conn.execute(
            "SELECT * FROM memorial_photos WHERE id = ?", (photo_id,)
        ).fetchone()
        conn.close()
        return photo
    
    def delete_memorial_photo(self, photo_id):
        """Deleta uma foto do memorial"""
        conn = self.get_connection()
        conn.execute("DELETE FROM memorial_photos WHERE id = ?", (photo_id,))
        conn.commit()
        conn.close()
    
    def add_memorial_comment(self, memorial_id, author_name, comment_text):
        """Adiciona um comentário ao memorial"""
        conn = self.get_connection()
        conn.execute(
            "INSERT INTO memorial_comments (memorial_id, author_name, comment_text) VALUES (?, ?, ?)",
            (memorial_id, author_name, comment_text)
        )
        conn.commit()
        conn.close()
    
    def get_memorial_comments(self, memorial_id):
        """Busca todos os comentários de um memorial"""
        conn = self.get_connection()
        cursor = conn.execute(
            "SELECT * FROM memorial_comments WHERE memorial_id = ? ORDER BY created_at DESC",
            (memorial_id,)
        )
        comments = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return comments
    
    def delete_memorial_comment(self, comment_id):
        """Deleta um comentário do memorial"""
        conn = self.get_connection()
        conn.execute("DELETE FROM memorial_comments WHERE id = ?", (comment_id,))
        conn.commit()
        conn.close()
    
    def save_memorial_questions(self, memorial_id, questions_data):
        """Salva ou atualiza questões do memorial"""
        conn = self.get_connection()
        
        # Primeiro, deletar questões existentes para este memorial
        conn.execute("DELETE FROM memorial_questions WHERE memorial_id = ?", (memorial_id,))
        
        # Inserir novas questões
        for question_key, answer in questions_data.items():
            if answer and answer.strip():  # Só salvar se houver resposta
                # Mapear question_key para question_text
                question_texts = {
                    'question_1': 'Qual era a comida favorita da pessoa?',
                    'question_2': 'Qual era o hobby ou atividade que mais gostava?',
                    'question_3': 'Qual era a música ou cantor favorito?',
                    'question_4': 'Qual era o lugar favorito para visitar?',
                    'question_5': 'Qual era a frase ou ditado que sempre dizia?',
                    'question_6': 'Qual era a qualidade que mais admiravam nela?',
                    'question_7': 'Qual era a lembrança mais especial que você tem?',
                    'question_8': 'O que ela mais gostava de fazer nos fins de semana?',
                    'question_9': 'Qual era o sonho ou objetivo de vida dela?',
                    'question_10': 'O que você gostaria que as pessoas soubessem sobre ela?'
                }
                
                question_text = question_texts.get(question_key, question_key)
                
                conn.execute(
                    "INSERT INTO memorial_questions (memorial_id, question_key, question_text, answer) VALUES (?, ?, ?, ?)",
                    (memorial_id, question_key, question_text, answer.strip())
                )
        
        conn.commit()
        conn.close()
    
    def get_memorial_questions(self, memorial_id):
        """Busca todas as questões de um memorial"""
        conn = self.get_connection()
        questions = conn.execute(
            "SELECT * FROM memorial_questions WHERE memorial_id = ? ORDER BY question_key",
            (memorial_id,)
        ).fetchall()
        conn.close()
        return questions
    
    def create_payment(self, user_id, memorial_id, amount, plan_type):
        """Cria um registro de pagamento"""
        conn = self.get_connection()
        cursor = conn.execute(
            "INSERT INTO payments (user_id, memorial_id, amount, plan_type) VALUES (?, ?, ?, ?)",
            (user_id, memorial_id, amount, plan_type)
        )
        payment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return payment_id
    
    def update_payment_status(self, payment_id, status, mercadopago_payment_id=None):
        """Atualiza o status de um pagamento"""
        conn = self.get_connection()
        if mercadopago_payment_id:
            conn.execute(
                "UPDATE payments SET mercadopago_payment_id = ?, status = ? WHERE id = ?",
                (mercadopago_payment_id, status, payment_id)
            )
        else:
            conn.execute(
                "UPDATE payments SET status = ? WHERE id = ?",
                (status, payment_id)
            )
        conn.commit()
        conn.close()

    def update_payment_status_by_memorial_id(self, memorial_id, status):
        """Atualiza o status do pagamento usando o memorial_id"""
        conn = self.get_connection()
        conn.execute(
            "UPDATE payments SET status = ? WHERE memorial_id = ?",
            (status, memorial_id)
        )
        conn.commit()
        conn.close()

    def update_memorial(self, memorial_id, name, biography=None, family_message=None, birth_date=None, death_date=None, profile_photo_path=None, cover_photo_path=None, timeline_events=None, music_embed_url=None, featured_testimonials=None, burial_location=None, donation_link=None, quotes_values=None):
        """Atualiza um memorial existente."""
        conn = self.get_connection()
        
        # Construir query dinamicamente
        update_fields = ["name = ?", "text_content = ?"]
        values = [name, biography or ""]
        
        if biography is not None:
            update_fields.append("biography = ?")
            values.append(biography)
        
        if family_message is not None:
            update_fields.append("family_message = ?")
            values.append(family_message)
            
        if birth_date is not None:
            update_fields.append("birth_date = ?")
            values.append(birth_date)
            
        if death_date is not None:
            update_fields.append("death_date = ?")
            values.append(death_date)
            
        if profile_photo_path is not None:
            update_fields.append("profile_photo_path = ?")
            values.append(profile_photo_path)
            
        if cover_photo_path is not None:
            update_fields.append("cover_photo_path = ?")
            values.append(cover_photo_path)
        
        if timeline_events is not None:
            update_fields.append("timeline_events = ?")
            values.append(timeline_events)
        
        if music_embed_url is not None:
            update_fields.append("music_embed_url = ?")
            values.append(music_embed_url)
        
        if featured_testimonials is not None:
            update_fields.append("featured_testimonials = ?")
            values.append(featured_testimonials)
        
        if burial_location is not None:
            update_fields.append("burial_location = ?")
            values.append(burial_location)
        
        if donation_link is not None:
            update_fields.append("donation_link = ?")
            values.append(donation_link)
        
        if quotes_values is not None:
            update_fields.append("quotes_values = ?")
            values.append(quotes_values)
        
        values.append(memorial_id)
        
        query = f"UPDATE memorials SET {', '.join(update_fields)} WHERE id = ?"
        conn.execute(query, values)
        conn.commit()
        conn.close()

    def activate_user_plan(self, user_id, plan_type, payment_id):
        """Ativa um plano para o usuário, adicionando 1 crédito ao tipo de plano correspondente."""
        conn = self.get_connection()
        
        # Tenta encontrar um registro existente para o user_id e plan_type
        existing_plan = conn.execute(
            "SELECT * FROM user_plans WHERE user_id = ? AND plan_type = ?",
            (user_id, plan_type)
        ).fetchone()
        
        if existing_plan:
            # Se o plano já existe, incrementa os créditos disponíveis
            conn.execute(
                "UPDATE user_plans SET credits_available = credits_available + 1, payment_id = ?, activated_at = CURRENT_TIMESTAMP WHERE user_id = ? AND plan_type = ?",
                (payment_id, user_id, plan_type)
            )
        else:
            # Se o plano não existe, cria um novo com 1 crédito
            conn.execute(
                "INSERT INTO user_plans (user_id, plan_type, credits_available, payment_id) VALUES (?, ?, ?, ?)",
                (user_id, plan_type, 1, payment_id)
            )
        
        conn.commit()
        conn.close()

    def get_user_plan_credits(self, user_id, plan_type):
        """Retorna o número de créditos disponíveis para um tipo de plano específico de um usuário."""
        conn = self.get_connection()
        plan = conn.execute(
            "SELECT credits_available FROM user_plans WHERE user_id = ? AND plan_type = ?",
            (user_id, plan_type)
        ).fetchone()
        conn.close()
        return plan['credits_available'] if plan else 0

    def can_create_memorial(self, user_id, plan_type):
        """Verifica se o usuário pode criar um novo memorial para um tipo de plano específico."""
        credits = self.get_user_plan_credits(user_id, plan_type)
        return credits > 0
    
    def decrement_memorial_usage(self, user_id, plan_type):
        """Decrementa o contador de créditos disponíveis para um tipo de plano específico."""
        conn = self.get_connection()
        conn.execute(
            "UPDATE user_plans SET credits_available = credits_available - 1 WHERE user_id = ? AND plan_type = ? AND credits_available > 0",
            (user_id, plan_type)
        )
        conn.commit()
        conn.close()
    
    def get_all_user_plans(self, user_id):
        """Retorna todos os planos (e seus créditos) que um usuário possui."""
        conn = self.get_connection()
        plans = conn.execute(
            "SELECT plan_type, credits_available FROM user_plans WHERE user_id = ?",
            (user_id,)
        ).fetchall()
        conn.close()
        return {plan['plan_type']: plan['credits_available'] for plan in plans}

    def get_payment_by_id(self, payment_id):
        """Busca um pagamento pelo ID"""
        conn = self.get_connection()
        payment = conn.execute(
            "SELECT * FROM payments WHERE id = ?", (payment_id,)
        ).fetchone()
        conn.close()
        return payment




    def mark_memorial_as_generated(self, memorial_id):
        """Marca um memorial como gerado."""
        conn = self.get_connection()
        conn.execute(
            "UPDATE memorials SET generated = 1 WHERE id = ?",
            (memorial_id,)
        )
        conn.commit()
        conn.close()




    def update_memorial_photos(self, memorial_id, profile_photo_path, cover_photo_path):
        """Atualiza os caminhos das fotos de perfil e capa de um memorial."""
        conn = self.get_connection()
        update_fields = []
        values = []

        if profile_photo_path is not None:
            update_fields.append("profile_photo_path = ?")
            values.append(profile_photo_path)

        if cover_photo_path is not None:
            update_fields.append("cover_photo_path = ?")
            values.append(cover_photo_path)

        if update_fields:
            query = f"UPDATE memorials SET {', '.join(update_fields)} WHERE id = ?"
            values.append(memorial_id)
            conn.execute(query, values)
            conn.commit()
        conn.close()

