# Memorial Digital Mobile

Aplicativo mobile do Memorial Digital desenvolvido com React Native e Expo.

## 🚀 Como testar no seu dispositivo

### Pré-requisitos
1. Instale o app **Expo Go** no seu celular:
   - [Android - Google Play Store](https://play.google.com/store/apps/details?id=host.exp.exponent)
   - [iOS - App Store](https://apps.apple.com/app/expo-go/id982107779)

### Executar o app

1. **Instalar dependências:**
   ```bash
   cd memorial-mobile
   npm install
   ```

2. **Iniciar o servidor de desenvolvimento:**
   ```bash
   npm start
   ```
   ou para usar túnel (recomendado se estiver em redes diferentes):
   ```bash
   npm run start:tunnel
   ```

3. **Conectar seu dispositivo:**
   - Abra o app **Expo Go** no seu celular
   - Escaneie o QR Code que aparece no terminal ou navegador
   - O app será carregado automaticamente no seu dispositivo

## 📱 Funcionalidades Implementadas

### ✅ Telas Principais
- **Home**: Dashboard com estatísticas e acesso rápido
- **Memoriais**: Lista de memoriais criados
- **Criar/Editar Memorial**: Formulário completo para memoriais
- **Visualizar Memorial**: Página pública do memorial
- **Perfil**: Configurações do usuário

### ✅ Recursos
- **Navegação por Tabs**: Interface intuitiva
- **Upload de Fotos**: Galeria e câmera
- **QR Code**: Geração e compartilhamento
- **Homenagens Virtuais**: Velas e flores
- **Compartilhamento**: Integração nativa
- **Design Responsivo**: Adaptado para mobile

### ✅ Componentes Especiais
- **Galeria de Fotos**: Visualização otimizada
- **Timeline de Vida**: Eventos importantes
- **Sistema de Homenagens**: Interativo
- **Perfil Completo**: Estatísticas e configurações

## 🎨 Design

O app segue o design system do Memorial Digital:
- **Cores**: Paleta turquesa (#4fd1c7) como cor principal
- **Tipografia**: Hierarquia clara e legível
- **Componentes**: Cards, botões e inputs consistentes
- **Animações**: Transições suaves
- **Acessibilidade**: Suporte a leitores de tela

## 🔧 Tecnologias Utilizadas

- **React Native**: Framework principal
- **Expo**: Plataforma de desenvolvimento
- **React Navigation**: Navegação entre telas
- **Expo Vector Icons**: Ícones
- **Expo Linear Gradient**: Gradientes
- **React Native QRCode SVG**: Geração de QR Codes
- **Expo Image Picker**: Seleção de imagens
- **Expo Camera**: Acesso à câmera

## 📂 Estrutura do Projeto

```
memorial-mobile/
├── App.js                 # Componente principal e navegação
├── src/
│   ├── screens/          # Telas do aplicativo
│   │   ├── HomeScreen.js
│   │   ├── MemorialsScreen.js
│   │   ├── CreateMemorialScreen.js
│   │   ├── ViewMemorialScreen.js
│   │   ├── ProfileScreen.js
│   │   ├── LoginScreen.js
│   │   └── RegisterScreen.js
│   └── components/       # Componentes reutilizáveis
│       └── TributeModal.js
├── assets/              # Imagens e ícones
└── package.json
```

## 🔄 Próximas Implementações

### Backend Integration
- [ ] Conectar com API do Memorial Digital
- [ ] Sistema de autenticação real
- [ ] Sincronização de dados
- [ ] Upload real de imagens

### Funcionalidades Avançadas
- [ ] Notificações push
- [ ] Modo offline
- [ ] Backup automático
- [ ] Compartilhamento avançado

### Melhorias UX/UI
- [ ] Animações mais elaboradas
- [ ] Temas personalizáveis
- [ ] Acessibilidade completa
- [ ] Suporte a tablets

## 🐛 Troubleshooting

### Problemas Comuns

1. **QR Code não aparece no terminal:**
   ```bash
   npm run start:tunnel
   ```

2. **Erro de dependências:**
   ```bash
   rm -rf node_modules
   npm install
   ```

3. **App não carrega no dispositivo:**
   - Verifique se está na mesma rede WiFi
   - Use o modo túnel se necessário
   - Reinicie o Expo Go

### Logs e Debug
- Use `console.log()` para debug
- Logs aparecem no terminal onde rodou `npm start`
- Shake o dispositivo para abrir o menu de desenvolvimento

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação do Expo: https://docs.expo.dev/
2. Consulte os logs no terminal
3. Teste em diferentes dispositivos se possível

---

**Memorial Digital Mobile** - Preservando memórias em qualquer lugar 💙