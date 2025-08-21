import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Image,
  TouchableOpacity,
  Dimensions,
  Share,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import QRCode from 'react-native-qrcode-svg';

const { width, height } = Dimensions.get('window');

export default function ViewMemorialScreen({ route, navigation }) {
  const { memorial } = route.params;
  const [activePhotoIndex, setActivePhotoIndex] = useState(0);
  const scrollViewRef = useRef(null);

  const shareMemorial = async () => {
    try {
      const result = await Share.share({
        message: `Visite o memorial de ${memorial.name} - Memorial Digital`,
        url: `https://memorial-digital.com/memorial/${memorial.id}`,
        title: `Memorial de ${memorial.name}`,
      });
    } catch (error) {
      Alert.alert('Erro', 'Não foi possível compartilhar o memorial');
    }
  };

  const addTribute = () => {
    Alert.alert(
      'Adicionar Homenagem',
      'Escolha o tipo de homenagem:',
      [
        { text: 'Cancelar', style: 'cancel' },
        { text: 'Acender Vela', onPress: () => addVirtualTribute('candle') },
        { text: 'Deixar Flor', onPress: () => addVirtualTribute('flower') },
      ]
    );
  };

  const addVirtualTribute = (type) => {
    Alert.prompt(
      `${type === 'candle' ? 'Acender Vela' : 'Deixar Flor'}`,
      'Deixe uma mensagem especial (opcional):',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Confirmar',
          onPress: (message) => {
            Alert.alert('Sucesso', `${type === 'candle' ? 'Vela acesa' : 'Flor deixada'} com sucesso!`);
          },
        },
      ],
      'plain-text'
    );
  };

  const mockPhotos = [
    'https://images.pexels.com/photos/1181690/pexels-photo-1181690.jpeg?auto=compress&cs=tinysrgb&w=400',
    'https://images.pexels.com/photos/1181686/pexels-photo-1181686.jpeg?auto=compress&cs=tinysrgb&w=400',
    'https://images.pexels.com/photos/1181677/pexels-photo-1181677.jpeg?auto=compress&cs=tinysrgb&w=400',
  ];

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Cover Photo and Profile */}
      <View style={styles.coverSection}>
        <Image
          source={{ 
            uri: memorial.coverPhoto || 'https://images.pexels.com/photos/1181690/pexels-photo-1181690.jpeg?auto=compress&cs=tinysrgb&w=800'
          }}
          style={styles.coverImage}
        />
        <LinearGradient
          colors={['transparent', 'rgba(0,0,0,0.7)']}
          style={styles.coverOverlay}
        />
        
        <View style={styles.profileSection}>
          <Image
            source={{ uri: memorial.profilePhoto }}
            style={styles.profileImage}
          />
          <View style={styles.profileInfo}>
            <Text style={styles.memorialName}>{memorial.name}</Text>
            <Text style={styles.memorialDates}>
              {memorial.birthDate} - {memorial.deathDate}
            </Text>
            <Text style={styles.memorialSubtitle}>Em memória de uma vida especial</Text>
          </View>
        </View>

        {/* Action Buttons */}
        <View style={styles.actionButtons}>
          <TouchableOpacity style={styles.actionButton} onPress={shareMemorial}>
            <Ionicons name="share-outline" size={20} color="#4fd1c7" />
            <Text style={styles.actionButtonText}>Compartilhar</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.actionButton} onPress={addTribute}>
            <Ionicons name="heart-outline" size={20} color="#4fd1c7" />
            <Text style={styles.actionButtonText}>Homenagem</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Content Sections */}
      <View style={styles.content}>
        {/* Biography */}
        {memorial.biography && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>
              <Ionicons name="book-outline" size={20} color="#4fd1c7" /> História de Vida
            </Text>
            <Text style={styles.biographyText}>{memorial.biography}</Text>
          </View>
        )}

        {/* Family Message */}
        {memorial.familyMessage && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>
              <Ionicons name="heart-outline" size={20} color="#4fd1c7" /> Mensagem da Família
            </Text>
            <View style={styles.messageCard}>
              <Text style={styles.messageText}>{memorial.familyMessage}</Text>
            </View>
          </View>
        )}

        {/* Photo Gallery */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>
            <Ionicons name="images-outline" size={20} color="#4fd1c7" /> Galeria de Memórias
          </Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            {mockPhotos.map((photo, index) => (
              <TouchableOpacity
                key={index}
                style={styles.galleryPhoto}
                onPress={() => setActivePhotoIndex(index)}
              >
                <Image source={{ uri: photo }} style={styles.galleryPhotoImage} />
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>

        {/* Virtual Tributes */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>
            <Ionicons name="flame-outline" size={20} color="#4fd1c7" /> Homenagens Virtuais
          </Text>
          <View style={styles.tributesContainer}>
            <View style={styles.tributeStats}>
              <View style={styles.tributeStat}>
                <Ionicons name="flame" size={24} color="#ff6b35" />
                <Text style={styles.tributeCount}>3</Text>
                <Text style={styles.tributeLabel}>Velas</Text>
              </View>
              <View style={styles.tributeStat}>
                <Ionicons name="flower" size={24} color="#e91e63" />
                <Text style={styles.tributeCount}>5</Text>
                <Text style={styles.tributeLabel}>Flores</Text>
              </View>
            </View>
            
            <TouchableOpacity style={styles.addTributeButton} onPress={addTribute}>
              <Ionicons name="add" size={20} color="#fff" />
              <Text style={styles.addTributeText}>Deixar Homenagem</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* QR Code */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>
            <Ionicons name="qr-code-outline" size={20} color="#4fd1c7" /> Compartilhar Memorial
          </Text>
          <View style={styles.qrContainer}>
            <View style={styles.qrCodeWrapper}>
              <QRCode
                value={`https://memorial-digital.com/memorial/${memorial.id}`}
                size={120}
                color="#2d3748"
                backgroundColor="#fff"
              />
            </View>
            <View style={styles.qrInfo}>
              <Text style={styles.qrTitle}>QR Code do Memorial</Text>
              <Text style={styles.qrDescription}>
                Escaneie para acessar o memorial facilmente
              </Text>
              <TouchableOpacity style={styles.shareQrButton} onPress={shareMemorial}>
                <Ionicons name="share" size={16} color="#4fd1c7" />
                <Text style={styles.shareQrText}>Compartilhar</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>

        {/* Recent Tributes */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>
            <Ionicons name="chatbubbles-outline" size={20} color="#4fd1c7" /> Homenagens Recentes
          </Text>
          
          {[
            { author: 'Ana Costa', message: 'Saudades eternas de uma pessoa especial', time: '2 horas atrás' },
            { author: 'Carlos Silva', message: 'Sempre será lembrado com carinho', time: '1 dia atrás' },
          ].map((tribute, index) => (
            <View key={index} style={styles.tributeCard}>
              <View style={styles.tributeHeader}>
                <View style={styles.tributeAvatar}>
                  <Text style={styles.tributeAvatarText}>{tribute.author[0]}</Text>
                </View>
                <View style={styles.tributeInfo}>
                  <Text style={styles.tributeAuthor}>{tribute.author}</Text>
                  <Text style={styles.tributeTime}>{tribute.time}</Text>
                </View>
              </View>
              <Text style={styles.tributeMessage}>{tribute.message}</Text>
            </View>
          ))}
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
  coverSection: {
    position: 'relative',
    height: 300,
  },
  coverImage: {
    width: '100%',
    height: '100%',
  },
  coverOverlay: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: 150,
  },
  profileSection: {
    position: 'absolute',
    bottom: 20,
    left: 20,
    right: 20,
    flexDirection: 'row',
    alignItems: 'flex-end',
  },
  profileImage: {
    width: 100,
    height: 100,
    borderRadius: 50,
    borderWidth: 4,
    borderColor: '#fff',
    marginRight: 15,
  },
  profileInfo: {
    flex: 1,
  },
  memorialName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 5,
  },
  memorialDates: {
    fontSize: 16,
    color: '#fff',
    opacity: 0.9,
    marginBottom: 2,
  },
  memorialSubtitle: {
    fontSize: 14,
    color: '#fff',
    opacity: 0.8,
  },
  actionButtons: {
    position: 'absolute',
    top: 20,
    right: 20,
    flexDirection: 'row',
    gap: 10,
  },
  actionButton: {
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    gap: 5,
  },
  actionButtonText: {
    color: '#4fd1c7',
    fontSize: 14,
    fontWeight: '600',
  },
  content: {
    padding: 20,
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
    marginBottom: 15,
    flexDirection: 'row',
    alignItems: 'center',
  },
  biographyText: {
    fontSize: 16,
    color: '#4a5568',
    lineHeight: 24,
  },
  messageCard: {
    backgroundColor: '#e6fffa',
    padding: 20,
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#4fd1c7',
  },
  messageText: {
    fontSize: 16,
    color: '#2d3748',
    fontStyle: 'italic',
    lineHeight: 24,
  },
  galleryPhoto: {
    marginRight: 15,
    borderRadius: 12,
    overflow: 'hidden',
  },
  galleryPhotoImage: {
    width: 150,
    height: 150,
  },
  tributesContainer: {
    alignItems: 'center',
  },
  tributeStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
    marginBottom: 20,
  },
  tributeStat: {
    alignItems: 'center',
    backgroundColor: '#f7fafc',
    padding: 20,
    borderRadius: 15,
    flex: 1,
    marginHorizontal: 5,
  },
  tributeCount: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2d3748',
    marginVertical: 5,
  },
  tributeLabel: {
    fontSize: 12,
    color: '#718096',
  },
  addTributeButton: {
    backgroundColor: '#4fd1c7',
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 25,
    paddingVertical: 15,
    borderRadius: 25,
    gap: 8,
  },
  addTributeText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  qrContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 20,
  },
  qrCodeWrapper: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  qrInfo: {
    flex: 1,
  },
  qrTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2d3748',
    marginBottom: 5,
  },
  qrDescription: {
    fontSize: 14,
    color: '#718096',
    marginBottom: 10,
    lineHeight: 20,
  },
  shareQrButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
  },
  shareQrText: {
    color: '#4fd1c7',
    fontSize: 14,
    fontWeight: '600',
  },
  tributeCard: {
    backgroundColor: '#f7fafc',
    padding: 15,
    borderRadius: 12,
    marginBottom: 15,
    borderLeftWidth: 4,
    borderLeftColor: '#4fd1c7',
  },
  tributeHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  tributeAvatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#4fd1c7',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  tributeAvatarText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  tributeInfo: {
    flex: 1,
  },
  tributeAuthor: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2d3748',
  },
  tributeTime: {
    fontSize: 12,
    color: '#718096',
  },
  tributeMessage: {
    fontSize: 14,
    color: '#4a5568',
    lineHeight: 20,
    fontStyle: 'italic',
  },
});