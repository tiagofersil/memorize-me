/**
 * Sistema de Formatação Automática da Biografia
 * Converte texto simples em HTML formatado com suporte a markdown básico
 */

class BiographyFormatter {
    constructor() {
        this.init();
    }

    init() {
        // Aplicar formatação na página de visualização
        this.formatBiographyDisplay();
        
        // Inicializar editor WYSIWYG na página de edição
        this.initWYSIWYGEditor();
        
        // Inicializar salvamento automático
        this.initAutoSave();
    }

    /**
     * Formatar biografia para exibição na página pública
     */
    formatBiographyDisplay() {
        const biographySection = document.querySelector('.biography-section p');
        if (biographySection && biographySection.textContent.trim()) {
            const rawText = biographySection.textContent;
            const formattedHTML = this.formatText(rawText);
            
            // Substituir o parágrafo simples por div formatada
            const formattedDiv = document.createElement('div');
            formattedDiv.className = 'biography-formatted';
            formattedDiv.innerHTML = formattedHTML;
            
            biographySection.parentNode.replaceChild(formattedDiv, biographySection);
        }
    }

    /**
     * Converter texto simples em HTML formatado
     */
    formatText(text) {
        if (!text || text.trim() === '') return '<p>Nenhuma biografia disponível.</p>';
        
        let formatted = text.trim();
        
        // Converter quebras de linha duplas em parágrafos
        formatted = formatted.replace(/\n\s*\n/g, '</p><p>');
        
        // Converter quebras de linha simples em <br> dentro de parágrafos
        formatted = formatted.replace(/\n/g, '<br>');
        
        // Adicionar tags de parágrafo no início e fim
        formatted = '<p>' + formatted + '</p>';
        
        // Converter markdown básico
        // Negrito: **texto** ou *texto*
        formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        formatted = formatted.replace(/\*([^*]+)\*/g, '<strong>$1</strong>');
        
        // Itálico: _texto_
        formatted = formatted.replace(/_([^_]+)_/g, '<em>$1</em>');
        
        // Títulos: ### Título
        formatted = formatted.replace(/^### (.+)$/gm, '<h3>$1</h3>');
        formatted = formatted.replace(/^## (.+)$/gm, '<h3>$1</h3>');
        
        // Citações: > texto
        formatted = formatted.replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>');
        
        // Listas simples: - item
        formatted = this.formatLists(formatted);
        
        // Limpar parágrafos vazios
        formatted = formatted.replace(/<p>\s*<\/p>/g, '');
        
        return formatted;
    }

    /**
     * Formatar listas
     */
    formatLists(text) {
        // Lista não ordenada
        const unorderedListRegex = /^- (.+)$/gm;
        let matches = text.match(unorderedListRegex);
        
        if (matches) {
            let listItems = matches.map(match => match.replace(/^- /, '<li>') + '</li>').join('');
            text = text.replace(unorderedListRegex, '');
            text += '<ul>' + listItems + '</ul>';
        }
        
        return text;
    }

    /**
     * Inicializar editor WYSIWYG
     */
    initWYSIWYGEditor() {
        const biographyTextarea = document.getElementById('biography');
        if (!biographyTextarea) return;

        // Criar estrutura do editor
        const editorContainer = this.createEditorStructure();
        biographyTextarea.parentNode.insertBefore(editorContainer, biographyTextarea);
        biographyTextarea.style.display = 'none';

        // Configurar editor
        const editorContent = editorContainer.querySelector('.editor-content');
        const toolbar = editorContainer.querySelector('.editor-toolbar');

        // Carregar conteúdo inicial
        if (biographyTextarea.value) {
            editorContent.innerHTML = this.formatText(biographyTextarea.value);
        }

        // Configurar botões da toolbar
        this.setupToolbarButtons(toolbar, editorContent);

        // Sincronizar conteúdo
        this.syncEditorContent(editorContent, biographyTextarea);
    }

    /**
     * Criar estrutura HTML do editor
     */
    createEditorStructure() {
        const container = document.createElement('div');
        container.className = 'biography-editor';
        container.innerHTML = `
            <div class="editor-toolbar">
                <button type="button" class="editor-btn" data-command="bold" title="Negrito">
                    <i class="fas fa-bold"></i>
                </button>
                <button type="button" class="editor-btn" data-command="italic" title="Itálico">
                    <i class="fas fa-italic"></i>
                </button>
                <button type="button" class="editor-btn" data-command="insertUnorderedList" title="Lista">
                    <i class="fas fa-list-ul"></i>
                </button>
                <button type="button" class="editor-btn" data-command="insertOrderedList" title="Lista Numerada">
                    <i class="fas fa-list-ol"></i>
                </button>
                <button type="button" class="editor-btn" data-command="formatBlock" data-value="h3" title="Título">
                    <i class="fas fa-heading"></i>
                </button>
                <button type="button" class="editor-btn" data-command="formatBlock" data-value="blockquote" title="Citação">
                    <i class="fas fa-quote-left"></i>
                </button>
            </div>
            <div class="editor-content" contenteditable="true" placeholder="Conte a história de vida, conquistas, momentos especiais e o que tornava essa pessoa única..."></div>
        `;
        return container;
    }

    /**
     * Configurar botões da toolbar
     */
    setupToolbarButtons(toolbar, editorContent) {
        toolbar.addEventListener('click', (e) => {
            e.preventDefault();
            const button = e.target.closest('.editor-btn');
            if (!button) return;

            const command = button.dataset.command;
            const value = button.dataset.value || null;

            // Focar no editor
            editorContent.focus();

            // Executar comando
            if (command === 'formatBlock' && value) {
                document.execCommand(command, false, value);
            } else {
                document.execCommand(command, false, value);
            }

            // Atualizar estado dos botões
            this.updateToolbarState(toolbar);
        });

        // Atualizar estado inicial
        editorContent.addEventListener('keyup', () => this.updateToolbarState(toolbar));
        editorContent.addEventListener('mouseup', () => this.updateToolbarState(toolbar));
    }

    /**
     * Atualizar estado visual dos botões da toolbar
     */
    updateToolbarState(toolbar) {
        const buttons = toolbar.querySelectorAll('.editor-btn');
        buttons.forEach(button => {
            const command = button.dataset.command;
            const isActive = document.queryCommandState(command);
            button.classList.toggle('active', isActive);
        });
    }

    /**
     * Sincronizar conteúdo do editor com textarea
     */
    syncEditorContent(editorContent, textarea) {
        const updateTextarea = () => {
            // Converter HTML de volta para texto simples com markdown
            const htmlContent = editorContent.innerHTML;
            const textContent = this.htmlToMarkdown(htmlContent);
            textarea.value = textContent;
            
            // Disparar evento de mudança para salvamento automático
            textarea.dispatchEvent(new Event('input'));
        };

        editorContent.addEventListener('input', updateTextarea);
        editorContent.addEventListener('paste', () => {
            setTimeout(updateTextarea, 100);
        });
    }

    /**
     * Converter HTML de volta para markdown simples
     */
    htmlToMarkdown(html) {
        let text = html;
        
        // Converter tags HTML para markdown
        text = text.replace(/<strong>(.*?)<\/strong>/g, '**$1**');
        text = text.replace(/<em>(.*?)<\/em>/g, '_$1_');
        text = text.replace(/<h3>(.*?)<\/h3>/g, '### $1');
        text = text.replace(/<blockquote>(.*?)<\/blockquote>/g, '> $1');
        
        // Converter listas
        text = text.replace(/<ul><li>(.*?)<\/li><\/ul>/g, '- $1');
        text = text.replace(/<li>(.*?)<\/li>/g, '- $1\n');
        
        // Converter parágrafos e quebras de linha
        text = text.replace(/<\/p><p>/g, '\n\n');
        text = text.replace(/<p>(.*?)<\/p>/g, '$1');
        text = text.replace(/<br\s*\/?>/g, '\n');
        
        // Remover tags HTML restantes
        text = text.replace(/<[^>]*>/g, '');
        
        // Limpar espaços extras
        text = text.replace(/\n\s*\n\s*\n/g, '\n\n');
        text = text.trim();
        
        return text;
    }

    /**
     * Inicializar salvamento automático
     */
    initAutoSave() {
        const form = document.querySelector('.memorial-form');
        if (!form) return;

        let saveTimeout;
        let indicator = this.createSaveIndicator();

        // Monitorar mudanças em todos os campos
        const inputs = form.querySelectorAll('input, textarea, .editor-content');
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                clearTimeout(saveTimeout);
                this.showSaveIndicator(indicator, 'saving', 'Salvando...');
                
                saveTimeout = setTimeout(() => {
                    this.autoSave(form, indicator);
                }, 2000); // Salvar após 2 segundos de inatividade
            });
        });
    }

    /**
     * Criar indicador de salvamento
     */
    createSaveIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'auto-save-indicator';
        document.body.appendChild(indicator);
        return indicator;
    }

    /**
     * Mostrar indicador de salvamento
     */
    showSaveIndicator(indicator, type, message) {
        indicator.textContent = message;
        indicator.className = `auto-save-indicator ${type} show`;
        
        if (type === 'saved' || type === 'error') {
            setTimeout(() => {
                indicator.classList.remove('show');
            }, 3000);
        }
    }

    /**
     * Executar salvamento automático
     */
    async autoSave(form, indicator) {
        try {
            const formData = new FormData(form);
            
            const response = await fetch(form.action || window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Auto-Save': 'true'
                }
            });

            if (response.ok) {
                this.showSaveIndicator(indicator, 'saved', 'Salvo automaticamente');
            } else {
                throw new Error('Erro no salvamento');
            }
        } catch (error) {
            console.error('Erro no salvamento automático:', error);
            this.showSaveIndicator(indicator, 'error', 'Erro ao salvar');
        }
    }
}

// Inicializar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    new BiographyFormatter();
});

// Exportar para uso global
window.BiographyFormatter = BiographyFormatter;

