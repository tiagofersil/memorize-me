import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Image,
  Alert,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function MemorialsScreen({ navigation }) {
  const [memorials, setMemorials] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  // Dados simulados - em produção, viria da API
  const mockMemorials = [
    {
      id: 1,
      name: 'Maria Silva',
      birthDate: '1950-03-15',
      deathDate: '2024-01-15',
      biography: 'Uma pessoa especial que tocou muitas vidas...',
      profilePhoto: 'https://images.pexels.com/photos/415829/pexels-photo-415829.jpeg?auto=compress&cs=tinysrgb&w=150',
      photosCount: 12,
      tributesCount: 5,
      createdAt: '2024-01-16',
    },
    {
      id: 2,
      name: 'João Santos',
      birthDate: '1945-07-22',
      deathDate: '2024-01-10',
      biography: 'Um homem de família dedicado e trabalhador...',
      profilePhoto: 'https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&cs=tinysrgb&w=150',
      photosCount: 8,
      tributesCount: 3,
      createdAt: '2024-01-11',
    },
  ];

  useEffect(() => {
    loadMemorials();
  }, []);

  const loadMemorials = async () => {
    try {
      // Simular carregamento da API
      setRefreshing(true);
      await new Promise(resolve => setTimeout(resolve, 1000));
      setMemorials(mockMemorials);
    } catch (error) {
      Alert.alert('Erro', 'Não foi possível carregar os memoriais');
    } finally {
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    loadMemorials();
  };

  const deleteMemorial = (memorialId, memorialName) => {
    Alert.alert(
      'Confirmar Exclusão',
      `Tem certeza que deseja excluir o memorial de ${memorialName}?`,
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Excluir',
          style: 'destructive',
          onPress: () => {
            setMemorials(prev => prev.filter(m => m.id !== memorialId));
            Alert.alert('Sucesso', 'Memorial excluído com sucesso');
          },
        },
      ]
    );
  };

  const renderMemorialCard = ({ item }) => (
    <TouchableOpacity
      style={styles.memorialCard}
      onPress={() => navigation.navigate('ViewMemorial', { memorial: item })}
    >
      <View style={styles.cardHeader}>
        <Image source={{ uri: item.profilePhoto }} style={styles.profileImage} />
        <View style={styles.memorialInfo}>
          <Text style={styles.memorialName}>{item.name}</Text>
          <Text style={styles.memorialDates}>
            {item.birthDate} - {item.deathDate}
          </Text>
          <Text style={styles.createdDate}>
            Criado em {new Date(item.createdAt).toLocaleDateString('pt-BR')}
          </Text>
        </View>
        <TouchableOpacity
          style={styles.menuButton}
          onPress={() => deleteMemorial(item.id, item.name)}
        >
          <Ionicons name="ellipsis-vertical" size={20} color="#718096" />
        </TouchableOpacity>
      </View>

      <Text style={styles.biography} numberOfLines={2}>
        {item.biography}
      </Text>

      <View style={styles.cardStats}>
        <View style={styles.statItem}>
          <Ionicons name="images" size={16} color="#4fd1c7" />
          <Text style={styles.statText}>{item.photosCount} fotos</Text>
        </View>
        <View style={styles.statItem}>
          <Ionicons name="heart" size={16} color="#4fd1c7" />
          <Text style={styles.statText}>{item.tributesCount} homenagens</Text>
        </View>
      </View>

      <View style={styles.cardActions}>
        <TouchableOpacity
          style={[styles.actionButton, styles.viewButton]}
          onPress={() => navigation.navigate('ViewMemorial', { memorial: item })}
        >
          <Ionicons name="eye" size={16} color="#fff" />
          <Text style={styles.actionButtonText}>Ver</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.actionButton, styles.editButton]}
          onPress={() => navigation.navigate('CreateMemorial', { memorial: item })}
        >
          <Ionicons name="create" size={16} color="#fff" />
          <Text style={styles.actionButtonText}>Editar</Text>
        </TouchableOpacity>
      </View>
    </TouchableOpacity>
  );

  const renderEmptyState = () => (
    <View style={styles.emptyState}>
      <Ionicons name="heart-outline" size={80} color="#cbd5e0" />
      <Text style={styles.emptyTitle}>Nenhum memorial criado</Text>
      <Text style={styles.emptyDescription}>
        Crie seu primeiro memorial para preservar memórias especiais
      </Text>
      <TouchableOpacity
        style={styles.createButton}
        onPress={() => navigation.navigate('CreateMemorial')}
      >
        <Ionicons name="add" size={20} color="#fff" />
        <Text style={styles.createButtonText}>Criar Memorial</Text>
      </TouchableOpacity>
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Meus Memoriais</Text>
        <TouchableOpacity
          style={styles.addButton}
          onPress={() => navigation.navigate('CreateMemorial')}
        >
          <Ionicons name="add" size={24} color="#4fd1c7" />
        </TouchableOpacity>
      </View>

      <FlatList
        data={memorials}
        renderItem={renderMemorialCard}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.listContainer}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={renderEmptyState}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f7fafc',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e2e8f0',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2d3748',
  },
  addButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#e6fffa',
    alignItems: 'center',
    justifyContent: 'center',
  },
  listContainer: {
    padding: 20,
    paddingBottom: 100,
  },
  memorialCard: {
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 20,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  profileImage: {
    width: 60,
    height: 60,
    borderRadius: 30,
    marginRight: 15,
  },
  memorialInfo: {
    flex: 1,
  },
  memorialName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2d3748',
    marginBottom: 5,
  },
  memorialDates: {
    fontSize: 14,
    color: '#4fd1c7',
    fontWeight: '600',
    marginBottom: 2,
  },
  createdDate: {
    fontSize: 12,
    color: '#718096',
  },
  menuButton: {
    padding: 5,
  },
  biography: {
    fontSize: 14,
    color: '#4a5568',
    lineHeight: 20,
    marginBottom: 15,
  },
  cardStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 15,
    paddingVertical: 10,
    backgroundColor: '#f7fafc',
    borderRadius: 10,
  },
  statItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
  },
  statText: {
    fontSize: 12,
    color: '#718096',
    fontWeight: '500',
  },
  cardActions: {
    flexDirection: 'row',
    gap: 10,
  },
  actionButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    borderRadius: 8,
    gap: 5,
  },
  viewButton: {
    backgroundColor: '#4fd1c7',
  },
  editButton: {
    backgroundColor: '#fbb040',
  },
  actionButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  emptyState: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 60,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2d3748',
    marginTop: 20,
    marginBottom: 10,
  },
  emptyDescription: {
    fontSize: 14,
    color: '#718096',
    textAlign: 'center',
    marginBottom: 30,
    lineHeight: 20,
    paddingHorizontal: 40,
  },
  createButton: {
    backgroundColor: '#4fd1c7',
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 25,
    paddingVertical: 15,
    borderRadius: 25,
    gap: 8,
  },
  createButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});