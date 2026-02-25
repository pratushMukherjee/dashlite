import { FilePlus, Search, MessageSquare, Bot, FileText, Trash2 } from 'lucide-react';
import type { ActivityEvent } from '../../types';
import { formatDate } from '../../utils/formatters';

const eventIcons: Record<string, typeof FilePlus> = {
  file_added: FilePlus,
  file_deleted: Trash2,
  query_search: Search,
  query_ask: MessageSquare,
  query_agent: Bot,
  summary_generated: FileText,
};

const eventColors: Record<string, string> = {
  file_added: 'bg-green-100 text-green-600',
  file_deleted: 'bg-red-100 text-red-600',
  query_search: 'bg-blue-100 text-blue-600',
  query_ask: 'bg-purple-100 text-purple-600',
  query_agent: 'bg-orange-100 text-orange-600',
  summary_generated: 'bg-teal-100 text-teal-600',
};

interface Props {
  events: ActivityEvent[];
  compact?: boolean;
}

export default function ActivityFeedComponent({ events, compact = false }: Props) {
  if (events.length === 0) {
    return <p className="text-sm text-slate-400 text-center py-4">No activity yet</p>;
  }

  return (
    <div className="space-y-2">
      {events.map((event) => {
        const Icon = eventIcons[event.event_type] || FileText;
        const colorClass = eventColors[event.event_type] || 'bg-slate-100 text-slate-600';
        return (
          <div key={event.id} className="flex items-center gap-3 py-2">
            <div className={`w-7 h-7 rounded-full flex items-center justify-center ${colorClass}`}>
              <Icon size={14} />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-slate-700 truncate">
                {event.event_type.replace(/_/g, ' ')}
                {event.detail && !compact && (() => {
                  try {
                    const d = JSON.parse(event.detail);
                    return <span className="text-slate-400"> — {d.file_name || d.query || event.detail}</span>;
                  } catch {
                    return <span className="text-slate-400"> — {event.detail}</span>;
                  }
                })()}
              </p>
            </div>
            <span className="text-xs text-slate-400 whitespace-nowrap">
              {formatDate(event.created_at)}
            </span>
          </div>
        );
      })}
    </div>
  );
}
