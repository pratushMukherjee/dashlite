import { useState, useEffect, useRef, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { Send, MessageSquare } from 'lucide-react';
import SourceCard from '../components/ask/SourceCard';
import LoadingSpinner from '../components/shared/LoadingSpinner';
import EmptyState from '../components/shared/EmptyState';
import { askQuestion } from '../api/ask';
import type { AskResponse } from '../types';
import { formatLatency } from '../utils/formatters';

interface QAPair {
  question: string;
  response: AskResponse;
}

export default function AskPage() {
  const [searchParams] = useSearchParams();
  const [question, setQuestion] = useState('');
  const [history, setHistory] = useState<QAPair[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const hasFiredRef = useRef(false);

  const submitQuestion = useCallback(async (q: string) => {
    if (!q.trim() || isLoading) return;
    setIsLoading(true);
    try {
      const data = await askQuestion(q);
      setHistory((prev) => [...prev, { question: data.question, response: data }]);
      setQuestion('');
    } finally {
      setIsLoading(false);
    }
  }, [isLoading]);

  useEffect(() => {
    const q = searchParams.get('q');
    if (q && !hasFiredRef.current) {
      hasFiredRef.current = true;
      setQuestion(q);
      submitQuestion(q);
    }
  }, []);

  const handleSubmit = () => {
    submitQuestion(question);
  };

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold text-slate-900 mb-6">Ask AI</h1>

      {history.length === 0 && !isLoading && (
        <EmptyState
          icon={MessageSquare}
          title="Ask a question about your files"
          description="DashLite will search your indexed documents and provide answers with source citations."
        />
      )}

      <div className="space-y-6 mb-6">
        {history.map((pair, i) => (
          <div key={i} className="space-y-4">
            <div className="flex justify-end">
              <div className="bg-blue-600 text-white px-4 py-2.5 rounded-2xl rounded-br-sm max-w-lg text-sm">
                {pair.question}
              </div>
            </div>
            <div className="bg-white border border-slate-200 rounded-lg p-5">
              <div className="prose prose-sm prose-slate max-w-none mb-4">
                <ReactMarkdown>{pair.response.answer}</ReactMarkdown>
              </div>
              {pair.response.sources.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-slate-500 mb-2 uppercase">Sources</p>
                  <div className="grid grid-cols-2 gap-2">
                    {pair.response.sources.map((source, j) => (
                      <SourceCard key={j} source={source} index={j} />
                    ))}
                  </div>
                </div>
              )}
              <p className="text-xs text-slate-400 mt-3">{formatLatency(pair.response.latency_ms)}</p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex items-center gap-3 py-4">
            <LoadingSpinner size={20} />
            <span className="text-sm text-slate-500">Searching and analyzing your files...</span>
          </div>
        )}
      </div>

      <div className="sticky bottom-4">
        <div className="flex gap-2 bg-white border border-slate-200 rounded-xl p-2 shadow-lg">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
            placeholder="Ask a question about your files..."
            className="flex-1 px-3 py-2 text-sm focus:outline-none"
            disabled={isLoading}
          />
          <button
            onClick={handleSubmit}
            disabled={!question.trim() || isLoading}
            className="p-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
