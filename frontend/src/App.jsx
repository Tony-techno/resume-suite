import { useState } from 'react'
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
