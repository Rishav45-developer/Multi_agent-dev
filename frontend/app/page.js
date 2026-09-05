'use client';

import { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Zap, Check, FileCode2, Download, Copy, Terminal, Loader2, ClipboardList, Code2, FlaskConical, ShieldCheck, Wrench } from 'lucide-react';

const AGENTS = [
  { name: 'Planner', icon: ClipboardList, color: 'blue' },
  { name: 'Coder', icon: Code2, color: 'purple' },
  { name: 'Tester', icon: FlaskConical, color: 'amber' },
  { name: 'Reviewer', icon: ShieldCheck, color: 'green' },
  { name: 'Debugger', icon: Wrench, color: 'rose' },
];

const COLOR_MAP = {
  blue: { border: 'border-blue-500/40', glow: 'shadow-blue-500/20', text: 'text-blue-400', bg: 'bg-blue-500/10' },
  purple: { border: 'border-purple-500/40', glow: 'shadow-purple-500/20', text: 'text-purple-400', bg: 'bg-purple-500/10' },
  amber: { border: 'border-amber-500/40', glow: 'shadow-amber-500/20', text: 'text-amber-400', bg: 'bg-amber-500/10' },
  green: { border: 'border-green-500/40', glow: 'shadow-green-500/20', text: 'text-green-400', bg: 'bg-green-500/10' },
  rose: { border: 'border-rose-500/40', glow: 'shadow-rose-500/20', text: 'text-rose-400', bg: 'bg-rose-500/10' },
};

export default function Home() {
  const [task, setTask] = useState('');
  const [framework, setFramework] = useState('fastapi');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [activeFile, setActiveFile] = useState(null);
  const [activeTab, setActiveTab] = useState('files');
  const [elapsedMs, setElapsedMs] = useState(null);
  const [copied, setCopied] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    setError('');
    setResult(null);
    setElapsedMs(null);
    const start = performance.now();

    try {
      const response = await fetch('http://127.0.0.1:8000/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task, framework }),
      });

      if (!response.ok) throw new Error('Something went wrong on the server.');

      const data = await response.json();
      setResult(data);
      setElapsedMs(Math.round(performance.now() - start));
      const firstFile = Object.keys(data.files || {})[0];
      setActiveFile(firstFile);
      setActiveTab('files');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (!activeFile) return;
    navigator.clipboard.writeText(result.files[activeFile]);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const language = framework === 'nodejs' ? 'javascript' : 'python';
  const fileCount = result ? Object.keys(result.files || {}).length : 0;

  return (
    <div className="min-h-screen text-white" style={{ background: 'radial-gradient(ellipse 80% 50% at 50% -10%, #0d1526 0%, #000000 60%)' }}>
      <div className="max-w-4xl mx-auto p-6">

        <div className="border border-gray-800 rounded-xl p-5 mb-6 bg-black/40">
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div className="flex items-center gap-3">
              <div className="border border-blue-500/50 rounded-lg p-2 bg-blue-500/10">
                <Zap size={18} className="text-blue-400" />
              </div>
              <div>
                <p className="font-semibold">AgentForge <span className="text-gray-500 font-normal">/ Multi-Agent Backend Generator</span></p>
                <p className="text-xs text-gray-500">5-agent pipeline &middot; Planner, Coder, Tester, Reviewer, Debugger</p>
              </div>
            </div>

            <a href={result ? `http://127.0.0.1:8000/download/${result.task_id}` : undefined} className={`flex items-center gap-2 text-sm px-4 py-2 rounded font-medium ${result ? 'bg-blue-600 hover:bg-blue-700 text-white' : 'bg-gray-900 text-gray-600 cursor-not-allowed pointer-events-none'}`}>
              <Download size={14} /> Export Repo (.zip)
            </a>
          </div>
        </div>

        <div className="border border-gray-800 rounded-xl p-6 mb-6 bg-black/40">
          <div className="flex items-center justify-between mb-2">
            <label className="text-xs font-semibold text-gray-400 tracking-wide">DESCRIBE THE BACKEND YOU WANT</label>
            <span className="text-xs text-gray-600">{task.length} chars</span>
          </div>

          <div className="glow-wrapper mb-4">
            <div className="glow-border p-[1px]">
              <textarea
                className="w-full bg-black rounded-[7px] p-4 text-white focus:outline-none resize-none"
                rows="4"
                placeholder="e.g. a todo app with create, read, update, delete endpoints"
                value={task}
                onChange={(e) => setTask(e.target.value)}
              />
            </div>
          </div>

          <div className="flex items-center gap-3 flex-wrap">
            <select value={framework} onChange={(e) => setFramework(e.target.value)} className="bg-black border border-gray-700 rounded-lg p-2.5 text-sm">
              <option value="fastapi">FastAPI</option>
              <option value="nodejs">Node.js (Express)</option>
            </select>

            <span className="text-xs text-gray-500">5 Active Agents: Planner &rarr; Coder &rarr; Tester &rarr; Reviewer &rarr; Debugger</span>

            <button onClick={handleGenerate} disabled={loading || !task} className="ml-auto flex items-center gap-2 bg-gradient-to-r from-blue-600 to-cyan-500 hover:opacity-90 disabled:opacity-40 text-white px-5 py-2.5 rounded-lg font-medium">
              {loading ? <><Loader2 size={16} className="animate-spin" /> Generating...</> : <>Generate Backend</>}
            </button>
          </div>
        </div>

        <div className="flex items-center gap-2 mb-6">
          {AGENTS.map(({ name, icon: Icon, color }, i) => {
            const c = COLOR_MAP[color];
            const done = !!result;
            const working = loading;
            return (
              <div key={name} className="flex items-center flex-1">
                <div
                  className={`relative rounded-xl p-4 bg-black/60 border transition-all duration-300 w-full ${
                    done ? `${c.border} shadow-lg ${c.glow}` : working ? `${c.border} shadow-lg ${c.glow} animate-pulse` : 'border-gray-800'
                  }`}
                >
                  <div className={`w-9 h-9 rounded-lg flex items-center justify-center mb-2 ${done || working ? c.bg : 'bg-gray-900'}`}>
                    <Icon size={16} className={done || working ? c.text : 'text-gray-600'} />
                  </div>
                  <p className="text-sm font-semibold mb-1">{name}</p>
                  <div className="flex items-center gap-1.5">
                    {done ? (
                      <>
                        <Check size={12} className="text-green-500" />
                        <span className="text-xs text-green-500">Done</span>
                      </>
                    ) : working ? (
                      <>
                        <Loader2 size={12} className={`animate-spin ${c.text}`} />
                        <span className={`text-xs ${c.text}`}>Working...</span>
                      </>
                    ) : (
                      <span className="text-xs text-gray-600">Idle</span>
                    )}
                  </div>
                </div>
                {i < AGENTS.length - 1 && (
                  <div className="px-1 text-gray-700 shrink-0">&rarr;</div>
                )}
              </div>
            );
          })}
        </div>

        {result && (
          <div className="flex items-center gap-4 text-xs text-gray-500 mb-6 flex-wrap">
            {elapsedMs !== null && <span>Generation time: <span className="text-gray-300 font-mono">{(elapsedMs / 1000).toFixed(2)}s</span></span>}
            <span>&middot;</span>
            <span>Debugger iterations: <span className="text-gray-300 font-mono">{result.iteration}</span></span>
          </div>
        )}

        {error && <p className="text-red-500 mb-6">{error}</p>}

        {result && (
          <div>
            <h2 className="text-xl font-bold mb-1">Execution Result</h2>
            <p className="text-sm text-gray-500 mb-4">{fileCount} file{fileCount !== 1 ? 's' : ''} generated</p>

            <div className="flex gap-2 mb-4 flex-wrap">
              <span className="flex items-center gap-2 bg-green-950 text-green-400 border border-green-800 px-3 py-1.5 rounded-full text-xs">
                <Check size={13} /> Passed: {String(result.passed)}
              </span>
              <span className="flex items-center gap-2 bg-green-950 text-green-400 border border-green-800 px-3 py-1.5 rounded-full text-xs">
                <Check size={13} /> Approved: {String(result.approved)}
              </span>
            </div>

            <div className="border border-gray-800 rounded-xl overflow-hidden bg-[#0a0e14]">
              <div className="flex items-center border-b border-gray-800 px-2">
                <button onClick={() => setActiveTab('files')} className={`flex items-center gap-2 px-4 py-3 text-sm font-medium ${activeTab === 'files' ? 'text-white border-b-2 border-blue-500' : 'text-gray-500 hover:text-gray-300'}`}>
                  <FileCode2 size={14} /> Code Files ({fileCount})
                </button>
                <button onClick={() => setActiveTab('logs')} className={`flex items-center gap-2 px-4 py-3 text-sm font-medium ${activeTab === 'logs' ? 'text-white border-b-2 border-blue-500' : 'text-gray-500 hover:text-gray-300'}`}>
                  <Terminal size={14} /> Test Results
                </button>
              </div>

              {activeTab === 'files' && (
                <div>
                  <div className="flex border-b border-gray-800 overflow-x-auto">
                    {Object.keys(result.files || {}).map((filename) => (
                      <button key={filename} onClick={() => setActiveFile(filename)} className={`flex items-center gap-2 px-4 py-2.5 text-sm font-mono whitespace-nowrap ${activeFile === filename ? 'bg-gray-900 text-white' : 'text-gray-500 hover:text-gray-300'}`}>
                        {filename}
                      </button>
                    ))}
                  </div>

                  {activeFile && (
                    <div>
                      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-900">
                        <span className="text-xs text-gray-500 font-mono">{activeFile}</span>
                        <button onClick={handleCopy} className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-white">
                          <Copy size={12} /> {copied ? 'Copied!' : 'Copy Code'}
                        </button>
                      </div>
                      <SyntaxHighlighter language={language} style={vscDarkPlus} showLineNumbers customStyle={{ margin: 0, padding: '1.25rem', background: 'transparent', fontSize: '0.85rem' }}>
                        {result.files[activeFile]}
                      </SyntaxHighlighter>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'logs' && (
                <pre className="p-5 text-sm text-gray-300 font-mono whitespace-pre-wrap">{result.test_result}</pre>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}