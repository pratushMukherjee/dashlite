import { motion } from 'framer-motion';
import { CheckCircle, Search, FileText, GitCompare, Brain, Loader2 } from 'lucide-react';
import type { AgentStep } from '../../types';

const toolIcons: Record<string, typeof Search> = {
  search: Search,
  summarize: FileText,
  compare: GitCompare,
  extract: FileText,
  analyze: Brain,
};

interface Props {
  steps: AgentStep[];
  isRunning: boolean;
}

export default function StepTimeline({ steps, isRunning }: Props) {
  return (
    <div className="space-y-3">
      {steps.map((step, i) => {
        const Icon = step.tool ? (toolIcons[step.tool] || Brain) : Brain;
        return (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.1 }}
            className="flex items-start gap-3"
          >
            <div className="flex flex-col items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                step.step_type === 'plan' ? 'bg-purple-100 text-purple-600' :
                step.step_type === 'synthesize' ? 'bg-green-100 text-green-600' :
                'bg-blue-100 text-blue-600'
              }`}>
                <Icon size={16} />
              </div>
              {i < steps.length - 1 && <div className="w-0.5 h-6 bg-slate-200 mt-1" />}
            </div>
            <div className="flex-1 pb-4">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-slate-800">{step.description}</span>
                <span className="text-xs text-slate-400">{step.duration_ms}ms</span>
              </div>
              {step.detail && (
                <p className="text-xs text-slate-500 mt-1 line-clamp-2">{step.detail}</p>
              )}
            </div>
            <CheckCircle size={16} className="text-green-500 mt-1" />
          </motion.div>
        );
      })}
      {isRunning && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex items-center gap-3 text-slate-400"
        >
          <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center">
            <Loader2 size={16} className="animate-spin" />
          </div>
          <span className="text-sm">Processing...</span>
        </motion.div>
      )}
    </div>
  );
}
