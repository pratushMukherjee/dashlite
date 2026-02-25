import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import ReactMarkdown from 'react-markdown';
import { Send, Bot } from 'lucide-react';
import StepTimeline from '../components/agent/StepTimeline';
import LoadingSpinner from '../components/shared/LoadingSpinner';
import EmptyState from '../components/shared/EmptyState';
import { runAgentQuery } from '../api/agent';
import type { AgentResponse } from '../types';
import { formatLatency } from '../utils/formatters';

export default function AgentPage() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<AgentResponse | null>(null);

  const agentMutation = useMutation({
    mutationFn: runAgentQuery,
    onSuccess: (data) => {
      setResult(data);
      setQuery('');
    },
  });

  const handleSubmit = () => {
    if (query.trim() && !agentMutation.isPending) {
      setResult(null);
      agentMutation.mutate(query);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold text-slate-900 mb-2">Multi-Step Agent</h1>
      <p className="text-sm text-slate-500 mb-6">
        Ask complex questions that require searching, comparing, and analyzing across multiple documents.
        The agent will plan and execute a multi-step strategy.
      </p>

      {!result && !agentMutation.isPending && (
        <EmptyState
          icon={Bot}
          title="Ask a complex question"
          description="The agent will decompose your query into steps, execute them, and synthesize a comprehensive answer."
        />
      )}

      {agentMutation.isPending && (
        <div className="bg-white border border-slate-200 rounded-lg p-6">
          <div className="flex items-center gap-3 mb-6">
            <LoadingSpinner size={20} />
            <span className="text-sm font-medium text-slate-700">Agent is working...</span>
          </div>
          <StepTimeline steps={[]} isRunning />
        </div>
      )}

      {result && (
        <div className="space-y-4 mb-6">
          <div className="flex justify-end">
            <div className="bg-blue-600 text-white px-4 py-2.5 rounded-2xl rounded-br-sm max-w-lg text-sm">
              {result.query}
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-lg p-6">
            <h3 className="text-sm font-semibold text-slate-700 mb-4">Execution Steps</h3>
            <StepTimeline steps={result.steps} isRunning={false} />
          </div>

          <div className="bg-white border border-slate-200 rounded-lg p-6">
            <h3 className="text-sm font-semibold text-slate-700 mb-3">Answer</h3>
            <div className="prose prose-sm prose-slate max-w-none">
              <ReactMarkdown>{result.answer}</ReactMarkdown>
            </div>
            <p className="text-xs text-slate-400 mt-4">
              Completed in {formatLatency(result.latency_ms)} with {result.steps.length} steps
            </p>
          </div>
        </div>
      )}

      <div className="sticky bottom-4">
        <div className="flex gap-2 bg-white border border-slate-200 rounded-xl p-2 shadow-lg">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
            placeholder="Ask a complex question (e.g., Compare the design doc and API spec...)"
            className="flex-1 px-3 py-2 text-sm focus:outline-none"
            disabled={agentMutation.isPending}
          />
          <button
            onClick={handleSubmit}
            disabled={!query.trim() || agentMutation.isPending}
            className="p-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
