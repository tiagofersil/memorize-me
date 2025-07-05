import threading
import time
import schedule
from datetime import datetime
from database_tributes import TributesDatabase

class TributeScheduler:
    """Sistema de agendamento para gerenciar homenagens virtuais"""
    
    def __init__(self):
        self.db = TributesDatabase()
        self.running = False
        self.thread = None
    
    def start(self):
        """Inicia o agendador"""
        if self.running:
            return
        
        self.running = True
        
        # Agendar limpeza a cada hora
        schedule.every().hour.do(self.cleanup_expired_tributes)
        
        # Agendar limpeza diária às 3:00 AM
        schedule.every().day.at("03:00").do(self.daily_cleanup)
        
        # Iniciar thread do agendador
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        
        print("Sistema de agendamento de homenagens iniciado")
    
    def stop(self):
        """Para o agendador"""
        self.running = False
        schedule.clear()
        if self.thread:
            self.thread.join(timeout=5)
        print("Sistema de agendamento de homenagens parado")
    
    def _run_scheduler(self):
        """Executa o loop do agendador"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Verificar a cada minuto
            except Exception as e:
                print(f"Erro no agendador de homenagens: {e}")
                time.sleep(60)
    
    def cleanup_expired_tributes(self):
        """Remove homenagens expiradas"""
        try:
            affected_rows = self.db.cleanup_expired_tributes()
            if affected_rows > 0:
                print(f"[{datetime.now()}] Limpeza automática: {affected_rows} homenagens expiradas removidas")
            return affected_rows
        except Exception as e:
            print(f"Erro na limpeza de homenagens: {e}")
            return 0
    
    def daily_cleanup(self):
        """Limpeza diária mais completa"""
        try:
            print(f"[{datetime.now()}] Iniciando limpeza diária de homenagens...")
            
            # Limpeza de homenagens expiradas
            expired_count = self.cleanup_expired_tributes()
            
            # Estatísticas gerais
            stats = self.get_system_stats()
            
            print(f"Limpeza diária concluída:")
            print(f"  - Homenagens expiradas removidas: {expired_count}")
            print(f"  - Total de homenagens ativas: {stats['total_active']}")
            print(f"  - Total de velas ativas: {stats['active_candles']}")
            print(f"  - Total de flores ativas: {stats['active_flowers']}")
            
        except Exception as e:
            print(f"Erro na limpeza diária: {e}")
    
    def get_system_stats(self):
        """Obtém estatísticas do sistema de homenagens"""
        try:
            conn = self.db.get_connection()
            
            # Total de homenagens ativas
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_active,
                    SUM(CASE WHEN type = 'candle' THEN 1 ELSE 0 END) as active_candles,
                    SUM(CASE WHEN type = 'flower' THEN 1 ELSE 0 END) as active_flowers
                FROM memorial_tributes 
                WHERE is_active = 1
                AND (expires_at IS NULL OR expires_at > ?)
            """, (datetime.now().isoformat(),))
            
            stats = cursor.fetchone()
            conn.close()
            
            if stats:
                return dict(stats)
            return {'total_active': 0, 'active_candles': 0, 'active_flowers': 0}
            
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return {'total_active': 0, 'active_candles': 0, 'active_flowers': 0}

# Instância global do agendador
tribute_scheduler = TributeScheduler()

def start_tribute_scheduler():
    """Função para iniciar o agendador"""
    tribute_scheduler.start()

def stop_tribute_scheduler():
    """Função para parar o agendador"""
    tribute_scheduler.stop()

# Função para uso em aplicações Flask
def init_tribute_scheduler(app):
    """Inicializa o agendador com a aplicação Flask"""
    @app.before_first_request
    def start_scheduler():
        start_tribute_scheduler()
    
    import atexit
    atexit.register(stop_tribute_scheduler)

