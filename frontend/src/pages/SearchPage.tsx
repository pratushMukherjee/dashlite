import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import SearchBar from '../components/search/SearchBar';
import SearchResultCard from '../components/search/SearchResultCard';
import LoadingSpinner from '../components/shared/LoadingSpinner';
import EmptyState from '../components/shared/EmptyState';
import { searchFiles } from '../api/search';
import { Search } from 'lucide-react';

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get('q') || '');

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['search', query],
    queryFn: () => searchFiles(query),
    enabled: query.length > 0,
  });

  useEffect(() => {
    const q = searchParams.get('q');
    if (q) setQuery(q);
  }, [searchParams]);

  const handleSearch = () => {
    if (query.trim()) {
      setSearchParams({ q: query });
      refetch();
    }
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900 mb-4">Search</h1>
        <SearchBar value={query} onChange={setQuery} onSubmit={handleSearch} />
      </div>

      {data && (
        <p className="text-sm text-slate-500 mb-4">
          {data.total} results for "{data.query}" ({data.latency_ms}ms)
        </p>
      )}

      {isLoading && (
        <div className="flex justify-center py-12">
          <LoadingSpinner />
        </div>
      )}

      {data && data.results.length > 0 && (
        <div className="space-y-3">
          {data.results.map((result) => (
            <SearchResultCard key={result.chunk_id} result={result} />
          ))}
        </div>
      )}

      {data && data.results.length === 0 && (
        <EmptyState
          icon={Search}
          title="No results found"
          description="Try a different query or ingest more files to search through."
        />
      )}
    </div>
  );
}
