/**
 * Composition Members List Component
 * Displays squad members with profession, elite spec, and role
 */

import { motion } from 'framer-motion';
import { Crown, Shield, Swords, Heart, Sparkles, Users } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface CompositionMember {
  id: number;
  profession_name: string;
  elite_specialization_name?: string;
  role_type: string;
  is_commander: boolean;
  username: string;
  notes?: string;
}

interface CompositionMembersListProps {
  members: CompositionMember[];
  squadSize: number;
}

const professionColors: Record<string, string> = {
  Guardian: 'from-blue-500 to-cyan-500',
  Warrior: 'from-yellow-500 to-orange-500',
  Engineer: 'from-amber-500 to-yellow-500',
  Ranger: 'from-green-500 to-emerald-500',
  Thief: 'from-gray-500 to-slate-500',
  Elementalist: 'from-red-500 to-pink-500',
  Mesmer: 'from-purple-500 to-violet-500',
  Necromancer: 'from-green-700 to-teal-700',
  Revenant: 'from-red-700 to-orange-700',
};

const getRoleIcon = (role: string) => {
  const roleLower = role.toLowerCase();
  if (roleLower.includes('healer')) return Heart;
  if (roleLower.includes('support') || roleLower.includes('boon')) return Sparkles;
  if (roleLower.includes('dps') || roleLower.includes('damage')) return Swords;
  if (roleLower.includes('tank')) return Shield;
  return Users;
};

const getRoleColor = (role: string) => {
  const roleLower = role.toLowerCase();
  if (roleLower.includes('healer')) return 'text-green-400 bg-green-500/20';
  if (roleLower.includes('support') || roleLower.includes('boon')) return 'text-purple-400 bg-purple-500/20';
  if (roleLower.includes('dps') || roleLower.includes('damage')) return 'text-red-400 bg-red-500/20';
  if (roleLower.includes('tank')) return 'text-blue-400 bg-blue-500/20';
  return 'text-slate-400 bg-slate-500/20';
};

export default function CompositionMembersList({ members, squadSize }: CompositionMembersListProps) {
  return (
    <Card className="bg-slate-900/50 border-purple-500/30">
      <CardHeader>
        <CardTitle className="flex items-center justify-between text-slate-200">
          <div className="flex items-center space-x-2">
            <Users className="w-5 h-5 text-purple-400" />
            <span>Squad Members</span>
          </div>
          <Badge variant="outline" className="text-purple-300 border-purple-500/50">
            {members.length} / {squadSize}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          {members.map((member, index) => {
            const RoleIcon = getRoleIcon(member.role_type);
            const professionGradient = professionColors[member.profession_name] || 'from-slate-500 to-slate-600';
            const roleColorClass = getRoleColor(member.role_type);

            return (
              <motion.div
                key={member.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.02 }}
                className="relative rounded-lg p-4 bg-gradient-to-br from-slate-800/80 to-slate-900/80 border border-slate-700 hover:border-purple-500/50 transition-all"
              >
                {/* Commander Badge */}
                {member.is_commander && (
                  <div className="absolute top-2 right-2">
                    <Crown className="w-4 h-4 text-yellow-400" />
                  </div>
                )}

                {/* Profession Header */}
                <div className="flex items-center space-x-3 mb-3">
                  <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${professionGradient} flex items-center justify-center text-white font-bold text-lg shadow-lg`}>
                    {member.profession_name.charAt(0)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-semibold text-slate-200 truncate">
                      {member.profession_name}
                    </h4>
                    {member.elite_specialization_name && (
                      <p className="text-xs text-purple-300 truncate">
                        {member.elite_specialization_name}
                      </p>
                    )}
                  </div>
                </div>

                {/* Role Badge */}
                <div className="flex items-center space-x-2">
                  <div className={`flex items-center space-x-1 px-2 py-1 rounded-md ${roleColorClass}`}>
                    <RoleIcon className="w-3 h-3" />
                    <span className="text-xs font-medium capitalize">
                      {member.role_type.replace('_', ' ')}
                    </span>
                  </div>
                </div>

                {/* Notes */}
                {member.notes && member.notes !== member.role_type.replace('_', ' ') && (
                  <p className="mt-2 text-xs text-slate-400 truncate">
                    {member.notes}
                  </p>
                )}

                {/* Player Number */}
                <div className="absolute bottom-2 right-2 text-xs text-slate-600 font-mono">
                  #{index + 1}
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Empty Slots */}
        {members.length < squadSize && (
          <div className="mt-4 p-3 rounded-lg bg-slate-800/30 border border-dashed border-slate-700">
            <p className="text-sm text-slate-400 text-center">
              {squadSize - members.length} slot{squadSize - members.length > 1 ? 's' : ''} disponible{squadSize - members.length > 1 ? 's' : ''}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
