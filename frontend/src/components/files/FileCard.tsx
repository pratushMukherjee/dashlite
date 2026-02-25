import { FileText, FileImage, FileCode, File } from 'lucide-react';
import type { FileRecord } from '../../types';
import { formatFileSize, formatDate } from '../../utils/formatters';

const typeIcons: Record<string, typeof FileText> = {
  pdf: FileText,
  docx: FileText,
  doc: FileText,
  txt: FileText,
  md: FileText,
  png: FileImage,
  jpg: FileImage,
  jpeg: FileImage,
  py: FileCode,
  js: FileCode,
  ts: FileCode,
  go: FileCode,
};

interface Props {
  file: FileRecord;
  onClick: () => void;
}

export default function FileCard({ file, onClick }: Props) {
  const Icon = typeIcons[file.file_type] || File;

  return (
    <div
      onClick={onClick}
      className="bg-white border border-slate-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
    >
      <div className="flex items-center gap-3 mb-3">
        <div className="p-2.5 bg-blue-50 rounded-lg">
          <Icon size={20} className="text-blue-600" />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-medium text-slate-900 text-sm truncate">{file.file_name}</h3>
          <p className="text-xs text-slate-500">{formatFileSize(file.file_size)}</p>
        </div>
      </div>
      <div className="flex items-center justify-between text-xs text-slate-400">
        <span className="px-2 py-0.5 bg-slate-100 rounded-full uppercase">{file.file_type}</span>
        <span>{file.chunk_count} chunks</span>
      </div>
      {file.status === 'indexed' && file.indexed_at && (
        <p className="text-xs text-slate-400 mt-2">Indexed {formatDate(file.indexed_at)}</p>
      )}
      {file.status === 'error' && (
        <p className="text-xs text-red-500 mt-2">Error: {file.error_message}</p>
      )}
    </div>
  );
}
