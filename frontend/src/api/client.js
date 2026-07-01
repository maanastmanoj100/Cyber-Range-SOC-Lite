const API = '/api'

async function get(path) {
  const res = await fetch(path)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

async function post(path, body) {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export const api = {
  // Logs
  getLogs: (params = {}) => {
    const q = new URLSearchParams(params).toString()
    return get(`${API}/logs?${q}`)
  },

  // Detection (analyze logs → alerts)
  analyzeLogs: (logs) => post(`${API}/logs/analyze`, logs),

  // Alerts
  listAlerts: (params = {}) => {
    const q = new URLSearchParams(params).toString()
    return get(`${API}/alerts?${q}`)
  },
  updateAlert: (id, data) =>
    fetch(`${API}/alerts/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }).then(r => r.json()),
  deleteAlert: (id) =>
    fetch(`${API}/alerts/${id}`, { method: 'DELETE' }),

  // Dashboard
  getSummary: () => get(`${API}/dashboard/summary`),

  // Attack simulation
  simulateAttack: () => post(`${API}/attacks/simulate`),
  batchSimulate: (count = 5) => post(`${API}/attacks/batch-simulate?count=${count}`),

  // Explainer
  explainAlert: (attackType, logs, ipAddress) =>
    post(`${API}/explain`, {
      attack_type: attackType,
      logs: logs.map(l => ({
        ip: l.ip,
        event_type: l.event_type || l.attack_type || 'unknown',
        endpoint: l.endpoint || '',
        timestamp: l.timestamp,
      })),
      ip_address: ipAddress,
    }),
}
