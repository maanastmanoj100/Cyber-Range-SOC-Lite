import { useState, useCallback, useRef } from 'react'
import { api } from './api/client'
import { usePolling } from './hooks/usePolling'
import Header from './components/Header'
import StatsCards from './components/StatsCards'
import Charts from './components/Charts'
import AlertTable from './components/AlertTable'
import RecentLogs from './components/RecentLogs'
import AttackReplay from './components/AttackReplay'

const TABS = ['Dashboard', 'Attack Replay']

function computeSummary(alerts) {
  const critical = alerts.filter(a => a.severity === 'Critical')
  return {
    total_alerts: alerts.length,
    critical_count: critical.length,
    high_count: alerts.filter(a => a.severity === 'High').length,
    medium_count: alerts.filter(a => a.severity === 'Medium').length,
    low_count: alerts.filter(a => a.severity === 'Low').length,
    active_ips: new Set(alerts.map(a => a.ip || a.source_ip)).size,
    has_critical: critical.length > 0,
  }
}

export default function App() {
  const [tab, setTab] = useState('Dashboard')

  const [logs, setLogs] = useState([])
  const [detectionAlerts, setDetectionAlerts] = useState([])
  const [explanations, setExplanations] = useState({})
  const [summary, setSummary] = useState(null)

  const [loading, setLoading] = useState(false)
  const [lastUpdated, setLastUpdated] = useState(null)
  const [error, setError] = useState(null)
  const explainedRef = useRef(new Set())

  const runPipeline = useCallback(async () => {
    try {
      const freshLogs = await api.getLogs({ limit: 100 }).catch(() => [])

      let detAlerts = []
      if (freshLogs.length > 0) {
        const result = await api.analyzeLogs(freshLogs).catch(() => null)
        detAlerts = result?.alerts || []
      }

      const newExplanations = {}
      const today = new Set(explainedRef.current)

      for (const alert of detAlerts) {
        const key = `${alert.attack_type}|${alert.source_ip || alert.ip}`
        if (today.has(key)) continue

        const result = await api.explainAlert(
          alert.attack_type,
          freshLogs.filter(l => l.ip === (alert.source_ip || alert.ip)),
          alert.source_ip || alert.ip,
        ).catch(() => null)

        if (result) {
          newExplanations[key] = result
          today.add(key)
        }
      }

      const enriched = detAlerts.map(a => {
        const key = `${a.attack_type}|${a.source_ip || a.ip}`
        return { ...a, explain: explanations[key] || newExplanations[key] || null }
      })

      const mergedExplanations = { ...explanations, ...newExplanations }
      const fullyEnriched = enriched.map(a => {
        const key = `${a.attack_type}|${a.source_ip || a.ip}`
        return { ...a, explain: mergedExplanations[key] || null }
      })

      setLogs(freshLogs)
      setDetectionAlerts(fullyEnriched)
      setExplanations(mergedExplanations)
      setSummary(computeSummary(detAlerts))
      explainedRef.current = today
      setLastUpdated(new Date())
      setError(null)
    } catch (e) {
      setError('Pipeline error: ' + (e.message || 'unknown'))
    }
  }, [explanations])

  usePolling(runPipeline, 5000)

  const handleSimulate = async () => {
    setLoading(true)
    await api.simulateAttack().catch(() => {})
    await runPipeline()
    setLoading(false)
  }

  const handleBatch = async () => {
    setLoading(true)
    await api.batchSimulate(5).catch(() => {})
    await runPipeline()
    setLoading(false)
  }

  const handleRefresh = async () => {
    setLoading(true)
    await runPipeline()
    setLoading(false)
  }

  const handleResolve = async (id) => {
    await api.updateAlert(id, { is_resolved: true }).catch(() => {})
    await runPipeline()
  }

  const handleDelete = async (id) => {
    await api.deleteAlert(id).catch(() => {})
    await runPipeline()
  }

  return (
    <div className="min-h-screen bg-[#0a0e17] scanline">
      <Header
        lastUpdated={lastUpdated}
        onRefresh={handleRefresh}
        onSimulate={handleSimulate}
        onBatch={handleBatch}
        loading={loading}
      />

      <div className="border-b border-[#1e3a5f] bg-[#0d1525]">
        <div className="max-w-7xl mx-auto px-6 flex gap-6">
          {TABS.map(t => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`py-3 text-xs font-semibold uppercase tracking-wider border-b-2 transition ${
                tab === t
                  ? 'text-cyan-400 border-cyan-400'
                  : 'text-gray-500 border-transparent hover:text-gray-300'
              }`}
            >
              {t === 'Attack Replay' ? '\u25B6 Attack Replay' : t}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="max-w-7xl mx-auto mt-3 px-6">
          <div className="px-4 py-2 rounded bg-red-600/10 border border-red-600/30 text-red-400 text-xs">
            {error}
          </div>
        </div>
      )}

      <main className="p-6 space-y-4 max-w-7xl mx-auto">
        {tab === 'Dashboard' && (
          <>
            <StatsCards summary={summary} />
            <Charts alerts={detectionAlerts} logs={logs} />

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <div className="lg:col-span-2">
                <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
                  Detection Alerts
                  <span className="text-gray-600 font-normal ml-2">({detectionAlerts.length})</span>
                </h2>
                <AlertTable
                  alerts={detectionAlerts}
                  onResolve={handleResolve}
                  onDelete={handleDelete}
                  loading={loading}
                />
              </div>

              <div className="space-y-4">
                {detectionAlerts.length > 0 && detectionAlerts[0].explain && (
                  <div className="card p-4">
                    <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                      AI Analysis
                    </h3>
                    <div className="text-xs text-gray-300 leading-relaxed">
                      {detectionAlerts[0].explain.explanation}
                    </div>
                    <div className="mt-2 flex items-center gap-2">
                      <span className="text-[10px] font-semibold uppercase tracking-wider text-gray-500">Risk:</span>
                      <span className={`text-[10px] px-1.5 py-0.5 rounded border font-semibold ${
                        detectionAlerts[0].explain.risk_level === 'Critical' ? 'border-red-500 bg-red-500/20 text-red-400' :
                        detectionAlerts[0].explain.risk_level === 'High' ? 'border-orange-500 bg-orange-500/20 text-orange-400' :
                        detectionAlerts[0].explain.risk_level === 'Medium' ? 'border-yellow-500 bg-yellow-500/20 text-yellow-400' :
                        'border-green-500 bg-green-500/20 text-green-400'
                      }`}>
                        {detectionAlerts[0].explain.risk_level}
                      </span>
                    </div>
                    <div className="mt-2 text-[10px] text-gray-400 leading-relaxed border-t border-[#1e3a5f] pt-2">
                      <span className="font-semibold text-gray-500">Recommended: </span>
                      {detectionAlerts[0].explain.recommended_action}
                    </div>
                  </div>
                )}

                <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Activity Feed</h2>
                <RecentLogs logs={logs} loading={loading} />
              </div>
            </div>
          </>
        )}

        {tab === 'Attack Replay' && <AttackReplay logs={logs} />}
      </main>

      <footer className="border-t border-[#1e3a5f] px-6 py-3 text-[10px] text-gray-600 flex justify-between">
        <span>Cyber Range SOC Lite &mdash; Training Environment</span>
        <span className="mono">v2.0.0</span>
      </footer>
    </div>
  )
}
