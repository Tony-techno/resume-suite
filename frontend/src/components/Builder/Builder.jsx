import { useState } from 'react'

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

function analyzeSummary(summary) {
  if (!summary || summary.length < 20) return { score: 0, tips: ['Write a summary of at least 2-3 sentences.'] }
  const tips = []
  let score = 40

  if (summary.length > 100) score += 15
  if (summary.length > 200) score += 10

  const hasYears = /\d+\s*(year|month)/i.test(summary)
  if (hasYears) score += 10
  else tips.push('Mention your years of experience e.g. "2+ years of experience in..."')

  const hasSkills = /(python|java|react|sql|machine learning|data|cloud|aws|node|django)/i.test(summary)
  if (hasSkills) score += 10
  else tips.push('Mention 2-3 key technical skills in your summary.')

  const hasRole = /(engineer|developer|analyst|scientist|designer|manager|intern)/i.test(summary)
  if (hasRole) score += 10
  else tips.push('Include your job title or target role e.g. "Software Engineer" or "Data Analyst".')

  const hasImpact = /(built|developed|improved|delivered|led|achieved|designed|optimized)/i.test(summary)
  if (hasImpact) score += 5
  else tips.push('Add at least one achievement verb like "Built", "Developed", or "Led".')

  const firstPerson = /^i\s/i.test(summary.trim())
  if (firstPerson) tips.push('Avoid starting with "I". Start with your role e.g. "Data Analyst with 2+ years..."')

  if (tips.length === 0) tips.push('Your summary looks strong!')

  return { score: Math.min(score, 100), tips }
}

function SummaryAnalyzer({ value, onChange }) {
  const analysis = analyzeSummary(value)
  const color = analysis.score >= 70 ? 'text-green-600' : analysis.score >= 40 ? 'text-yellow-600' : 'text-red-500'
  const barColor = analysis.score >= 70 ? 'bg-green-500' : analysis.score >= 40 ? 'bg-yellow-500' : 'bg-red-500'

  const exampleSummary = 'Results-driven Data Analyst with 1+ year of experience in Python, SQL, and Machine Learning. Developed predictive models that improved data processing efficiency by 30%. Passionate about turning raw data into actionable business insights.'

  return (
    <div className="space-y-3">
      <Textarea label="Professional Summary" rows={5} value={value} onChange={onChange}
        placeholder="Results-driven Data Analyst with 1+ year of experience in Python, SQL, and Machine Learning..." />
      {value.length > 10 && (
        <div className="border rounded-lg p-4 bg-gray-50 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Summary Score</span>
            <span className={"text-lg font-bold " + color}>{analysis.score}/100</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className={"h-2 rounded-full transition-all " + barColor} style={{width: analysis.score + '%'}} />
          </div>
          <div className="space-y-1 mt-2">
            {analysis.tips.map((tip, i) => (
              <p key={i} className="text-xs text-gray-600 flex gap-1">
                <span className={analysis.tips[0] === 'Your summary looks strong!' ? 'text-green-500' : 'text-amber-500'}>-</span>
                {tip}
              </p>
            ))}
          </div>
          {analysis.score < 80 && (
            <div className="mt-3 border-t pt-3">
              <p className="text-xs font-medium text-gray-600 mb-1">Example of a strong summary:</p>
              <p className="text-xs text-gray-500 italic">{exampleSummary}</p>
              <button onClick={() => onChange(exampleSummary)}
                className="mt-2 text-xs text-indigo-600 hover:underline">
                Use this as a starting point (you can edit it)
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

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
                  {e.bullets.split('\n').filter(Boolean).map((b,j) => (
                    <li key={j}>{b.replace(/^[-*]\s*/,'')}</li>
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
            <div key={i} className="flex justify-between mb-1">
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

    <SummaryAnalyzer value={data.summary} onChange={v=>upd('summary',v)} />,

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
          <div>
            <Textarea label="Bullets (one per line, start each with an action verb)" rows={5} value={e.bullets}
              onChange={v=>updArr('experience',i,'bullets',v)}
              placeholder={"Developed ML pipeline that improved accuracy by 25%\nAnalyzed 50K+ records using Python and SQL\nBuilt dashboards in Power BI for 3 business teams"} />
            <p className="text-xs text-gray-400 mt-1">Tip: Start each bullet with a strong verb: Developed, Built, Analyzed, Improved, Designed, Led</p>
          </div>
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

    <div className="space-y-2">
      <Textarea label="Skills (comma-separated)" rows={3} value={data.skills}
        onChange={v=>upd('skills',v)} placeholder="Python, SQL, Power BI, Pandas, NumPy, Machine Learning, TensorFlow, Git" />
      <p className="text-xs text-gray-400">Tip: Include both technical skills and tools. Separate with commas.</p>
    </div>,

    <div className="space-y-4">
      {data.projects.map((p,i) => (
        <div key={i} className="border rounded-lg p-4 space-y-3 bg-gray-50">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <Input label="Project Name"     value={p.name} onChange={v=>updArr('projects',i,'name',v)} placeholder="Resume Intelligence Suite" />
            <Input label="Tech Stack"       value={p.tech} onChange={v=>updArr('projects',i,'tech',v)} placeholder="React, FastAPI, Python" />
            <Input label="GitHub/Live Link" value={p.link} onChange={v=>updArr('projects',i,'link',v)} placeholder="github.com/Tony-techno/resume-suite" />
          </div>
          <div>
            <Textarea label="Description (start with an action verb + impact)" rows={2} value={p.desc} onChange={v=>updArr('projects',i,'desc',v)}
              placeholder="Built a full-stack resume analysis tool with ATS scoring, keyword gap analysis, and AI-powered tailoring." />
            <p className="text-xs text-gray-400 mt-1">Tip: Mention what you built, the tech used, and the impact or purpose.</p>
          </div>
        </div>
      ))}
      <button onClick={() => setData(d=>({...d,projects:[...d.projects,{name:'',desc:'',tech:'',link:''}]}))}
        className="text-indigo-600 text-sm hover:underline">+ Add Project</button>
    </div>,

    <div className="space-y-4">
      <ResumePreview data={data} />
      <div className="flex gap-3 justify-center flex-wrap">
        <button onClick={() => window.print()}
          className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 text-sm">
          Print / Save as PDF
        </button>
      </div>
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-blue-700 text-xs text-center">
        When print dialog opens: set Destination to "Save as PDF", turn off Headers and Footers, set margins to None or Minimum.
      </div>
    </div>
  ]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-800">Resume Builder</h2>
        <p className="text-gray-500 text-sm mt-1">Build your resume step by step. Each section has tips to improve your score.</p>
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
