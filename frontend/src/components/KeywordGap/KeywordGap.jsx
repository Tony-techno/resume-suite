import { useState } from 'react'
import { analyzeKeywords } from '../../utils/api'

const STATUS_STYLE = {
  matched: 'bg-green-100 text-green-700 border-green-200',
  partial:  'bg-yellow-100 text-yellow-700 border-yellow-200',
  missing:  'bg-red-100 text-red-600 border-red-200',
}

export default function KeywordGap({ resumeText }) {
  const [jd, setJd] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [filter, setFilter] = useState('all')

  async function run() {
    if (!resumeText) { setError('Parse a resume first (Parser tab)'); return }
    if (!jd.trim())  { setError('Paste a job description'); return }
    setLoading(true); setError(''); setResult(null)
    try { setResult(await analyzeKeywords(resumeText, jd)) }
    catch(e) { setError(e.message) } finally { setLoading(false) }
  }

  const filtered = result?.keywords?.filter(k => filter === 'all' || k.status === filter) || []

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-800">Keyword Gap Analyzer</h2>
        <p className="text-gray-500 text-sm mt-1">See which JD keywords are matched, partial, or missing from your resume.</p>
      </div>
      {!resumeText && <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-amber-700 text-sm">No resume loaded - go to Parser tab first.</div>}
      <textarea rows={7} placeholder="Paste job description..."
        value={jd} onChange={e => setJd(e.target.value)}
        className="w-full border rounded-lg p-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
      <button onClick={run} disabled={loading}
        className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50">
        {loading ? 'Analyzing...' : 'Analyze Keywords'}
      </button>
      {error && <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">Error: {error}</div>}
      {result && (
        <div className="space-y-5">
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-green-50 border border-green-200 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-green-700">{result.stats.matched||0}</div>
              <div className="text-sm text-green-600">Matched</div>
            </div>
            <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-yellow-700">{result.stats.partial||0}</div>
              <div className="text-sm text-yellow-600">Partial</div>
            </div>
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-red-700">{result.stats.missing||0}</div>
              <div className="text-sm text-red-600">Missing</div>
            </div>
          </div>
          <div className="bg-white border rounded-xl p-4 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-700">Match: {result.match_percentage}%</h3>
              <div className="flex gap-1">
                {['all','matched','partial','missing'].map(f => (
                  <button key={f} onClick={() => setFilter(f)}
                    className={"px-3 py-1 rounded text-xs font-medium " + (filter===f ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600')}>
                    {f}
                  </button>
                ))}
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              {filtered.map(k => (
                <span key={k.keyword}
                  title={k.add_to ? 'Add to: ' + k.add_to : ''}
                  className={"text-xs px-2 py-1 rounded-full border cursor-default " + (STATUS_STYLE[k.status]||'')}>
                  {k.keyword}
                  {k.add_to && <span className="ml-1 opacity-60">({k.add_to})</span>}
                </span>
              ))}
            </div>
          </div>
          {result.top_missing?.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4">
              <h3 className="font-semibold text-red-700 mb-2">Top Missing Keywords to Add</h3>
              <div className="flex flex-wrap gap-2">
                {result.top_missing.map(k => (
                  <span key={k} className="bg-white border border-red-300 text-red-700 text-xs px-2 py-1 rounded-full">{k}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
