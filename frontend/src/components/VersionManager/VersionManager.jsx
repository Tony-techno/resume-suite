import { useState, useEffect } from 'react'
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
