import {
  Chart as ChartJS,
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import { Doughnut, Bar, Line } from 'react-chartjs-2'

ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler)

const plugin = {
  id: 'bgColor',
  beforeDraw: (chart) => {
    const { ctx, width, height } = chart
    ctx.fillStyle = '#111827'
    ctx.fillRect(0, 0, width, height)
  },
}

const tickOpts = { color: '#667', font: { family: 'JetBrains Mono', size: 10 } }
const gridOpts = { color: '#1e3a5f' }

export default function Charts({ alerts, logs }) {
  const severityData = {
    labels: ['Critical', 'High', 'Medium', 'Low'],
    datasets: [{
      data: [
        (alerts || []).filter(a => a.severity === 'Critical').length,
        (alerts || []).filter(a => a.severity === 'High').length,
        (alerts || []).filter(a => a.severity === 'Medium').length,
        (alerts || []).filter(a => a.severity === 'Low').length,
      ],
      backgroundColor: ['#ef4444', '#f97316', '#eab308', '#22c55e'],
      borderColor: ['#ef444488', '#f9731688', '#eab30888', '#22c55e88'],
      borderWidth: 1,
      hoverOffset: 8,
    }],
  }

  const attackTypes = {}
  ;(alerts || []).forEach(a => {
    const t = a.attack_type || 'Unknown'
    attackTypes[t] = (attackTypes[t] || 0) + 1
  })
  const barData = {
    labels: Object.keys(attackTypes),
    datasets: [{
      label: 'Alerts',
      data: Object.values(attackTypes),
      backgroundColor: '#06b6d480',
      borderColor: '#06b6d4',
      borderWidth: 1,
      borderRadius: 4,
    }],
  }

  const timeSlots = []
  const now = Date.now()
  for (let i = 9; i >= 0; i--) {
    timeSlots.push(new Date(now - i * 60000).toLocaleTimeString())
  }
  const timeCounts = timeSlots.map(() => 0)
  const windowMs = 60000
  ;(alerts || []).forEach(a => {
    const t = new Date(a.timestamp || a.created_at || Date.now()).getTime()
    const idx = timeSlots.findIndex((_, i) => {
      const slotStart = now - (9 - i) * windowMs
      return t >= slotStart && t < slotStart + windowMs
    })
    if (idx >= 0) timeCounts[idx]++
  })
  const lineData = {
    labels: timeSlots,
    datasets: [{
      label: 'Events / min',
      data: timeCounts,
      borderColor: '#00d4aa',
      backgroundColor: 'rgba(0,212,170,0.08)',
      fill: true,
      tension: 0.4,
      pointRadius: 3,
      pointHoverRadius: 6,
      pointBackgroundColor: '#00d4aa',
    }],
  }

  const opts = (legend) => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: legend, labels: { color: '#8892a4', font: { family: 'Inter', size: 11 } } } },
    scales: {
      x: { ticks: tickOpts, grid: gridOpts },
      y: { ticks: tickOpts, grid: gridOpts, beginAtZero: true },
    },
  })

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div className="card p-4">
        <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Severity Distribution</h3>
        <div className="h-52 flex items-center justify-center">
          {(alerts || []).length > 0
            ? <Doughnut data={severityData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: '#8892a4', font: { family: 'Inter', size: 11 } } } } }} />
            : <p className="text-gray-600 text-xs">No alert data yet</p>}
        </div>
      </div>

      <div className="card p-4">
        <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Attack Types</h3>
        <div className="h-52">
          {Object.keys(attackTypes).length > 0
            ? <Bar data={barData} options={opts(false)} plugins={[plugin]} />
            : <p className="text-gray-600 text-xs">No attack data yet</p>}
        </div>
      </div>

      <div className="card p-4">
        <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Timeline (10 min)</h3>
        <div className="h-52">
          {alerts && alerts.length > 0
            ? <Line data={lineData} options={opts(false)} plugins={[plugin]} />
            : <p className="text-gray-600 text-xs">No timeline data yet</p>}
        </div>
      </div>
    </div>
  )
}
