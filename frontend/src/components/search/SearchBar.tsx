import { Search } from 'lucide-react';

interface Props {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  placeholder?: string;
  large?: boolean;
}

export default function SearchBar({ value, onChange, onSubmit, placeholder = 'Search your files...', large = false }: Props) {
  return (
    <div className={`relative ${large ? 'max-w-2xl mx-auto' : 'w-full'}`}>
      <Search
        size={large ? 22 : 18}
        className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"
      />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && onSubmit()}
        placeholder={placeholder}
        className={`w-full bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow shadow-sm hover:shadow-md ${
          large ? 'pl-12 pr-6 py-4 text-lg' : 'pl-10 pr-4 py-2.5 text-sm'
        }`}
      />
    </div>
  );
}
