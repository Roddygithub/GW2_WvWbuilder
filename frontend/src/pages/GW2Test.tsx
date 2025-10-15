/**
 * GW2 API Test Page
 * Test page to verify GW2 API integration
 */

import { useGW2Professions, useGW2APIStatus } from "../hooks/useGW2Professions";

export default function GW2Test() {
  const { data: professions, isLoading, isError, error } = useGW2Professions();
  const { data: apiAvailable, isLoading: statusLoading } = useGW2APIStatus();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-4">
            Guild Wars 2 API Test
          </h1>
          <p className="text-gray-300">Vérification de la connexion API GW2</p>
        </div>

        {/* API Status */}
        <div className="mb-8 bg-slate-800/50 rounded-lg p-6 backdrop-blur-sm">
          <h2 className="text-2xl font-bold text-white mb-4">📡 Statut API</h2>
          {statusLoading ? (
            <p className="text-gray-400">Vérification...</p>
          ) : (
            <div className="flex items-center gap-3">
              <div
                className={`w-4 h-4 rounded-full ${apiAvailable ? "bg-green-500" : "bg-red-500"}`}
              />
              <span className="text-white font-medium">
                {apiAvailable
                  ? "✅ API GW2 Connectée"
                  : "❌ API GW2 Non Disponible"}
              </span>
            </div>
          )}
        </div>

        {/* Professions List */}
        <div className="bg-slate-800/50 rounded-lg p-6 backdrop-blur-sm">
          <h2 className="text-2xl font-bold text-white mb-6">
            ⚔️ Professions GW2
          </h2>

          {isLoading && (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent"></div>
              <p className="mt-4 text-gray-400">
                Chargement des professions...
              </p>
            </div>
          )}

          {isError && (
            <div className="bg-red-500/10 border border-red-500 rounded-lg p-4">
              <p className="text-red-400 font-medium">
                ❌ Erreur de chargement
              </p>
              <p className="text-red-300 text-sm mt-2">{error?.message}</p>
            </div>
          )}

          {professions && (
            <>
              <div className="mb-4 text-gray-300">
                <p>
                  <strong>Total:</strong> {professions.length} professions
                </p>
                <p>
                  <strong>Source:</strong> API officielle Guild Wars 2
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {professions.map((profession) => (
                  <div
                    key={profession.id}
                    className="bg-slate-700/50 rounded-lg p-4 border border-slate-600 hover:border-purple-500 transition-colors"
                  >
                    <div className="flex items-center gap-3 mb-3">
                      {profession.icon && (
                        <img
                          src={profession.icon}
                          alt={profession.name}
                          className="w-12 h-12 rounded"
                        />
                      )}
                      <div>
                        <h3 className="text-white font-bold">
                          {profession.name}
                        </h3>
                        <p className="text-gray-400 text-sm">{profession.id}</p>
                      </div>
                    </div>

                    <div className="space-y-2 text-sm">
                      <div className="text-gray-300">
                        <strong>Spécialisations:</strong>{" "}
                        {profession.specializations.length}
                      </div>
                      <div className="text-gray-300">
                        <strong>Armes:</strong>{" "}
                        {Object.keys(profession.weapons).length}
                      </div>
                      {profession.flags && profession.flags.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {profession.flags.map((flag) => (
                            <span
                              key={flag}
                              className="px-2 py-1 bg-purple-500/20 text-purple-300 rounded text-xs"
                            >
                              {flag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>

        {/* Info */}
        <div className="mt-8 bg-blue-500/10 border border-blue-500/50 rounded-lg p-4">
          <p className="text-blue-300">
            ℹ️ <strong>Info:</strong> Cette page teste la connexion avec l'API
            officielle Guild Wars 2. Les données affichées sont récupérées en
            temps réel depuis l'API.
          </p>
        </div>
      </div>
    </div>
  );
}
