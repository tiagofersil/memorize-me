import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  Alert,
  Switch,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';

export default function ProfileScreen({ navigation }) {
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [darkMode, setDarkMode] = useState(false);

  const user = {
    name: 'João Silva',
    email: 'joao@email.com',
    avatar: 'https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&cs=tinysrgb&w=150',
    joinDate: '2024-01-01',
    memorialsCount: 2,
    photosCount: 15,
    tributesCount: 8,
  };

  const menuItems = [
    {
      icon: 'person-outline',
      title: 'Editar Perfil',
      subtitle: 'Alterar informações pessoais',
      onPress: () => Alert.alert('Em breve', 'Funcionalidade em desenvolvimento'),
    },
    {
      icon: 'heart-outline',
      title: 'Meus Memoriais',
      subtitle: 'Gerenciar memoriais criados',
      onPress: () => navigation.navigate('Memoriais'),
    },
    {
      icon: 'card-outline',
      title: 'Planos e Pagamentos',
      subtitle: 'Gerenciar assinatura',
      onPress: () => Alert.alert('Em breve', 'Funcionalidade em desenvolvimento'),
    },
    {
      icon: 'shield-outline',
      title: 'Privacidade',
      subtitle: 'Configurações de privacidade',
      onPress: () => Alert.alert('Em breve', 'Funcionalidade em desenvolvimento'),
    },
    {
      icon: 'help-circle-outline',
      title: 'Ajuda e Suporte',
      subtitle: 'Central de ajuda',
      onPress: () => Alert.alert('Em breve', 'Funcionalidade em desenvolvimento'),
    },
    {
      icon: 'information-circle-outline',
      title: 'Sobre o App',
      subtitle: 'Versão 1.0.0',
      onPress: () => Alert.alert('Memorial Digital', 'Versão 1.0.0\nDesenvolvido com ❤️'),
    },
  ];

  const logout = () => {
    Alert.alert(
      'Sair',
      'Tem certeza que deseja sair da sua conta?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Sair',
          style: 'destructive',
          onPress: () => {
            Alert.alert('Logout', 'Você foi desconectado com sucesso');
            // Em produção, limpar dados de autenticação e navegar para login
          },
        },
      ]
    );
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Profile Header */}
      <LinearGradient
        colors={['#4fd1c7', '#38b2ac']}
        style={styles.profileHeader}
      >
        <View style={styles.profileInfo}>
          <Image source={{ uri: user.avatar }} style={styles.avatar} />
          <View style={styles.userInfo}>
            <Text style={styles.userName}>{user.name}</Text>
            <Text style={styles.userEmail}>{user.email}</Text>
            <Text style={styles.joinDate}>
              Membro desde {new Date(user.joinDate).toLocaleDateString('pt-BR')}
            </Text>
          </View>
        </View>
      </LinearGradient>

      {/* Statistics */}
      <View style={styles.statsSection}>
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>{user.memorialsCount}</Text>
            <Text style={styles.statLabel}>Memoriais</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>{user.photosCount}</Text>
            <Text style={styles.statLabel}>Fotos</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>{user.tributesCount}</Text>
            <Text style={styles.statLabel}>Homenagens</Text>
          </View>
        </View>
      </View>

      {/* Menu Items */}
      <View style={styles.menuSection}>
        {menuItems.map((item, index) => (
          <TouchableOpacity
            key={index}
            style={styles.menuItem}
            onPress={item.onPress}
          >
            <View style={styles.menuItemLeft}>
              <View style={styles.menuIcon}>
                <Ionicons name={item.icon} size={24} color="#4fd1c7" />
              </View>
              <View style={styles.menuText}>
                <Text style={styles.menuTitle}>{item.title}</Text>
                <Text style={styles.menuSubtitle}>{item.subtitle}</Text>
              </View>
            </View>
            <Ionicons name="chevron-forward" size={20} color="#a0aec0" />
          </TouchableOpacity>
        ))}
      </View>

      {/* Settings */}
      <View style={styles.settingsSection}>
        <Text style={styles.settingsTitle}>Configurações</Text>
        
        <View style={styles.settingItem}>
          <View style={styles.settingLeft}>
            <Ionicons name="notifications-outline" size={24} color="#4fd1c7" />
            <View style={styles.settingText}>
              <Text style={styles.settingTitle}>Notificações</Text>
              <Text style={styles.settingSubtitle}>Receber notificações push</Text>
            </View>
          </View>
          <Switch
            value={notificationsEnabled}
            onValueChange={setNotificationsEnabled}
            trackColor={{ false: '#e2e8f0', true: '#4fd1c7' }}
            thumbColor={notificationsEnabled ? '#fff' : '#f4f3f4'}
          />
        </View>

        <View style={styles.settingItem}>
          <View style={styles.settingLeft}>
            <Ionicons name="moon-outline" size={24} color="#4fd1c7" />
            <View style={styles.settingText}>
              <Text style={styles.settingTitle}>Modo Escuro</Text>
              <Text style={styles.settingSubtitle}>Tema escuro do aplicativo</Text>
            </View>
          </View>
          <Switch
            value={darkMode}
            onValueChange={setDarkMode}
            trackColor={{ false: '#e2e8f0', true: '#4fd1c7' }}
            thumbColor={darkMode ? '#fff' : '#f4f3f4'}
          />
        </View>
      </View>

      {/* Logout Button */}
      <View style={styles.logoutSection}>
        <TouchableOpacity style={styles.logoutButton} onPress={logout}>
          <Ionicons name="log-out-outline" size={20} color="#fc8181" />
          <Text style={styles.logoutText}>Sair da Conta</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>Memorial Digital v1.0.0</Text>
        <Text style={styles.footerSubtext}>Preservando memórias com amor</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f7fafc',
  },
  profileHeader: {
    padding: 30,
    paddingTop: 50,
    borderBottomLeftRadius: 25,
    borderBottomRightRadius: 25,
  },
  profileInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 3,
    borderColor: '#fff',
    marginRight: 20,
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 5,
  },
  userEmail: {
    fontSize: 16,
    color: '#fff',
    opacity: 0.9,
    marginBottom: 2,
  },
  joinDate: {
    fontSize: 14,
    color: '#fff',
    opacity: 0.8,
  },
  statsSection: {
    padding: 20,
    paddingBottom: 0,
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
  menuSection: {
    padding: 20,
    paddingTop: 10,
  },
  menuItem: {
    backgroundColor: '#fff',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 20,
    borderRadius: 12,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  menuItemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  menuIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#e6fffa',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 15,
  },
  menuText: {
    flex: 1,
  },
  menuTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2d3748',
    marginBottom: 2,
  },
  menuSubtitle: {
    fontSize: 12,
    color: '#718096',
  },
  settingsSection: {
    padding: 20,
    paddingTop: 0,
  },
  settingsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2d3748',
    marginBottom: 15,
  },
  settingItem: {
    backgroundColor: '#fff',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 20,
    borderRadius: 12,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  settingLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  settingText: {
    marginLeft: 15,
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2d3748',
    marginBottom: 2,
  },
  settingSubtitle: {
    fontSize: 12,
    color: '#718096',
  },
  logoutSection: {
    padding: 20,
    paddingTop: 10,
  },
  logoutButton: {
    backgroundColor: '#fff',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#fed7d7',
    gap: 10,
  },
  logoutText: {
    color: '#fc8181',
    fontSize: 16,
    fontWeight: '600',
  },
  footer: {
    padding: 20,
    alignItems: 'center',
  },
  footerText: {
    fontSize: 14,
    color: '#718096',
    fontWeight: '600',
  },
  footerSubtext: {
    fontSize: 12,
    color: '#a0aec0',
    marginTop: 2,
  },
});