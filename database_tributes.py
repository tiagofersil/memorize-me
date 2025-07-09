import sqlite3
from datetime import datetime, timedelta
from database import Database

class TributesDatabase(Database):
    """Extensão da classe Database para gerenciar homenagens virtuais (velas e flores)"""
    
    def __init__(self, db_path='meumemorial.db'):
        super().__init__(db_path)
        self.init_tributes_tables()
    
    def init_tributes_tables(self):
        """Inicializa as tabelas específicas para homenagens virtuais"""
        conn = self.get_connection()
        
        # Tabela de homenagens (velas e flores)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memorial_tributes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memorial_id INTEGER NOT NULL,
                user_name TEXT NOT NULL,
                type TEXT NOT NULL CHECK (type IN ('candle', 'flower')),
                flower_type TEXT CHECK (flower_type IN ('rose', 'lotus') OR flower_type IS NULL),
                duration TEXT NOT NULL CHECK (duration IN ('12h', '1d', '7d', 'forever')),
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (memorial_id) REFERENCES memorials (id) ON DELETE CASCADE
            )
        """)
        
        # Índices para melhor performance
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tributes_memorial_id 
            ON memorial_tributes (memorial_id)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tributes_expires_at 
            ON memorial_tributes (expires_at)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tributes_active 
            ON memorial_tributes (is_active)
        """)
        
        conn.commit()
        conn.close()
    
    def add_tribute(self, memorial_id, user_name, tribute_type, duration, message=None, flower_type=None):
        """Adiciona uma nova homenagem (vela ou flor)"""
        conn = self.get_connection()
        
        # Calcular data de expiração
        expires_at = None
        if duration != 'forever':
            now = datetime.now()
            if duration == '12h':
                expires_at = now + timedelta(hours=12)
            elif duration == '1d':
                expires_at = now + timedelta(days=1)
            elif duration == '7d':
                expires_at = now + timedelta(days=7)
        
        # Se for flor e não especificou tipo, usar rosa como padrão
        if tribute_type == 'flower' and not flower_type:
            flower_type = 'rose'
        
        cursor = conn.execute("""
            INSERT INTO memorial_tributes 
            (memorial_id, user_name, type, flower_type, duration, message, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (memorial_id, user_name, tribute_type, flower_type, duration, message, expires_at))
        
        tribute_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return self.get_tribute_by_id(tribute_id)
    
    def get_tribute_by_id(self, tribute_id):
        """Busca uma homenagem pelo ID"""
        conn = self.get_connection()
        cursor = conn.execute("""
            SELECT * FROM memorial_tributes WHERE id = ?
        """, (tribute_id,))
        
        tribute = cursor.fetchone()
        conn.close()
        
        if tribute:
            return dict(tribute)
        return None
    
    def get_memorial_tributes(self, memorial_id, include_expired=False):
        """Busca todas as homenagens de um memorial"""
        conn = self.get_connection()
        
        query = """
            SELECT * FROM memorial_tributes 
            WHERE memorial_id = ? AND is_active = 1
        """
        params = [memorial_id]
        
        if not include_expired:
            query += " AND (expires_at IS NULL OR expires_at > ?)"
            params.append(datetime.now().isoformat())
        
        query += " ORDER BY created_at DESC"
        
        cursor = conn.execute(query, params)
        tributes = cursor.fetchall()
        conn.close()
        
        return [dict(tribute) for tribute in tributes]
    
    def get_active_tributes(self, memorial_id):
        """Busca apenas homenagens ativas (não expiradas)"""
        return self.get_memorial_tributes(memorial_id, include_expired=False)
    
    def cleanup_expired_tributes(self):
        """Remove homenagens expiradas do banco de dados"""
        conn = self.get_connection()
        
        # Marcar como inativas ao invés de deletar (para histórico)
        cursor = conn.execute("""
            UPDATE memorial_tributes 
            SET is_active = 0 
            WHERE expires_at IS NOT NULL 
            AND expires_at <= ? 
            AND is_active = 1
        """, (datetime.now().isoformat(),))
        
        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected_rows
    
    def get_tribute_stats(self, memorial_id):
        """Obtém estatísticas das homenagens de um memorial"""
        conn = self.get_connection()
        
        # Total de homenagens ativas
        cursor = conn.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN type = 'candle' THEN 1 ELSE 0 END) as candles,
                SUM(CASE WHEN type = 'flower' THEN 1 ELSE 0 END) as flowers
            FROM memorial_tributes 
            WHERE memorial_id = ? AND is_active = 1
            AND (expires_at IS NULL OR expires_at > ?)
        """, (memorial_id, datetime.now().isoformat()))
        
        stats = cursor.fetchone()
        conn.close()
        
        if stats:
            return dict(stats)
        return {'total': 0, 'candles': 0, 'flowers': 0}
    
    def delete_tribute(self, tribute_id, user_name=None):
        """Remove uma homenagem (apenas o próprio usuário pode remover)"""
        conn = self.get_connection()
        
        query = "UPDATE memorial_tributes SET is_active = 0 WHERE id = ?"
        params = [tribute_id]
        
        if user_name:
            query += " AND user_name = ?"
            params.append(user_name)
        
        cursor = conn.execute(query, params)
        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected_rows > 0
    
    def get_user_tributes(self, user_name, limit=50):
        """Busca todas as homenagens de um usuário"""
        conn = self.get_connection()
        
        cursor = conn.execute("""
            SELECT t.*, m.name as memorial_name 
            FROM memorial_tributes t
            JOIN memorials m ON t.memorial_id = m.id
            WHERE t.user_name = ? AND t.is_active = 1
            ORDER BY t.created_at DESC
            LIMIT ?
        """, (user_name, limit))
        
        tributes = cursor.fetchall()
        conn.close()
        
        return [dict(tribute) for tribute in tributes]
    
    def get_recent_tributes(self, limit=20):
        """Busca homenagens recentes de todos os memoriais"""
        conn = self.get_connection()
        
        cursor = conn.execute("""
            SELECT t.*, m.name as memorial_name 
            FROM memorial_tributes t
            JOIN memorials m ON t.memorial_id = m.id
            WHERE t.is_active = 1
            AND (t.expires_at IS NULL OR t.expires_at > ?)
            ORDER BY t.created_at DESC
            LIMIT ?
        """, (datetime.now().isoformat(), limit))
        
        tributes = cursor.fetchall()
        conn.close()
        
        return [dict(tribute) for tribute in tributes]

