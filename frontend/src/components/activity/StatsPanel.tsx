import { Files, Layers, Search, Clock } from 'lucide-react';

interface Props {
  totalFiles: number;
  totalChunks: number;
  totalQueries: number;
  queriesToday: number;
}

export default function StatsPanel({ totalFiles, totalChunks, totalQueries, queriesToday }: Props) {
  const stats = [
    { label: 'Files Indexed', value: totalFiles, icon: Files, color: 'text-blue-600 bg-blue-50' },
    { label: 'Total Chunks', value: totalChunks, icon: Layers, color: 'text-purple-600 bg-purple-50' },
    { label: 'Total Queries', value: totalQueries, icon: Search, color: 'text-green-600 bg-green-50' },
    { label: 'Queries Today', value: queriesToday, icon: Clock, color: 'text-orange-600 bg-orange-50' },
  ];

  return (
    <div className="grid grid-cols-4 gap-4">
      {stats.map(({ label, value, icon: Icon, color }) => (
        <div key={label} className="bg-white border border-slate-200 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${color}`}>
              <Icon size={18} />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-900">{value.toLocaleString()}</p>
              <p className="text-xs text-slate-500">{label}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
