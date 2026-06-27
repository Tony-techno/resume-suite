import { useState, useRef } from 'react'
import { uploadResume, parseText } from '../../utils/api'

const Card = ({ title, children }) => (
  <div className="bg-white border rounded-xl p-4 shadow-sm">
    <h4 className="font-semibold text-gray-700 mb-2">{title}</h4>
    {children}
  </div>
)

const Row = ({ label, value }) => value ? (
  <div className="flex gap-2 text-sm py-0.5">
    <span className="text-gray-400 w-28 shrink-0">{label}</span>
    <span className="text-gray-800 break-all">{String(value)}</span>
  </div>
) : null

export default function Parser({ setResumeText, setParsed }) {
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState('')
  const [result,  setResult]  = useState(null)
  const [mode,    setMode]    = useState('upload')
  const [paste,   setPaste]   = useState('')
  const fileRef = useRef()

  async function handleFile(e) {
    const file = e.target.files[0]
    if (!file) return
    setLoading(true); setError(''); setResult(null)
    try {
      const d = await uploadResume(file)
      setResult(d); setResumeText(d.raw_text || ''); setParsed(d)
    } catch(err) { setError(err.message) }
    finally { setLoading(false) }
  }

  async function handlePaste() {
    if (!paste.trim()) return
    setLoading(true); setError(''); setResult(null)
    try {
      const d = await parseText(paste)
      setResult(d); setResumeText(paste); setParsed(d)
    } catch(err) { setError(err.message) }
    finally { setLoading(false) }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-800">Resume Parser</h2>
        <p className="text-gray-500 text-sm mt-1">Upload PDF, DOCX, or TXT to extract structured data from your resume.</p>
      </div>
      <div className="flex gap-2">
        {['upload','paste'].map(m => (
          <button key={m} onClick={() => setMode(m)}
            className={"px-4 py-2 rounded text-sm font-medium " + (mode===m ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200')}>
            {m === 'upload' ? 'Upload File' : 'Paste Text'}
          </button>
        ))}
      </div>
      {mode === 'upload' ? (
        <div onClick={() => fileRef.current.click()}
          className="border-2 border-dashed border-indigo-300 rounded-xl p-10 text-center cursor-pointer hover:bg-indigo-50 transition-colors">
          <p className="font-medium text-gray-700 text-lg">Click to upload resume</p>
          <p className="text-sm text-gray-400 mt-1">PDF / DOCX / TXT</p>
          <input ref={fileRef} type="file" accept=".pdf,.docx,.txt" className="hidden" onChange={handleFile} />
        </div>
      ) : (
        <div className="space-y-2">
          <textarea rows={10} placeholder="Paste resume text here..."
            value={paste} onChange={e => setPaste(e.target.value)}
            className="w-full border rounded-lg p-3 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-indigo-400" />
          <button onClick={handlePaste}
            className="bg-indigo-600 text-white px-6 py-2 rounded-lg text-sm hover:bg-indigo-700">
            Parse Resume
          </button>
        </div>
      )}
      {loading && <div className="text-center py-8 text-indigo-600 animate-pulse">Parsing your resume...</div>}
      {error   && <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">Error: {error}</div>}
      {result && (
        <div className="space-y-4">
          <h3 className="font-semibold text-gray-700 text-lg">Parsed Results</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card title="Identity">
              <Row label="Name"     value={result.name} />
              <Row label="Email"    value={result.contact?.email} />
              <Row label="Phone"    value={result.contact?.phone} />
              <Row label="LinkedIn" value={result.contact?.linkedin} />
              <Row label="GitHub"   value={result.contact?.github} />
            </Card>
            <Card title="Quality Scores">
              <Row label="Word Count"   value={result.word_count} />
              <Row label="Action Verbs" value={result.action_verb_score?.score + '/100 (' + result.action_verb_score?.strong + ' strong, ' + result.action_verb_score?.weak + ' weak)'} />
              <Row label="Quantified"   value={result.quantification_score?.score + '/100 (' + result.quantification_score?.quantified + '/' + result.quantification_score?.total + ' bullets)'} />
              <Row label="Sections"     value={(result.sections_found || []).join(', ')} />
            </Card>
          </div>
          <Card title="Skills Detected">
            <div className="flex flex-wrap gap-2 mt-1">
              {(result.skills || []).map(s => (
                <span key={s} className="bg-indigo-100 text-indigo-700 text-xs px-2 py-1 rounded-full">{s}</span>
              ))}
              {!result.skills?.length && <span className="text-gray-400 text-sm">No skills detected</span>}
            </div>
          </Card>
          {result.experience_bullets?.length > 0 && (
            <Card title="Experience Bullets">
              <ul className="space-y-1 mt-1">
                {result.experience_bullets.slice(0,8).map((b,i) => (
                  <li key={i} className="text-sm text-gray-700 flex gap-2">
                    <span className="text-indigo-400 shrink-0">-</span>{b}
                  </li>
                ))}
              </ul>
            </Card>
          )}
          {result.formatting_issues?.length > 0 && (
            <Card title="Formatting Warnings">
              {result.formatting_issues.map((iss,i) => (
                <p key={i} className="text-amber-700 text-sm">- {iss}</p>
              ))}
            </Card>
          )}
          <p className="text-xs text-gray-400">Resume stored. Switch to ATS Score, Keywords, or Tailor tabs to continue.</p>
        </div>
      )}
    </div>
  )
}
