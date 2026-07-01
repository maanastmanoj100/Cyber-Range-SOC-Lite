const cards = [
  { key: 'total', label: 'Total Attacks', color: 'text-gray-100', border: 'border-gray-600/30' },
  { key: 'critical', label: 'Critical', color: 'text-red-400', border: 'border-red-500/30', glow: 'glow-red' },
  { key: 'high', label: 'High', color: 'text-orange-400', border: 'border-orange-500/30' },
  { key: 'medium', label: 'Medium', color: 'text-yellow-400', border: 'border-yellow-500/30' },
  { key: 'low', label: 'Low', color: 'text-green-400', border: 'border-green-500/30' },
  { key: 'activeIps', label: 'Active IPs', color: 'text-cyan-400', border: 'border-cyan-500/30' },
]

export default function StatsCards({ summary }) {
  if (!summary) return null

  const raw = summary
  const values = {
    total: raw.total_alerts ?? 0,
    critical: raw.critical_count ?? 0,
    high: raw.high_count ?? 0,
    medium: raw.medium_count ?? 0,
    low: raw.low_count ?? 0,
    activeIps: raw.active_ips ?? raw.total_alerts ?? 0,
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      {cards.map((c) => (
        <div
          key={c.key}
          className={`card p-4 fade-in ${c.glow || ''}`}
          style={{ borderColor: c.key === 'critical' && values.critical > 0 ? 'rgba(239,68,68,0.4)' : undefined }}
        >
          <div className={`stat-value ${c.color}`}>{values[c.key].toLocaleString()}</div>
          <div className="stat-label text-gray-500 mt-1">{c.label}</div>
        </div>
      ))}
    </div>
  )
}
