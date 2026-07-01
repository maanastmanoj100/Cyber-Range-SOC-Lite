import { useState, useEffect, useRef, useCallback } from 'react'
import { api } from '../api/client'

const SPEEDS = [0.5, 1, 2, 4]

function formatTime(ts) {
  const d = new Date(ts)
  return d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

function eventIcon(eventType = '', attackType = '') {
  const e = (eventType + ' ' + attackType).toLowerCase()
  if (e.includes('login') || e.includes('auth')) return '🔑'
  if (e.includes('sql') || e.includes('sqli') || e.includes('injection')) return '💉'
  if (e.includes('scan') || e.includes('port')) return '🔍'
  if (e.includes('ddos') || e.includes('flood') || e.includes('brute')) return '⚡'
  if (e.includes('malware') || e.includes('upload')) return '🦠'
  if (e.includes('xss')) return '📝'
  if (e.includes('phish')) return '🎣'
  return '⚠️'
}

function sevColor(sev) {
  switch (sev) {
    case 'Critical': return 'border-red-500 bg-red-500/20 text-red-400'
    case 'High': return 'border-orange-500 bg-orange-500/20 text-orange-400'
    case 'Medium': return 'border-yellow-500 bg-yellow-500/20 text-yellow-400'
    case 'Low': return 'border-green-500 bg-green-500/20 text-green-400'
    default: return 'border-gray-500 bg-gray-500/20 text-gray-400'
  }
}

function dotColor(sev) {
  switch (sev) {
    case 'Critical': return 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]'
    case 'High': return 'bg-orange-500 shadow-[0_0_8px_rgba(249,115,22,0.5)]'
    case 'Medium': return 'bg-yellow-500'
    case 'Low': return 'bg-green-500'
    default: return 'bg-gray-500'
  }
}

export default function AttackReplay({ logs: initialLogs }) {
  const [allEvents, setAllEvents] = useState([])
  const [index, setIndex] = useState(0)
  const [playing, setPlaying] = useState(false)
  const [speed, setSpeed] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [feedType, setFeedType] = useState('alerts')
  const timerRef = useRef(null)
  const listRef = useRef(null)

  const fetchEvents = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      let events = []

      if (feedType === 'alerts') {
        const alerts = await api.listAlerts({ limit: 100 })
        events = (alerts || []).map(a => ({
          id: a.id,
          ts: new Date(a.timestamp || Date.now()).getTime(),
          timeDisplay: formatTime(a.timestamp),
          event_type: a.attack_type || 'Alert',
          ip: a.source_ip || a.ip || '—',
          endpoint: a.destination_ip || '',
          severity: a.severity || 'Low',
          description: a.title || a.description || '',
        }))
      } else if (feedType === 'logs') {
        const logs = await api.getLogs({ limit: 100 })
        events = (logs || []).map(l => ({
          id: l.id,
          ts: new Date(l.timestamp || Date.now()).getTime(),
          timeDisplay: formatTime(l.timestamp),
          event_type: l.event_type || 'request',
          ip: l.ip || '—',
          endpoint: l.endpoint || '',
          severity: l.event_type?.toLowerCase().includes('login') ? 'Medium' :
                    l.event_type?.toLowerCase().includes('sql') ? 'Critical' : 'Low',
          description: l.payload || '',
        }))
      }

      events.sort((a, b) => a.ts - b.ts || a.id - b.id)
      setAllEvents(events)
      setIndex(0)
      setPlaying(false)
    } catch (e) {
      setError('Failed to load events: ' + e.message)
    }
    setLoading(false)
  }, [feedType])

  useEffect(() => { fetchEvents() }, [fetchEvents])

  useEffect(() => {
    if (playing && index < allEvents.length) {
      const delay = (1000 / speed)
      timerRef.current = setTimeout(() => {
        setIndex(prev => {
          if (prev >= allEvents.length - 1) {
            setPlaying(false)
            return prev
          }
          return prev + 1
        })
      }, delay)
    }
    return () => clearTimeout(timerRef.current)
  }, [playing, index, speed, allEvents.length])

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight
    }
  }, [index])

  const handlePlayPause = () => {
    if (index >= allEvents.length) {
      setIndex(0)
    }
    setPlaying(p => !p)
  }

  const handleReset = () => {
    setPlaying(false)
    setIndex(0)
  }

  const handleStep = () => {
    if (index < allEvents.length - 1) {
      setIndex(i => i + 1)
    }
  }

  const handleStepBack = () => {
    if (index > 0) setIndex(i => i - 1)
  }

  const handleJump = (e) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const pct = (e.clientX - rect.left) / rect.width
    const newIdx = Math.floor(pct * allEvents.length)
    setIndex(Math.max(0, Math.min(allEvents.length - 1, newIdx)))
  }

  const progress = allEvents.length > 0 ? ((index + 1) / allEvents.length) * 100 : 0
  const visible = allEvents.slice(0, index + 1)

  return (
    <div className="card overflow-hidden">
      {/* Header */}
      <div className="border-b border-[#1e3a5f] px-5 py-3 flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-4">
          <h2 className="text-sm font-bold text-gray-300">Attack Replay</h2>
          <div className="flex bg-[#0a0e17] rounded border border-[#1e3a5f] text-xs">
            <button
              onClick={() => { setFeedType('alerts'); setPlaying(false) }}
              className={`px-3 py-1.5 rounded-l transition ${feedType === 'alerts' ? 'bg-cyan-500/20 text-cyan-400' : 'text-gray-500 hover:text-gray-300'}`}
            >Alerts</button>
            <button
              onClick={() => { setFeedType('logs'); setPlaying(false) }}
              className={`px-3 py-1.5 rounded-r transition ${feedType === 'logs' ? 'bg-cyan-500/20 text-cyan-400' : 'text-gray-500 hover:text-gray-300'}`}
            >Logs</button>
          </div>
        </div>
        <button onClick={fetchEvents} className="text-xs text-gray-500 hover:text-cyan-400 transition px-2 py-1 border border-[#1e3a5f] rounded">
          &#x21bb; Reload
        </button>
      </div>

      {/* Controls */}
      <div className="border-b border-[#1e3a5f] px-5 py-3 flex items-center justify-between flex-wrap gap-3 bg-[#0d1525]">
        <div className="flex items-center gap-2">
          <button
            onClick={handleStepBack}
            disabled={index === 0}
            className="w-8 h-8 rounded flex items-center justify-center border border-[#1e3a5f] text-gray-400 hover:text-cyan-400 hover:border-cyan-500/40 disabled:opacity-30 disabled:cursor-not-allowed transition text-sm"
          >⏮</button>
          <button
            onClick={handlePlayPause}
            disabled={allEvents.length === 0}
            className="w-10 h-10 rounded-lg flex items-center justify-center bg-cyan-500/20 border border-cyan-500/40 text-cyan-400 hover:bg-cyan-500/30 disabled:opacity-30 transition text-lg"
          >
            {playing ? '⏸' : index >= allEvents.length ? '⟳' : '▶'}
          </button>
          <button
            onClick={handleStep}
            disabled={index >= allEvents.length - 1}
            className="w-8 h-8 rounded flex items-center justify-center border border-[#1e3a5f] text-gray-400 hover:text-cyan-400 hover:border-cyan-500/40 disabled:opacity-30 disabled:cursor-not-allowed transition text-sm"
          >⏭</button>
          <button
            onClick={handleReset}
            disabled={index === 0}
            className="text-xs px-2.5 py-1.5 rounded border border-[#1e3a5f] text-gray-500 hover:text-orange-400 disabled:opacity-30 transition"
          >Reset</button>
        </div>

        <div className="flex items-center gap-2">
          <div className="text-[10px] text-gray-500 mono mr-1">
            {Math.min(index + 1, allEvents.length)} / {allEvents.length}
          </div>
          {SPEEDS.map(s => (
            <button
              key={s}
              onClick={() => setSpeed(s)}
              className={`text-xs px-2 py-1 rounded border transition ${
                speed === s
                  ? 'bg-cyan-500/20 border-cyan-500/40 text-cyan-400'
                  : 'border-[#1e3a5f] text-gray-500 hover:text-gray-300'
              }`}
            >{s}x</button>
          ))}
        </div>
      </div>

      {/* Progress bar */}
      <div
        className="h-1 bg-[#0a0e17] cursor-pointer relative"
        onClick={handleJump}
      >
        <div
          className="h-full bg-gradient-to-r from-cyan-500 to-cyan-400 transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
        <div
          className="absolute top-0 w-3 h-3 bg-cyan-400 rounded-full -translate-y-1/3 transition-all duration-300 shadow-[0_0_10px_rgba(0,212,170,0.5)]"
          style={{ left: `calc(${progress}% - 6px)` }}
        />
      </div>

      {/* Timeline */}
      <div
        ref={listRef}
        className="overflow-y-auto"
        style={{ maxHeight: '520px' }}
      >
        {loading && (
          <div className="flex items-center justify-center py-16 text-gray-500 text-sm pulse">Loading events...</div>
        )}
        {error && (
          <div className="mx-5 my-4 px-3 py-2 rounded bg-red-600/10 border border-red-600/30 text-red-400 text-xs">{error}</div>
        )}
        {!loading && !error && allEvents.length === 0 && (
          <div className="flex items-center justify-center py-16 text-gray-600 text-sm">
            No events available. Simulate an attack first.
          </div>
        )}
        {!loading && allEvents.length > 0 && (
          <div className="relative px-5 py-4">
            {/* Vertical timeline line */}
            <div className="absolute left-[72px] top-0 bottom-0 w-px bg-[#1e3a5f]" />

            {visible.map((event, i) => {
              const isLast = i === visible.length - 1
              return (
                <div
                  key={`${event.id}-${i}`}
                  className="relative flex items-start gap-4 py-2 fade-in group"
                  style={{ animationDelay: `${i * 20}ms` }}
                >
                  {/* Time */}
                  <div className="w-14 shrink-0 text-right">
                    <span className="text-[10px] text-gray-500 mono leading-6">{event.timeDisplay}</span>
                  </div>

                  {/* Dot */}
                  <div className="relative shrink-0" style={{ marginLeft: '-5px' }}>
                    <div className={`w-2.5 h-2.5 rounded-full ${dotColor(event.severity)} ${isLast ? 'pulse' : ''}`} />
                    {isLast && (
                      <div className="absolute -inset-1 rounded-full bg-cyan-400/20 animate-ping" />
                    )}
                  </div>

                  {/* Card */}
                  <div className={`flex-1 p-3 rounded-lg border transition ${
                    isLast
                      ? 'border-cyan-500/40 bg-cyan-500/5 shadow-[0_0_15px_rgba(0,212,170,0.08)]'
                      : 'border-[#1e3a5f] bg-[#111827] hover:border-[#1e3a5f]/80'
                  }`}>
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <span className="text-sm">{eventIcon(event.event_type)}</span>
                        <span className={`text-[10px] px-1.5 py-0.5 rounded border font-semibold ${sevColor(event.severity)}`}>
                          {event.severity}
                        </span>
                        <span className="text-xs font-medium text-cyan-300">{event.event_type}</span>
                      </div>
                      <span className="text-[10px] mono text-gray-500">{event.ip}</span>
                    </div>
                    {event.endpoint && (
                      <div className="mt-1 text-[10px] text-gray-500 mono truncate">{event.endpoint}</div>
                    )}
                    {event.description && (
                      <div className="mt-1 text-[10px] text-gray-600 italic truncate">{event.description}</div>
                    )}
                  </div>
                </div>
              )
            })}

            {index >= allEvents.length - 1 && allEvents.length > 0 && (
              <div className="text-center py-4 text-[10px] text-cyan-500/60 mono pulse">
                — Replay complete —
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
