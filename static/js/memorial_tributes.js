// Sistema de Velas e Flores Virtuais para Memorial

class MemorialTributes {
    constructor(memorialId) {
        this.memorialId = memorialId;
        this.tributes = [];
        this.currentTributeType = null;
        this.init();
    }

    init() {
        this.loadTributes();
        this.setupEventListeners();
        this.startTimerUpdates();
    }

    setupEventListeners() {
        // Botões de acender vela e deixar flor
        document.getElementById('light-candle-btn')?.addEventListener('click', () => {
            this.showDurationSelector('candle');
        });

        document.getElementById('leave-flower-btn')?.addEventListener('click', () => {
            this.showDurationSelector('flower');
        });

        // Seletor de duração
        document.getElementById('duration-confirm')?.addEventListener('click', () => {
            this.confirmTribute();
        });

        document.getElementById('duration-cancel')?.addEventListener('click', () => {
            this.hideDurationSelector();
        });

        // Overlay do modal
        document.getElementById('modal-overlay')?.addEventListener('click', () => {
            this.hideDurationSelector();
        });

        // Opções de duração
        document.querySelectorAll('.duration-option').forEach(option => {
            option.addEventListener('click', () => {
                this.selectDuration(option);
            });
        });
    }

    showDurationSelector(type) {
        this.currentTributeType = type;
        const selector = document.getElementById('duration-selector');
        const overlay = document.getElementById('modal-overlay');
        const title = document.getElementById('selector-title');
        
        if (type === 'candle') {
            title.textContent = 'Acender uma Vela Virtual';
        } else {
            title.textContent = 'Deixar uma Flor Virtual';
        }

        selector.classList.add('active');
        overlay.classList.add('active');
        
        // Limpar seleção anterior
        document.querySelectorAll('.duration-option').forEach(opt => {
            opt.classList.remove('selected');
        });
        document.getElementById('tribute-message').value = '';
    }

    hideDurationSelector() {
        document.getElementById('duration-selector').classList.remove('active');
        document.getElementById('modal-overlay').classList.remove('active');
        this.currentTributeType = null;
    }

    selectDuration(option) {
        document.querySelectorAll('.duration-option').forEach(opt => {
            opt.classList.remove('selected');
        });
        option.classList.add('selected');
    }

    async confirmTribute() {
        const selectedDuration = document.querySelector('.duration-option.selected');
        const message = document.getElementById('tribute-message').value.trim();
        
        if (!selectedDuration) {
            alert('Por favor, selecione uma duração.');
            return;
        }

        const duration = selectedDuration.dataset.duration;
        const userName = this.getCurrentUserName();
        
        if (!userName) {
            alert('Você precisa estar logado para deixar uma homenagem.');
            return;
        }

        try {
            const response = await fetch('/memorial/tribute/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    memorial_id: this.memorialId,
                    type: this.currentTributeType,
                    duration: duration,
                    message: message,
                    user_name: userName
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.addTributeToDisplay(result.tribute);
                this.hideDurationSelector();
                this.showSuccessMessage();
            } else {
                throw new Error('Erro ao adicionar homenagem');
            }
        } catch (error) {
            console.error('Erro:', error);
            alert('Erro ao adicionar homenagem. Tente novamente.');
        }
    }

    addTributeToDisplay(tribute) {
        this.tributes.push(tribute);
        this.renderTributes();
    }

    async loadTributes() {
        try {
            const response = await fetch(`/memorial/tributes/${this.memorialId}`);
            if (response.ok) {
                const data = await response.json();
                this.tributes = data.tributes || [];
                this.renderTributes();
            }
        } catch (error) {
            console.error('Erro ao carregar homenagens:', error);
        }
    }

    renderTributes() {
        const container = document.getElementById('tributes-display');
        if (!container) return;

        // Filtrar homenagens expiradas
        this.tributes = this.tributes.filter(tribute => {
            if (tribute.duration === 'forever') return true;
            return new Date(tribute.expires_at) > new Date();
        });

        if (this.tributes.length === 0) {
            container.innerHTML = `
                <div class="empty-tributes">
                    <p>Seja o primeiro a deixar uma homenagem</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.tributes.map(tribute => {
            return this.createTributeHTML(tribute);
        }).join('');

        // Sincronizar com o sistema de timer
        if (window.tributeTimer) {
            this.tributes.forEach(tribute => {
                if (tribute.expires_at && tribute.duration !== 'forever') {
                    window.tributeTimer.addTribute(tribute.id, tribute.expires_at, tribute.duration);
                }
            });
        }
    }

    createTributeHTML(tribute) {
        const timeRemaining = this.getTimeRemaining(tribute);
        const tooltipText = this.createTooltipText(tribute, timeRemaining);
        
        if (tribute.type === 'candle') {
            return `
                <div class="tribute-item candle-item" data-tribute-id="${tribute.id}">
                    <div class="candle-flame"></div>
                    <div class="candle-base"></div>
                    <div class="tribute-tooltip">${tooltipText}</div>
                    ${timeRemaining ? `<div class="tribute-timer">${timeRemaining}</div>` : ''}
                </div>
            `;
        } else {
            const flowerClass = tribute.flower_type === 'lotus' ? 'lotus-icon' : 'rose-icon';
            return `
                <div class="tribute-item flower-item" data-tribute-id="${tribute.id}">
                    <div class="flower-icon ${flowerClass}">
                        <img src="/static/images/${tribute.flower_type}_flower.png" 
                             alt="${tribute.flower_type}" 
                             style="width: 30px; height: 30px; object-fit: contain;">
                    </div>
                    <div class="tribute-tooltip">${tooltipText}</div>
                    ${timeRemaining ? `<div class="tribute-timer">${timeRemaining}</div>` : ''}
                </div>
            `;
        }
    }

    createTooltipText(tribute, timeRemaining) {
        let text = `Por: ${tribute.user_name}`;
        if (tribute.message) {
            text += `<br>"${tribute.message}"`;
        }
        if (timeRemaining) {
            text += `<br>Restam: ${timeRemaining}`;
        } else if (tribute.duration === 'forever') {
            text += `<br>Para sempre`;
        }
        return text;
    }

    getTimeRemaining(tribute) {
        if (tribute.duration === 'forever') return null;
        
        const now = new Date();
        const expiresAt = new Date(tribute.expires_at);
        const diff = expiresAt - now;
        
        if (diff <= 0) return null;
        
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        
        if (days > 0) {
            return `${days}d ${hours}h`;
        } else if (hours > 0) {
            return `${hours}h ${minutes}m`;
        } else {
            return `${minutes}m`;
        }
    }

    startTimerUpdates() {
        setInterval(() => {
            this.updateTimers();
        }, 60000); // Atualizar a cada minuto
    }

    updateTimers() {
        const tributeItems = document.querySelectorAll('.tribute-item');
        let needsRerender = false;
        
        tributeItems.forEach(item => {
            const tributeId = parseInt(item.dataset.tributeId);
            const tribute = this.tributes.find(t => t.id === tributeId);
            
            if (tribute && tribute.duration !== 'forever') {
                const timeRemaining = this.getTimeRemaining(tribute);
                const timerElement = item.querySelector('.tribute-timer');
                
                if (timeRemaining) {
                    if (timerElement) {
                        timerElement.textContent = timeRemaining;
                    }
                    
                    // Atualizar tooltip
                    const tooltip = item.querySelector('.tribute-tooltip');
                    if (tooltip) {
                        tooltip.innerHTML = this.createTooltipText(tribute, timeRemaining);
                    }
                } else {
                    // Homenagem expirou
                    needsRerender = true;
                }
            }
        });
        
        if (needsRerender) {
            this.renderTributes();
        }
    }

    getCurrentUserName() {
        // Esta função deve ser implementada para obter o nome do usuário logado
        // Se o usuário não estiver logado, solicitar o nome
        const userNameElement = document.querySelector("[data-user-name]");
        if (userNameElement && userNameElement.dataset.userName) {
            return userNameElement.dataset.userName;
        }
        
        let userName = localStorage.getItem("tribute_user_name");
        if (!userName) {
            userName = prompt("Digite seu nome para a homenagem:");
            if (userName) {
                localStorage.setItem("tribute_user_name", userName);
            }
        }
        return userName;
    }

    showSuccessMessage() {
        // Criar e mostrar mensagem de sucesso
        const message = document.createElement('div');
        message.className = 'alert alert-success';
        message.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 3000;
            padding: 15px 20px;
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        `;
        message.textContent = 'Homenagem adicionada com sucesso!';
        
        document.body.appendChild(message);
        
        setTimeout(() => {
            message.remove();
        }, 3000);
    }
}

// Inicializar quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    const memorialIdElement = document.querySelector('[data-memorial-id]');
    if (memorialIdElement) {
        const memorialId = memorialIdElement.dataset.memorialId;
        window.memorialTributes = new MemorialTributes(memorialId);
    }
});

// Função para escolher tipo de flor
function selectFlowerType(type) {
    const currentType = window.memorialTributes.currentTributeType;
    if (currentType === 'flower') {
        window.memorialTributes.currentFlowerType = type;
    }
}

