import { useState } from 'react'
import { tailorResume } from '../../utils/api'

const STRONG_VERBS = ['Developed','Built','Designed','Implemented','Optimized','Automated',
  'Analyzed','Delivered','Led','Improved','Created','Deployed','Architected','Streamlined',
  'Generated','Reduced','Increased','Launched','Engineered','Transformed']

const WEAK_VERBS = ['helped','assisted','tried','did','was responsible for','worked on','responsible for']

function autoFixBullet(bullet) {
  if (!bullet.trim()) return bullet
  const lower = bullet.trim().toLowerCase()
  const firstWord = lower.split(' ')[0]
  const isWeak = WEAK_VERBS.some(w => lower.startsWith(w))
  const hasNumber = /\d/.test(bullet)

  let fixed = bullet.trim()

  if (isWeak) {
    const verb = STRONG_VERBS[Math.floor(Math.random() * 5)]
    fixed = verb + ' ' + fixed.replace(/^(helped|assisted|tried|did|worked on)\s*/i, '')
  }

  if (!hasNumber) {
    fixed = fixed.replace(/\.\s*$/, '') + ', improving efficiency by 20%.'
  }

  const cap = fixed.charAt(0).toUpperCase() + fixed.slice(1)
  return cap
}

function autoFixSummary(summary, skills) {
  if (!summary) return summary
  let fixed = summary.trim()
  if (/^i\s/i.test(fixed)) {
    fixed = fixed.replace(/^I am /i, '').replace(/^I have /i, 'Professional with ')
    fixed = fixed.charAt(0).toUpperCase() + fixed.slice(1)
  }
  if (!/\d+\s*(year|month)/i.test(fixed) && skills?.length > 0) {
    fixed = fixed + ' Bringing hands-on experience with ' + skills.slice(0,3).join(', ') + '.'
  }
  return fixed
}

export default function Tailoring({ resumeText, parsed }) {
  const [jd, setJd] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [autoFixed, setAutoFixed] = useState(null)
  const [copied, setCopied] = useState(false)

  async function runAI() {
    if (!resumeText) { setError('Parse a resume first (Parser tab)'); return }
    if (!jd.trim())  { setError('Paste a job description'); return }
    setLoading(true); setError(''); setResult(null); setAutoFixed(null)
    try { setResult(await tailorResume(resumeText, jd)) }
    catch(e) { setError(e.message) } finally { setLoading(false) }
  }

  function runAutoFix() {
    if (!parsed) { setError('Parse a resume first (Parser tab)'); return }
    const bullets = parsed.experience_bullets || []
    const fixedBullets = bullets.map(b => autoFixBullet(b))
    const fixedSummary = autoFixSummary(parsed.summary, parsed.skills)
    setAutoFixed({
      original_bullets: bullets,
      fixed_bullets: fixedBullets,
      original_summary: parsed.summary,
      fixed_summary: fixedSummary,
      skills_to_add: jd ? [] : [],
    })
  }

  async function copyText(text) {
    await navigator.clipboard.writeText(text)
    setCopied(true); setTimeout(() => setCopied(false), 2000)
  }

  function buildFixedResume() {
    if (!autoFixed || !parsed) return ''
    const lines = []
    if (parsed.name) lines.push(parsed.name)
    if (parsed.contact?.email) lines.push(parsed.contact.email)
    if (parsed.contact?.phone) lines.push(parsed.contact.phone)
    lines.push('')
    if (autoFixed.fixed_summary) { lines.push('SUMMARY'); lines.push(autoFixed.fixed_summary); lines.push('') }
    if (autoFixed.fixed_bullets?.length) { lines.push('EXPERIENCE'); autoFixed.fixed_bullets.forEach(b => lines.push('- ' + b)); lines.push('') }
    if (parsed.skills?.length) { lines.push('SKILLS'); lines.push(parsed.skills.join(', ')); lines.push('') }
    return lines.join('\n')
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-800">AI Resume Tailor + Auto-Fix</h2>
        <p className="text-gray-500 text-sm mt-1">Two modes: AI rewrites bullets to match a JD, or Auto-Fix instantly improves weak verbs and adds quantification.</p>
      </div>
      {!resumeText && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-amber-700 text-sm">
          No resume loaded - go to Parser tab first.
        </div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
          <h3 className="font-semibold text-blue-800 mb-1">Mode 1: Auto-Fix (No API needed)</h3>
          <p className="text-blue-600 text-xs mb-3">Instantly fixes weak verbs, adds quantification, and improves your summary. Works 100% offline.</p>
          <button onClick={runAutoFix} disabled={!resumeText}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50 w-full">
            Auto-Fix My Resume Now
          </button>
        </div>
        <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-4">
          <h3 className="font-semibold text-indigo-800 mb-1">Mode 2: AI Tailor (HuggingFace)</h3>
          <p className="text-indigo-600 text-xs mb-3">Rewrites bullets specifically for a job description using Mistral-7B AI. Paste JD below first.</p>
          <button onClick={runAI} disabled={loading || !resumeText}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-50 w-full">
            {loading ? 'AI generating (20-30s)...' : 'AI Tailor for This JD'}
          </button>
        </div>
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">Job Description (for AI Tailor mode)</label>
        <textarea rows={6} placeholder="Paste job description here for AI tailoring..."
          value={jd} onChange={e => setJd(e.target.value)}
          className="w-full border rounded-lg p-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
      </div>
      {error && <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">Error: {error}</div>}

      {autoFixed && (
        <div className="space-y-4">
          <div className="bg-green-50 border border-green-200 rounded-xl p-4">
            <h3 className="font-semibold text-green-800 mb-1">Auto-Fix Complete</h3>
            <p className="text-green-600 text-xs">Weak verbs replaced, quantification added, summary improved.</p>
          </div>
          {autoFixed.fixed_summary && autoFixed.original_summary !== autoFixed.fixed_summary && (
            <div className="bg-white border rounded-xl p-5 shadow-sm space-y-3">
              <h3 className="font-semibold text-gray-700">Summary - Fixed</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <p className="text-xs text-gray-400 mb-1 font-medium">Original</p>
                  <p className="text-sm text-gray-500 bg-red-50 rounded p-2 border border-red-100">{autoFixed.original_summary}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400 mb-1 font-medium">Improved</p>
                  <p className="text-sm text-gray-800 bg-green-50 rounded p-2 border border-green-100">{autoFixed.fixed_summary}</p>
                </div>
              </div>
            </div>
          )}
          {autoFixed.fixed_bullets?.length > 0 && (
            <div className="bg-white border rounded-xl p-5 shadow-sm space-y-3">
              <h3 className="font-semibold text-gray-700">Experience Bullets - Fixed</h3>
              {autoFixed.original_bullets.map((orig, i) => (
                <div key={i} className="grid grid-cols-1 md:grid-cols-2 gap-3 border-b pb-2 last:border-0 last:pb-0">
                  <div>
                    <p className="text-xs text-red-400 mb-1 font-medium">Original</p>
                    <p className="text-sm text-gray-500">{orig}</p>
                  </div>
                  <div>
                    <p className="text-xs text-green-500 mb-1 font-medium">Improved</p>
                    <p className="text-sm text-gray-800 font-medium">{autoFixed.fixed_bullets[i]}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
          <div className="flex gap-3">
            <button onClick={() => copyText(buildFixedResume())}
              className="bg-green-600 text-white px-5 py-2 rounded-lg text-sm hover:bg-green-700">
              {copied ? 'Copied!' : 'Copy Fixed Resume Text'}
            </button>
          </div>
        </div>
      )}

      {result && (
        <div className="space-y-4">
          <div className={"rounded-lg px-4 py-2 text-sm font-medium border " + (result.mode==='ai' ? 'bg-green-50 text-green-700 border-green-200' : 'bg-blue-50 text-blue-700 border-blue-200')}>
            {result.mode === 'ai' ? 'AI-generated output (Mistral-7B via HuggingFace)' : 'Rule-based analysis mode'}
            {result.notice && <span className="ml-2 font-normal opacity-75">- {result.notice}</span>}
          </div>
          {result.mode === 'ai' && result.rewritten_bullets?.length > 0 && (
            <div className="bg-white border rounded-xl p-5 shadow-sm">
              <h3 className="font-semibold text-gray-700 mb-3">AI Rewritten Bullets for This Job</h3>
              <ul className="space-y-2">
                {result.rewritten_bullets.map((b,i) => (
                  <li key={i} className="text-sm text-gray-700 bg-indigo-50 rounded-lg px-3 py-2 border border-indigo-100">
                    {b}
                  </li>
                ))}
              </ul>
              <button onClick={() => copyText(result.rewritten_bullets.join('\n'))}
                className="mt-3 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700">
                {copied ? 'Copied!' : 'Copy All Bullets'}
              </button>
            </div>
          )}
          {result.mode === 'rule_based' && result.suggestions?.length > 0 && (
            <div className="bg-white border rounded-xl p-5 shadow-sm space-y-3">
              <h3 className="font-semibold text-gray-700">Bullet Suggestions</h3>
              {result.suggestions.map((s,i) => (
                <div key={i} className="border rounded-lg p-3 space-y-1">
                  <p className="text-sm text-gray-500"><span className="font-medium text-gray-700">Original: </span>{s.original}</p>
                  <p className={"text-sm " + (s.is_weak_verb ? 'text-red-600' : 'text-indigo-600')}>
                    <span className="font-medium">{s.is_weak_verb ? 'Weak verb - ' : 'Tip: '}</span>{s.suggestion}
                  </p>
                </div>
              ))}
            </div>
          )}
          {result.skills_to_add?.length > 0 && (
            <div className="bg-white border rounded-xl p-5 shadow-sm">
              <h3 className="font-semibold text-gray-700 mb-2">Add These Skills to Match the JD</h3>
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
