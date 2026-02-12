export interface Call {
  id: string;
  twilio_call_sid: string;
  direction: 'inbound' | 'outbound';
  from_number: string;
  to_number: string;
  status: string;
  duration: number | null;
  recording_url: string | null;
  transcription: string | null;
  metadata: Record<string, any> | null;
  created_at: string;
  updated_at: string;
}

export interface VoiceProfile {
  id: string;
  name: string;
  description: string | null;
  elevenlabs_voice_id: string;
  sample_audio_urls: string[];
  is_active: boolean;
  user_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface Conversation {
  id: string;
  call_id: string;
  messages: ConversationMessage[];
  summary: string | null;
  intent: string | null;
  sentiment: string | null;
  metadata: Record<string, any> | null;
  created_at: string;
  updated_at: string;
}

export interface ConversationMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

export interface DashboardStats {
  total_calls: number;
  today_calls: number;
  active_calls: number;
  avg_duration: number;
  success_rate: number;
}

export interface CallListResponse {
  items: Call[];
  total: number;
  page: number;
  page_size: number;
}
