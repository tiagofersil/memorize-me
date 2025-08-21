import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Image,
  Alert,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';

export default function CreateMemorialScreen({ navigation, route }) {
  const memorial = route?.params?.memorial;
  const isEditing = !!memorial;

  const [formData, setFormData] = useState({
    name: memorial?.name || '',
    birthDate: memorial?.birthDate || '',
    deathDate: memorial?.deathDate || '',
    biography: memorial?.biography || '',
    familyMessage: memorial?.familyMessage || '',
    profilePhoto: memorial?.profilePhoto || null,
    coverPhoto: memorial?.coverPhoto || null,
    photos: memorial?.photos || [],
  });

  const [loading, setLoading] = useState(false);

  const updateField = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const pickImage = async (type) => {
    try {
      const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
      
      if (permissionResult.granted === false) {
        Alert.alert('Permissão necessária', 'É necessário permitir acesso à galeria de fotos');
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: type === 'profile' ? [1, 1] : [16, 9],
        quality: 0.8,
      });

      if (!result.canceled) {
        updateField(type === 'profile' ? 'profilePhoto' : 'coverPhoto', result.assets[0].uri);
      }
    } catch (error) {
      Alert.alert('Erro', 'Não foi possível selecionar a imagem');
    }
  };

  const addGalleryPhoto = async () => {
    try {
      const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
      
      if (permissionResult.granted === false) {
        Alert.alert('Permissão necessária', 'É necessário permitir acesso à galeria de fotos');
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsMultipleSelection: true,
        quality: 0.8,
      });

      if (!result.canceled) {
        const newPhotos = result.assets.map(asset => ({
          id: Date.now() + Math.random(),
          uri: asset.uri,
          title: '',
          description: '',
        }));
        
        updateField('photos', [...formData.photos, ...newPhotos]);
      }
    } catch (error) {
      Alert.alert('Erro', 'Não foi possível selecionar as imagens');
    }
  };

  const removePhoto = (photoId) => {
    updateField('photos', formData.photos.filter(photo => photo.id !== photoId));
  };

  const saveMemorial = async () => {
    if (!formData.name.trim()) {
      Alert.alert('Erro', 'Nome é obrigatório');
      return;
    }

    if (!formData.biography.trim()) {
      Alert.alert('Erro', 'Biografia é obrigatória');
      return;
    }

    setLoading(true);

    try {
      // Simular salvamento na API
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      Alert.alert(
        'Sucesso',
        `Memorial ${isEditing ? 'atualizado' : 'criado'} com sucesso!`,
        [
          {
            text: 'OK',
            onPress: () => navigation.goBack(),
          },
        ]
      );
    } catch (error) {
      Alert.alert('Erro', 'Não foi possível salvar o memorial');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>
            {isEditing ? 'Editar Memorial' : 'Criar Memorial'}
          </Text>
          <Text style={styles.subtitle}>
            Preencha as informações para criar um memorial especial
          </Text>
        </View>

        {/* Informações Básicas */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>
            <Ionicons name="person" size={20} color="#4fd1c7" /> Informações Básicas
          </Text>
          
          <View style={styles.formGroup}>
            <Text style={styles.label}>Nome Completo *</Text>
            <TextInput
              style={styles.input}
              value={formData.name}
              onChangeText={(text) => updateField('name', text)}
              placeholder="Nome da pessoa"
              placeholderTextColor="#a0aec0"
            />
          </View>

          <View style={styles.formRow}>
            <View style={[styles.formGroup, { flex: 1, marginRight: 10 }]}>
              <Text style={styles.label}>Data de Nascimento</Text>
              <TextInput
                style={styles.input}
                value={formData.birthDate}
                onChangeText={(text) => updateField('birthDate', text)}
                placeholder="DD/MM/AAAA"
                placeholderTextColor="#a0aec0"
              />
            </View>
            <View style={[styles.formGroup, { flex: 1, marginLeft: 10 }]}>
              <Text style={styles.label}>Data de Falecimento</Text>
              <TextInput
                style={styles.input}
                value={formData.deathDate}
                onChangeText={(text) => updateField('deathDate', text)}
                placeholder="DD/MM/AAAA"
                placeholderTextColor="#a0aec0"
              />
            </View>
          </View>
        </View>

        {/* Fotos */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>
            <Ionicons name="camera" size={20} color="#4fd1c7" /> Fotos
          </Text>

          {/* Foto de Perfil */}
          <View style={styles.photoSection}>
            <Text style={styles.photoLabel}>Foto de Perfil</Text>
            <TouchableOpacity
              style={styles.photoUpload}
              onPress={() => pickImage('profile')}
            >
              {formData.profilePhoto ? (
                <Image source={{ uri: formData.profilePhoto }} style={styles.profilePreview} />
              ) : (
                <View style={styles.photoPlaceholder}>
                  <Ionicons name="person" size={40} color="#a0aec0" />
                  <Text style={styles.photoPlaceholderText}>Adicionar Foto</Text>
                </View>
              )}
            </TouchableOpacity>
          </View>

          {/* Foto de Capa */}
          <View style={styles.photoSection}>
            <Text style={styles.photoLabel}>Foto de Capa</Text>
            <TouchableOpacity
              style={styles.coverUpload}
              onPress={() => pickImage('cover')}
            >
              {formData.coverPhoto ? (
                <Image source={{ uri: formData.coverPhoto }} style={styles.coverPreview} />
              ) : (
                <View style={styles.coverPlaceholder}>
                  <Ionicons name="image" size={40} color="#a0aec0" />
                  <Text style={styles.photoPlaceholderText}>Adicionar Capa</Text>
                </View>
              )}
            </TouchableOpacity>
          </View>

          {/* Galeria */}
          <View style={styles.photoSection}>
            <View style={styles.galleryHeader}>
              <Text style={styles.photoLabel}>Galeria de Fotos</Text>
              <TouchableOpacity
                style={styles.addPhotoButton}
                onPress={addGalleryPhoto}
              >
                <Ionicons name="add" size={20} color="#4fd1c7" />
                <Text style={styles.addPhotoText}>Adicionar</Text>
              </TouchableOpacity>
            </View>
            
            {formData.photos.length > 0 ? (
              <View style={styles.galleryGrid}>
                {formData.photos.map((photo) => (
                  <View key={photo.id} style={styles.galleryItem}>
                    <Image source={{ uri: photo.uri }} style={styles.galleryImage} />
                    <TouchableOpacity
                      style={styles.removePhotoButton}
                      onPress={() => removePhoto(photo.id)}
                    >
                      <Ionicons name="close" size={16} color="#fff" />
                    </TouchableOpacity>
                  </View>
                ))}
              </View>
            ) : (
              <View style={styles.emptyGallery}>
                <Ionicons name="images-outline" size={40} color="#a0aec0" />
                <Text style={styles.emptyGalleryText}>Nenhuma foto adicionada</Text>
              </View>
            )}
          </View>
        </View>

        {/* Biografia */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>
            <Ionicons name="book" size={20} color="#4fd1c7" /> História de Vida
          </Text>
          
          <View style={styles.formGroup}>
            <Text style={styles.label}>Biografia *</Text>
            <TextInput
              style={[styles.input, styles.textArea]}
              value={formData.biography}
              onChangeText={(text) => updateField('biography', text)}
              placeholder="Conte a história de vida, conquistas e momentos especiais..."
              placeholderTextColor="#a0aec0"
              multiline
              numberOfLines={6}
              textAlignVertical="top"
            />
          </View>
        </View>

        {/* Mensagem da Família */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>
            <Ionicons name="heart" size={20} color="#4fd1c7" /> Mensagem da Família
          </Text>
          
          <View style={styles.formGroup}>
            <Text style={styles.label}>Mensagem Especial</Text>
            <TextInput
              style={[styles.input, styles.textArea]}
              value={formData.familyMessage}
              onChangeText={(text) => updateField('familyMessage', text)}
              placeholder="Uma mensagem especial da família..."
              placeholderTextColor="#a0aec0"
              multiline
              numberOfLines={4}
              textAlignVertical="top"
            />
          </View>
        </View>

        {/* Botões de Ação */}
        <View style={styles.actions}>
          <TouchableOpacity
            style={[styles.button, styles.saveButton]}
            onPress={saveMemorial}
            disabled={loading}
          >
            <Ionicons name="save" size={20} color="#fff" />
            <Text style={styles.buttonText}>
              {loading ? 'Salvando...' : (isEditing ? 'Atualizar' : 'Criar Memorial')}
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.button, styles.cancelButton]}
            onPress={() => navigation.goBack()}
          >
            <Ionicons name="close" size={20} color="#718096" />
            <Text style={styles.cancelButtonText}>Cancelar</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f7fafc',
  },
  content: {
    padding: 20,
    paddingBottom: 40,
  },
  header: {
    marginBottom: 30,
    alignItems: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2d3748',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#718096',
    textAlign: 'center',
    lineHeight: 22,
  },
  section: {
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2d3748',
    marginBottom: 20,
    flexDirection: 'row',
    alignItems: 'center',
  },
  formGroup: {
    marginBottom: 20,
  },
  formRow: {
    flexDirection: 'row',
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#4a5568',
    marginBottom: 8,
  },
  input: {
    borderWidth: 2,
    borderColor: '#e2e8f0',
    borderRadius: 10,
    padding: 15,
    fontSize: 16,
    color: '#2d3748',
    backgroundColor: '#fff',
  },
  textArea: {
    height: 120,
    textAlignVertical: 'top',
  },
  photoSection: {
    marginBottom: 25,
  },
  photoLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#4a5568',
    marginBottom: 10,
  },
  photoUpload: {
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: '#e2e8f0',
    borderStyle: 'dashed',
    borderRadius: 15,
    padding: 20,
    backgroundColor: '#f7fafc',
  },
  coverUpload: {
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: '#e2e8f0',
    borderStyle: 'dashed',
    borderRadius: 15,
    padding: 20,
    backgroundColor: '#f7fafc',
    height: 120,
  },
  photoPlaceholder: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  coverPlaceholder: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  photoPlaceholderText: {
    fontSize: 14,
    color: '#a0aec0',
    marginTop: 10,
  },
  profilePreview: {
    width: 120,
    height: 120,
    borderRadius: 60,
  },
  coverPreview: {
    width: '100%',
    height: 100,
    borderRadius: 10,
  },
  galleryHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  addPhotoButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#e6fffa',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    gap: 5,
  },
  addPhotoText: {
    color: '#4fd1c7',
    fontSize: 14,
    fontWeight: '600',
  },
  galleryGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  galleryItem: {
    position: 'relative',
    width: (width - 80) / 3,
    height: (width - 80) / 3,
    borderRadius: 10,
    overflow: 'hidden',
  },
  galleryImage: {
    width: '100%',
    height: '100%',
  },
  removePhotoButton: {
    position: 'absolute',
    top: 5,
    right: 5,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    borderRadius: 12,
    width: 24,
    height: 24,
    alignItems: 'center',
    justifyContent: 'center',
  },
  emptyGallery: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 40,
    backgroundColor: '#f7fafc',
    borderRadius: 10,
    borderWidth: 2,
    borderColor: '#e2e8f0',
    borderStyle: 'dashed',
  },
  emptyGalleryText: {
    fontSize: 14,
    color: '#a0aec0',
    marginTop: 10,
  },
  actions: {
    gap: 15,
    marginTop: 20,
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 15,
    borderRadius: 12,
    gap: 10,
  },
  saveButton: {
    backgroundColor: '#4fd1c7',
  },
  cancelButton: {
    backgroundColor: '#f7fafc',
    borderWidth: 2,
    borderColor: '#e2e8f0',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  cancelButtonText: {
    color: '#718096',
    fontSize: 16,
    fontWeight: '600',
  },
});

const { width } = require('react-native').Dimensions.get('window');