import { useState, useEffect } from 'react'

export default function Header({ lastUpdated, onRefresh, onSimulate, onBatch, loading }) {
  const [time, setTime] = useState(new Date())

  useEffect(() => {
    const id = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(id)
  }, [])

  return (
    <header className="bg-[#111827] border-b border-[#1e3a5f] px-6 py-3 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center">
            <span className="text-cyan-400 text-lg font-bold mono">&lt;/&gt;</span>
          </div>
          <div>
            <h1 className="text-base font-bold text-cyan-400 tracking-wide">Cyber Range SOC</h1>
            <p className="text-[10px] text-gray-500 tracking-widest uppercase">Security Operations Center</p>
          </div>
        </div>
        <div className="h-8 w-px bg-[#1e3a5f] mx-2" />
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span className="inline-block w-2 h-2 rounded-full bg-green-500 pulse" />
          <span>All Systems Online</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="text-right">
          <div className="text-xs text-gray-500 mono">{time.toLocaleDateString()}</div>
          <div className="text-sm text-cyan-400 mono font-semibold">{time.toLocaleTimeString()}</div>
        </div>

        <div className="h-8 w-px bg-[#1e3a5f]" />

        {lastUpdated && (
          <div className="text-[10px] text-gray-500 mono">
            Updated {lastUpdated.toLocaleTimeString()}
          </div>
        )}

        <div className="flex gap-2">
          <button
            onClick={onRefresh}
            disabled={loading}
            className="text-xs px-3 py-1.5 rounded border border-[#1e3a5f] text-gray-400 hover:border-cyan-500/40 hover:text-cyan-400 transition disabled:opacity-50"
          >
            &#x21bb; Refresh
          </button>
          <button
            onClick={onSimulate}
            disabled={loading}
            className="text-xs px-3 py-1.5 rounded bg-red-600/20 border border-red-600/40 text-red-400 hover:bg-red-600/30 transition disabled:opacity-50"
          >
            + Attack
          </button>
          <button
            onClick={onBatch}
            disabled={loading}
            className="text-xs px-3 py-1.5 rounded bg-orange-600/20 border border-orange-600/40 text-orange-400 hover:bg-orange-600/30 transition disabled:opacity-50"
          >
            + Batch 5
          </button>
        </div>
      </div>
    </header>
  )
}
