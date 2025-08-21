import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  Dimensions,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');

export default function HomeScreen({ navigation }) {
  const features = [
    {
      icon: 'heart',
      title: 'Criar Memorial',
      description: 'Crie memoriais únicos e especiais',
      color: '#ff6b6b',
    },
    {
      icon: 'images',
      title: 'Galeria de Fotos',
      description: 'Adicione fotos e memórias',
      color: '#4ecdc4',
    },
    {
      icon: 'qr-code',
      title: 'QR Code',
      description: 'Compartilhe facilmente',
      color: '#45b7d1',
    },
    {
      icon: 'people',
      title: 'Homenagens',
      description: 'Receba mensagens especiais',
      color: '#f9ca24',
    },
  ];

  const recentMemorials = [
    {
      id: 1,
      name: 'Maria Silva',
      date: '2024-01-15',
      image: 'https://images.pexels.com/photos/415829/pexels-photo-415829.jpeg?auto=compress&cs=tinysrgb&w=150',
    },
    {
      id: 2,
      name: 'João Santos',
      date: '2024-01-10',
      image: 'https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&cs=tinysrgb&w=150',
    },
  ];

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Hero Section */}
      <LinearGradient
        colors={['#4fd1c7', '#38b2ac']}
        style={styles.heroSection}
      >
        <View style={styles.heroContent}>
          <Text style={styles.heroTitle}>Memorial Digital</Text>
          <Text style={styles.heroSubtitle}>
            Preserve memórias preciosas para sempre
          </Text>
          <TouchableOpacity
            style={styles.ctaButton}
            onPress={() => navigation.navigate('Memoriais', { screen: 'CreateMemorial' })}
          >
            <Ionicons name="add-circle" size={24} color="#4fd1c7" />
            <Text style={styles.ctaButtonText}>Criar Memorial</Text>
          </TouchableOpacity>
        </View>
      </LinearGradient>

      {/* Features Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Funcionalidades</Text>
        <View style={styles.featuresGrid}>
          {features.map((feature, index) => (
            <TouchableOpacity key={index} style={styles.featureCard}>
              <View style={[styles.featureIcon, { backgroundColor: feature.color }]}>
                <Ionicons name={feature.icon} size={24} color="#fff" />
              </View>
              <Text style={styles.featureTitle}>{feature.title}</Text>
              <Text style={styles.featureDescription}>{feature.description}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Recent Memorials */}
      {recentMemorials.length > 0 && (
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Memoriais Recentes</Text>
            <TouchableOpacity onPress={() => navigation.navigate('Memoriais')}>
              <Text style={styles.seeAllText}>Ver todos</Text>
            </TouchableOpacity>
          </View>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            {recentMemorials.map((memorial) => (
              <TouchableOpacity
                key={memorial.id}
                style={styles.memorialCard}
                onPress={() => navigation.navigate('Memoriais', { 
                  screen: 'ViewMemorial', 
                  params: { memorialId: memorial.id } 
                })}
              >
                <Image source={{ uri: memorial.image }} style={styles.memorialImage} />
                <View style={styles.memorialInfo}>
                  <Text style={styles.memorialName}>{memorial.name}</Text>
                  <Text style={styles.memorialDate}>{memorial.date}</Text>
                </View>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>
      )}

      {/* Statistics */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Estatísticas</Text>
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>2</Text>
            <Text style={styles.statLabel}>Memoriais</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>15</Text>
            <Text style={styles.statLabel}>Fotos</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>8</Text>
            <Text style={styles.statLabel}>Homenagens</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>42</Text>
            <Text style={styles.statLabel}>Visitas</Text>
          </View>
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
  heroSection: {
    padding: 30,
    borderBottomLeftRadius: 25,
    borderBottomRightRadius: 25,
    marginBottom: 20,
  },
  heroContent: {
    alignItems: 'center',
    paddingTop: 20,
  },
  heroTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 10,
    textAlign: 'center',
  },
  heroSubtitle: {
    fontSize: 16,
    color: '#fff',
    opacity: 0.9,
    textAlign: 'center',
    marginBottom: 30,
    lineHeight: 24,
  },
  ctaButton: {
    backgroundColor: '#fff',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 25,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  ctaButtonText: {
    color: '#4fd1c7',
    fontSize: 16,
    fontWeight: '600',
  },
  section: {
    padding: 20,
    marginBottom: 10,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2d3748',
    marginBottom: 15,
  },
  seeAllText: {
    color: '#4fd1c7',
    fontSize: 16,
    fontWeight: '600',
  },
  featuresGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  featureCard: {
    backgroundColor: '#fff',
    width: (width - 60) / 2,
    padding: 20,
    borderRadius: 15,
    alignItems: 'center',
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  featureIcon: {
    width: 50,
    height: 50,
    borderRadius: 25,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 15,
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2d3748',
    marginBottom: 5,
    textAlign: 'center',
  },
  featureDescription: {
    fontSize: 12,
    color: '#718096',
    textAlign: 'center',
    lineHeight: 18,
  },
  memorialCard: {
    backgroundColor: '#fff',
    width: 200,
    marginRight: 15,
    borderRadius: 15,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  memorialImage: {
    width: '100%',
    height: 120,
  },
  memorialInfo: {
    padding: 15,
  },
  memorialName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2d3748',
    marginBottom: 5,
  },
  memorialDate: {
    fontSize: 12,
    color: '#718096',
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  statCard: {
    backgroundColor: '#fff',
    flex: 1,
    marginHorizontal: 5,
    padding: 20,
    borderRadius: 15,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#4fd1c7',
    marginBottom: 5,
  },
  statLabel: {
    fontSize: 12,
    color: '#718096',
    textAlign: 'center',
  },
});