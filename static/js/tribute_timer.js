// Sistema de Timer em Tempo Real para Homenagens Virtuais

class TributeTimer {
    constructor() {
        this.timers = new Map();
        this.updateInterval = null;
        this.init();
    }

    init() {
        this.startGlobalTimer();
        this.setupVisibilityHandling();
    }

    startGlobalTimer() {
        // Atualizar a cada 30 segundos
        this.updateInterval = setInterval(() => {
            this.updateAllTimers();
        }, 30000);

        // Primeira atualização imediata
        this.updateAllTimers();
    }

    stopGlobalTimer() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    setupVisibilityHandling() {
        // Pausar/retomar timer quando a aba não está visível
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.stopGlobalTimer();
            } else {
                this.startGlobalTimer();
            }
        });
    }

    addTribute(tributeId, expiresAt, duration) {
        if (duration === 'forever') return;

        this.timers.set(tributeId, {
            expiresAt: new Date(expiresAt),
            duration: duration,
            element: document.querySelector(`[data-tribute-id="${tributeId}"] .tribute-timer`)
        });
    }

    removeTribute(tributeId) {
        this.timers.delete(tributeId);
    }

    updateAllTimers() {
        const now = new Date();
        const expiredTributes = [];

        this.timers.forEach((timer, tributeId) => {
            const timeRemaining = this.calculateTimeRemaining(now, timer.expiresAt);
            
            if (timeRemaining === null) {
                // Homenagem expirou
                expiredTributes.push(tributeId);
                this.handleExpiredTribute(tributeId);
            } else {
                // Atualizar display do timer
                this.updateTimerDisplay(tributeId, timeRemaining, timer.element);
            }
        });

        // Remover homenagens expiradas
        expiredTributes.forEach(id => {
            this.removeTribute(id);
        });

        // Se houver homenagens expiradas, recarregar a lista
        if (expiredTributes.length > 0 && window.memorialTributes) {
            window.memorialTributes.renderTributes();
        }
    }

    calculateTimeRemaining(now, expiresAt) {
        const diff = expiresAt - now;
        
        if (diff <= 0) return null;

        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);

        return { days, hours, minutes, seconds, totalMs: diff };
    }

    updateTimerDisplay(tributeId, timeRemaining, element) {
        if (!element) return;

        const { days, hours, minutes, seconds, totalMs } = timeRemaining;
        let displayText = '';
        let urgencyClass = '';

        // Determinar formato de exibição baseado no tempo restante
        if (days > 0) {
            displayText = `${days}d ${hours}h`;
        } else if (hours > 0) {
            displayText = `${hours}h ${minutes}m`;
        } else if (minutes > 0) {
            displayText = `${minutes}m`;
            if (minutes <= 5) urgencyClass = 'timer-urgent';
        } else {
            displayText = `${seconds}s`;
            urgencyClass = 'timer-critical';
        }

        // Atualizar texto
        element.textContent = displayText;

        // Aplicar classes de urgência
        element.className = `tribute-timer ${urgencyClass}`;

        // Adicionar animação para últimos minutos
        if (totalMs <= 300000) { // 5 minutos
            element.classList.add('timer-pulse');
        }

        // Atualizar tooltip também
        this.updateTooltipTimer(tributeId, displayText);
    }

    updateTooltipTimer(tributeId, timeText) {
        const tooltipElement = document.querySelector(`[data-tribute-id="${tributeId}"] .tribute-tooltip`);
        if (!tooltipElement) return;

        const tooltipHTML = tooltipElement.innerHTML;
        const updatedHTML = tooltipHTML.replace(
            /Restam: [^<]+/,
            `Restam: ${timeText}`
        );
        tooltipElement.innerHTML = updatedHTML;
    }

    handleExpiredTribute(tributeId) {
        const tributeElement = document.querySelector(`[data-tribute-id="${tributeId}"]`);
        if (!tributeElement) return;

        // Adicionar animação de fade out
        tributeElement.classList.add('tribute-expiring');
        
        // Remover após animação
        setTimeout(() => {
            if (tributeElement.parentNode) {
                tributeElement.remove();
            }
        }, 1000);

        // Mostrar notificação discreta
        this.showExpirationNotification();
    }

    showExpirationNotification() {
        // Evitar spam de notificações
        if (this.lastNotification && Date.now() - this.lastNotification < 5000) {
            return;
        }

        const notification = document.createElement('div');
        notification.className = 'tribute-notification';
        notification.innerHTML = `
            <i class="fas fa-clock"></i>
            Uma homenagem expirou
        `;

        document.body.appendChild(notification);

        // Remover após alguns segundos
        setTimeout(() => {
            notification.remove();
        }, 3000);

        this.lastNotification = Date.now();
    }

    // Método para sincronizar com dados do servidor
    async syncWithServer(memorialId) {
        try {
            const response = await fetch(`/memorial/tributes/${memorialId}`);
            if (response.ok) {
                const data = await response.json();
                
                // Limpar timers existentes
                this.timers.clear();
                
                // Adicionar novos timers
                data.tributes.forEach(tribute => {
                    if (tribute.expires_at) {
                        this.addTribute(tribute.id, tribute.expires_at, tribute.duration);
                    }
                });
            }
        } catch (error) {
            console.error('Erro ao sincronizar timers:', error);
        }
    }

    // Método para pausar todos os timers
    pauseAll() {
        this.stopGlobalTimer();
    }

    // Método para retomar todos os timers
    resumeAll() {
        this.startGlobalTimer();
    }

    // Cleanup quando a página é fechada
    destroy() {
        this.stopGlobalTimer();
        this.timers.clear();
    }
}

// CSS adicional para animações de timer
const timerStyles = `
.timer-urgent {
    color: #ff9800 !important;
    font-weight: bold;
}

.timer-critical {
    color: #f44336 !important;
    font-weight: bold;
}

.timer-pulse {
    animation: timerPulse 1s ease-in-out infinite alternate;
}

@keyframes timerPulse {
    from { opacity: 1; }
    to { opacity: 0.6; }
}

.tribute-expiring {
    animation: fadeOut 1s ease-out forwards;
}

@keyframes fadeOut {
    from { 
        opacity: 1; 
        transform: scale(1);
    }
    to { 
        opacity: 0; 
        transform: scale(0.8);
    }
}

.tribute-notification {
    position: fixed;
    top: 80px;
    right: 20px;
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 14px;
    z-index: 3000;
    display: flex;
    align-items: center;
    gap: 8px;
    animation: slideInRight 0.3s ease-out;
}

@keyframes slideInRight {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}
`;

// Adicionar estilos ao documento
const styleSheet = document.createElement('style');
styleSheet.textContent = timerStyles;
document.head.appendChild(styleSheet);

// Instância global do timer
window.tributeTimer = new TributeTimer();

// Cleanup ao fechar a página
window.addEventListener('beforeunload', () => {
    if (window.tributeTimer) {
        window.tributeTimer.destroy();
    }
});

