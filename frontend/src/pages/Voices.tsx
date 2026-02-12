import { useEffect, useState } from 'react';
import { Mic, Plus, Play, Trash2 } from 'lucide-react';
import { voicesApi } from '@/services/api';
import type { VoiceProfile } from '@/types';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

export default function Voices() {
  const [voices, setVoices] = useState<VoiceProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    loadVoices();
  }, []);

  const loadVoices = async () => {
    try {
      setLoading(true);
      const response = await voicesApi.list();
      setVoices(response.data);
    } catch (error) {
      console.error('Error loading voices:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('¿Estás seguro de eliminar esta voz?')) return;

    try {
      await voicesApi.delete(id);
      setVoices(voices.filter(v => v.id !== id));
    } catch (error) {
      console.error('Error deleting voice:', error);
      alert('Error al eliminar la voz');
    }
  };

  const handleTest = async (id: string) => {
    try {
      const response = await voicesApi.test(id, 'Hola, esta es una prueba de mi voz clonada.');
      // Handle audio playback
      console.log('Test audio:', response.data);
    } catch (error) {
      console.error('Error testing voice:', error);
      alert('Error al probar la voz');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Voces</h1>
          <p className="mt-2 text-gray-600">
            Gestiona los perfiles de voz clonados
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn btn-primary"
        >
          <Plus className="w-5 h-5 mr-2" />
          Clonar Voz
        </button>
      </div>

      {/* Voices Grid */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Cargando voces...</div>
        </div>
      ) : voices.length === 0 ? (
        <div className="card text-center py-12">
          <Mic className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No hay voces clonadas
          </h3>
          <p className="text-gray-600 mb-6">
            Comienza clonando tu primera voz para usarla en las llamadas
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn btn-primary inline-flex items-center"
          >
            <Plus className="w-5 h-5 mr-2" />
            Clonar Voz
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {voices.map((voice) => (
            <div key={voice.id} className="card">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  <div className="p-3 bg-primary-100 rounded-lg">
                    <Mic className="w-6 h-6 text-primary-600" />
                  </div>
                  <div className="ml-3">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {voice.name}
                    </h3>
                    <div className="flex items-center mt-1">
                      <span className={`
                        inline-flex items-center px-2 py-0.5 rounded text-xs font-medium
                        ${voice.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}
                      `}>
                        {voice.is_active ? 'Activa' : 'Inactiva'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {voice.description && (
                <p className="text-sm text-gray-600 mb-4">
                  {voice.description}
                </p>
              )}

              <div className="text-xs text-gray-500 mb-4">
                Creada {format(new Date(voice.created_at), 'PP', { locale: es })}
              </div>

              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleTest(voice.id)}
                  className="flex-1 btn btn-secondary text-sm"
                >
                  <Play className="w-4 h-4 mr-1" />
                  Probar
                </button>
                <button
                  onClick={() => handleDelete(voice.id)}
                  className="btn btn-secondary text-sm text-red-600 hover:bg-red-50"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Modal (Simplified) */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Clonar Nueva Voz
            </h2>
            <p className="text-sm text-gray-600 mb-4">
              Para clonar una voz, necesitas subir al menos 1 minuto de audio
              con muestras claras de la voz.
            </p>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nombre de la voz
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="Ej: Voz Profesional"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Archivos de audio
                </label>
                <input
                  type="file"
                  multiple
                  accept="audio/*"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
            </div>
            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 btn btn-secondary"
              >
                Cancelar
              </button>
              <button className="flex-1 btn btn-primary">
                Clonar Voz
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
