import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';

// Screens
import HomeScreen from './src/screens/HomeScreen';
import MemorialsScreen from './src/screens/MemorialsScreen';
import CreateMemorialScreen from './src/screens/CreateMemorialScreen';
import ViewMemorialScreen from './src/screens/ViewMemorialScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

// Stack Navigator para Memoriais
function MemorialsStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: '#4fd1c7',
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}
    >
      <Stack.Screen 
        name="MemorialsList" 
        component={MemorialsScreen} 
        options={{ title: 'Meus Memoriais' }}
      />
      <Stack.Screen 
        name="CreateMemorial" 
        component={CreateMemorialScreen} 
        options={{ title: 'Criar Memorial' }}
      />
      <Stack.Screen 
        name="ViewMemorial" 
        component={ViewMemorialScreen} 
        options={{ title: 'Memorial' }}
      />
    </Stack.Navigator>
  );
}

// Stack Navigator para Autenticação
function AuthStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Register" component={RegisterScreen} />
    </Stack.Navigator>
  );
}

// Tab Navigator Principal
function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          if (route.name === 'Home') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Memoriais') {
            iconName = focused ? 'heart' : 'heart-outline';
          } else if (route.name === 'Perfil') {
            iconName = focused ? 'person' : 'person-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#4fd1c7',
        tabBarInactiveTintColor: 'gray',
        tabBarStyle: {
          backgroundColor: '#fff',
          borderTopWidth: 1,
          borderTopColor: '#e2e8f0',
          paddingBottom: 5,
          paddingTop: 5,
          height: 60,
        },
        headerStyle: {
          backgroundColor: '#4fd1c7',
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      })}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen} 
        options={{ title: 'Início' }}
      />
      <Tab.Screen 
        name="Memoriais" 
        component={MemorialsStack} 
        options={{ headerShown: false, title: 'Memoriais' }}
      />
      <Tab.Screen 
        name="Perfil" 
        component={ProfileScreen} 
        options={{ title: 'Perfil' }}
      />
    </Tab.Navigator>
  );
}

export default function App() {
  // Por enquanto, sempre mostrar as tabs principais
  // Em uma implementação real, você verificaria se o usuário está logado
  const isLoggedIn = true;

  return (
    <NavigationContainer>
      <StatusBar style="light" backgroundColor="#4fd1c7" />
      {isLoggedIn ? <MainTabs /> : <AuthStack />}
    </NavigationContainer>
  );
}