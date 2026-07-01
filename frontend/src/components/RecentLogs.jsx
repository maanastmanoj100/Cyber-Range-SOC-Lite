export default function RecentLogs({ logs, loading }) {
  if (loading && (!logs || logs.length === 0)) {
    return (
      <div className="card p-4 h-full">
        <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Recent Events</h3>
        <div className="text-gray-600 text-xs pulse">Loading...</div>
      </div>
    )
  }

  return (
    <div className="card p-4 h-full">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Recent Events</h3>
        {logs && logs.length > 0 && (
          <span className="text-[10px] text-gray-600 mono">{logs.length} entries</span>
        )}
      </div>
      <div className="space-y-1.5 max-h-72 overflow-y-auto">
        {logs && logs.length > 0 ? (
          logs.slice(0, 30).map((log, i) => (
            <div key={log.id || i} className="flex items-start gap-2 text-[11px] fade-in py-1 border-b border-[#1e3a5f]/30 last:border-0">
              <span className="text-gray-600 mono whitespace-nowrap w-16 shrink-0">
                {new Date(log.timestamp || Date.now()).toLocaleTimeString()}
              </span>
              <span className="text-gray-400 mono w-28 shrink-0">{log.ip || '—'}</span>
              <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium shrink-0 ${
                log.event_type?.toLowerCase().includes('login') ? 'text-yellow-400 bg-yellow-400/10' :
                log.event_type?.toLowerCase().includes('sqli') || log.event_type?.toLowerCase().includes('sql') ? 'text-red-400 bg-red-400/10' :
                'text-gray-500 bg-gray-500/10'
              }`}>
                {log.event_type || log.attack_type || 'request'}
              </span>
              <span className="text-gray-500 truncate flex-1">{log.endpoint || '—'}</span>
            </div>
          ))
        ) : (
          <div className="text-gray-600 text-xs py-4 text-center">No events recorded yet</div>
        )}
      </div>
    </div>
  )
}
