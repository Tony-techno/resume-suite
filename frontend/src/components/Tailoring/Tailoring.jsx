import { useState } from 'react'
import { tailorResume } from '../../utils/api'

export default function Tailoring({ resumeText }) {
  const [jd, setJd] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  async function run() {
    if (!resumeText) { setError('Parse a resume first (Parser tab)'); return }
    if (!jd.trim())  { setError('Paste a job description'); return }
    setLoading(true); setError(''); setResult(null)
    try { setResult(await tailorResume(resumeText, jd)) }
    catch(e) { setError(e.message) } finally { setLoading(false) }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-800">AI Resume Tailor</h2>
        <p className="text-gray-500 text-sm mt-1">Rewrites your experience bullets to match a job description using HuggingFace Mistral-7B with rule-based fallback.</p>
      </div>
      {!resumeText && <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-amber-700 text-sm">No resume loaded - go to Parser tab first.</div>}
      <textarea rows={8} placeholder="Paste job description..."
        value={jd} onChange={e => setJd(e.target.value)}
        className="w-full border rounded-lg p-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
      <button onClick={run} disabled={loading}
        className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50">
        {loading ? 'AI generating (may take 20-30s)...' : 'Tailor My Resume'}
      </button>
      {error && <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">Error: {error}</div>}
      {result && (
        <div className="space-y-4">
          <div className={"rounded-lg px-4 py-2 text-sm font-medium border " + (result.mode==='ai' ? 'bg-green-50 text-green-700 border-green-200' : 'bg-blue-50 text-blue-700 border-blue-200')}>
            {result.mode === 'ai' ? 'AI-generated output (Mistral-7B via HuggingFace)' : 'Rule-based analysis mode'}
            {result.notice && <span className="ml-2 font-normal opacity-75">- {result.notice}</span>}
          </div>
          {result.mode === 'ai' && result.rewritten_bullets?.length > 0 && (
            <div className="bg-white border rounded-xl p-5 shadow-sm">
              <h3 className="font-semibold text-gray-700 mb-3">Rewritten Bullets</h3>
              <ul className="space-y-2">
                {result.rewritten_bullets.map((b,i) => (
                  <li key={i} className="text-sm text-gray-700 bg-indigo-50 rounded-lg px-3 py-2 border border-indigo-100">{b}</li>
                ))}
              </ul>
            </div>
          )}
          {result.mode === 'rule_based' && result.suggestions?.length > 0 && (
            <div className="bg-white border rounded-xl p-5 shadow-sm space-y-3">
              <h3 className="font-semibold text-gray-700">Bullet-by-Bullet Suggestions</h3>
              {result.suggestions.map((s,i) => (
                <div key={i} className="border rounded-lg p-3 space-y-1">
                  <p className="text-sm text-gray-600"><span className="font-medium">Original: </span>{s.original}</p>
                  <p className={"text-sm " + (s.is_weak_verb ? 'text-red-600' : 'text-indigo-600')}>
                    <span className="font-medium">{s.is_weak_verb ? 'Weak verb - ' : 'Tip: '}</span>{s.suggestion}
                  </p>
                </div>
              ))}
            </div>
          )}
          {result.skills_to_add?.length > 0 && (
            <div className="bg-white border rounded-xl p-5 shadow-sm">
              <h3 className="font-semibold text-gray-700 mb-2">Skills to Add from JD</h3>
              <div className="flex flex-wrap gap-2">
                {result.skills_to_add.map(s => (
                  <span key={s} className="bg-green-50 text-green-700 border border-green-200 text-xs px-2 py-1 rounded-full">+ {s}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
