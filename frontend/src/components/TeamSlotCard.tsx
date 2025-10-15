/**
 * TeamSlotCard Component
 * Interactive card for assigning class, build, and role to a team slot
 */

import { motion } from "framer-motion";
import { User, Trash2, Edit2 } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

interface TeamSlotCardProps {
  slotNumber: number;
  profession?: string;
  role?: string;
  build?: string;
  playerName?: string;
  isEmpty?: boolean;
  onEdit?: () => void;
  onRemove?: () => void;
  onClick?: () => void;
}

const professionColors: Record<string, string> = {
  Guardian: "#72C1D9",
  Warrior: "#FFD166",
  Engineer: "#D09C59",
  Ranger: "#8CDC82",
  Thief: "#C08F95",
  Elementalist: "#F68A87",
  Mesmer: "#B679D5",
  Necromancer: "#52A76F",
  Revenant: "#D16E5A",
};

export default function TeamSlotCard({
  slotNumber,
  profession,
  role,
  build,
  playerName,
  isEmpty = true,
  onEdit,
  onRemove,
  onClick,
}: TeamSlotCardProps) {
  const [isHovered, setIsHovered] = useState(false);

  const professionColor = profession
    ? professionColors[profession] || "#A855F7"
    : "#64748b";

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02, y: -4 }}
      transition={{ duration: 0.3 }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      onClick={onClick}
      className={cn(
        "relative rounded-xl p-4 backdrop-blur-sm cursor-pointer transition-all duration-300",
        isEmpty
          ? "bg-slate-800/40 border-2 border-dashed border-slate-600/50 hover:border-purple-500/50 hover:bg-slate-800/60"
          : "bg-gradient-to-br from-slate-800/80 to-slate-900/80 border-2 border-solid hover:shadow-[0_0_20px_rgba(168,85,247,0.3)]",
      )}
      style={{
        borderColor: !isEmpty ? `${professionColor}50` : undefined,
      }}
    >
      {/* Slot Number Badge */}
      <div
        className="absolute -top-3 -left-3 w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm shadow-lg"
        style={{
          background: isEmpty ? "#64748b" : professionColor,
          boxShadow: isEmpty ? undefined : `0 0 15px ${professionColor}80`,
        }}
      >
        {slotNumber}
      </div>

      {isEmpty ? (
        /* Empty Slot */
        <div className="flex flex-col items-center justify-center py-6 text-slate-400">
          <User className="w-8 h-8 mb-2 opacity-50" />
          <p className="text-sm font-medium">Empty Slot</p>
          <p className="text-xs mt-1 opacity-70">Click to assign</p>
        </div>
      ) : (
        /* Filled Slot */
        <>
          {/* Profession Header */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <div
                className="w-3 h-3 rounded-full shadow-lg"
                style={{
                  background: professionColor,
                  boxShadow: `0 0 10px ${professionColor}`,
                }}
              />
              <h3
                className="font-bold text-lg"
                style={{ color: professionColor }}
              >
                {profession}
              </h3>
            </div>

            {/* Action Buttons */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: isHovered ? 1 : 0 }}
              className="flex space-x-1"
            >
              {onEdit && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onEdit();
                  }}
                  className="p-1.5 rounded-lg bg-blue-500/20 hover:bg-blue-500/30 border border-blue-500/30 transition-colors"
                >
                  <Edit2 className="w-4 h-4 text-blue-400" />
                </button>
              )}
              {onRemove && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onRemove();
                  }}
                  className="p-1.5 rounded-lg bg-red-500/20 hover:bg-red-500/30 border border-red-500/30 transition-colors"
                >
                  <Trash2 className="w-4 h-4 text-red-400" />
                </button>
              )}
            </motion.div>
          </div>

          {/* Role Badge */}
          {role && (
            <div className="mb-2">
              <span className="inline-block px-3 py-1 rounded-full text-xs font-medium bg-purple-500/20 text-purple-300 border border-purple-500/30">
                {role}
              </span>
            </div>
          )}

          {/* Build Name */}
          {build && (
            <p className="text-sm text-slate-300 mb-2 font-medium">
              📋 {build}
            </p>
          )}

          {/* Player Name */}
          {playerName && (
            <div className="flex items-center space-x-2 mt-2 pt-2 border-t border-slate-700/50">
              <User className="w-4 h-4 text-slate-400" />
              <p className="text-xs text-slate-400">{playerName}</p>
            </div>
          )}
        </>
      )}

      {/* Glow Effect */}
      {!isEmpty && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: isHovered ? 0.3 : 0 }}
          className="absolute inset-0 rounded-xl blur-xl"
          style={{
            background: `radial-gradient(circle at center, ${professionColor}, transparent 70%)`,
          }}
        />
      )}
    </motion.div>
  );
}
