import { useState } from 'react'
import { getATSScore } from '../../utils/api'

function ScoreBar({ label, score, weight, detail }) {
  const color = score >= 70 ? '#4f46e5' : score >= 50 ? '#f59e0b' : '#ef4444'
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-gray-700 font-medium">{label} <span className="text-gray-400 font-normal">({weight}%)</span></span>
        <span className="font-bold text-indigo-700">{score}/100</span>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-2">
        <div className="h-2 rounded-full transition-all" style={{width: score + '%', background: color}} />
      </div>
      {detail && <p className="text-xs text-gray-400">{detail}</p>}
    </div>
  )
}

export default function ATSScorer({ resumeText }) {
  const [jd, setJd] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  async function run() {
    if (!resumeText) { setError('Parse a resume first (Parser tab)'); return }
    if (!jd.trim())  { setError('Paste a job description below'); return }
    setLoading(true); setError(''); setResult(null)
    try { setResult(await getATSScore(resumeText, jd)) }
    catch(e) { setError(e.message) } finally { setLoading(false) }
  }

  const bd = result?.breakdown
  const gradeColor = { A:'bg-green-100 text-green-700', B:'bg-blue-100 text-blue-700', C:'bg-yellow-100 text-yellow-700', D:'bg-orange-100 text-orange-700', F:'bg-red-100 text-red-700' }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-800">ATS Score Analyzer</h2>
        <p className="text-gray-500 text-sm mt-1">Paste a job description to score your resume across 6 ATS criteria.</p>
      </div>
      {!resumeText && <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-amber-700 text-sm">No resume loaded - go to Parser tab first.</div>}
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">Job Description</label>
        <textarea rows={8} placeholder="Paste the full job description here..."
          value={jd} onChange={e => setJd(e.target.value)}
          className="w-full border rounded-lg p-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
      </div>
      <button onClick={run} disabled={loading}
        className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50">
        {loading ? 'Analyzing...' : 'Get ATS Score'}
      </button>
      {error && <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">Error: {error}</div>}
      {result && (
        <div className="space-y-6">
          <div className="bg-white border rounded-xl p-6 flex items-center gap-6 shadow-sm">
            <div className="text-center">
              <div className="text-5xl font-bold text-indigo-700">{result.total_score}</div>
              <div className="text-gray-400 text-sm">/ 100</div>
            </div>
            <div>
              <span className={"text-4xl font-black px-4 py-1 rounded-lg " + (gradeColor[result.grade] || 'bg-gray-100')}>{result.grade}</span>
              <p className="text-gray-500 text-sm mt-2">
                {result.total_score >= 85 ? 'Excellent match!' : result.total_score >= 70 ? 'Good match, minor gaps' : result.total_score >= 55 ? 'Moderate match - tailor further' : 'Needs significant tailoring'}
              </p>
            </div>
          </div>
          {bd && (
            <div className="bg-white border rounded-xl p-5 space-y-4 shadow-sm">
              <h3 className="font-semibold text-gray-700">Score Breakdown</h3>
              <ScoreBar label="Keyword Match"        score={bd.keyword_match?.score}        weight={35} detail={(bd.keyword_match?.matched?.length||0) + ' matched, ' + (bd.keyword_match?.missing?.length||0) + ' missing'} />
              <ScoreBar label="Section Completeness" score={bd.section_completeness?.score}  weight={20} detail={'Found: ' + (bd.section_completeness?.found?.join(', ')||'none')} />
              <ScoreBar label="Formatting"           score={bd.formatting?.score}            weight={15} detail={bd.formatting?.issues?.join(' | ')||'No issues'} />
              <ScoreBar label="Action Verbs"         score={bd.action_verbs?.score}          weight={15} detail={bd.action_verbs?.strong + ' strong, ' + bd.action_verbs?.medium + ' medium, ' + bd.action_verbs?.weak + ' weak'} />
              <ScoreBar label="Quantification"       score={bd.quantification?.score}        weight={10} detail={bd.quantification?.quantified + '/' + bd.quantification?.total + ' bullets have numbers'} />
              <ScoreBar label="Contact Info"         score={bd.contact_info?.score}          weight={5}  detail={Object.entries(bd.contact_info?.checks||{}).map(([k,v]) => (v?'yes':'no') + ' ' + k).join(', ')} />
            </div>
          )}
          {bd?.keyword_match?.missing?.length > 0 && (
            <div className="bg-white border rounded-xl p-5 shadow-sm">
              <h3 className="font-semibold text-gray-700 mb-3">Missing Keywords</h3>
              <div className="flex flex-wrap gap-2">
                {bd.keyword_match.missing.slice(0,20).map(k => (
                  <span key={k} className="bg-red-50 text-red-600 text-xs px-2 py-1 rounded-full border border-red-200">{k}</span>
                ))}
              </div>
            </div>
          )}
          {result.recommendations?.length > 0 && (
            <div className="bg-white border rounded-xl p-5 shadow-sm">
              <h3 className="font-semibold text-gray-700 mb-3">Recommendations</h3>
              <ul className="space-y-2">
                {result.recommendations.map((r,i) => (
                  <li key={i} className="text-sm text-gray-700 flex gap-2">
                    <span className="text-indigo-500 shrink-0">-</span>{r}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
