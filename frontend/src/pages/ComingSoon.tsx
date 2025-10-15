/**
 * Coming Soon Page Component
 * Placeholder for pages under development
 */

import { useNavigate } from "react-router-dom";
import { ArrowLeft, Wrench } from "lucide-react";

interface ComingSoonProps {
  pageName: string;
  description?: string;
  features?: string[];
}

export default function ComingSoon({
  pageName,
  description,
  features,
}: ComingSoonProps) {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        {/* Card */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg border border-purple-500/30 shadow-2xl p-8">
          {/* Icon */}
          <div className="flex justify-center mb-6">
            <div className="bg-purple-500/20 p-6 rounded-full border border-purple-500/50">
              <Wrench className="w-16 h-16 text-purple-400" />
            </div>
          </div>

          {/* Title */}
          <h1 className="text-4xl font-bold text-white text-center mb-4">
            {pageName}
          </h1>

          {/* Status Badge */}
          <div className="flex justify-center mb-6">
            <span className="px-4 py-2 bg-yellow-500/20 text-yellow-300 rounded-full text-sm font-medium border border-yellow-500/50">
              🚧 En Cours de Développement
            </span>
          </div>

          {/* Description */}
          {description && (
            <p className="text-gray-300 text-center text-lg mb-6">
              {description}
            </p>
          )}

          {/* Features List */}
          {features && features.length > 0 && (
            <div className="bg-slate-700/30 rounded-lg p-6 mb-8">
              <h2 className="text-xl font-semibold text-white mb-4">
                ✨ Fonctionnalités Prévues
              </h2>
              <ul className="space-y-3">
                {features.map((feature, index) => (
                  <li
                    key={index}
                    className="flex items-start gap-3 text-gray-300"
                  >
                    <span className="text-purple-400 mt-1">▸</span>
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Info Box */}
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4 mb-8">
            <p className="text-blue-300 text-sm">
              💡 <strong>Info:</strong> Cette page est en cours de
              développement. Les fonctionnalités seront ajoutées progressivement
              dans les prochaines versions.
            </p>
          </div>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => navigate("/dashboard")}
              className="flex items-center justify-center gap-2 px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors font-medium"
            >
              <ArrowLeft className="w-5 h-5" />
              Retour au Dashboard
            </button>

            <button
              onClick={() => navigate(-1)}
              className="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors font-medium"
            >
              Page Précédente
            </button>
          </div>
        </div>

        {/* Footer Note */}
        <p className="text-gray-500 text-center text-sm mt-6">
          GW2 WvW Builder v1.0.0 - Production Ready
        </p>
      </div>
    </div>
  );
}
