import { FileText } from 'lucide-react';
import type { SourceCitation } from '../../types';

interface Props {
  source: SourceCitation;
  index: number;
}

export default function SourceCard({ source, index }: Props) {
  return (
    <div className="bg-slate-50 border border-slate-200 rounded-lg p-3">
      <div className="flex items-center gap-2 mb-2">
        <span className="w-5 h-5 bg-blue-100 text-blue-700 text-xs font-bold rounded flex items-center justify-center">
          {index + 1}
        </span>
        <FileText size={14} className="text-slate-400" />
        <span className="text-sm font-medium text-slate-700 truncate">{source.file_name}</span>
        <span className="text-xs text-slate-400 ml-auto">
          {(source.relevance_score * 100).toFixed(0)}% relevant
        </span>
      </div>
      <p className="text-xs text-slate-500 line-clamp-2">{source.chunk_text}</p>
    </div>
  );
}
