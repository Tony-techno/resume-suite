import { useState } from 'react'
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
