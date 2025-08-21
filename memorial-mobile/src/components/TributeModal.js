import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Modal,
  TouchableOpacity,
  TextInput,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function TributeModal({ visible, onClose, onSubmit, type }) {
  const [message, setMessage] = useState('');
  const [duration, setDuration] = useState('1d');
  const [userName, setUserName] = useState('');

  const durations = [
    { value: '12h', label: '12 horas', price: 'Grátis' },
    { value: '1d', label: '1 dia', price: 'Grátis' },
    { value: '7d', label: '7 dias', price: 'R$ 2,00' },
    { value: 'forever', label: 'Para sempre', price: 'R$ 10,00' },
  ];

  const handleSubmit = () => {
    if (!userName.trim()) {
      Alert.alert('Erro', 'Nome é obrigatório');
      return;
    }

    onSubmit({
      type,
      duration,
      message: message.trim(),
      userName: userName.trim(),
    });

    // Reset form
    setMessage('');
    setUserName('');
    setDuration('1d');
    onClose();
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent={true}
      onRequestClose={onClose}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          {/* Header */}
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>
              {type === 'candle' ? 'Acender Vela Virtual' : 'Deixar Flor Virtual'}
            </Text>
            <TouchableOpacity style={styles.closeButton} onPress={onClose}>
              <Ionicons name="close" size={24} color="#718096" />
            </TouchableOpacity>
          </View>

          {/* Icon */}
          <View style={styles.iconContainer}>
            <View style={[
              styles.tributeIcon,
              { backgroundColor: type === 'candle' ? '#ff6b35' : '#e91e63' }
            ]}>
              <Ionicons
                name={type === 'candle' ? 'flame' : 'flower'}
                size={40}
                color="#fff"
              />
            </View>
          </View>

          {/* Form */}
          <View style={styles.form}>
            <View style={styles.inputGroup}>
              <Text style={styles.label}>Seu nome *</Text>
              <TextInput
                style={styles.input}
                value={userName}
                onChangeText={setUserName}
                placeholder="Digite seu nome"
                placeholderTextColor="#a0aec0"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Mensagem (opcional)</Text>
              <TextInput
                style={[styles.input, styles.textArea]}
                value={message}
                onChangeText={setMessage}
                placeholder={`Deixe uma mensagem especial junto com sua ${type === 'candle' ? 'vela' : 'flor'}...`}
                placeholderTextColor="#a0aec0"
                multiline
                numberOfLines={3}
                textAlignVertical="top"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Duração</Text>
              <View style={styles.durationOptions}>
                {durations.map((option) => (
                  <TouchableOpacity
                    key={option.value}
                    style={[
                      styles.durationOption,
                      duration === option.value && styles.durationOptionSelected
                    ]}
                    onPress={() => setDuration(option.value)}
                  >
                    <Text style={[
                      styles.durationLabel,
                      duration === option.value && styles.durationLabelSelected
                    ]}>
                      {option.label}
                    </Text>
                    <Text style={[
                      styles.durationPrice,
                      duration === option.value && styles.durationPriceSelected
                    ]}>
                      {option.price}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          </View>

          {/* Actions */}
          <View style={styles.actions}>
            <TouchableOpacity
              style={[styles.button, styles.submitButton]}
              onPress={handleSubmit}
              disabled={loading}
            >
              <Ionicons
                name={type === 'candle' ? 'flame' : 'flower'}
                size={20}
                color="#fff"
              />
              <Text style={styles.submitButtonText}>
                {loading ? 'Processando...' : (type === 'candle' ? 'Acender Vela' : 'Deixar Flor')}
              </Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={[styles.button, styles.cancelButton]}
              onPress={onClose}
            >
              <Text style={styles.cancelButtonText}>Cancelar</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modalContent: {
    backgroundColor: '#fff',
    borderRadius: 20,
    padding: 25,
    width: '100%',
    maxWidth: 400,
    maxHeight: '80%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2d3748',
    flex: 1,
  },
  closeButton: {
    padding: 5,
  },
  iconContainer: {
    alignItems: 'center',
    marginBottom: 25,
  },
  tributeIcon: {
    width: 80,
    height: 80,
    borderRadius: 40,
    alignItems: 'center',
    justifyContent: 'center',
  },
  form: {
    marginBottom: 25,
  },
  inputGroup: {
    marginBottom: 20,
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
    backgroundColor: '#f7fafc',
  },
  textArea: {
    height: 80,
    textAlignVertical: 'top',
  },
  durationOptions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  durationOption: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: '#f7fafc',
    borderWidth: 2,
    borderColor: '#e2e8f0',
    borderRadius: 10,
    padding: 15,
    alignItems: 'center',
  },
  durationOptionSelected: {
    backgroundColor: '#e6fffa',
    borderColor: '#4fd1c7',
  },
  durationLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#4a5568',
    marginBottom: 5,
  },
  durationLabelSelected: {
    color: '#4fd1c7',
  },
  durationPrice: {
    fontSize: 12,
    color: '#718096',
  },
  durationPriceSelected: {
    color: '#4fd1c7',
  },
  actions: {
    gap: 10,
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 15,
    borderRadius: 12,
    gap: 8,
  },
  submitButton: {
    backgroundColor: '#4fd1c7',
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  cancelButton: {
    backgroundColor: 'transparent',
    borderWidth: 2,
    borderColor: '#e2e8f0',
  },
  cancelButtonText: {
    color: '#718096',
    fontSize: 16,
    fontWeight: '600',
  },
});