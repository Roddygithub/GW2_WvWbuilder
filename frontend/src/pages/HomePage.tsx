/**
 * GW2Optimizer - HomePage
 * Page principale avec ChatBox et affichage des compositions
 */

import { FC, useState } from 'react';
import { Header } from '@/components/layout/Header';
import { ChatBox } from '@/components/chat/ChatBox';
import { SquadCard } from '@/components/squad/SquadCard';
import { ChatMessage, Squad } from '@/types/gw2optimizer';
import { generateComposition } from '@/api/gw2optimizer';
import { Loader2, AlertCircle } from 'lucide-react';

export const HomePage: FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [squads, setSquads] = useState<Squad[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSendMessage = async (message: string) => {
    setError(null);

    // Ajouter le message utilisateur
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);

    setIsLoading(true);

    try {
      // Extraire la taille d'escouade du message (simple regex)
      const sizeMatch = message.match(/(\d+)\s*(joueurs?|players?)/i);
      const squadSize = sizeMatch ? parseInt(sizeMatch[1]) : 15;

      // Détecter le mode
      let mode: 'zerg' | 'havoc' | 'roaming' | 'defense' | 'gank' | undefined;
      const lowerMessage = message.toLowerCase();
      if (lowerMessage.includes('zerg')) mode = 'zerg';
      else if (lowerMessage.includes('havoc')) mode = 'havoc';
      else if (lowerMessage.includes('roam')) mode = 'roaming';
      else if (lowerMessage.includes('defense') || lowerMessage.includes('défense')) mode = 'defense';
      else if (lowerMessage.includes('gank')) mode = 'gank';

      // Appeler le backend
      const result = await generateComposition(message, squadSize, mode);

      // Créer la réponse de l'AI
      const aiResponse = generateAIResponse(result);
      const aiMessage: ChatMessage = {
        id: `ai-${Date.now()}`,
        role: 'assistant',
        content: aiResponse,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, aiMessage]);
      setSquads(result.squads);
    } catch (err: any) {
      console.error('Error generating composition:', err);
      setError(err.response?.data?.detail || 'Erreur lors de la génération de la composition');
      
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: `Désolé, une erreur s'est produite: ${err.response?.data?.detail || err.message}`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const generateAIResponse = (result: any): string => {
    const { squads, meta } = result;
    
    if (squads.length === 0) {
      return "Je n'ai pas pu générer de composition optimale avec ces paramètres.";
    }

    const squad = squads[0];
    const buildsList = squad.builds
      .map((b: any) => `${b.count}x ${b.specialization}`)
      .join(', ');

    return `J'ai généré une composition optimale de ${squad.squad_size} joueurs avec un score de ${(squad.weight * 100).toFixed(0)}% et une synergie de ${(squad.synergy * 100).toFixed(0)}%.\n\nComposition: ${buildsList}\n\nVous pouvez voir les détails ci-dessous.`;
  };

  return (
    <div className="min-h-screen bg-gw2-dark">
      <Header />
      
      <main className="container py-8">
        {/* Error Alert */}
        {error && (
          <div className="mb-6 gw2-card bg-danger/10 border-danger flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-danger flex-shrink-0 mt-0.5" />
            <div>
              <div className="font-semibold text-danger mb-1">Erreur</div>
              <div className="text-sm text-gw2-text">{error}</div>
            </div>
          </div>
        )}

        <div className="grid lg:grid-cols-2 gap-6">
          {/* ChatBox */}
          <div className="lg:col-span-1">
            <ChatBox
              messages={messages}
              isLoading={isLoading}
              onSendMessage={handleSendMessage}
            />
          </div>

          {/* Squads Display */}
          <div className="lg:col-span-1 space-y-4">
            {squads.length === 0 ? (
              <div className="gw2-card h-[600px] flex flex-col items-center justify-center">
                <div className="text-center">
                  <div className="text-6xl mb-4">⚔️</div>
                  <h3 className="text-xl font-bold text-gw2-gold mb-2">
                    Aucune composition
                  </h3>
                  <p className="text-gw2-textSecondary">
                    Demandez une composition via le chat pour commencer
                  </p>
                </div>
              </div>
            ) : (
              <>
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-bold text-gw2-gold">
                    Compositions Générées
                  </h2>
                  <span className="text-sm text-gw2-textSecondary">
                    {squads.length} composition{squads.length > 1 ? 's' : ''}
                  </span>
                </div>
                
                <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
                  {squads.map((squad) => (
                    <SquadCard
                      key={squad.id}
                      squad={squad}
                      onSelect={(id) => console.log('Selected squad:', id)}
                    />
                  ))}
                </div>
              </>
            )}
          </div>
        </div>

        {/* Loading Overlay */}
        {isLoading && squads.length === 0 && (
          <div className="fixed inset-0 bg-gw2-dark/80 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="gw2-card text-center">
              <Loader2 className="h-12 w-12 text-gw2-gold animate-spin mx-auto mb-4" />
              <p className="text-gw2-text font-semibold mb-2">
                Génération en cours...
              </p>
              <p className="text-sm text-gw2-textSecondary">
                Mistral 7B analyse votre demande
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default HomePage;
