import os

# ── ATSScorer ─────────────────────────────────────────────────────────────
ats = """import { useState } from 'react'
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
"""

# ── KeywordGap ────────────────────────────────────────────────────────────
kw = """import { useState } from 'react'
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
"""

# ── Tailoring ─────────────────────────────────────────────────────────────
tailor = """import { useState } from 'react'
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
"""

# ── CoverLetter ───────────────────────────────────────────────────────────
cl = """import { useState } from 'react'
import { generateCoverLetter } from '../../utils/api'

export default function CoverLetter({ resumeText, parsed }) {
  const [form, setForm] = useState({ name:'', company:'', role:'', jd:'' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [copied, setCopied] = useState(false)

  const update = (k, v) => setForm(f => ({...f, [k]: v}))

  async function run() {
    if (!resumeText) { setError('Parse a resume first (Parser tab)'); return }
    setLoading(true); setError(''); setResult(null)
    try {
      const d = await generateCoverLetter({
        resume_text: resumeText,
        job_description: form.jd,
        name: form.name || parsed?.name || 'Applicant',
        company: form.company,
        role: form.role,
      })
      setResult(d)
    } catch(e) { setError(e.message) } finally { setLoading(false) }
  }

  async function copy() {
    await navigator.clipboard.writeText(result.content)
    setCopied(true); setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-800">Cover Letter Generator</h2>
        <p className="text-gray-500 text-sm mt-1">Generates a professional cover letter from your resume and job description.</p>
      </div>
      {!resumeText && <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-amber-700 text-sm">No resume loaded - go to Parser tab first.</div>}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {[['name','Your Name','e.g. Anvesh Sharma'],['company','Company','e.g. Google'],['role','Role','e.g. Software Engineer']].map(([k,label,ph]) => (
          <div key={k}>
            <label className="text-sm font-medium text-gray-700">{label}</label>
            <input type="text" placeholder={ph} value={form[k]} onChange={e => update(k, e.target.value)}
              className="mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
          </div>
        ))}
      </div>
      <div>
        <label className="text-sm font-medium text-gray-700">Job Description</label>
        <textarea rows={6} placeholder="Paste the job description..."
          value={form.jd} onChange={e => update('jd', e.target.value)}
          className="mt-1 w-full border rounded-lg p-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
      </div>
      <button onClick={run} disabled={loading}
        className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50">
        {loading ? 'Generating (may take 20-30s)...' : 'Generate Cover Letter'}
      </button>
      {error && <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">Error: {error}</div>}
      {result && (
        <div className="space-y-3">
          <div className={"rounded-lg px-4 py-2 text-sm font-medium border " + (result.mode==='ai' ? 'bg-green-50 text-green-700 border-green-200' : 'bg-blue-50 text-blue-700 border-blue-200')}>
            {result.mode === 'ai' ? 'AI-generated' : 'Template-based'}
            {result.notice && <span className="ml-2 font-normal opacity-75">- {result.notice}</span>}
          </div>
          <div className="bg-white border rounded-xl p-5 shadow-sm">
            <textarea rows={12} value={result.content}
              onChange={e => setResult({...result, content: e.target.value})}
              className="w-full text-sm text-gray-700 focus:outline-none resize-none leading-relaxed" />
          </div>
          <div className="flex gap-3">
            <button onClick={copy}
              className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700">
              {copied ? 'Copied!' : 'Copy'}
            </button>
            <button onClick={() => {
                const b = new Blob([result.content], {type:'text/plain'})
                const a = document.createElement('a')
                a.href = URL.createObjectURL(b)
                a.download = 'cover-letter.txt'
                a.click()
              }}
              className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg text-sm hover:bg-gray-200">
              Download .txt
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
"""

# ── VersionManager ────────────────────────────────────────────────────────
vm = """import { useState, useEffect } from 'react'
import { listVersions, saveVersion, deleteVersion, compareVersions } from '../../utils/api'

export default function VersionManager({ resumeText, parsed }) {
  const [versions, setVersions] = useState([])
  const [error, setError]       = useState('')
  const [name, setName]         = useState('')
  const [label, setLabel]       = useState('')
  const [saved, setSaved]       = useState(false)
  const [loading, setLoading]   = useState(false)
  const [cmp, setCmp]           = useState({ id1:'', id2:'', result:null })

  useEffect(() => { fetchVersions() }, [])

  async function fetchVersions() {
    try { setVersions(await listVersions()) } catch(e) { setError(e.message) }
  }

  async function handleSave() {
    if (!name.trim()) { setError('Enter a version name'); return }
    setLoading(true); setError('')
    try {
      await saveVersion({ name, label, content_text: resumeText, structured_json: parsed, ats_score: parsed?.total_score || null })
      setSaved(true); setName(''); setLabel(''); fetchVersions()
      setTimeout(() => setSaved(false), 2000)
    } catch(e) { setError(e.message) } finally { setLoading(false) }
  }

  async function handleDelete(id) {
    if (!confirm('Delete this version?')) return
    try { await deleteVersion(id); fetchVersions() } catch(e) { setError(e.message) }
  }

  async function handleCompare() {
    if (!cmp.id1 || !cmp.id2) { setError('Select two versions to compare'); return }
    try {
      const r = await compareVersions(cmp.id1, cmp.id2)
      setCmp(c => ({...c, result: r}))
    } catch(e) { setError(e.message) }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-800">Resume Version Manager</h2>
        <p className="text-gray-500 text-sm mt-1">Save and compare multiple resume versions in local SQLite database.</p>
      </div>
      <div className="bg-white border rounded-xl p-5 shadow-sm space-y-3">
        <h3 className="font-semibold text-gray-700">Save Current Resume</h3>
        {!resumeText && <p className="text-amber-600 text-sm">No resume loaded - go to Parser tab first.</p>}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label className="text-sm font-medium text-gray-700">Version Name</label>
            <input value={name} onChange={e => setName(e.target.value)} placeholder="SDE Resume - Google"
              className="mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700">Label (optional)</label>
            <input value={label} onChange={e => setLabel(e.target.value)} placeholder="Tailored for backend roles"
              className="mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
          </div>
        </div>
        <button onClick={handleSave} disabled={loading || !resumeText}
          className="bg-indigo-600 text-white px-5 py-2 rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-50">
          {saved ? 'Saved!' : loading ? 'Saving...' : 'Save Version'}
        </button>
      </div>
      {error && <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">Error: {error}</div>}
      <div className="bg-white border rounded-xl p-5 shadow-sm">
        <h3 className="font-semibold text-gray-700 mb-3">Saved Versions ({versions.length})</h3>
        {versions.length === 0 ? <p className="text-gray-400 text-sm">No versions saved yet.</p> : (
          <div className="space-y-2">
            {versions.map(v => (
              <div key={v.id} className="flex items-center justify-between border rounded-lg px-4 py-3">
                <div>
                  <p className="font-medium text-gray-800 text-sm">{v.name}</p>
                  <p className="text-xs text-gray-400">{v.label} - {new Date(v.created_at).toLocaleDateString()}{v.ats_score ? ' - ATS: ' + v.ats_score : ''}</p>
                </div>
                <button onClick={() => handleDelete(v.id)} className="text-red-400 text-xs hover:text-red-600">Delete</button>
              </div>
            ))}
          </div>
        )}
      </div>
      {versions.length >= 2 && (
        <div className="bg-white border rounded-xl p-5 shadow-sm space-y-3">
          <h3 className="font-semibold text-gray-700">Compare Two Versions</h3>
          <div className="grid grid-cols-2 gap-3">
            {['id1','id2'].map((k,idx) => (
              <select key={k} value={cmp[k]} onChange={e => setCmp(c => ({...c, [k]: e.target.value, result: null}))}
                className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400">
                <option value="">-- Version {idx+1} --</option>
                {versions.map(v => <option key={v.id} value={v.id}>{v.name}</option>)}
              </select>
            ))}
          </div>
          <button onClick={handleCompare} className="bg-indigo-600 text-white px-5 py-2 rounded-lg text-sm hover:bg-indigo-700">Compare</button>
          {cmp.result && (
            <div className="grid grid-cols-2 gap-4 mt-3">
              {[cmp.result.version1, cmp.result.version2].map((v,i) => (
                <div key={i} className="border rounded-lg p-4 bg-gray-50">
                  <h4 className="font-semibold text-gray-700 mb-1 text-sm">{v.name}</h4>
                  <p className="text-xs text-gray-500">{v.label}</p>
                  {v.ats_score && <p className="text-sm font-bold text-indigo-600 mt-1">ATS: {v.ats_score}</p>}
                  <p className="text-xs text-gray-400 mt-1">{new Date(v.created_at).toLocaleDateString()}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
"""

# ── Dashboard ─────────────────────────────────────────────────────────────
dash = """import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function Dashboard({ parsed }) {
  if (!parsed) return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-gray-800">Resume Health Dashboard</h2>
      <div className="bg-amber-50 border border-amber-200 rounded-xl p-8 text-center">
        <p className="text-amber-700 font-medium">No resume parsed yet</p>
        <p className="text-amber-600 text-sm mt-1">Go to Parser tab, upload your resume, then come back here.</p>
      </div>
    </div>
  )

  const av   = parsed.action_verb_score || {}
  const qt   = parsed.quantification_score || {}
  const secs = parsed.sections_found || []
  const all_secs = ['summary','experience','education','skills','projects','certifications']
  const missing_secs = all_secs.filter(s => !secs.includes(s))

  const overall = Math.round(
    (av.score||0)*0.25 + (qt.score||0)*0.25 +
    (secs.length/6*100)*0.25 +
    (parsed.word_count >= 400 && parsed.word_count <= 800 ? 100 : 50)*0.25
  )

  const barData = [
    { name: 'Action Verbs',   score: av.score||0 },
    { name: 'Quantification', score: qt.score||0 },
    { name: 'Sections',       score: Math.round(secs.length/6*100) },
    { name: 'Word Count',     score: parsed.word_count>=400&&parsed.word_count<=800 ? 100 : 60 },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-800">Resume Health Dashboard</h2>
        <p className="text-gray-500 text-sm mt-1">Visual breakdown of your resume quality.</p>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          ['Overall Score', overall + '/100', overall>=70?'text-green-600':overall>=50?'text-yellow-600':'text-red-600'],
          ['Word Count', parsed.word_count, parsed.word_count>=400&&parsed.word_count<=800?'text-green-600':'text-yellow-600'],
          ['Skills Found', (parsed.skills||[]).length, 'text-indigo-600'],
          ['Sections', secs.length + '/6', secs.length>=4?'text-green-600':'text-yellow-600'],
        ].map(([label,val,color]) => (
          <div key={label} className="bg-white border rounded-xl p-4 text-center shadow-sm">
            <div className={"text-3xl font-bold " + color}>{val}</div>
            <div className="text-gray-500 text-sm mt-1">{label}</div>
          </div>
        ))}
      </div>
      <div className="bg-white border rounded-xl p-5 shadow-sm">
        <h3 className="font-semibold text-gray-700 mb-4">Section-wise Scores</h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={barData} margin={{top:0,right:10,left:-10,bottom:0}}>
            <XAxis dataKey="name" tick={{fontSize:11}} />
            <YAxis domain={[0,100]} tick={{fontSize:11}} />
            <Tooltip formatter={v => v + '/100'} />
            <Bar dataKey="score" fill="#4f46e5" radius={[4,4,0,0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white border rounded-xl p-5 shadow-sm">
          <h3 className="font-semibold text-gray-700 mb-3">Action Verb Breakdown</h3>
          {[['Strong', av.strong||0, '#4f46e5'],['Medium', av.medium||0, '#818cf8'],['Weak', av.weak||0, '#fca5a5']].map(([name,value,fill]) => (
            <div key={name} className="flex items-center gap-3 mb-2">
              <span className="text-sm text-gray-600 w-16">{name}</span>
              <div className="flex-1 bg-gray-100 rounded-full h-3">
                <div className="h-3 rounded-full" style={{width: Math.min(100,(value/((av.strong||0)+(av.medium||0)+(av.weak||1))*100)) + '%', background: fill}} />
              </div>
              <span className="text-sm font-bold text-gray-700 w-6 text-right">{value}</span>
            </div>
          ))}
        </div>
        <div className="bg-white border rounded-xl p-5 shadow-sm">
          <h3 className="font-semibold text-gray-700 mb-3">Top Skills Detected</h3>
          <div className="flex flex-wrap gap-2">
            {(parsed.skills||[]).slice(0,12).map(s => (
              <span key={s} className="bg-indigo-100 text-indigo-700 text-xs px-2 py-1 rounded-full">{s}</span>
            ))}
            {!parsed.skills?.length && <p className="text-gray-400 text-sm">No skills detected</p>}
          </div>
        </div>
      </div>
      {missing_secs.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
          <h3 className="font-semibold text-red-700 mb-2">Missing Sections</h3>
          <div className="flex flex-wrap gap-2">
            {missing_secs.map(s => (
              <span key={s} className="bg-white border border-red-300 text-red-600 text-xs px-2 py-1 rounded-full capitalize">{s}</span>
            ))}
          </div>
          <p className="text-red-600 text-xs mt-2">Add these sections to improve your ATS score.</p>
        </div>
      )}
    </div>
  )
}
"""

# ── Builder ───────────────────────────────────────────────────────────────
builder = """import { useState } from 'react'

const STEPS = ['Personal','Summary','Experience','Education','Skills','Projects','Preview']
const EMPTY = {
  name:'', email:'', phone:'', linkedin:'', github:'', location:'',
  summary:'',
  experience:[{company:'',role:'',dates:'',bullets:''}],
  education:[{institution:'',degree:'',year:''}],
  skills:'',
  projects:[{name:'',desc:'',tech:'',link:''}]
}

const Input = ({label,value,onChange,placeholder='',type='text'}) => (
  <div>
    <label className="text-sm font-medium text-gray-700">{label}</label>
    <input type={type} value={value} onChange={e=>onChange(e.target.value)} placeholder={placeholder}
      className="mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
  </div>
)

const Textarea = ({label,value,onChange,rows=4,placeholder=''}) => (
  <div>
    <label className="text-sm font-medium text-gray-700">{label}</label>
    <textarea rows={rows} value={value} onChange={e=>onChange(e.target.value)} placeholder={placeholder}
      className="mt-1 w-full border rounded-lg p-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
  </div>
)

function ResumePreview({ data }) {
  return (
    <div id="resume-preview" className="bg-white border rounded-xl p-8 shadow-sm max-w-2xl mx-auto text-gray-800 text-sm leading-relaxed">
      <div className="text-center border-b pb-4 mb-4">
        <h1 className="text-2xl font-bold tracking-wide">{data.name || 'Your Name'}</h1>
        <div className="flex flex-wrap justify-center gap-x-4 gap-y-1 text-gray-500 text-xs mt-1">
          {data.email    && <span>{data.email}</span>}
          {data.phone    && <span>{data.phone}</span>}
          {data.location && <span>{data.location}</span>}
          {data.linkedin && <span>{data.linkedin}</span>}
          {data.github   && <span>{data.github}</span>}
        </div>
      </div>
      {data.summary && (
        <section className="mb-4">
          <h2 className="font-bold uppercase tracking-widest text-xs text-indigo-700 border-b border-indigo-200 pb-1 mb-2">Summary</h2>
          <p>{data.summary}</p>
        </section>
      )}
      {data.experience?.some(e=>e.company) && (
        <section className="mb-4">
          <h2 className="font-bold uppercase tracking-widest text-xs text-indigo-700 border-b border-indigo-200 pb-1 mb-2">Experience</h2>
          {data.experience.filter(e=>e.company).map((e,i) => (
            <div key={i} className="mb-3">
              <div className="flex justify-between">
                <span className="font-semibold">{e.role}</span>
                <span className="text-gray-400 text-xs">{e.dates}</span>
              </div>
              <div className="text-gray-500 text-xs mb-1">{e.company}</div>
              {e.bullets && (
                <ul className="list-disc list-inside space-y-0.5">
                  {e.bullets.split('\\n').filter(Boolean).map((b,j) => (
                    <li key={j}>{b.replace(/^[-*]\\s*/,'')}</li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </section>
      )}
      {data.education?.some(e=>e.institution) && (
        <section className="mb-4">
          <h2 className="font-bold uppercase tracking-widest text-xs text-indigo-700 border-b border-indigo-200 pb-1 mb-2">Education</h2>
          {data.education.filter(e=>e.institution).map((e,i) => (
            <div key={i} className="flex justify-between">
              <span><span className="font-semibold">{e.degree}</span>, {e.institution}</span>
              <span className="text-gray-400 text-xs">{e.year}</span>
            </div>
          ))}
        </section>
      )}
      {data.skills && (
        <section className="mb-4">
          <h2 className="font-bold uppercase tracking-widest text-xs text-indigo-700 border-b border-indigo-200 pb-1 mb-2">Skills</h2>
          <p>{data.skills}</p>
        </section>
      )}
      {data.projects?.some(p=>p.name) && (
        <section className="mb-4">
          <h2 className="font-bold uppercase tracking-widest text-xs text-indigo-700 border-b border-indigo-200 pb-1 mb-2">Projects</h2>
          {data.projects.filter(p=>p.name).map((p,i) => (
            <div key={i} className="mb-2">
              <span className="font-semibold">{p.name}</span>
              {p.tech && <span className="text-gray-400 text-xs ml-2">({p.tech})</span>}
              {p.desc && <p className="text-gray-700">{p.desc}</p>}
              {p.link && <p className="text-indigo-600 text-xs">{p.link}</p>}
            </div>
          ))}
        </section>
      )}
    </div>
  )
}

export default function Builder() {
  const [step, setStep] = useState(0)
  const [data, setData] = useState(EMPTY)

  const upd = (k, v) => setData(d => ({...d, [k]: v}))
  const updArr = (k, i, field, v) => setData(d => {
    const arr = [...d[k]]; arr[i] = {...arr[i], [field]: v}; return {...d, [k]: arr}
  })

  const steps = [
    <div className="space-y-3">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <Input label="Full Name"    value={data.name}     onChange={v=>upd('name',v)}     placeholder="Anvesh Sharma" />
        <Input label="Email"        value={data.email}    onChange={v=>upd('email',v)}    placeholder="you@email.com" type="email" />
        <Input label="Phone"        value={data.phone}    onChange={v=>upd('phone',v)}    placeholder="+91 98765 43210" />
        <Input label="Location"     value={data.location} onChange={v=>upd('location',v)} placeholder="Indore, MP" />
        <Input label="LinkedIn URL" value={data.linkedin} onChange={v=>upd('linkedin',v)} placeholder="linkedin.com/in/yourname" />
        <Input label="GitHub URL"   value={data.github}   onChange={v=>upd('github',v)}   placeholder="github.com/yourname" />
      </div>
    </div>,
    <Textarea label="Professional Summary (2-3 sentences)" rows={5} value={data.summary}
      onChange={v=>upd('summary',v)} placeholder="Results-driven software engineer with 2+ years experience..." />,
    <div className="space-y-4">
      {data.experience.map((e,i) => (
        <div key={i} className="border rounded-lg p-4 space-y-3 bg-gray-50">
          <div className="flex justify-between items-center">
            <h4 className="font-medium text-gray-700">Experience #{i+1}</h4>
            {i > 0 && <button onClick={() => setData(d=>({...d,experience:d.experience.filter((_,j)=>j!==i)}))} className="text-red-400 text-xs hover:text-red-600">Remove</button>}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <Input label="Company" value={e.company} onChange={v=>updArr('experience',i,'company',v)} placeholder="Google" />
            <Input label="Role"    value={e.role}    onChange={v=>updArr('experience',i,'role',v)}    placeholder="Software Engineer" />
            <Input label="Dates"   value={e.dates}   onChange={v=>updArr('experience',i,'dates',v)}   placeholder="Jun 2022 - Present" />
          </div>
          <Textarea label="Bullets (one per line)" rows={4} value={e.bullets}
            onChange={v=>updArr('experience',i,'bullets',v)}
            placeholder={"Developed React dashboard used by 5000+ users\\nReduced API response time by 40%"} />
        </div>
      ))}
      <button onClick={() => setData(d=>({...d,experience:[...d.experience,{company:'',role:'',dates:'',bullets:''}]}))}
        className="text-indigo-600 text-sm hover:underline">+ Add Another Position</button>
    </div>,
    <div className="space-y-4">
      {data.education.map((e,i) => (
        <div key={i} className="border rounded-lg p-4 bg-gray-50">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <Input label="Institution" value={e.institution} onChange={v=>updArr('education',i,'institution',v)} placeholder="IIT Indore" />
            <Input label="Degree"      value={e.degree}      onChange={v=>updArr('education',i,'degree',v)}      placeholder="B.Tech Computer Science" />
            <Input label="Year"        value={e.year}        onChange={v=>updArr('education',i,'year',v)}        placeholder="2024" />
          </div>
        </div>
      ))}
      <button onClick={() => setData(d=>({...d,education:[...d.education,{institution:'',degree:'',year:''}]}))}
        className="text-indigo-600 text-sm hover:underline">+ Add Another</button>
    </div>,
    <Textarea label="Skills (comma-separated)" rows={4} value={data.skills}
      onChange={v=>upd('skills',v)} placeholder="Python, React, FastAPI, PostgreSQL, Docker, Git" />,
    <div className="space-y-4">
      {data.projects.map((p,i) => (
        <div key={i} className="border rounded-lg p-4 space-y-3 bg-gray-50">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <Input label="Project Name"     value={p.name} onChange={v=>updArr('projects',i,'name',v)} placeholder="Resume Intelligence Suite" />
            <Input label="Tech Stack"       value={p.tech} onChange={v=>updArr('projects',i,'tech',v)} placeholder="React, FastAPI, spaCy" />
            <Input label="GitHub/Live Link" value={p.link} onChange={v=>updArr('projects',i,'link',v)} placeholder="github.com/you/project" />
          </div>
          <Textarea label="Description" rows={2} value={p.desc} onChange={v=>updArr('projects',i,'desc',v)}
            placeholder="Built a full-stack resume analysis tool..." />
        </div>
      ))}
      <button onClick={() => setData(d=>({...d,projects:[...d.projects,{name:'',desc:'',tech:'',link:''}]}))}
        className="text-indigo-600 text-sm hover:underline">+ Add Project</button>
    </div>,
    <div className="space-y-4">
      <ResumePreview data={data} />
      <div className="flex gap-3 justify-center">
        <button onClick={() => window.print()}
          className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700">
          Print / Save as PDF
        </button>
      </div>
      <p className="text-center text-xs text-gray-400">Use browser Print then Save as PDF for best results</p>
    </div>
  ]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-800">Resume Builder</h2>
        <p className="text-gray-500 text-sm mt-1">Build your resume from scratch. Export to PDF via browser print.</p>
      </div>
      <div className="flex gap-1 overflow-x-auto">
        {STEPS.map((s,i) => (
          <button key={s} onClick={() => setStep(i)}
            className={"px-3 py-1.5 rounded text-xs font-medium whitespace-nowrap " + (step===i ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200')}>
            {i+1}. {s}
          </button>
        ))}
      </div>
      <div className="bg-white border rounded-xl p-5 shadow-sm">
        <h3 className="font-semibold text-gray-700 mb-4">{STEPS[step]}</h3>
        {steps[step]}
      </div>
      {step < STEPS.length - 1 && (
        <div className="flex justify-between">
          {step > 0
            ? <button onClick={() => setStep(s=>s-1)} className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg text-sm hover:bg-gray-200">Back</button>
            : <div />}
          <button onClick={() => setStep(s=>s+1)} className="bg-indigo-600 text-white px-5 py-2 rounded-lg text-sm hover:bg-indigo-700">Next</button>
        </div>
      )}
    </div>
  )
}
"""

# ── App.jsx ───────────────────────────────────────────────────────────────
app = """import { useState } from 'react'
import Parser from './components/Parser/Parser'
import ATSScorer from './components/ATSScorer/ATSScorer'
import KeywordGap from './components/KeywordGap/KeywordGap'
import Builder from './components/Builder/Builder'
import Tailoring from './components/Tailoring/Tailoring'
import CoverLetter from './components/CoverLetter/CoverLetter'
import VersionManager from './components/VersionManager/VersionManager'
import Dashboard from './components/Dashboard/Dashboard'

const TABS = [
  { id:'parser',   label:'Parser',        component: Parser },
  { id:'ats',      label:'ATS Score',     component: ATSScorer },
  { id:'keywords', label:'Keywords',      component: KeywordGap },
  { id:'builder',  label:'Builder',       component: Builder },
  { id:'tailor',   label:'AI Tailor',     component: Tailoring },
  { id:'cover',    label:'Cover Letter',  component: CoverLetter },
  { id:'versions', label:'Versions',      component: VersionManager },
  { id:'dash',     label:'Dashboard',     component: Dashboard },
]

export default function App() {
  const [tab, setTab]             = useState('parser')
  const [resumeText, setResumeText] = useState('')
  const [parsed, setParsed]       = useState(null)

  const Active = TABS.find(t => t.id === tab)?.component || Parser

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-indigo-700 text-white px-6 py-3 flex items-center gap-3 shadow-md">
        <div>
          <h1 className="font-bold text-lg leading-tight">Resume Intelligence Suite</h1>
          <p className="text-indigo-200 text-xs">Free - Runs locally - No cloud required</p>
        </div>
        <div className="ml-auto">
          <a href="https://github.com/Tony-techno/resume-suite" target="_blank" rel="noreferrer"
            className="text-indigo-200 hover:text-white text-sm">GitHub</a>
        </div>
      </header>
      <nav className="bg-white border-b flex overflow-x-auto">
        {TABS.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={"px-4 py-3 text-sm whitespace-nowrap border-b-2 transition-colors " + (tab===t.id ? 'border-indigo-600 text-indigo-700 font-medium' : 'border-transparent text-gray-500 hover:text-gray-800')}>
            {t.label}
          </button>
        ))}
      </nav>
      <div className="bg-amber-50 border-b border-amber-200 px-6 py-2 text-xs text-amber-800">
        Backend must be running: open a terminal in the backend folder, activate venv, then run: uvicorn main:app --reload --port 8000
      </div>
      <main className="flex-1 p-6 max-w-5xl mx-auto w-full">
        <Active resumeText={resumeText} setResumeText={setResumeText} parsed={parsed} setParsed={setParsed} />
      </main>
      <footer className="text-center text-xs text-gray-400 py-4 border-t">
        Resume Intelligence Suite - MIT License - Built with FastAPI + React + HuggingFace
      </footer>
    </div>
  )
}
"""

files = {
    "src/components/ATSScorer/ATSScorer.jsx": ats,
    "src/components/KeywordGap/KeywordGap.jsx": kw,
    "src/components/Tailoring/Tailoring.jsx": tailor,
    "src/components/CoverLetter/CoverLetter.jsx": cl,
    "src/components/VersionManager/VersionManager.jsx": vm,
    "src/components/Dashboard/Dashboard.jsx": dash,
    "src/components/Builder/Builder.jsx": builder,
    "src/App.jsx": app,
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Written: " + path)

print("All files written OK")