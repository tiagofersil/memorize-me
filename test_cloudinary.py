#!/usr/bin/env python3
"""
Script de teste para verificar se o Cloudinary está funcionando corretamente
"""

from dotenv import load_dotenv
import os
import cloudinary
import cloudinary.uploader
from PIL import Image
import io

# Carregar variáveis de ambiente
load_dotenv()

# Configurar Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

def test_cloudinary_config():
    """Testa se a configuração do Cloudinary está correta"""
    print("=== Teste de Configuração do Cloudinary ===")
    
    # Verificar se as variáveis de ambiente estão carregadas
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY')
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
    
    print(f"CLOUDINARY_CLOUD_NAME: {cloud_name}")
    print(f"CLOUDINARY_API_KEY: {api_key}")
    print(f"CLOUDINARY_API_SECRET: {'*' * len(api_secret) if api_secret else None}")
    
    if not all([cloud_name, api_key, api_secret]):
        print("❌ ERRO: Credenciais do Cloudinary não encontradas!")
        return False
    
    # Verificar se a configuração foi aplicada
    config = cloudinary.config()
    print(f"Configuração aplicada: {config}")
    
    return True

def create_test_image():
    """Cria uma imagem de teste"""
    # Criar uma imagem simples de teste
    img = Image.new('RGB', (100, 100), color='red')
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    return img_buffer

def test_cloudinary_upload():
    """Testa o upload para o Cloudinary"""
    print("=== Teste de Upload ===")
    
    try:
        # Criar imagem de teste
        test_image = create_test_image()
        
        # Fazer upload
        result = cloudinary.uploader.upload(
            test_image,
            folder="test_uploads",
            public_id="test_image_" + str(int(os.time.time()) if hasattr(os, 'time') else 123456)
        )
        
        print("✅ Upload realizado com sucesso!")
        print(f"URL: {result['secure_url']}")
        print(f"Public ID: {result['public_id']}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ ERRO no upload: {str(e)}")
        return False, None

def main():
    """Função principal"""
    print("Iniciando testes do Cloudinary...")
    
    # Teste 1: Configuração
    if not test_cloudinary_config():
        return
    
    # Teste 2: Upload
    success, result = test_cloudinary_upload()
    
    if success:
        print("✅ Todos os testes passaram! O Cloudinary está funcionando corretamente.")
    else:
        print("❌ Falha nos testes. Verifique a configuração.")

if __name__ == "__main__":
    main()

