content = """const API = 'http://localhost:8000/api'

async function req(path, options = {}) {
  try {
    const res = await fetch(`${API}${path}`, options)
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }))
      throw new Error(err.detail || 'Request failed')
    }
    return res.json()
  } catch (e) {
    if (e.message.includes('Failed to fetch')) throw new Error('Cannot connect to backend. Make sure backend is running on port 8000.')
    throw e
  }
}

export const uploadResume = (file) => { const fd = new FormData(); fd.append('file', file); return req('/parser/upload', { method:'POST', body:fd }) }
export const parseText    = (text) => req('/parser/parse-text', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({text}) })
export const getATSScore  = (resume_text, job_description) => req('/ats/score', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({resume_text,job_description}) })
export const analyzeKeywords = (resume_text, job_description) => req('/keywords/analyze', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({resume_text,job_description}) })
export const tailorResume    = (resume_text, job_description) => req('/tailor/', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({resume_text,job_description}) })
export const generateCoverLetter = (data) => req('/cover-letter/generate', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data) })
export const listVersions    = () => req('/versions/')
export const saveVersion     = (data) => req('/versions/', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data) })
export const getVersion      = (id) => req(`/versions/${id}`)
export const deleteVersion   = (id) => req(`/versions/${id}`, { method:'DELETE' })
export const compareVersions = (id1,id2) => req(`/versions/compare/${id1}/${id2}`)
"""

with open("src/utils/api.js", "w", encoding="utf-8") as f:
    f.write(content)
print("src/utils/api.js written OK")