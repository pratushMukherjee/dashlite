import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import SearchBar from '../components/search/SearchBar';
import StatsPanel from '../components/activity/StatsPanel';
import ActivityFeedComponent from '../components/activity/ActivityFeed';
import { getFileStats } from '../api/files';
import { getActivityFeed, getActivityStats } from '../api/activity';

export default function DashboardPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const { data: fileStats } = useQuery({
    queryKey: ['fileStats'],
    queryFn: getFileStats,
  });

  const { data: activityStats } = useQuery({
    queryKey: ['activityStats'],
    queryFn: getActivityStats,
  });

  const { data: activityFeed } = useQuery({
    queryKey: ['activityFeed'],
    queryFn: () => getActivityFeed(0, 10),
  });

  const handleSearch = () => {
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-10 mt-8">
        <h1 className="text-4xl font-bold text-slate-900 mb-2">
          <span className="text-blue-600">Dash</span>Lite
        </h1>
        <p className="text-slate-500 mb-8">Search, ask, and explore your files with AI</p>
        <SearchBar
          value={searchQuery}
          onChange={setSearchQuery}
          onSubmit={handleSearch}
          placeholder="Search your files with natural language..."
          large
        />
      </div>

      <div className="mb-8">
        <StatsPanel
          totalFiles={fileStats?.total_files ?? 0}
          totalChunks={fileStats?.total_chunks ?? 0}
          totalQueries={activityStats?.total_queries ?? 0}
          queriesToday={activityStats?.queries_today ?? 0}
        />
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white border border-slate-200 rounded-lg p-5">
          <h2 className="text-sm font-semibold text-slate-700 mb-4">Recent Activity</h2>
          <ActivityFeedComponent events={activityFeed?.events ?? []} compact />
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-5">
          <h2 className="text-sm font-semibold text-slate-700 mb-4">Try Asking</h2>
          <div className="space-y-2">
            {[
              'What are the key decisions in the architecture review?',
              'Summarize the quarterly report findings',
              'Compare the API spec with the design doc',
            ].map((q) => (
              <button
                key={q}
                onClick={() => navigate(`/ask?q=${encodeURIComponent(q)}`)}
                className="w-full text-left px-3 py-2 text-sm text-slate-600 bg-slate-50 rounded-lg hover:bg-blue-50 hover:text-blue-700 transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
