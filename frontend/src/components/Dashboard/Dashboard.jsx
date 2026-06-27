import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

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
