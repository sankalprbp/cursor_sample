"use client";

import React, { useState, useEffect } from 'react';
import { Phone, PhoneCall, PhoneOff, Mic, MicOff, Volume2, VolumeX, Settings, AlertCircle } from 'lucide-react';
import api from '@/services/api';

interface AICallingPanelProps {
  onCallStarted?: (callId: string) => void;
  onCallEnded?: (callId: string) => void;
}

interface CallStatus {
  callId: string;
  status: 'idle' | 'dialing' | 'connected' | 'ended' | 'failed';
  phoneNumber: string;
  duration: number;
  transcript: string[];
}

export default function AICallingPanel({ onCallStarted, onCallEnded }: AICallingPanelProps) {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [isMakingCall, setIsMakingCall] = useState(false);
  const [callStatus, setCallStatus] = useState<CallStatus | null>(null);
  const [twilioStatus, setTwilioStatus] = useState<{ available: boolean; configured: boolean } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isMuted, setIsMuted] = useState(false);
  const [isSpeakerOn, setIsSpeakerOn] = useState(true);

  // Check Twilio status on component mount
  useEffect(() => {
    checkTwilioStatus();
  }, []);

  const checkTwilioStatus = async () => {
    try {
      const response = await api.get('/api/v1/voice/twilio/status');
      setTwilioStatus(response.data);
    } catch (error) {
      console.error('Failed to check Twilio status:', error);
      setTwilioStatus({ available: false, configured: false });
    }
  };

  const handleMakeCall = async () => {
    if (!phoneNumber.trim()) {
      setError('Please enter a phone number');
      return;
    }

    if (!twilioStatus?.available) {
      setError('Twilio service is not available. Please check your configuration.');
      return;
    }

    setIsMakingCall(true);
    setError(null);

    try {
      const response = await api.post('/api/v1/voice/twilio/make-call', {
        caller_number: phoneNumber,
      });

      const callData = response.data.data;
      
      setCallStatus({
        callId: callData.call_id,
        status: 'dialing',
        phoneNumber: phoneNumber,
        duration: 0,
        transcript: []
      });

      onCallStarted?.(callData.call_id);

      // Start polling for call status
      pollCallStatus(callData.call_id);

    } catch (error: any) {
      console.error('Failed to make call:', error);
      setError(error.response?.data?.detail || 'Failed to initiate call');
    } finally {
      setIsMakingCall(false);
    }
  };

  const pollCallStatus = async (callId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await api.get(`/api/v1/voice/calls/${callId}/status`);
        const status = response.data.status;

        setCallStatus(prev => {
          if (!prev) return prev;

          if (status === 'completed' || status === 'failed' || status === 'busy' || status === 'no-answer') {
            clearInterval(pollInterval);
            onCallEnded?.(callId);
            return { ...prev, status: 'ended' };
          }

          if (status === 'in-progress' || status === 'answered') {
            return { ...prev, status: 'connected' };
          }

          return prev;
        });

        // Update duration
        setCallStatus(prev => {
          if (!prev) return prev;
          return { ...prev, duration: prev.duration + 1 };
        });

      } catch (error) {
        console.error('Failed to poll call status:', error);
        clearInterval(pollInterval);
      }
    }, 1000);

    // Cleanup after 5 minutes
    setTimeout(() => {
      clearInterval(pollInterval);
    }, 300000);
  };

  const handleEndCall = async () => {
    if (!callStatus?.callId) return;

    try {
      await api.post(`/api/v1/voice/calls/${callStatus.callId}/end`);
      setCallStatus(prev => prev ? { ...prev, status: 'ended' } : null);
      onCallEnded?.(callStatus.callId);
    } catch (error) {
      console.error('Failed to end call:', error);
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatPhoneNumber = (number: string) => {
    // Basic phone number formatting
    const cleaned = number.replace(/\D/g, '');
    if (cleaned.length === 10) {
      return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
    }
    return number;
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">AI Phone Call</h3>
          <p className="text-sm text-gray-600">Make AI-powered phone calls with Twilio</p>
        </div>
        <div className="flex items-center space-x-2">
          {twilioStatus && (
            <div className={`flex items-center text-sm ${
              twilioStatus.available ? 'text-green-600' : 'text-red-600'
            }`}>
              <div className={`w-2 h-2 rounded-full mr-2 ${
                twilioStatus.available ? 'bg-green-500' : 'bg-red-500'
              }`} />
              {twilioStatus.available ? 'Twilio Ready' : 'Twilio Unavailable'}
            </div>
          )}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <div className="flex items-center">
            <AlertCircle className="h-4 w-4 text-red-500 mr-2" />
            <span className="text-sm text-red-700">{error}</span>
          </div>
        </div>
      )}

      {/* Call Input */}
      {!callStatus && (
        <div className="space-y-4">
          <div>
            <label htmlFor="phoneNumber" className="block text-sm font-medium text-gray-700 mb-2">
              Phone Number
            </label>
            <div className="flex space-x-2">
              <input
                type="tel"
                id="phoneNumber"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                placeholder="+1 (555) 123-4567"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                disabled={isMakingCall}
              />
              <button
                onClick={handleMakeCall}
                disabled={isMakingCall || !phoneNumber.trim() || !twilioStatus?.available}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isMakingCall ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                ) : (
                  <Phone className="h-4 w-4 mr-2" />
                )}
                {isMakingCall ? 'Dialing...' : 'Make Call'}
              </button>
            </div>
          </div>

          {/* Configuration Warning */}
          {!twilioStatus?.configured && (
            <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-md">
              <div className="flex items-center">
                <AlertCircle className="h-4 w-4 text-yellow-500 mr-2" />
                <span className="text-sm text-yellow-700">
                  Twilio is not configured. Please add your Twilio credentials to the environment variables.
                </span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Active Call Display */}
      {callStatus && (
        <div className="space-y-4">
          {/* Call Status */}
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900 mb-2">
              {formatPhoneNumber(callStatus.phoneNumber)}
            </div>
            <div className="text-sm text-gray-600 mb-4">
              {callStatus.status === 'dialing' && 'Dialing...'}
              {callStatus.status === 'connected' && `Connected - ${formatDuration(callStatus.duration)}`}
              {callStatus.status === 'ended' && 'Call ended'}
            </div>
          </div>

          {/* Call Controls */}
          <div className="flex justify-center space-x-4">
            <button
              onClick={() => setIsMuted(!isMuted)}
              className={`p-3 rounded-full ${
                isMuted ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-600'
              } hover:bg-opacity-80`}
            >
              {isMuted ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
            </button>

            <button
              onClick={() => setIsSpeakerOn(!isSpeakerOn)}
              className={`p-3 rounded-full ${
                isSpeakerOn ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'
              } hover:bg-opacity-80`}
            >
              {isSpeakerOn ? <Volume2 className="h-5 w-5" /> : <VolumeX className="h-5 w-5" />}
            </button>

            {callStatus.status === 'connected' && (
              <button
                onClick={handleEndCall}
                className="p-3 rounded-full bg-red-100 text-red-600 hover:bg-red-200"
              >
                <PhoneOff className="h-5 w-5" />
              </button>
            )}
          </div>

          {/* Call Status Indicator */}
          <div className="flex justify-center">
            <div className={`w-3 h-3 rounded-full ${
              callStatus.status === 'dialing' ? 'bg-yellow-500 animate-pulse' :
              callStatus.status === 'connected' ? 'bg-green-500' :
              callStatus.status === 'ended' ? 'bg-gray-500' : 'bg-red-500'
            }`} />
          </div>

          {/* Transcript Preview */}
          {callStatus.transcript.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Recent Conversation</h4>
              <div className="bg-gray-50 rounded-md p-3 max-h-32 overflow-y-auto">
                {callStatus.transcript.slice(-3).map((line, index) => (
                  <div key={index} className="text-sm text-gray-600 mb-1">
                    {line}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Help Text */}
      <div className="mt-6 text-xs text-gray-500">
        <p>• Calls are powered by Twilio and OpenAI</p>
        <p>• AI agent will handle the conversation automatically</p>
        <p>• Call transcripts are saved for review</p>
      </div>
    </div>
  );
}