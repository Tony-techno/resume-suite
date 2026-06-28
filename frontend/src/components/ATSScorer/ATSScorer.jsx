import { useState } from 'react'
import { getATSScore } from '../../utils/api'

function ScoreRing({ score }) {
  const color = score >= 70 ? '#16a34a' : score >= 50 ? '#d97706' : '#dc2626'
  const label = score >= 85 ? 'Excellent' : score >= 70 ? 'Good' : score >= 55 ? 'Average' : score >= 40 ? 'Weak' : 'Poor'
  return (
    <div className="flex flex-col items-center justify-center p-6 bg-white border rounded-xl shadow-sm">
      <svg width="120" height="120" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r="50" fill="none" stroke="#e5e7eb" strokeWidth="10" />
        <circle cx="60" cy="60" r="50" fill="none" stroke={color} strokeWidth="10"
          strokeDasharray={`${score * 3.14} 314`}
          strokeLinecap="round"
          transform="rotate(-90 60 60)" />
        <text x="60" y="55" textAnchor="middle" fontSize="26" fontWeight="bold" fill={color}>{score}</text>
        <text x="60" y="72" textAnchor="middle" fontSize="11" fill="#6b7280">out of 100</text>
      </svg>
      <p className="font-bold text-lg mt-1" style={{color}}>{label}</p>
      <p className="text-gray-400 text-xs mt-1">ATS Compatibility Score</p>
    </div>
  )
}

function ScoreBar({ label, score, weight, detail }) {
  const color = score >= 70 ? '#16a34a' : score >= 50 ? '#d97706' : '#dc2626'
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-gray-700 font-medium">{label} <span className="text-gray-400 font-normal text-xs">({weight}% weight)</span></span>
        <span className="font-bold" style={{color}}>{score}/100</span>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-3">
        <div className="h-3 rounded-full transition-all" style={{width: score + '%', background: color}} />
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

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-800">ATS Score Analyzer</h2>
        <p className="text-gray-500 text-sm mt-1">Scores your resume against a job description across 6 real ATS criteria used by Workday, Greenhouse, and Lever.</p>
      </div>
      {!resumeText && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-amber-700 text-sm">
          No resume loaded - go to Parser tab and upload your resume first.
        </div>
      )}
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">Paste Job Description</label>
        <textarea rows={8} placeholder="Paste the full job description here. The more complete it is, the more accurate your score will be..."
          value={jd} onChange={e => setJd(e.target.value)}
          className="w-full border rounded-lg p-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
      </div>
      <button onClick={run} disabled={loading}
        className="bg-indigo-600 text-white px-8 py-2.5 rounded-lg hover:bg-indigo-700 disabled:opacity-50 font-medium">
        {loading ? 'Analyzing your resume...' : 'Analyze ATS Score'}
      </button>
      {error && <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">Error: {error}</div>}
      {result && (
        <div className="space-y-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <ScoreRing score={result.total_score} />
            <div className="bg-white border rounded-xl p-5 shadow-sm space-y-3">
              <h3 className="font-semibold text-gray-700">What this score means</h3>
              <div className="space-y-2 text-sm">
                {[
                  ['85-100', 'Excellent match. Apply with confidence.', '#16a34a'],
                  ['70-84',  'Good match. Minor improvements needed.', '#2563eb'],
                  ['55-69',  'Average. Tailor resume to this JD.', '#d97706'],
                  ['40-54',  'Weak match. Significant gaps found.', '#ea580c'],
                  ['0-39',   'Poor match. Major tailoring needed.', '#dc2626'],
                ].map(([range, desc, color]) => (
                  <div key={range} className="flex gap-2 items-start">
                    <span className="font-bold w-16 shrink-0 text-xs mt-0.5" style={{color}}>{range}</span>
                    <span className="text-gray-600">{desc}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
          {bd && (
            <div className="bg-white border rounded-xl p-5 shadow-sm space-y-4">
              <h3 className="font-semibold text-gray-700">Detailed Score Breakdown</h3>
              <ScoreBar label="Keyword Match"        score={bd.keyword_match?.score}        weight={35}
                detail={(bd.keyword_match?.matched?.length||0) + ' keywords matched, ' + (bd.keyword_match?.missing?.length||0) + ' missing from your resume'} />
              <ScoreBar label="Section Completeness" score={bd.section_completeness?.score}  weight={20}
                detail={'Sections found: ' + (bd.section_completeness?.found?.join(', ')||'none') + (bd.section_completeness?.missing?.length ? ' | Missing: ' + bd.section_completeness.missing.join(', ') : '')} />
              <ScoreBar label="Formatting"           score={bd.formatting?.score}            weight={15}
                detail={bd.formatting?.issues?.length ? bd.formatting.issues.join(' | ') : 'No formatting issues detected'} />
              <ScoreBar label="Action Verbs"         score={bd.action_verbs?.score}          weight={15}
                detail={bd.action_verbs?.strong + ' strong verbs, ' + bd.action_verbs?.medium + ' medium, ' + bd.action_verbs?.weak + ' weak verbs in your bullets'} />
              <ScoreBar label="Quantification"       score={bd.quantification?.score}        weight={10}
                detail={bd.quantification?.quantified + ' out of ' + bd.quantification?.total + ' bullets contain numbers or percentages'} />
              <ScoreBar label="Contact Info"         score={bd.contact_info?.score}          weight={5}
                detail={Object.entries(bd.contact_info?.checks||{}).map(([k,v]) => (v ? 'has ' : 'missing ') + k).join(', ')} />
            </div>
          )}
          {bd?.keyword_match?.matched?.length > 0 && (
            <div className="bg-white border rounded-xl p-5 shadow-sm">
              <h3 className="font-semibold text-gray-700 mb-3">Matched Keywords ({bd.keyword_match.matched.length})</h3>
              <div className="flex flex-wrap gap-2">
                {bd.keyword_match.matched.slice(0,20).map(k => (
                  <span key={k} className="bg-green-50 text-green-700 text-xs px-2 py-1 rounded-full border border-green-200">{k}</span>
                ))}
              </div>
            </div>
          )}
          {bd?.keyword_match?.missing?.length > 0 && (
            <div className="bg-white border rounded-xl p-5 shadow-sm">
              <h3 className="font-semibold text-gray-700 mb-3">Missing Keywords - Add These to Your Resume ({bd.keyword_match.missing.length})</h3>
              <div className="flex flex-wrap gap-2">
                {bd.keyword_match.missing.slice(0,20).map(k => (
                  <span key={k} className="bg-red-50 text-red-600 text-xs px-2 py-1 rounded-full border border-red-200">{k}</span>
                ))}
              </div>
            </div>
          )}
          {result.recommendations?.length > 0 && (
            <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-5">
              <h3 className="font-semibold text-indigo-800 mb-3">Action Items to Improve Your Score</h3>
              <ul className="space-y-2">
                {result.recommendations.map((r,i) => (
                  <li key={i} className="text-sm text-indigo-700 flex gap-2 items-start">
                    <span className="font-bold shrink-0">{i+1}.</span>{r}
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
