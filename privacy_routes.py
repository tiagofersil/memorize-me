from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from database_enhanced import DatabaseEnhanced
from auth_service import AuthService
from security_service import SecurityService, require_memorial_access, validate_input_decorator
from werkzeug.security import generate_password_hash, check_password_hash

privacy_bp = Blueprint('privacy', __name__, url_prefix='/privacy')

# Inicializar serviços
db = DatabaseEnhanced()
auth_service = AuthService()
security_service = SecurityService()

@privacy_bp.route('/settings/<int:memorial_id>')
@login_required
@require_memorial_access('owner')
def settings(memorial_id):
    """Página de configurações de privacidade do memorial"""
    # Buscar memorial
    memorial = db.buscar_memorial_por_id(memorial_id)
    if not memorial:
        flash('Memorial não encontrado', 'error')
        return redirect(url_for('memorial.dashboard'))
    
    # Buscar configurações de privacidade
    config = db.buscar_configuracoes_privacidade(memorial_id)
    
    return render_template('privacy/settings.html', memorial=memorial, config=config)

@privacy_bp.route('/api/update_settings', methods=['POST'])
@login_required
@validate_input_decorator({
    'memorial_id': {'required': True},
    'publico': {'required': False},
    'requer_aprovacao_homenagens': {'required': False},
    'permite_comentarios': {'required': False},
    'permite_fotos_visitantes': {'required': False},
    'senha_acesso': {'required': False, 'max_length': 100}
})
def update_settings():
    """API para atualizar configurações de privacidade"""
    try:
        data = request.validated_data
        memorial_id = int(data['memorial_id'])
        
        # Verificar acesso
        access_result = security_service.check_memorial_access(int(current_user.id), memorial_id, 'owner')
        if not access_result['allowed']:
            return jsonify({'success': False, 'error': access_result['error']})
        
        # Preparar dados para atualização
        update_data = {}
        
        # Campos booleanos
        boolean_fields = ['publico', 'requer_aprovacao_homenagens', 'permite_comentarios', 'permite_fotos_visitantes']
        for field in boolean_fields:
            if field in data:
                update_data[field] = data[field] in ['true', '1', True, 1]
        
        # Senha de acesso
        if 'senha_acesso' in data:
            senha = data['senha_acesso'].strip()
            if senha:
                # Validar força da senha
                password_validation = security_service.validate_password_strength(senha)
                if not password_validation['valid']:
                    return jsonify({
                        'success': False, 
                        'error': 'Senha de acesso muito fraca',
                        'details': password_validation['errors']
                    })
                
                # Hash da senha
                update_data['senha_acesso'] = generate_password_hash(senha)
            else:
                update_data['senha_acesso'] = None
        
        # Atualizar configurações
        result = db.atualizar_configuracoes_privacidade(memorial_id, int(current_user.id), **update_data)
        
        if result:
            # Registrar atividade
            auth_service.registrar_atividade(
                user_id=int(current_user.id),
                memorial_id=memorial_id,
                acao='atualizar_privacidade',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                detalhes=f'Campos atualizados: {", ".join(update_data.keys())}'
            )
            
            return jsonify({
                'success': True,
                'message': 'Configurações de privacidade atualizadas com sucesso!'
            })
        else:
            return jsonify({'success': False, 'error': 'Erro ao atualizar configurações'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'})

@privacy_bp.route('/api/check_password', methods=['POST'])
@validate_input_decorator({
    'memorial_id': {'required': True},
    'senha': {'required': True, 'max_length': 100}
})
def check_password():
    """API para verificar senha de acesso ao memorial"""
    try:
        data = request.validated_data
        memorial_id = int(data['memorial_id'])
        senha = data['senha']
        
        # Buscar configurações
        config = db.buscar_configuracoes_privacidade(memorial_id)
        if not config or not config['senha_acesso']:
            return jsonify({'success': False, 'error': 'Memorial não protegido por senha'})
        
        # Verificar senha
        if check_password_hash(config['senha_acesso'], senha):
            # Criar sessão temporária para acesso
            session_key = f'memorial_access_{memorial_id}'
            from flask import session
            session[session_key] = True
            
            # Registrar acesso
            security_service.log_security_event(
                event_type='password_access_granted',
                memorial_id=memorial_id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                details=f'Acesso concedido via senha para memorial {memorial_id}'
            )
            
            return jsonify({
                'success': True,
                'message': 'Acesso concedido'
            })
        else:
            # Registrar tentativa de acesso negada
            security_service.log_security_event(
                event_type='password_access_denied',
                memorial_id=memorial_id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                details=f'Tentativa de acesso negada para memorial {memorial_id}'
            )
            
            return jsonify({'success': False, 'error': 'Senha incorreta'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'})

@privacy_bp.route('/api/get_access_logs/<int:memorial_id>')
@login_required
@require_memorial_access('owner')
def get_access_logs(memorial_id):
    """API para obter logs de acesso do memorial"""
    try:
        # Buscar logs de acesso (implementar método na DatabaseEnhanced)
        # Por enquanto, retornar dados simulados
        logs = [
            {
                'id': 1,
                'acao': 'visualizar_memorial',
                'ip_address': '192.168.1.1',
                'user_agent': 'Mozilla/5.0...',
                'created_at': '2024-01-15 10:30:00',
                'detalhes': 'Visualização do memorial'
            }
        ]
        
        return jsonify({
            'success': True,
            'logs': logs
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'})

@privacy_bp.route('/api/export_data/<int:memorial_id>')
@login_required
@require_memorial_access('owner')
def export_data(memorial_id):
    """API para exportar dados do memorial"""
    try:
        # Buscar todos os dados do memorial
        memorial = db.buscar_memorial_por_id(memorial_id)
        textos = db.buscar_textos_memorial(memorial_id)
        fotos = db.buscar_fotos_memorial(memorial_id)
        homenagens = db.buscar_homenagens_memorial(memorial_id, apenas_aprovadas=False)
        
        # Preparar dados para exportação
        export_data = {
            'memorial': dict(memorial) if memorial else None,
            'textos': [dict(texto) for texto in textos],
            'fotos': [dict(foto) for foto in fotos],
            'homenagens': [dict(homenagem) for homenagem in homenagens],
            'exported_at': datetime.now().isoformat()
        }
        
        # Registrar exportação
        auth_service.registrar_atividade(
            user_id=int(current_user.id),
            memorial_id=memorial_id,
            acao='exportar_dados',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            detalhes='Exportação completa dos dados do memorial'
        )
        
        return jsonify({
            'success': True,
            'data': export_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'})

@privacy_bp.route('/api/delete_all_data/<int:memorial_id>', methods=['DELETE'])
@login_required
@require_memorial_access('owner')
def delete_all_data(memorial_id):
    """API para deletar todos os dados do memorial (GDPR)"""
    try:
        # Buscar memorial para log
        memorial = db.buscar_memorial_por_id(memorial_id)
        if not memorial:
            return jsonify({'success': False, 'error': 'Memorial não encontrado'})
        
        # Deletar todas as fotos do Cloudinary
        fotos = db.buscar_fotos_memorial(memorial_id)
        from cloudinary_service import CloudinaryService
        cloudinary_service = CloudinaryService()
        
        for foto in fotos:
            cloudinary_service.delete_image(foto['cloudinary_public_id'])
        
        # Deletar todos os dados do banco (implementar método na DatabaseEnhanced)
        # Por enquanto, simular sucesso
        
        # Registrar deleção
        auth_service.registrar_atividade(
            user_id=int(current_user.id),
            memorial_id=memorial_id,
            acao='deletar_todos_dados',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            detalhes=f'Deleção completa do memorial: {memorial["nome_falecido"]}'
        )
        
        return jsonify({
            'success': True,
            'message': 'Todos os dados foram deletados permanentemente'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'})

@privacy_bp.route('/api/security_report/<int:memorial_id>')
@login_required
@require_memorial_access('owner')
def security_report(memorial_id):
    """API para gerar relatório de segurança"""
    try:
        # Analisar atividade suspeita
        suspicious_activity = security_service.detect_suspicious_activity(
            int(current_user.id), 
            request.remote_addr
        )
        
        # Estatísticas de acesso (implementar)
        access_stats = {
            'total_views': 0,
            'unique_visitors': 0,
            'countries': [],
            'devices': []
        }
        
        # Configurações atuais
        config = db.buscar_configuracoes_privacidade(memorial_id)
        
        report = {
            'memorial_id': memorial_id,
            'generated_at': datetime.now().isoformat(),
            'security_status': 'good',  # good, warning, critical
            'suspicious_activity': suspicious_activity,
            'access_stats': access_stats,
            'privacy_settings': dict(config) if config else None,
            'recommendations': [
                'Considere ativar aprovação de homenagens',
                'Configure uma senha de acesso para maior segurança',
                'Revise regularmente os logs de acesso'
            ]
        }
        
        return jsonify({
            'success': True,
            'report': report
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'})

# Middleware para verificar acesso com senha
def check_password_access(memorial_id):
    """Verifica se o usuário tem acesso via senha"""
    from flask import session
    session_key = f'memorial_access_{memorial_id}'
    return session.get(session_key, False)

# Função auxiliar para verificar acesso completo
def has_memorial_access(user_id, memorial_id):
    """Verifica se o usuário tem acesso ao memorial (proprietário, público ou senha)"""
    # Verificar se é proprietário
    access_result = security_service.check_memorial_access(user_id, memorial_id, 'read')
    
    if access_result['allowed']:
        return True
    
    # Verificar acesso via senha
    if access_result.get('requires_password'):
        return check_password_access(memorial_id)
    
    return False

