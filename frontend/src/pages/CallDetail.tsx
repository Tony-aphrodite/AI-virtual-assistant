import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Phone, Clock, MessageSquare } from 'lucide-react';
import { callsApi } from '@/services/api';
import type { Call, Conversation } from '@/types';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

export default function CallDetail() {
  const { id } = useParams<{ id: string }>();
  const [call, setCall] = useState<Call | null>(null);
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      loadCallDetails(id);
    }
  }, [id]);

  const loadCallDetails = async (callId: string) => {
    try {
      setLoading(true);
      const [callRes, convRes] = await Promise.all([
        callsApi.get(callId),
        callsApi.getConversation(callId).catch(() => ({ data: null })),
      ]);
      setCall(callRes.data);
      setConversation(convRes.data);
    } catch (error) {
      console.error('Error loading call details:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Cargando...</div>
      </div>
    );
  }

  if (!call) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Llamada no encontrada</p>
        <Link to="/calls" className="text-primary-600 hover:text-primary-700 mt-4 inline-block">
          Volver a llamadas
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <Link
          to="/calls"
          className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Volver a llamadas
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">Detalles de Llamada</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Call Information */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Info */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Información Básica
            </h2>
            <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <dt className="text-sm font-medium text-gray-500">Call SID</dt>
                <dd className="mt-1 text-sm text-gray-900 font-mono">
                  {call.twilio_call_sid}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Dirección</dt>
                <dd className="mt-1">
                  <span className={`
                    inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                    ${call.direction === 'inbound' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'}
                  `}>
                    {call.direction === 'inbound' ? 'Entrante' : 'Saliente'}
                  </span>
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">De</dt>
                <dd className="mt-1 text-sm text-gray-900">{call.from_number}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Para</dt>
                <dd className="mt-1 text-sm text-gray-900">{call.to_number}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Fecha</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {format(new Date(call.created_at), 'PPpp', { locale: es })}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Duración</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {call.duration ? `${call.duration} segundos` : 'N/A'}
                </dd>
              </div>
            </dl>
          </div>

          {/* Conversation */}
          {conversation && conversation.messages.length > 0 && (
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <MessageSquare className="w-5 h-5 mr-2" />
                Conversación
              </h2>
              <div className="space-y-4">
                {conversation.messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`
                        max-w-[80%] rounded-lg px-4 py-3
                        ${
                          message.role === 'user'
                            ? 'bg-primary-600 text-white'
                            : 'bg-gray-100 text-gray-900'
                        }
                      `}
                    >
                      <div className="text-xs opacity-75 mb-1">
                        {message.role === 'user' ? 'Usuario' : 'Asistente'}
                      </div>
                      <div className="text-sm">{message.content}</div>
                    </div>
                  </div>
                ))}
              </div>

              {conversation.summary && (
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Resumen</h3>
                  <p className="text-sm text-gray-600">{conversation.summary}</p>
                </div>
              )}
            </div>
          )}

          {/* Transcription */}
          {call.transcription && (
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Transcripción
              </h2>
              <p className="text-gray-700 whitespace-pre-wrap">
                {call.transcription}
              </p>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Status */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Estado</h3>
            <div className={`
              px-4 py-3 rounded-lg text-center font-medium
              ${
                call.status === 'completed'
                  ? 'bg-green-100 text-green-800'
                  : call.status === 'in-progress'
                  ? 'bg-blue-100 text-blue-800'
                  : 'bg-gray-100 text-gray-800'
              }
            `}>
              {call.status}
            </div>
          </div>

          {/* Analysis */}
          {conversation && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Análisis</h3>
              <dl className="space-y-3">
                {conversation.intent && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Intención</dt>
                    <dd className="mt-1 text-sm text-gray-900">{conversation.intent}</dd>
                  </div>
                )}
                {conversation.sentiment && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Sentimiento</dt>
                    <dd className="mt-1">
                      <span className={`
                        inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                        ${
                          conversation.sentiment === 'positive'
                            ? 'bg-green-100 text-green-800'
                            : conversation.sentiment === 'negative'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-gray-100 text-gray-800'
                        }
                      `}>
                        {conversation.sentiment}
                      </span>
                    </dd>
                  </div>
                )}
              </dl>
            </div>
          )}

          {/* Recording */}
          {call.recording_url && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Grabación</h3>
              <audio controls className="w-full">
                <source src={call.recording_url} type="audio/mpeg" />
                Tu navegador no soporta el elemento de audio.
              </audio>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
