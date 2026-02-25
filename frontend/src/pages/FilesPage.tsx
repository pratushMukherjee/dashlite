import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { FolderPlus, Files } from 'lucide-react';
import FileCard from '../components/files/FileCard';
import LoadingSpinner from '../components/shared/LoadingSpinner';
import EmptyState from '../components/shared/EmptyState';
import { getFiles } from '../api/files';
import { ingestDirectory } from '../api/ingest';

export default function FilesPage() {
  const [dirPath, setDirPath] = useState('');
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['files'],
    queryFn: () => getFiles(0, 50),
  });

  const ingestMutation = useMutation({
    mutationFn: ingestDirectory,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files'] });
      queryClient.invalidateQueries({ queryKey: ['fileStats'] });
      setDirPath('');
    },
  });

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Files</h1>
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={dirPath}
            onChange={(e) => setDirPath(e.target.value)}
            placeholder="Directory path to ingest..."
            className="px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-72"
          />
          <button
            onClick={() => dirPath && ingestMutation.mutate(dirPath)}
            disabled={!dirPath || ingestMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <FolderPlus size={16} />
            {ingestMutation.isPending ? 'Ingesting...' : 'Add Folder'}
          </button>
        </div>
      </div>

      {ingestMutation.isSuccess && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-700">
          Directory ingested successfully!
        </div>
      )}

      {ingestMutation.isError && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
          Error: {(ingestMutation.error as Error).message}
        </div>
      )}

      {isLoading && (
        <div className="flex justify-center py-12">
          <LoadingSpinner />
        </div>
      )}

      {data && data.files.length > 0 && (
        <>
          <p className="text-sm text-slate-500 mb-4">{data.total} files indexed</p>
          <div className="grid grid-cols-3 gap-4">
            {data.files.map((file) => (
              <FileCard
                key={file.id}
                file={file}
                onClick={() => {}}
              />
            ))}
          </div>
        </>
      )}

      {data && data.files.length === 0 && (
        <EmptyState
          icon={Files}
          title="No files indexed yet"
          description="Add a folder above to start indexing files for search and AI queries."
        />
      )}
    </div>
  );
}
