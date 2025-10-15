/**
 * ActivityChart Component - GW2 Themed Activity Graph
 * Recharts visualization of user activity over time
 */

import { motion } from "framer-motion";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { TrendingUp } from "lucide-react";

interface ActivityData {
  date: string;
  compositions: number;
  builds: number;
  teams: number;
}

interface ActivityChartProps {
  data?: ActivityData[];
}

// Mock data for demonstration (replace with real API data)
const defaultData: ActivityData[] = [
  { date: "Mon", compositions: 4, builds: 3, teams: 2 },
  { date: "Tue", compositions: 3, builds: 5, teams: 1 },
  { date: "Wed", compositions: 2, builds: 4, teams: 3 },
  { date: "Thu", compositions: 5, builds: 6, teams: 2 },
  { date: "Fri", compositions: 4, builds: 4, teams: 4 },
  { date: "Sat", compositions: 6, builds: 7, teams: 3 },
  { date: "Sun", compositions: 5, builds: 5, teams: 2 },
];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-slate-900/95 backdrop-blur-sm border border-purple-500/30 rounded-xl p-4 shadow-[0_0_20px_rgba(168,85,247,0.3)]">
        <p className="text-slate-300 font-medium mb-2">{label}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} className="text-sm" style={{ color: entry.color }}>
            {entry.name}: {entry.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export default function ActivityChart({
  data = defaultData,
}: ActivityChartProps) {
  return (
    <motion.div
      data-testid="activity-chart"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.6, duration: 0.5 }}
      className="rounded-2xl bg-gradient-to-br from-slate-800/60 to-slate-900/60 backdrop-blur-sm border border-purple-500/20 p-6 shadow-[0_0_20px_rgba(168,85,247,0.2)] hover:shadow-[0_0_30px_rgba(168,85,247,0.3)] transition-all duration-500"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-purple-400" />
            Activity Overview
          </h3>
          <p className="text-sm text-slate-400 mt-1">Last 7 days</p>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-emerald-500" />
            <span className="text-slate-400">Compositions</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-blue-500" />
            <span className="text-slate-400">Builds</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-purple-500" />
            <span className="text-slate-400">Teams</span>
          </div>
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={250}>
        <AreaChart
          data={data}
          margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
        >
          <defs>
            <linearGradient id="colorCompositions" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorBuilds" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorTeams" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#a855f7" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#a855f7" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.2} />
          <XAxis
            dataKey="date"
            stroke="#94a3b8"
            style={{ fontSize: "12px" }}
            tick={{ fill: "#94a3b8" }}
          />
          <YAxis
            stroke="#94a3b8"
            style={{ fontSize: "12px" }}
            tick={{ fill: "#94a3b8" }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="compositions"
            stroke="#10b981"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorCompositions)"
            name="Compositions"
          />
          <Area
            type="monotone"
            dataKey="builds"
            stroke="#3b82f6"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorBuilds)"
            name="Builds"
          />
          <Area
            type="monotone"
            dataKey="teams"
            stroke="#a855f7"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorTeams)"
            name="Teams"
          />
        </AreaChart>
      </ResponsiveContainer>
    </motion.div>
  );
}
