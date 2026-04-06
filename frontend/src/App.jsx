import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Upload, History, Activity, ShieldCheck, Download, AlertCircle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [file, setFile] = useState(null);
  const [weight, setWeight] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => { fetchHistory(); }, []);

  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${API_BASE}/history`);
      setHistory(res.data.history);
    } catch (err) { console.error("Backend not reachable"); }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file || !weight) return alert("Upload image and enter weight!");
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("weight_g", weight);

    try {
      const res = await axios.post(`${API_BASE}/analyze`, formData);
      setResult(res.data);
      fetchHistory();
    } catch (err) { alert("Analysis failed!"); }
    finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-8 text-slate-900">
      <header className="max-w-6xl mx-auto mb-10 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-black text-indigo-900 flex items-center gap-2">
            <Activity className="text-indigo-600" /> SOIL_SCAN
          </h1>
          <p className="text-slate-500 font-medium">UV Microplastic Analysis Dashboard</p>
        </div>
      </header>

      <main className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">

        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white p-6 rounded-3xl shadow-xl border border-indigo-50">
            <h2 className="text-xl font-bold mb-6 flex items-center gap-2"><Upload size={20} /> New Scan</h2>
            <form onSubmit={handleUpload} className="space-y-4">
              <input type="file" onChange={(e) => setFile(e.target.files[0])} className="w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100" />
              <input type="number" placeholder="Soil weight (g)" value={weight} onChange={(e) => setWeight(e.target.value)} className="w-full p-3 rounded-xl bg-slate-50 border-none focus:ring-2 focus:ring-indigo-500 outline-none" />
              <button className="w-full bg-indigo-600 text-white font-bold p-4 rounded-xl hover:bg-indigo-700 transition-all">
                {loading ? "Analyzing..." : "Start UV Analysis"}
              </button>
            </form>

            {result && (
              <div className="mt-8 pt-8 border-t border-slate-100">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  <div>
                    <img src={result.processed_image_url} className="rounded-2xl border-4 border-slate-50 w-full" />
                    <button
                      onClick={() => window.open(`${API_BASE}/download-pdf/${result.filename}/${weight}/${result.summary.total_particles}`)}
                      className="mt-4 w-full flex items-center justify-center gap-2 bg-slate-900 text-white p-3 rounded-xl font-bold hover:bg-slate-800 transition-all"
                    >
                      <Download size={18} /> Download PDF Report
                    </button>
                  </div>

                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <p className="text-4xl font-black text-indigo-600">{result.summary.concentration_p_kg} <span className="text-sm font-normal text-slate-400">p/kg</span></p>
                      <div className={`px-4 py-2 rounded-full text-xs font-black uppercase ${result.summary.risk_level === 'High' ? 'bg-red-100 text-red-600' : 'bg-green-100 text-green-600'}`}>
                        {result.summary.risk_level} Risk
                      </div>
                    </div>

                    <div className="bg-indigo-50 p-4 rounded-2xl border border-indigo-100">
                      <h3 className="text-sm font-bold text-indigo-900 mb-2 flex items-center gap-2">
                        <AlertCircle size={16} /> Remediation Advice
                      </h3>
                      <ul className="text-xs space-y-2 text-indigo-800">
                        {result.summary.suggestions.map((s, i) => <li key={i}>• {s}</li>)}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="bg-white p-6 rounded-3xl shadow-xl border border-indigo-50">
            <h3 className="text-sm font-bold text-slate-400 uppercase mb-4">Concentration Trend</h3>
            <div className="h-48 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={[...history].reverse()}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="date" hide />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="concentration" stroke="#4f46e5" strokeWidth={3} dot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-3xl shadow-xl border border-indigo-50 h-[800px] overflow-y-auto">
          <h2 className="text-xl font-bold mb-6 flex items-center gap-2"><History size={20} /> History</h2>
          <div className="space-y-3">
            {history.map(item => (
              <div key={item.id} className="p-4 bg-slate-50 rounded-2xl flex items-center gap-4">
                <img src={item.image_url} className="w-12 h-12 rounded-lg object-cover" />
                <div className="flex-1">
                  <p className="font-bold text-slate-800">{item.concentration} p/kg</p>
                  <p className="text-[10px] text-slate-400">{item.date}</p>
                </div>
                <ShieldCheck size={18} className={item.risk === 'High' ? 'text-red-400' : 'text-green-400'} />
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;