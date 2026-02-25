import { FileText } from 'lucide-react';
import type { SearchResult } from '../../types';

interface Props {
  result: SearchResult;
}

export default function SearchResultCard({ result }: Props) {
  return (
    <div className="bg-white border border-slate-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3">
        <div className="p-2 bg-blue-50 rounded-lg">
          <FileText size={18} className="text-blue-600" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-medium text-slate-900 text-sm truncate">{result.file_name}</h3>
            <span className="px-2 py-0.5 bg-slate-100 text-slate-600 text-xs rounded-full uppercase">
              {result.file_type}
            </span>
            <span className="text-xs text-slate-400 ml-auto">
              Score: {result.score.toFixed(3)}
            </span>
          </div>
          <p className="text-sm text-slate-600 line-clamp-3">{result.text}</p>
        </div>
      </div>
    </div>
  );
}
