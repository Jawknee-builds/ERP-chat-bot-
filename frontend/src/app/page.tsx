"use client";

import { useEffect, useState, useRef } from "react";
import UnifiedDirectory from "@unified-api/react-directory";

export default function Dashboard() {
  const [data, setData] = useState({ customers: [], products: [], invoices: [], invoice_items: [] });
  const [activeTab, setActiveTab] = useState("customers");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  // Chat state
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState<{role: 'user'|'agent', content: string}[]>([
    { role: 'agent', content: 'Hello! I am your Erpy Discovery Agent. Connect an integration in the Integrations tab, then ask me to map data or trigger automations!' }
  ]);
  const [chatInput, setChatInput] = useState("");
  const [isChatLoading, setIsChatLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Connection state
  const [connectionId, setConnectionId] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      const newConnectionId = params.get("connectionId") || params.get("id"); // Unified.to often returns connectionId or id
      if (newConnectionId) {
        setConnectionId(newConnectionId);
        setActiveTab("customers");
        setChatMessages(prev => [...prev, { 
          role: 'agent', 
          content: `Success! I've linked to connection \`${newConnectionId}\`. You can now ask me to create objects, update records, or fetch data from this specific ERP.` 
        }]);
        setIsChatOpen(true);
        // Clean up URL to prevent false triggers on refresh
        window.history.replaceState({}, document.title, window.location.pathname);
      }
    }
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [custRes, prodRes, invRes, itemRes] = await Promise.all([
          fetch("http://localhost:8000/api/customers"),
          fetch("http://localhost:8000/api/products"),
          fetch("http://localhost:8000/api/invoices"),
          fetch("http://localhost:8000/api/invoice_items"),
        ]);
        const customers = await custRes.json();
        const products = await prodRes.json();
        const invoices = await invRes.json();
        const invoice_items = await itemRes.json();
        setData({ customers, products, invoices, invoice_items });
        setError(false);
      } catch (err) {
        console.error("Failed to fetch mock data:", err);
        setError(true);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [chatMessages, isChatOpen]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMsg = chatInput;
    setChatMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setChatInput("");
    setIsChatLoading(true);

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_message: userMsg, connection_id: connectionId || "test_conn_123" })
      });
      
      const responseData = await res.json();
      
      let agentReply = "No response generated.";
      if (responseData.result) agentReply = typeof responseData.result === 'string' ? responseData.result : JSON.stringify(responseData.result, null, 2);
      else if (responseData.message) agentReply = responseData.message;
      else if (responseData.detail) agentReply = responseData.detail;
      
      setChatMessages(prev => [...prev, { role: 'agent', content: agentReply }]);
    } catch {
      setChatMessages(prev => [...prev, { role: 'agent', content: "Network error interacting with AI backend." }]);
    } finally {
      setIsChatLoading(false);
    }
  };

  const renderTable = () => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const items = data[activeTab as keyof typeof data] as any[];
    if (error) return <div className="p-8 text-center text-red-400">Failed to connect to backend on port 8000. Is it running?</div>;
    if (items.length === 0) return <div className="p-8 text-center text-slate-400">No data available</div>;

    const headers = Object.keys(items[0]);

    return (
      <div className="overflow-x-auto rounded-2xl border border-slate-700/50 bg-slate-800/40 backdrop-blur-xl shadow-2xl">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="bg-slate-900/50 text-xs uppercase text-slate-400 border-b border-slate-700/50">
            <tr>
              {headers.map((key) => (
                <th key={key} scope="col" className="px-6 py-5 font-semibold tracking-wider">
                  {key.replace("_", " ")}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700/50">
            {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
            {items.map((row: any, i: number) => (
              <tr key={i} className="hover:bg-slate-700/30 transition-colors duration-200">
                {headers.map((key) => (
                  <td key={key} className="px-6 py-4 whitespace-nowrap">
                    {row[key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-900 to-indigo-950 font-sans text-slate-100 selection:bg-indigo-500/30">
      <div className="mx-auto max-w-6xl px-4 py-16">
        <header className="mb-16 text-center animate-in fade-in slide-in-from-top-8 duration-700">
          <h1 className="bg-gradient-to-b from-indigo-300 to-cyan-300 bg-clip-text text-6xl font-extrabold tracking-tight text-transparent drop-shadow-sm pb-2">
            Erpy-Middleware
          </h1>
          <p className="mt-6 text-xl text-slate-400 font-light tracking-wide">
            Unified Data Discovery & Integration Panel
          </p>
        </header>

        <div className="flex justify-center space-x-3 mb-10 animate-in fade-in zoom-in-95 duration-500 delay-150">
          {["customers", "products", "invoices", "invoice_items", "integrations"].map((tab) => (
             <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-8 py-3 rounded-full font-medium text-sm transition-all duration-300 ${
                activeTab === tab
                  ? "bg-indigo-500 text-white shadow-[0_0_20px_rgba(99,102,241,0.4)] scale-105"
                  : "bg-slate-800/60 text-slate-400 hover:bg-slate-700 hover:text-slate-200 border border-slate-700/50"
              }`}
            >
              {tab.replace("_", " ").charAt(0).toUpperCase() + tab.replace("_", " ").slice(1)} {tab !== 'integrations' ? `(${data[tab as keyof typeof data]?.length || 0})` : ''}
            </button>
          ))}
        </div>

        {loading && activeTab !== "integrations" ? (
          <div className="flex justify-center mt-20">
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-indigo-500 border-t-transparent shadow-lg shadow-indigo-500/20"></div>
          </div>
        ) : (
          <div className="animate-in fade-in slide-in-from-bottom-8 duration-700 delay-300">
             {activeTab === "integrations" ? (
               <div className="bg-slate-800/40 rounded-2xl p-6 border border-slate-700/50 backdrop-blur-xl shadow-2xl flex flex-col items-center w-full min-h-[500px]">
                 {connectionId && (
                   <div className="mb-6 rounded-lg bg-emerald-500/20 px-6 py-3 text-emerald-400 border border-emerald-500/50 shadow-[0_0_15px_rgba(16,185,129,0.2)]">
                     <span className="font-semibold">Connected ERP Link Established:</span> <span className="font-mono text-emerald-300 ml-2">{connectionId}</span>
                   </div>
                 )}
                 <UnifiedDirectory 
                   workspaceId="69c14bd1efbdb1d3d249cbcd" 
                   categories={["accounting", "crm"]} 
                   success_redirect={typeof window !== "undefined" ? window.location.href : ""}
                   failure_redirect={typeof window !== "undefined" ? window.location.href : ""}
                 />
               </div>
             ) : renderTable()}
          </div>
        )}
      </div>

      {/* Floating Chatbot Widget */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
        {isChatOpen && (
          <div className="mb-4 w-96 overflow-hidden rounded-2xl border border-slate-700 bg-slate-800/80 shadow-2xl backdrop-blur-xl animate-in fade-in slide-in-from-bottom-8 duration-300">
            {/* Header */}
            <div className="flex items-center justify-between border-b border-slate-700/80 bg-slate-900/60 p-4">
              <div className="flex items-center space-x-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-500 text-white">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M8 15c4.418 0 8-3.134 8-7s-3.582-7-8-7-8 3.134-8 7c0 1.76.743 3.37 1.97 4.6-.097 1.016-.417 2.13-.771 2.966-.079.186.074.394.273.362 2.256-.37 3.597-.938 4.18-1.234A9 9 0 0 0 8 15"/>
                  </svg>
                </div>
                <h3 className="font-semibold text-slate-200">Agent Gemini</h3>
              </div>
              <button 
                onClick={() => setIsChatOpen(false)}
                className="rounded-lg p-1 text-slate-400 hover:bg-slate-700 hover:text-white transition-colors"
                title="Close chat"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708"/>
                </svg>
              </button>
            </div>

            {/* Messages Body */}
            <div className="flex h-80 flex-col gap-3 overflow-y-auto p-4 scroller">
              {chatMessages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div 
                    className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm whitespace-pre-wrap ${
                      msg.role === 'user' 
                        ? 'bg-indigo-600 text-white rounded-tr-sm shadow-md' 
                        : 'bg-slate-700/80 text-slate-200 rounded-tl-sm shadow-inner'
                    }`}
                  >
                    {msg.content}
                  </div>
                </div>
              ))}
              {isChatLoading && (
                <div className="flex justify-start">
                  <div className="max-w-[85%] rounded-2xl rounded-tl-sm bg-slate-700/80 px-4 py-3 shadow-inner">
                    <div className="flex space-x-1">
                      <div className="h-2 w-2 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.3s]"></div>
                      <div className="h-2 w-2 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.15s]"></div>
                      <div className="h-2 w-2 animate-bounce rounded-full bg-slate-400"></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Input Footer */}
            <form onSubmit={handleSendMessage} className="border-t border-slate-700/80 bg-slate-900/60 p-3">
              <div className="relative flex items-center">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Ask agent to sync or discover..."
                  className="w-full rounded-full border border-slate-600 bg-slate-800 py-2.5 pl-4 pr-12 text-sm text-slate-200 placeholder-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  disabled={isChatLoading}
                />
                <button
                  type="submit"
                  disabled={isChatLoading || !chatInput.trim()}
                  className="absolute right-1.5 flex h-8 w-8 items-center justify-center rounded-full bg-indigo-500 text-white transition-colors hover:bg-indigo-600 disabled:opacity-50"
                  title="Send message"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                     <path d="M15.964.686a.5.5 0 0 0-.65-.65L.767 5.855H.766l-.452.18a.5.5 0 0 0-.082.887l.41.26.001.002 4.995 3.178 3.178 4.995.002.002.26.41a.5.5 0 0 0 .886-.083zm-1.833 1.89L6.637 10.07l-.215-.338a.5.5 0 0 0-.154-.154l-.338-.215 7.494-7.494 1.178-.471z"/>
                  </svg>
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Toggle Button */}
        <button
          onClick={() => setIsChatOpen(!isChatOpen)}
          className="flex h-14 w-14 items-center justify-center rounded-full bg-indigo-600 text-white shadow-[0_0_20px_rgba(99,102,241,0.5)] transition-transform hover:scale-105"
          title="Open AI Chatbot"
        >
          {isChatOpen ? (
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
              <path fillRule="evenodd" d="M13.854 2.146a.5.5 0 0 1 0 .708l-11 11a.5.5 0 0 1-.708-.708l11-11a.5.5 0 0 1 .708 0Z"/>
              <path fillRule="evenodd" d="M2.146 2.146a.5.5 0 0 0 0 .708l11 11a.5.5 0 0 0 .708-.708l-11-11a.5.5 0 0 0-.708 0Z"/>
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="currentColor" viewBox="0 0 16 16">
              <path d="M2 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v11.37A1.5 1.5 0 0 1 11.588 15l-3.34-1.67a1.5 1.5 0 0 0-1.34 0L2.912 15A1.5 1.5 0 0 1 1 13.629zM12 2a1 1 0 0 0-1-1H4a1 1 0 0 0-1 1v11.37a.5.5 0 0 0 .736.446l3.34-1.67a2.5 2.5 0 0 1 2.238 0l3.34 1.67a.5.5 0 0 0 .736-.446z"/>
              <path d="M4 5.5a.5.5 0 0 1 .5-.5h6a.5.5 0 0 1 0 1h-6a.5.5 0 0 1-.5-.5M4 8a.5.5 0 0 1 .5-.5h6a.5.5 0 0 1 0 1h-6A.5.5 0 0 1 4 8"/>
            </svg>
          )}
        </button>
      </div>
    </div>
  );
}
