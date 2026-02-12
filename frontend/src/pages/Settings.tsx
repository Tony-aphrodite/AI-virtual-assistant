import { useState } from 'react';
import { Save, Key, MessageSquare, Bell } from 'lucide-react';

export default function Settings() {
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Configuración</h1>
        <p className="mt-2 text-gray-600">
          Ajusta las preferencias del sistema
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Settings */}
        <div className="lg:col-span-2 space-y-6">
          {/* API Keys */}
          <div className="card">
            <div className="flex items-center mb-4">
              <Key className="w-5 h-5 text-gray-700 mr-2" />
              <h2 className="text-xl font-semibold text-gray-900">
                Claves API
              </h2>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  OpenAI API Key
                </label>
                <input
                  type="password"
                  placeholder="sk-..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Twilio Account SID
                </label>
                <input
                  type="text"
                  placeholder="AC..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  ElevenLabs API Key
                </label>
                <input
                  type="password"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </div>
          </div>

          {/* AI Settings */}
          <div className="card">
            <div className="flex items-center mb-4">
              <MessageSquare className="w-5 h-5 text-gray-700 mr-2" />
              <h2 className="text-xl font-semibold text-gray-900">
                Configuración de IA
              </h2>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nombre de la Empresa
                </label>
                <input
                  type="text"
                  placeholder="Tu Empresa"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Prompt del Sistema
                </label>
                <textarea
                  rows={6}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="Eres un asistente virtual profesional..."
                />
                <p className="mt-1 text-xs text-gray-500">
                  Este texto guía el comportamiento del asistente AI
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Temperatura (0.0 - 1.0)
                </label>
                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.1"
                  defaultValue="0.7"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Mayor = más creativo, Menor = más consistente
                </p>
              </div>
            </div>
          </div>

          {/* Notifications */}
          <div className="card">
            <div className="flex items-center mb-4">
              <Bell className="w-5 h-5 text-gray-700 mr-2" />
              <h2 className="text-xl font-semibold text-gray-900">
                Notificaciones
              </h2>
            </div>
            <div className="space-y-3">
              <label className="flex items-center">
                <input type="checkbox" className="rounded text-primary-600" />
                <span className="ml-3 text-sm text-gray-700">
                  Notificar cuando hay una nueva llamada
                </span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" className="rounded text-primary-600" defaultChecked />
                <span className="ml-3 text-sm text-gray-700">
                  Enviar resumen diario por email
                </span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" className="rounded text-primary-600" />
                <span className="ml-3 text-sm text-gray-700">
                  Alertas de errores del sistema
                </span>
              </label>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Save Button */}
          <div className="card">
            <button
              onClick={handleSave}
              className="w-full btn btn-primary"
            >
              <Save className="w-5 h-5 mr-2" />
              Guardar Cambios
            </button>
            {saved && (
              <div className="mt-3 text-sm text-green-600 text-center">
                ✓ Cambios guardados
              </div>
            )}
          </div>

          {/* System Info */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Información del Sistema
            </h3>
            <dl className="space-y-2 text-sm">
              <div>
                <dt className="text-gray-500">Versión</dt>
                <dd className="text-gray-900 font-medium">0.1.0</dd>
              </div>
              <div>
                <dt className="text-gray-500">Estado</dt>
                <dd className="text-green-600 font-medium">Operativo</dd>
              </div>
              <div>
                <dt className="text-gray-500">Última actualización</dt>
                <dd className="text-gray-900">12 Feb 2026</dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
}
