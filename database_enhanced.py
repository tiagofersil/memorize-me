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
                cover_photo_path TEXT,
                qr_code_path TEXT,
                theme_id INTEGER DEFAULT 1,
                custom_colors TEXT, -- JSON com cores personalizadas
                background_image_path TEXT,
                generated INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Adicionar novas colunas se não existirem
        self._add_column_if_not_exists(conn, 'memorials', 'generated', 'INTEGER DEFAULT 0')
        self._add_column_if_not_exists(conn, 'memorials', 'profile_photo_path', 'TEXT')
        self._add_column_if_not_exists(conn, 'memorials', 'cover_photo_path', 'TEXT')
        self._add_column_if_not_exists(conn, 'memorials', 'theme_id', 'INTEGER DEFAULT 1')
        self._add_column_if_not_exists(conn, 'memorials', 'custom_colors', 'TEXT')
        self._add_column_if_not_exists(conn, 'memorials', 'background_image_path', 'TEXT')

        # Tabela de fotos dos memoriais
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memorial_photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memorial_id INTEGER NOT NULL,
                photo_path TEXT NOT NULL,
                caption TEXT,
                uploaded_by TEXT,
                is_approved INTEGER DEFAULT 1,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memorial_id) REFERENCES memorials (id)
            )
        """)
        
        # Adicionar novas colunas para fotos
        self._add_column_if_not_exists(conn, 'memorial_photos', 'caption', 'TEXT')
        self._add_column_if_not_exists(conn, 'memorial_photos', 'uploaded_by', 'TEXT')
        self._add_column_if_not_exists(conn, 'memorial_photos', 'is_approved', 'INTEGER DEFAULT 1')
        
        # Tabela de comentários dos memoriais
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memorial_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memorial_id INTEGER NOT NULL,
                author_name TEXT NOT NULL,
                author_email TEXT,
                comment_text TEXT NOT NULL,
                is_approved INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memorial_id) REFERENCES memorials (id)
            )
        """)
        
        # Adicionar novas colunas para comentários
        self._add_column_if_not_exists(conn, 'memorial_comments', 'author_email', 'TEXT')
        self._add_column_if_not_exists(conn, 'memorial_comments', 'is_approved', 'INTEGER DEFAULT 1')
        
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
        
        # NOVAS TABELAS PARA FUNCIONALIDADES AVANÇADAS
        
        # 1. Linha do Tempo Interativa
        conn.execute("""
            CREATE TABLE IF NOT EXISTS timeline_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memorial_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                event_date TEXT,
                event_type TEXT DEFAULT 'milestone', -- milestone, achievement, memory, etc.
                photo_path TEXT,
                location TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memorial_id) REFERENCES memorials (id)
            )
        """)
        
        # 2. Livro de Visitas Digital
        conn.execute("""
            CREATE TABLE IF NOT EXISTS guestbook_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memorial_id INTEGER NOT NULL,
                author_name TEXT NOT NULL,
                author_email TEXT,
                relationship TEXT, -- família, amigo, colega, etc.
                message TEXT NOT NULL,
                photo_path TEXT,
                video_path TEXT,
                is_approved INTEGER DEFAULT 0, -- Requer moderação
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memorial_id) REFERENCES memorials (id)
            )
        """)
        
        # 3. Mapa de Memórias
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memory_locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memorial_id INTEGER NOT NULL,
                location_name TEXT NOT NULL,
                description TEXT,
                latitude REAL,
                longitude REAL,
                address TEXT,
                location_type TEXT DEFAULT 'memory', -- home, work, travel, memory, etc.
                photo_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memorial_id) REFERENCES memorials (id)
            )
        """)
        
        # 4. Árvore Genealógica
        conn.execute("""
            CREATE TABLE IF NOT EXISTS family_tree (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memorial_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                relationship TEXT NOT NULL, -- pai, mãe, filho, filha, cônjuge, etc.
                birth_date TEXT,
                death_date TEXT,
                photo_path TEXT,
                memorial_link TEXT, -- Link para outro memorial se existir
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memorial_id) REFERENCES memorials (id)
            )
        """)
        
        # 5. Músicas Favoritas
        conn.execute("""
            CREATE TABLE IF NOT EXISTS favorite_music (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memorial_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                artist TEXT,
                album TEXT,
                file_path TEXT, -- Para arquivos MP3 locais
                youtube_url TEXT,
                spotify_url TEXT,
                description TEXT, -- Por que era especial
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memorial_id) REFERENCES memorials (id)
            )
        """)
        
        # 6. Citações e Frases
        conn.execute("""
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memorial_id INTEGER NOT NULL,
                quote_text TEXT NOT NULL,
                context TEXT, -- Quando/onde foi dita
                category TEXT DEFAULT 'wisdom', -- wisdom, humor, love, advice, etc.
                contributed_by TEXT, -- Quem contribuiu com a citação
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memorial_id) REFERENCES memorials (id)
            )
        """)
        
        # 7. Receitas Favoritas
        conn.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memorial_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                ingredients TEXT NOT NULL, -- JSON ou texto formatado
                instructions TEXT NOT NULL,
                prep_time INTEGER, -- em minutos
                cook_time INTEGER, -- em minutos
                servings INTEGER,
                photo_path TEXT,
                story TEXT, -- História por trás da receita
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memorial_id) REFERENCES memorials (id)
            )
        """)
        
        # 8. Contribuições de Visitantes
        conn.execute("""
            CREATE TABLE IF NOT EXISTS visitor_contributions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memorial_id INTEGER NOT NULL,
                contributor_name TEXT NOT NULL,
                contributor_email TEXT,
                contribution_type TEXT NOT NULL, -- photo, video, audio, story, recipe, etc.
                title TEXT,
                description TEXT,
                file_path TEXT,
                content_text TEXT,
                is_approved INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memorial_id) REFERENCES memorials (id)
            )
        """)
        
        # 9. Eventos de Homenagem
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memorial_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memorial_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                event_date TEXT NOT NULL,
                event_time TEXT,
                location TEXT,
                event_type TEXT DEFAULT 'memorial', -- memorial, anniversary, celebration, etc.
                organizer_name TEXT,
                organizer_contact TEXT,
                max_attendees INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memorial_id) REFERENCES memorials (id)
            )
        """)
        
        # 10. RSVP para Eventos
        conn.execute("""
            CREATE TABLE IF NOT EXISTS event_rsvp (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                attendee_name TEXT NOT NULL,
                attendee_email TEXT,
                attendee_phone TEXT,
                status TEXT DEFAULT 'attending', -- attending, maybe, not_attending
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES memorial_events (id)
            )
        """)
        
        # 11. Fórum de Discussão - Tópicos
        conn.execute("""
            CREATE TABLE IF NOT EXISTS forum_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memorial_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT DEFAULT 'general', -- general, memories, support, etc.
                created_by TEXT NOT NULL,
                created_by_email TEXT,
                is_pinned INTEGER DEFAULT 0,
                is_locked INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memorial_id) REFERENCES memorials (id)
            )
        """)
        
        # 12. Fórum de Discussão - Posts
        conn.execute("""
            CREATE TABLE IF NOT EXISTS forum_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER NOT NULL,
                author_name TEXT NOT NULL,
                author_email TEXT,
                content TEXT NOT NULL,
                is_approved INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (topic_id) REFERENCES forum_topics (id)
            )
        """)
        
        # 13. Temas Visuais
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memorial_themes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                primary_color TEXT DEFAULT '#1877f2',
                secondary_color TEXT DEFAULT '#42a5f5',
                accent_color TEXT DEFAULT '#e91e63',
                background_color TEXT DEFAULT '#f0f2f5',
                text_color TEXT DEFAULT '#1c1e21',
                css_file_path TEXT,
                preview_image_path TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 14. Arquivos de Mídia (para organizar melhor)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS media_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memorial_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                file_type TEXT NOT NULL, -- image, video, audio, document
                file_size INTEGER,
                original_name TEXT,
                mime_type TEXT,
                uploaded_by TEXT,
                is_approved INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memorial_id) REFERENCES memorials (id)
            )
        """)
        
        # Tabelas existentes (mantidas para compatibilidade)
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
                UNIQUE(user_id, plan_type)
            )
        """)
        
        # Inserir temas padrão
        self._insert_default_themes(conn)
        
        conn.commit()
        conn.close()
    
    def _add_column_if_not_exists(self, conn, table_name, column_name, column_definition):
        """Adiciona uma coluna se ela não existir"""
        try:
            conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                raise
    
    def _insert_default_themes(self, conn):
        """Insere temas padrão se não existirem"""
        themes = [
            {
                'name': 'Clássico',
                'description': 'Tema elegante e atemporal',
                'primary_color': '#1877f2',
                'secondary_color': '#42a5f5',
                'accent_color': '#e91e63',
                'background_color': '#f0f2f5',
                'text_color': '#1c1e21'
            },
            {
                'name': 'Natureza',
                'description': 'Inspirado na natureza com tons verdes',
                'primary_color': '#4caf50',
                'secondary_color': '#81c784',
                'accent_color': '#ff9800',
                'background_color': '#f1f8e9',
                'text_color': '#2e7d32'
            },
            {
                'name': 'Serenidade',
                'description': 'Tons suaves e tranquilos',
                'primary_color': '#9c27b0',
                'secondary_color': '#ba68c8',
                'accent_color': '#ffc107',
                'background_color': '#fce4ec',
                'text_color': '#4a148c'
            },
            {
                'name': 'Oceano',
                'description': 'Inspirado no mar e céu',
                'primary_color': '#2196f3',
                'secondary_color': '#64b5f6',
                'accent_color': '#ff5722',
                'background_color': '#e3f2fd',
                'text_color': '#0d47a1'
            },
            {
                'name': 'Pôr do Sol',
                'description': 'Cores quentes e acolhedoras',
                'primary_color': '#ff9800',
                'secondary_color': '#ffb74d',
                'accent_color': '#e91e63',
                'background_color': '#fff3e0',
                'text_color': '#e65100'
            }
        ]
        
        for theme in themes:
            # Verificar se o tema já existe
            existing = conn.execute(
                "SELECT id FROM memorial_themes WHERE name = ?", (theme['name'],)
            ).fetchone()
            
            if not existing:
                conn.execute("""
                    INSERT INTO memorial_themes 
                    (name, description, primary_color, secondary_color, accent_color, background_color, text_color)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    theme['name'], theme['description'], theme['primary_color'],
                    theme['secondary_color'], theme['accent_color'], 
                    theme['background_color'], theme['text_color']
                ))
    
    # MÉTODOS EXISTENTES (mantidos para compatibilidade)
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
    
    def create_memorial(self, user_id, name, biography=None, family_message=None, birth_date=None, death_date=None, profile_photo_path=None, cover_photo_path=None):
        """Cria um novo memorial"""
        conn = self.get_connection()
        cursor = conn.execute(
            "INSERT INTO memorials (user_id, name, text_content, biography, family_message, birth_date, death_date, profile_photo_path, cover_photo_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, name, biography or "", biography, family_message, birth_date, death_date, profile_photo_path, cover_photo_path)
        )
        memorial_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return memorial_id
    
    def get_user_memorials(self, user_id):
        """Busca todos os memoriais de um usuário"""
        conn = self.get_connection()
        memorials = conn.execute(
            "SELECT * FROM memorials WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        ).fetchall()
        conn.close()
        return memorials
    
    def get_memorial_by_id(self, memorial_id):
        """Busca memorial pelo ID"""
        conn = self.get_connection()
        memorial = conn.execute(
            "SELECT * FROM memorials WHERE id = ?", (memorial_id,)
        ).fetchone()
        conn.close()
        return memorial
    
    # NOVOS MÉTODOS PARA FUNCIONALIDADES AVANÇADAS
    
    # 1. Timeline Events
    def add_timeline_event(self, memorial_id, title, description=None, event_date=None, event_type='milestone', photo_path=None, location=None):
        """Adiciona um evento à linha do tempo"""
        conn = self.get_connection()
        cursor = conn.execute(
            "INSERT INTO timeline_events (memorial_id, title, description, event_date, event_type, photo_path, location) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (memorial_id, title, description, event_date, event_type, photo_path, location)
        )
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return event_id
    
    def get_timeline_events(self, memorial_id):
        """Busca todos os eventos da linha do tempo"""
        conn = self.get_connection()
        events = conn.execute(
            "SELECT * FROM timeline_events WHERE memorial_id = ? ORDER BY event_date, created_at",
            (memorial_id,)
        ).fetchall()
        conn.close()
        return events
    
    # 2. Guestbook
    def add_guestbook_entry(self, memorial_id, author_name, message, author_email=None, relationship=None, photo_path=None, video_path=None):
        """Adiciona uma entrada no livro de visitas"""
        conn = self.get_connection()
        cursor = conn.execute(
            "INSERT INTO guestbook_entries (memorial_id, author_name, author_email, relationship, message, photo_path, video_path) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (memorial_id, author_name, author_email, relationship, message, photo_path, video_path)
        )
        entry_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return entry_id
    
    def get_guestbook_entries(self, memorial_id, approved_only=True):
        """Busca entradas do livro de visitas"""
        conn = self.get_connection()
        query = "SELECT * FROM guestbook_entries WHERE memorial_id = ?"
        params = [memorial_id]
        
        if approved_only:
            query += " AND is_approved = 1"
        
        query += " ORDER BY created_at DESC"
        
        entries = conn.execute(query, params).fetchall()
        conn.close()
        return entries
    
    # 3. Memory Locations
    def add_memory_location(self, memorial_id, location_name, description=None, latitude=None, longitude=None, address=None, location_type='memory', photo_path=None):
        """Adiciona um local de memória"""
        conn = self.get_connection()
        cursor = conn.execute(
            "INSERT INTO memory_locations (memorial_id, location_name, description, latitude, longitude, address, location_type, photo_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (memorial_id, location_name, description, latitude, longitude, address, location_type, photo_path)
        )
        location_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return location_id
    
    def get_memory_locations(self, memorial_id):
        """Busca locais de memória"""
        conn = self.get_connection()
        locations = conn.execute(
            "SELECT * FROM memory_locations WHERE memorial_id = ? ORDER BY location_name",
            (memorial_id,)
        ).fetchall()
        conn.close()
        return locations
    
    # 4. Family Tree
    def add_family_member(self, memorial_id, name, relationship, birth_date=None, death_date=None, photo_path=None, memorial_link=None, notes=None):
        """Adiciona um membro da família"""
        conn = self.get_connection()
        cursor = conn.execute(
            "INSERT INTO family_tree (memorial_id, name, relationship, birth_date, death_date, photo_path, memorial_link, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (memorial_id, name, relationship, birth_date, death_date, photo_path, memorial_link, notes)
        )
        member_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return member_id
    
    def get_family_members(self, memorial_id):
        """Busca membros da família"""
        conn = self.get_connection()
        members = conn.execute(
            "SELECT * FROM family_tree WHERE memorial_id = ? ORDER BY relationship, name",
            (memorial_id,)
        ).fetchall()
        conn.close()
        return members
    
    # 5. Favorite Music
    def add_favorite_music(self, memorial_id, title, artist=None, album=None, file_path=None, youtube_url=None, spotify_url=None, description=None):
        """Adiciona uma música favorita"""
        conn = self.get_connection()
        cursor = conn.execute(
            "INSERT INTO favorite_music (memorial_id, title, artist, album, file_path, youtube_url, spotify_url, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (memorial_id, title, artist, album, file_path, youtube_url, spotify_url, description)
        )
        music_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return music_id
    
    def get_favorite_music(self, memorial_id):
        """Busca músicas favoritas"""
        conn = self.get_connection()
        music = conn.execute(
            "SELECT * FROM favorite_music WHERE memorial_id = ? ORDER BY title",
            (memorial_id,)
        ).fetchall()
        conn.close()
        return music
    
    # 6. Quotes
    def add_quote(self, memorial_id, quote_text, context=None, category='wisdom', contributed_by=None):
        """Adiciona uma citação"""
        conn = self.get_connection()
        cursor = conn.execute(
            "INSERT INTO quotes (memorial_id, quote_text, context, category, contributed_by) VALUES (?, ?, ?, ?, ?)",
            (memorial_id, quote_text, context, category, contributed_by)
        )
        quote_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return quote_id
    
    def get_quotes(self, memorial_id, category=None):
        """Busca citações"""
        conn = self.get_connection()
        query = "SELECT * FROM quotes WHERE memorial_id = ?"
        params = [memorial_id]
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY created_at DESC"
        
        quotes = conn.execute(query, params).fetchall()
        conn.close()
        return quotes
    
    # 7. Recipes
    def add_recipe(self, memorial_id, title, ingredients, instructions, description=None, prep_time=None, cook_time=None, servings=None, photo_path=None, story=None):
        """Adiciona uma receita"""
        conn = self.get_connection()
        cursor = conn.execute(
            "INSERT INTO recipes (memorial_id, title, description, ingredients, instructions, prep_time, cook_time, servings, photo_path, story) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (memorial_id, title, description, ingredients, instructions, prep_time, cook_time, servings, photo_path, story)
        )
        recipe_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return recipe_id
    
    def get_recipes(self, memorial_id):
        """Busca receitas"""
        conn = self.get_connection()
        recipes = conn.execute(
            "SELECT * FROM recipes WHERE memorial_id = ? ORDER BY title",
            (memorial_id,)
        ).fetchall()
        conn.close()
        return recipes
    
    # 8. Visitor Contributions
    def add_visitor_contribution(self, memorial_id, contributor_name, contribution_type, title=None, description=None, file_path=None, content_text=None, contributor_email=None):
        """Adiciona uma contribuição de visitante"""
        conn = self.get_connection()
        cursor = conn.execute(
            "INSERT INTO visitor_contributions (memorial_id, contributor_name, contributor_email, contribution_type, title, description, file_path, content_text) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (memorial_id, contributor_name, contributor_email, contribution_type, title, description, file_path, content_text)
        )
        contribution_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return contribution_id
    
    def get_visitor_contributions(self, memorial_id, approved_only=True):
        """Busca contribuições de visitantes"""
        conn = self.get_connection()
        query = "SELECT * FROM visitor_contributions WHERE memorial_id = ?"
        params = [memorial_id]
        
        if approved_only:
            query += " AND is_approved = 1"
        
        query += " ORDER BY created_at DESC"
        
        contributions = conn.execute(query, params).fetchall()
        conn.close()
        return contributions
    
    # 9. Memorial Events
    def add_memorial_event(self, memorial_id, title, event_date, description=None, event_time=None, location=None, event_type='memorial', organizer_name=None, organizer_contact=None, max_attendees=None):
        """Adiciona um evento do memorial"""
        conn = self.get_connection()
        cursor = conn.execute(
            "INSERT INTO memorial_events (memorial_id, title, description, event_date, event_time, location, event_type, organizer_name, organizer_contact, max_attendees) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (memorial_id, title, description, event_date, event_time, location, event_type, organizer_name, organizer_contact, max_attendees)
        )
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return event_id
    
    def get_memorial_events(self, memorial_id):
        """Busca eventos do memorial"""
        conn = self.get_connection()
        events = conn.execute(
            "SELECT * FROM memorial_events WHERE memorial_id = ? ORDER BY event_date",
            (memorial_id,)
        ).fetchall()
        conn.close()
        return events
    
    # 10. Themes
    def get_all_themes(self):
        """Busca todos os temas disponíveis"""
        conn = self.get_connection()
        themes = conn.execute(
            "SELECT * FROM memorial_themes WHERE is_active = 1 ORDER BY name"
        ).fetchall()
        conn.close()
        return themes
    
    def get_theme_by_id(self, theme_id):
        """Busca tema pelo ID"""
        conn = self.get_connection()
        theme = conn.execute(
            "SELECT * FROM memorial_themes WHERE id = ?", (theme_id,)
        ).fetchone()
        conn.close()
        return theme
    
    # Métodos existentes mantidos para compatibilidade...
    def add_memorial_photo(self, memorial_id, photo_path, caption=None, uploaded_by=None):
        """Adiciona uma foto ao memorial"""
        conn = self.get_connection()
        conn.execute(
            "INSERT INTO memorial_photos (memorial_id, photo_path, caption, uploaded_by) VALUES (?, ?, ?, ?)",
            (memorial_id, photo_path, caption, uploaded_by)
        )
        conn.commit()
        conn.close()
    
    def get_memorial_photos(self, memorial_id):
        """Busca todas as fotos de um memorial"""
        conn = self.get_connection()
        photos = conn.execute(
            "SELECT * FROM memorial_photos WHERE memorial_id = ? AND is_approved = 1",
            (memorial_id,)
        ).fetchall()
        conn.close()
        return photos
    
    def add_memorial_comment(self, memorial_id, author_name, comment_text, author_email=None):
        """Adiciona um comentário ao memorial"""
        conn = self.get_connection()
        conn.execute(
            "INSERT INTO memorial_comments (memorial_id, author_name, author_email, comment_text) VALUES (?, ?, ?, ?)",
            (memorial_id, author_name, author_email, comment_text)
        )
        conn.commit()
        conn.close()
    
    def get_memorial_comments(self, memorial_id):
        """Busca todos os comentários de um memorial"""
        conn = self.get_connection()
        cursor = conn.execute(
            "SELECT * FROM memorial_comments WHERE memorial_id = ? AND is_approved = 1 ORDER BY created_at DESC",
            (memorial_id,)
        )
        comments = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return comments
    
    # Métodos de pagamento e planos mantidos...
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
    
    def update_memorial(self, memorial_id, name, biography=None, family_message=None, birth_date=None, death_date=None, profile_photo_path=None, cover_photo_path=None, theme_id=None):
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
            
        if theme_id is not None:
            update_fields.append("theme_id = ?")
            values.append(theme_id)
        
        values.append(memorial_id)
        
        query = f"UPDATE memorials SET {', '.join(update_fields)} WHERE id = ?"
        conn.execute(query, values)
        conn.commit()
        conn.close()



    def get_user_recent_activity(self, user_id):
        """Retorna a atividade recente do usuário. Implementação placeholder."""
        # Esta é uma implementação básica. Você pode expandir isso para incluir
        # atividades como memoriais criados, comentários feitos, etc.
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Exemplo: buscar os 5 memoriais mais recentes criados pelo usuário
        cursor.execute("""
            SELECT id, name, created_at FROM memorials
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 5
        """, (user_id,))
        
        recent_memorials = cursor.fetchall()
        conn.close()
        
        # Formatar para uma lista de dicionários para facilitar o uso no template
        activity = []
        for m in recent_memorials:
            activity.append({
                'type': 'memorial_created',
                'description': f'Criou o memorial "{m["name"]}"',
                'timestamp': m['created_at']
            })
        
        return activity




    def get_user_stats(self, user_id):
        """Retorna estatísticas do usuário. Implementação placeholder."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Exemplo: Contar o número de memoriais criados pelo usuário
        cursor.execute("""
            SELECT COUNT(*) FROM memorials
            WHERE user_id = ?
        """, (user_id,))
        total_memorials = cursor.fetchone()[0]
        
        # Exemplo: Contar o número de fotos carregadas pelo usuário
        cursor.execute("""
            SELECT COUNT(*) FROM memorial_photos mp
            JOIN memorials m ON mp.memorial_id = m.id
            WHERE m.user_id = ?
        """, (user_id,))
        total_photos = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_memorials': total_memorials,
            'total_photos': total_photos,
            'total_comments': 0, # Placeholder
            'total_tributes': 0  # Placeholder
        }


