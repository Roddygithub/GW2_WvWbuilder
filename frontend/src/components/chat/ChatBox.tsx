/**
 * GW2Optimizer - ChatBox Component
 * Interface de chat principale pour interagir avec Mistral 7B
 */

import { FC, useState, useRef, useEffect } from 'react';
import { Send, Bot, User as UserIcon } from 'lucide-react';
import { ChatMessage } from '@/types/gw2optimizer';

interface ChatBoxProps {
  messages: ChatMessage[];
  isLoading?: boolean;
  onSendMessage: (message: string) => Promise<void>;
}

export const ChatBox: FC<ChatBoxProps> = ({
  messages,
  isLoading = false,
  onSendMessage,
}) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll vers le bas
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const message = input.trim();
    setInput('');
    await onSendMessage(message);
    
    // Focus sur l'input après envoi
    setTimeout(() => inputRef.current?.focus(), 100);
  };

  return (
    <div className="gw2-card flex flex-col h-[600px]">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-gw2-border">
        <h2 className="text-xl font-bold text-gw2-gold flex items-center gap-2">
          <Bot className="h-5 w-5" />
          AI Squad Composer
        </h2>
        <span className="text-xs text-gw2-textSecondary">
          {messages.length} messages
        </span>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto py-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <Bot className="h-16 w-16 text-gw2-gold/50 mb-4" />
            <p className="text-gw2-textSecondary mb-2">
              Demandez une composition optimale pour votre escouade
            </p>
            <p className="text-sm text-gw2-textSecondary/70">
              Exemple: "Composition pour 15 joueurs en mode zerg"
            </p>
          </div>
        ) : (
          messages.map((message) => (
            <ChatMessageItem key={message.id} message={message} />
          ))
        )}
        
        {isLoading && (
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gw2-gold/20 flex items-center justify-center">
              <Bot className="h-5 w-5 text-gw2-gold animate-pulse" />
            </div>
            <div className="flex-1 gw2-card bg-gw2-dark p-3 rounded-lg border border-gw2-gold/50">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-gw2-gold rounded-full animate-pulse" />
                <span className="w-2 h-2 bg-gw2-gold rounded-full animate-pulse delay-100" />
                <span className="w-2 h-2 bg-gw2-gold rounded-full animate-pulse delay-200" />
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="pt-4 border-t border-gw2-border">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Demandez une composition optimale..."
            className="gw2-input flex-1"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="gw2-button-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
      </form>
    </div>
  );
};

interface ChatMessageItemProps {
  message: ChatMessage;
}

const ChatMessageItem: FC<ChatMessageItemProps> = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <div className={`flex items-start gap-3 ${isUser ? 'justify-end' : ''}`}>
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gw2-gold/20 flex items-center justify-center">
          <Bot className="h-5 w-5 text-gw2-gold" />
        </div>
      )}
      
      <div
        className={`flex-1 max-w-[80%] ${
          isUser
            ? 'bg-gw2-cardBg border border-gw2-border'
            : 'bg-gw2-dark border border-gw2-gold/50'
        } p-3 rounded-lg`}
      >
        <p className="text-sm text-gw2-text whitespace-pre-wrap">
          {message.content}
        </p>
        <span className="text-xs text-gw2-textSecondary mt-2 block">
          {new Date(message.timestamp).toLocaleTimeString()}
        </span>
      </div>
      
      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gw2-red/20 flex items-center justify-center">
          <UserIcon className="h-5 w-5 text-gw2-red" />
        </div>
      )}
    </div>
  );
};

export default ChatBox;
