import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Upload, MapPin, Activity, Download, Database, Info, Layers } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, Cell } from 'recharts';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [file, setFile] = useState(null);
  const [weight, setWeight] = useState("");
  const [location, setLocation] = useState({ lat: 20.5937, lon: 78.9629 }); // Default to India center
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [view, setView] = useState('dashboard'); // 'dashboard' or 'map'

  useEffect(() => {
    fetchHistory();
    navigator.geolocation.getCurrentPosition(
      (pos) => setLocation({ lat: pos.coords.latitude, lon: pos.coords.longitude }),
      () => console.log("Location access denied")
    );
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${API_BASE}/history`);
      setHistory(res.data.history);
    } catch (err) { console.error("API Offline"); }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file || !weight) return alert("Missing data!");
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("weight_g", weight);
    formData.append("lat", location.lat);
    formData.append("lon", location.lon);

    try {
      const res = await axios.post(`${API_BASE}/analyze`, formData);
      setResult(res.data);
      fetchHistory();
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-900 font-sans">
      {/* NAVIGATION BAR */}
      <nav className="bg-white border-b border-slate-200 px-8 py-4 sticky top-0 z-[1000] flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="bg-indigo-600 p-2 rounded-lg text-white"><Activity size={24} /></div>
          <h1 className="text-xl font-black tracking-tighter text-slate-800">SOIL_SCAN <span className="text-indigo-600">ULTRA</span></h1>
        </div>
        <div className="flex bg-slate-100 p-1 rounded-xl">
          <button onClick={() => setView('dashboard')} className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${view === 'dashboard' ? 'bg-white shadow-sm text-indigo-600' : 'text-slate-500'}`}>ANALYSIS</button>
          <button onClick={() => setView('map')} className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${view === 'map' ? 'bg-white shadow-sm text-indigo-600' : 'text-slate-500'}`}>SITE MAP</button>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto p-6 lg:p-10">
        {view === 'dashboard' ? (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

            {/* INPUT PANEL */}
            <div className="lg:col-span-4 space-y-6">
              <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-200">
                <h2 className="text-sm font-black text-slate-400 uppercase mb-6 flex items-center gap-2"><Layers size={16} /> Sample Input</h2>
                <form onSubmit={handleUpload} className="space-y-4">
                  <div className="group relative border-2 border-dashed border-slate-200 rounded-2xl p-8 text-center hover:bg-slate-50 transition-all">
                    <input type="file" onChange={(e) => setFile(e.target.files[0])} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" />
                    <Upload className="mx-auto mb-2 text-slate-300 group-hover:text-indigo-500" />
                    <p className="text-xs font-bold text-slate-500">{file ? file.name : "Drop UV Image Here"}</p>
                  </div>
                  <input type="number" placeholder="Weight (grams)" value={weight} onChange={(e) => setWeight(e.target.value)} className="w-full p-4 rounded-xl bg-slate-50 border-none focus:ring-2 focus:ring-indigo-500 outline-none font-bold" />
                  <div className="p-3 bg-indigo-50 rounded-xl flex items-center justify-between text-[10px] font-bold text-indigo-600">
                    <div className="flex items-center gap-1"><MapPin size={12} /> GPS STAMP</div>
                    <div>{location.lat.toFixed(4)}, {location.lon.toFixed(4)}</div>
                  </div>
                  <button className="w-full bg-indigo-600 text-white font-black py-4 rounded-xl shadow-xl shadow-indigo-100 hover:scale-[1.02] active:scale-[0.98] transition-all">
                    {loading ? "PROCESSING..." : "GENERATE ANALYSIS"}
                  </button>
                </form>
              </div>

              {/* RECENT HISTORY MINI-LIST */}
              <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-200">
                <h2 className="text-sm font-black text-slate-400 uppercase mb-4 flex items-center gap-2"><Database size={16} /> Log History</h2>
                <div className="space-y-3">
                  {history.slice(0, 5).map(h => (
                    <div key={h.id} className="flex justify-between items-center p-3 bg-slate-50 rounded-xl">
                      <div className="text-[10px] font-bold">#{h.id} — {h.conc} <span className="text-slate-400">p/kg</span></div>
                      <div className={`w-2 h-2 rounded-full ${h.risk === 'High' ? 'bg-red-500' : 'bg-green-500'}`}></div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* RESULTS PANEL */}
            <div className="lg:col-span-8 space-y-6">
              {result ? (
                <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-200 animate-in fade-in zoom-in duration-500">
                  <div className="flex justify-between items-start mb-8">
                    <div>
                      <h2 className="text-3xl font-black text-slate-800 tracking-tight">{result.summary.concentration} <span className="text-sm font-normal text-slate-400">Particles per Kilogram</span></h2>
                      <p className="text-xs font-bold text-slate-400 mt-1">UUID: {result.filename}</p>
                    </div>
                    <div className={`px-6 py-2 rounded-full text-xs font-black uppercase tracking-widest ${result.summary.risk === 'High' ? 'bg-red-100 text-red-600' : 'bg-emerald-100 text-emerald-600'}`}>
                      {result.summary.risk} POLLUTION RISK
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="space-y-4">
                      <div className="relative group">
                        <img src={result.image_url} className="rounded-2xl border-4 border-slate-100 shadow-inner w-full" alt="Analyzed" />
                        <div className="absolute top-4 left-4 bg-black/60 backdrop-blur-md text-white text-[10px] font-bold px-3 py-1 rounded-full uppercase">AI Overlay Active</div>
                      </div>
                      <button onClick={() => window.open(`${API_BASE}/download-pdf/${result.filename}/${weight}/${result.summary.total}/${result.summary.fibers}/${result.summary.fragments}/${location.lat}/${location.lon}`)} className="w-full flex items-center justify-center gap-2 bg-slate-900 text-white font-bold py-4 rounded-xl hover:bg-black transition-all">
                        <Download size={18} /> DOWNLOAD SCIENTIFIC DOSSIER
                      </button>
                    </div>

                    <div className="space-y-6">
                      <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100">
                        <h3 className="text-[10px] font-black text-slate-400 uppercase mb-4 flex items-center gap-1"><Info size={12} /> Morphological Breakdown</h3>
                        <div className="h-40 w-full">
                          <ResponsiveContainer>
                            <BarChart data={[
                              { name: 'Fibers', val: result.summary.fibers, color: '#06b6d4' },
                              { name: 'Frags', val: result.summary.fragments, color: '#10b981' }
                            ]}>
                              <XAxis dataKey="name" fontSize={10} fontWeight="bold" axisLine={false} tickLine={false} />
                              <Bar dataKey="val" radius={[6, 6, 0, 0]}>
                                {[0, 1].map((entry, index) => <Cell key={index} fill={index === 0 ? '#06b6d4' : '#10b981'} />)}
                              </Bar>
                              <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }} />
                            </BarChart>
                          </ResponsiveContainer>
                        </div>
                      </div>

                      <div className="bg-indigo-900 p-6 rounded-2xl text-white shadow-lg shadow-indigo-100">
                        <h3 className="text-[10px] font-black text-indigo-300 uppercase mb-3">Expert Remediation Strategy</h3>
                        <ul className="space-y-3">
                          {result.suggestions.map((s, i) => (
                            <li key={i} className="text-xs font-medium leading-relaxed flex gap-2">
                              <span className="text-indigo-400">⚡</span> {s}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="bg-white rounded-3xl border border-dashed border-slate-300 h-full flex flex-col items-center justify-center p-20 text-center opacity-50">
                  <div className="bg-slate-100 p-6 rounded-full mb-4"><Activity size={48} className="text-slate-400" /></div>
                  <h3 className="text-xl font-bold text-slate-700">Awaiting Sample Upload</h3>
                  <p className="text-sm text-slate-500 max-w-xs mt-2">Upload a high-resolution UV scan of the soil sample to begin the deep-characterization process.</p>
                </div>
              )}
            </div>
          </div>
        ) : (
          /* FULL SCREEN MAP VIEW */
          <div className="h-[75vh] w-full rounded-3xl overflow-hidden shadow-2xl border-4 border-white">
            <MapContainer center={[location.lat, location.lon]} zoom={5} style={{ height: '100%', width: '100%' }}>
              <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
              {history.map(h => (
                <Marker key={h.id} position={[h.lat || 0, h.lon || 0]}>
                  <Popup>
                    <div className="font-sans">
                      <p className="font-black text-indigo-600 uppercase text-[10px]">ID: #{h.id}</p>
                      <p className="text-sm font-bold">Conc: {h.conc} p/kg</p>
                      <p className="text-[10px] text-slate-400">{h.date}</p>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;