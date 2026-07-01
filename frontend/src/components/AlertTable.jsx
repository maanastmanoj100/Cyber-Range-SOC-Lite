const sevClass = {
  Critical: 'bg-red-600/20 text-red-400 border-red-600/30',
  High: 'bg-orange-600/20 text-orange-400 border-orange-600/30',
  Medium: 'bg-yellow-600/20 text-yellow-400 border-yellow-600/30',
  Low: 'bg-green-600/20 text-green-400 border-green-600/30',
}

export default function AlertTable({ alerts, onResolve, onDelete, loading }) {
  if (loading && (!alerts || alerts.length === 0)) {
    return (
      <div className="card p-8 text-center">
        <div className="text-gray-500 text-sm pulse">Loading alerts...</div>
      </div>
    )
  }

  if (!alerts || alerts.length === 0) {
    return (
      <div className="card p-8 text-center">
        <div className="text-gray-600 text-sm">No alerts detected. Simulate an attack to populate the dashboard.</div>
      </div>
    )
  }

  return (
    <div className="card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-[#1e3a5f] bg-[#0d1525]">
              <th className="text-left py-3 px-4 text-gray-500 font-semibold uppercase tracking-wider">Severity</th>
              <th className="text-left py-3 px-4 text-gray-500 font-semibold uppercase tracking-wider">Timestamp</th>
              <th className="text-left py-3 px-4 text-gray-500 font-semibold uppercase tracking-wider">Attack Type</th>
              <th className="text-left py-3 px-4 text-gray-500 font-semibold uppercase tracking-wider">Source IP</th>
              <th className="text-left py-3 px-4 text-gray-500 font-semibold uppercase tracking-wider">Destination</th>
              <th className="text-left py-3 px-4 text-gray-500 font-semibold uppercase tracking-wider">Status</th>
              <th className="text-right py-3 px-4 text-gray-500 font-semibold uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map((a, i) => (
              <tr
                key={a.id || i}
                className="border-b border-[#1e3a5f]/50 hover:bg-[#1a2035] transition fade-in"
                style={{ animationDelay: `${i * 30}ms` }}
              >
                <td className="py-3 px-4">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${sevClass[a.severity] || 'bg-gray-600/20 text-gray-400 border-gray-600/30'}`}>
                    {a.severity}
                  </span>
                </td>
                <td className="py-3 px-4 text-gray-400 mono whitespace-nowrap">
                  {new Date(a.timestamp || a.created_at || Date.now()).toLocaleString()}
                </td>
                <td className="py-3 px-4">
                  <span className="text-cyan-300 font-medium">{a.attack_type || a.event_type || '—'}</span>
                </td>
                <td className="py-3 px-4 mono text-gray-400">{a.ip || a.source_ip || '—'}</td>
                <td className="py-3 px-4 mono text-gray-500">{a.destination_ip || '—'}</td>
                <td className="py-3 px-4">
                  {a.is_resolved
                    ? <span className="text-green-500 text-[10px] font-semibold">Resolved</span>
                    : a.is_acknowledged
                      ? <span className="text-yellow-500 text-[10px] font-semibold">Acknowledged</span>
                      : <span className="text-gray-500 text-[10px] font-semibold">Open</span>}
                </td>
                <td className="py-3 px-4 text-right">
                  <div className="flex gap-2 justify-end">
                    {!a.is_resolved && (
                      <button
                        onClick={() => onResolve(a.id)}
                        className="text-[10px] px-2 py-1 rounded border border-green-600/30 text-green-500 hover:bg-green-600/10 transition"
                      >
                        Resolve
                      </button>
                    )}
                    <button
                      onClick={() => onDelete(a.id)}
                      className="text-[10px] px-2 py-1 rounded border border-red-600/30 text-red-500 hover:bg-red-600/10 transition"
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
