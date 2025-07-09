/**
 * Melhorias Visuais e Interações para Memorial Online
 * Adiciona animações, micro-interações e funcionalidades avançadas
 */

class MemorialEnhancements {
    constructor() {
        this.init();
    }

    init() {
        this.setupAnimations();
        this.setupGalleryLightbox();
        this.setupSmoothScrolling();
        this.setupParallaxEffect();
        this.setupProgressIndicator();
        this.setupShareFunctionality();
        this.setupPrintMode();
        this.setupAccessibility();
    }

    /**
     * Configurar animações de entrada
     */
    setupAnimations() {
        // Intersection Observer para animações de entrada
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);

        // Observar seções para animação
        document.querySelectorAll('.section').forEach(section => {
            observer.observe(section);
        });

        // Adicionar CSS para animações
        this.addAnimationStyles();
    }

    /**
     * Adicionar estilos de animação dinamicamente
     */
    addAnimationStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .section {
                opacity: 0;
                transform: translateY(30px);
                transition: all 0.6s ease-out;
            }
            
            .section.animate-in {
                opacity: 1;
                transform: translateY(0);
            }
            
            .gallery-item {
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            
            .gallery-item:hover {
                transform: translateY(-5px) scale(1.02);
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Configurar lightbox para galeria
     */
    setupGalleryLightbox() {
        const galleryItems = document.querySelectorAll('.gallery-item');
        if (galleryItems.length === 0) return;

        // Criar estrutura do lightbox
        const lightbox = this.createLightbox();
        document.body.appendChild(lightbox);

        // Adicionar eventos de clique
        galleryItems.forEach((item, index) => {
            item.addEventListener('click', () => {
                this.openLightbox(index, galleryItems);
            });
        });
    }

    /**
     * Criar estrutura HTML do lightbox
     */
    createLightbox() {
        const lightbox = document.createElement('div');
        lightbox.className = 'memorial-lightbox';
        lightbox.innerHTML = `
            <div class="lightbox-overlay"></div>
            <div class="lightbox-container">
                <button class="lightbox-close">&times;</button>
                <button class="lightbox-prev">&#8249;</button>
                <button class="lightbox-next">&#8250;</button>
                <div class="lightbox-content">
                    <img class="lightbox-image" src="" alt="">
                    <div class="lightbox-caption"></div>
                </div>
                <div class="lightbox-counter"></div>
            </div>
        `;

        // Adicionar estilos do lightbox
        this.addLightboxStyles();

        // Configurar eventos
        this.setupLightboxEvents(lightbox);

        return lightbox;
    }

    /**
     * Adicionar estilos do lightbox
     */
    addLightboxStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .memorial-lightbox {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 9999;
                display: none;
                align-items: center;
                justify-content: center;
            }
            
            .memorial-lightbox.active {
                display: flex;
            }
            
            .lightbox-overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.9);
                backdrop-filter: blur(5px);
            }
            
            .lightbox-container {
                position: relative;
                max-width: 90vw;
                max-height: 90vh;
                z-index: 1;
            }
            
            .lightbox-image {
                max-width: 100%;
                max-height: 80vh;
                object-fit: contain;
                border-radius: 8px;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            }
            
            .lightbox-close, .lightbox-prev, .lightbox-next {
                position: absolute;
                background: rgba(255, 255, 255, 0.9);
                border: none;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                font-size: 24px;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .lightbox-close {
                top: -60px;
                right: 0;
            }
            
            .lightbox-prev {
                left: -60px;
                top: 50%;
                transform: translateY(-50%);
            }
            
            .lightbox-next {
                right: -60px;
                top: 50%;
                transform: translateY(-50%);
            }
            
            .lightbox-close:hover, .lightbox-prev:hover, .lightbox-next:hover {
                background: white;
                transform: scale(1.1);
            }
            
            .lightbox-caption {
                text-align: center;
                color: white;
                margin-top: 20px;
                font-size: 16px;
            }
            
            .lightbox-counter {
                position: absolute;
                bottom: -50px;
                left: 50%;
                transform: translateX(-50%);
                color: white;
                font-size: 14px;
            }
            
            @media (max-width: 768px) {
                .lightbox-prev, .lightbox-next {
                    width: 40px;
                    height: 40px;
                    font-size: 20px;
                }
                
                .lightbox-prev { left: 10px; }
                .lightbox-next { right: 10px; }
                .lightbox-close { top: 10px; right: 10px; }
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Configurar eventos do lightbox
     */
    setupLightboxEvents(lightbox) {
        const overlay = lightbox.querySelector('.lightbox-overlay');
        const closeBtn = lightbox.querySelector('.lightbox-close');
        const prevBtn = lightbox.querySelector('.lightbox-prev');
        const nextBtn = lightbox.querySelector('.lightbox-next');

        // Fechar lightbox
        [overlay, closeBtn].forEach(element => {
            element.addEventListener('click', () => {
                this.closeLightbox();
            });
        });

        // Navegação
        prevBtn.addEventListener('click', () => this.navigateLightbox(-1));
        nextBtn.addEventListener('click', () => this.navigateLightbox(1));

        // Teclas do teclado
        document.addEventListener('keydown', (e) => {
            if (!lightbox.classList.contains('active')) return;
            
            switch(e.key) {
                case 'Escape':
                    this.closeLightbox();
                    break;
                case 'ArrowLeft':
                    this.navigateLightbox(-1);
                    break;
                case 'ArrowRight':
                    this.navigateLightbox(1);
                    break;
            }
        });
    }

    /**
     * Abrir lightbox
     */
    openLightbox(index, galleryItems) {
        this.currentIndex = index;
        this.galleryItems = galleryItems;
        
        const lightbox = document.querySelector('.memorial-lightbox');
        const image = lightbox.querySelector('.lightbox-image');
        const counter = lightbox.querySelector('.lightbox-counter');
        
        const currentItem = galleryItems[index];
        const img = currentItem.querySelector('img');
        
        image.src = img.src;
        image.alt = img.alt;
        counter.textContent = `${index + 1} de ${galleryItems.length}`;
        
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    /**
     * Fechar lightbox
     */
    closeLightbox() {
        const lightbox = document.querySelector('.memorial-lightbox');
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
    }

    /**
     * Navegar no lightbox
     */
    navigateLightbox(direction) {
        this.currentIndex += direction;
        
        if (this.currentIndex < 0) {
            this.currentIndex = this.galleryItems.length - 1;
        } else if (this.currentIndex >= this.galleryItems.length) {
            this.currentIndex = 0;
        }
        
        this.openLightbox(this.currentIndex, this.galleryItems);
    }

    /**
     * Configurar rolagem suave
     */
    setupSmoothScrolling() {
        // Adicionar navegação suave entre seções
        const sections = document.querySelectorAll('.section');
        if (sections.length > 1) {
            this.createSectionNavigation(sections);
        }
    }

    /**
     * Criar navegação entre seções
     */
    createSectionNavigation(sections) {
        const nav = document.createElement('nav');
        nav.className = 'section-navigation';
        nav.innerHTML = `
            <div class="nav-dots">
                ${Array.from(sections).map((_, index) => 
                    `<button class="nav-dot" data-section="${index}"></button>`
                ).join('')}
            </div>
        `;

        // Adicionar estilos
        const style = document.createElement('style');
        style.textContent = `
            .section-navigation {
                position: fixed;
                right: 30px;
                top: 50%;
                transform: translateY(-50%);
                z-index: 100;
            }
            
            .nav-dots {
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            
            .nav-dot {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                border: 2px solid var(--turquoise-400);
                background: transparent;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .nav-dot.active {
                background: var(--turquoise-400);
            }
            
            .nav-dot:hover {
                transform: scale(1.2);
            }
            
            @media (max-width: 768px) {
                .section-navigation {
                    display: none;
                }
            }
        `;
        document.head.appendChild(style);

        // Adicionar eventos
        nav.addEventListener('click', (e) => {
            if (e.target.classList.contains('nav-dot')) {
                const sectionIndex = parseInt(e.target.dataset.section);
                sections[sectionIndex].scrollIntoView({ behavior: 'smooth' });
            }
        });

        // Atualizar dot ativo baseado na rolagem
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const index = Array.from(sections).indexOf(entry.target);
                    nav.querySelectorAll('.nav-dot').forEach((dot, i) => {
                        dot.classList.toggle('active', i === index);
                    });
                }
            });
        }, { threshold: 0.5 });

        sections.forEach(section => observer.observe(section));
        document.body.appendChild(nav);
    }

    /**
     * Configurar efeito parallax sutil
     */
    setupParallaxEffect() {
        const heroSection = document.querySelector('.hero-section-fullwidth');
        if (!heroSection) return;

        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            
            const coverImage = heroSection.querySelector('.cover-image');
            if (coverImage) {
                coverImage.style.transform = `translateY(${rate}px)`;
            }
        });
    }

    /**
     * Configurar indicador de progresso de leitura
     */
    setupProgressIndicator() {
        const progressBar = document.createElement('div');
        progressBar.className = 'reading-progress';
        
        const style = document.createElement('style');
        style.textContent = `
            .reading-progress {
                position: fixed;
                top: 0;
                left: 0;
                width: 0%;
                height: 3px;
                background: linear-gradient(90deg, var(--turquoise-400), var(--turquoise-600));
                z-index: 1000;
                transition: width 0.3s ease;
            }
        `;
        document.head.appendChild(style);

        window.addEventListener('scroll', () => {
            const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (winScroll / height) * 100;
            progressBar.style.width = scrolled + '%';
        });

        document.body.appendChild(progressBar);
    }

    /**
     * Melhorar funcionalidade de compartilhamento
     */
    setupShareFunctionality() {
        const shareBtn = document.getElementById('share-memorial');
        if (!shareBtn) return;

        // Criar menu de compartilhamento
        const shareMenu = document.createElement('div');
        shareMenu.className = 'share-menu';
        shareMenu.innerHTML = `
            <div class="share-options">
                <button class="share-option" data-platform="whatsapp">
                    <i class="fab fa-whatsapp"></i> WhatsApp
                </button>
                <button class="share-option" data-platform="facebook">
                    <i class="fab fa-facebook"></i> Facebook
                </button>
                <button class="share-option" data-platform="twitter">
                    <i class="fab fa-twitter"></i> Twitter
                </button>
                <button class="share-option" data-platform="copy">
                    <i class="fas fa-copy"></i> Copiar Link
                </button>
            </div>
        `;

        // Adicionar estilos
        const style = document.createElement('style');
        style.textContent = `
            .share-menu {
                position: absolute;
                top: -200px;
                left: 0;
                background: white;
                border-radius: 8px;
                box-shadow: var(--shadow-lg);
                padding: 10px;
                opacity: 0;
                visibility: hidden;
                transition: all 0.3s ease;
                z-index: 1000;
            }
            
            .share-menu.active {
                opacity: 1;
                visibility: visible;
                top: -180px;
            }
            
            .share-options {
                display: flex;
                flex-direction: column;
                gap: 5px;
                min-width: 150px;
            }
            
            .share-option {
                background: none;
                border: none;
                padding: 10px;
                text-align: left;
                cursor: pointer;
                border-radius: 4px;
                transition: background 0.2s ease;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .share-option:hover {
                background: var(--gray-100);
            }
        `;
        document.head.appendChild(style);

        shareBtn.parentNode.style.position = 'relative';
        shareBtn.parentNode.appendChild(shareMenu);

        // Eventos
        shareBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            shareMenu.classList.toggle('active');
        });

        document.addEventListener('click', () => {
            shareMenu.classList.remove('active');
        });

        shareMenu.addEventListener('click', (e) => {
            const platform = e.target.closest('.share-option')?.dataset.platform;
            if (platform) {
                this.shareToplatform(platform);
                shareMenu.classList.remove('active');
            }
        });
    }

    /**
     * Compartilhar para plataforma específica
     */
    shareToplatform(platform) {
        const url = window.location.href;
        const title = document.title;
        const text = `Visite este memorial em memória de uma pessoa especial`;

        const urls = {
            whatsapp: `https://wa.me/?text=${encodeURIComponent(text + ' ' + url)}`,
            facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
            twitter: `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`
        };

        if (platform === 'copy') {
            navigator.clipboard.writeText(url).then(() => {
                this.showNotification('Link copiado para a área de transferência!');
            });
        } else if (urls[platform]) {
            window.open(urls[platform], '_blank', 'width=600,height=400');
        }
    }

    /**
     * Configurar modo de impressão
     */
    setupPrintMode() {
        const printBtn = document.createElement('button');
        printBtn.className = 'btn btn-secondary print-btn';
        printBtn.innerHTML = '<i class="fas fa-print"></i> Imprimir Memorial';
        
        const qrSection = document.querySelector('.qr-section');
        if (qrSection) {
            qrSection.appendChild(printBtn);
        }

        printBtn.addEventListener('click', () => {
            window.print();
        });

        // Estilos para impressão
        const printStyle = document.createElement('style');
        printStyle.textContent = `
            @media print {
                .sidebar, .section-navigation, .print-btn, .tribute-options {
                    display: none !important;
                }
                
                .content-layout {
                    grid-template-columns: 1fr !important;
                }
                
                .section {
                    break-inside: avoid;
                    margin-bottom: 30px;
                }
                
                .hero-section-fullwidth {
                    height: 300px;
                }
                
                body {
                    font-size: 12pt;
                    line-height: 1.4;
                }
            }
        `;
        document.head.appendChild(printStyle);
    }

    /**
     * Melhorar acessibilidade
     */
    setupAccessibility() {
        // Adicionar skip links
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.textContent = 'Pular para o conteúdo principal';
        skipLink.className = 'skip-link';
        
        const skipStyle = document.createElement('style');
        skipStyle.textContent = `
            .skip-link {
                position: absolute;
                top: -40px;
                left: 6px;
                background: var(--turquoise-600);
                color: white;
                padding: 8px;
                text-decoration: none;
                border-radius: 4px;
                z-index: 1000;
                transition: top 0.3s;
            }
            
            .skip-link:focus {
                top: 6px;
            }
        `;
        document.head.appendChild(skipStyle);
        document.body.insertBefore(skipLink, document.body.firstChild);

        // Melhorar foco do teclado
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
        });

        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-navigation');
        });

        const focusStyle = document.createElement('style');
        focusStyle.textContent = `
            .keyboard-navigation *:focus {
                outline: 2px solid var(--turquoise-400) !important;
                outline-offset: 2px !important;
            }
        `;
        document.head.appendChild(focusStyle);
    }

    /**
     * Mostrar notificação
     */
    showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        const style = document.createElement('style');
        style.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 20px;
                border-radius: 8px;
                color: white;
                font-weight: 500;
                z-index: 10000;
                transform: translateX(400px);
                transition: transform 0.3s ease;
            }
            
            .notification-success {
                background: var(--success-color);
            }
            
            .notification-error {
                background: var(--error-color);
            }
            
            .notification.show {
                transform: translateX(0);
            }
        `;
        
        if (!document.querySelector('style[data-notification]')) {
            style.setAttribute('data-notification', 'true');
            document.head.appendChild(style);
        }

        document.body.appendChild(notification);
        
        setTimeout(() => notification.classList.add('show'), 100);
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Inicializar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    new MemorialEnhancements();
});

// Exportar para uso global
window.MemorialEnhancements = MemorialEnhancements;

