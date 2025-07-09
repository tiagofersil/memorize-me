import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class CloudinaryService:
    def __init__(self):
        """Inicializa o serviço Cloudinary com as credenciais do .env"""
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET')
        )
        
        # Verificar se as credenciais foram carregadas
        if not all([os.getenv('CLOUDINARY_CLOUD_NAME'), os.getenv('CLOUDINARY_API_KEY'), os.getenv('CLOUDINARY_API_SECRET')]):
            raise ValueError("Credenciais do Cloudinary não encontradas no arquivo .env")
    
    def upload_image(self, file_path_or_file, folder="memorial_photos", 
                    public_id=None, transformation=None):
        """
        Faz upload de uma imagem para o Cloudinary
        
        Args:
            file_path_or_file: Caminho do arquivo ou objeto de arquivo
            folder: Pasta no Cloudinary onde a imagem será armazenada
            public_id: ID público personalizado (opcional)
            transformation: Transformações a serem aplicadas (opcional)
        
        Returns:
            dict: Resposta do Cloudinary com URL e public_id
        """
        try:
            upload_options = {
                'folder': folder,
                'resource_type': 'image',
                'quality': 'auto',
                'fetch_format': 'auto'
            }
            
            if public_id:
                upload_options['public_id'] = public_id
            
            if transformation:
                upload_options['transformation'] = transformation
            
            result = cloudinary.uploader.upload(file_path_or_file, **upload_options)
            
            return {
                'success': True,
                'url': result['secure_url'],
                'public_id': result['public_id'],
                'width': result.get('width'),
                'height': result.get('height'),
                'format': result.get('format'),
                'bytes': result.get('bytes')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_image(self, public_id):
        """
        Deleta uma imagem do Cloudinary
        
        Args:
            public_id: ID público da imagem no Cloudinary
        
        Returns:
            dict: Resultado da operação
        """
        try:
            result = cloudinary.uploader.destroy(public_id)
            return {
                'success': result.get('result') == 'ok',
                'result': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_image_url(self, public_id, transformation=None):
        """
        Gera URL de uma imagem com transformações opcionais
        
        Args:
            public_id: ID público da imagem
            transformation: Transformações a serem aplicadas
        
        Returns:
            str: URL da imagem
        """
        try:
            if transformation:
                return cloudinary.CloudinaryImage(public_id).build_url(transformation=transformation)
            else:
                return cloudinary.CloudinaryImage(public_id).build_url()
        except Exception as e:
            return None
    
    def get_optimized_url(self, public_id, width=None, height=None, crop="fill", quality="auto"):
        """
        Gera URL otimizada para uma imagem
        
        Args:
            public_id: ID público da imagem
            width: Largura desejada
            height: Altura desejada
            crop: Modo de recorte
            quality: Qualidade da imagem
        
        Returns:
            str: URL otimizada da imagem
        """
        transformation = {
            'quality': quality,
            'fetch_format': 'auto'
        }
        
        if width:
            transformation['width'] = width
        if height:
            transformation['height'] = height
        if width or height:
            transformation['crop'] = crop
        
        return self.get_image_url(public_id, transformation)
    
    def upload_multiple_images(self, files, folder="memorial_photos"):
        """
        Faz upload de múltiplas imagens
        
        Args:
            files: Lista de arquivos ou caminhos
            folder: Pasta no Cloudinary
        
        Returns:
            list: Lista com resultados de cada upload
        """
        results = []
        for file in files:
            result = self.upload_image(file, folder)
            results.append(result)
        return results
    
    def create_thumbnail(self, public_id, width=300, height=300):
        """
        Cria uma miniatura de uma imagem
        
        Args:
            public_id: ID público da imagem original
            width: Largura da miniatura
            height: Altura da miniatura
        
        Returns:
            str: URL da miniatura
        """
        return self.get_optimized_url(public_id, width, height, crop="thumb")
    
    def validate_image_file(self, file):
        """
        Valida se o arquivo é uma imagem válida
        
        Args:
            file: Objeto de arquivo
        
        Returns:
            dict: Resultado da validação
        """
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
        max_size = 10 * 1024 * 1024  # 10MB
        
        # Verificar extensão
        if file.filename:
            extension = file.filename.rsplit('.', 1)[1].lower()
            if extension not in allowed_extensions:
                return {
                    'valid': False,
                    'error': f'Tipo de arquivo não permitido. Use: {", ".join(allowed_extensions)}'
                }
        
        # Verificar tamanho (se possível)
        try:
            file.seek(0, 2)  # Ir para o final do arquivo
            size = file.tell()
            file.seek(0)  # Voltar para o início
            
            if size > max_size:
                return {
                    'valid': False,
                    'error': f'Arquivo muito grande. Tamanho máximo: {max_size // (1024*1024)}MB'
                }
        except:
            pass  # Se não conseguir verificar o tamanho, continua
        
        return {'valid': True}
    
    def get_folder_images(self, folder="memorial_photos", max_results=100):
        """
        Lista imagens de uma pasta específica
        
        Args:
            folder: Nome da pasta
            max_results: Número máximo de resultados
        
        Returns:
            list: Lista de imagens na pasta
        """
        try:
            result = cloudinary.api.resources(
                type="upload",
                prefix=folder,
                max_results=max_results
            )
            return {
                'success': True,
                'images': result.get('resources', [])
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

