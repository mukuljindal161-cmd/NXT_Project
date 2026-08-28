import React from "react";
import Link from "next/link";
import {
  GraduationCap,
  Sparkles,
  ShieldCheck,
  Search,
  FileText,
  Database,
  ArrowRight,
  CheckCircle2,
  Lock,
  Layers,
  Cpu
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen transition-colors">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-16 pb-24 lg:pt-24 lg:pb-32 bg-gradient-to-b from-blue-50/50 via-white to-slate-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
        <div className="absolute inset-0 z-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-100/40 via-transparent to-transparent dark:from-blue-900/20"></div>
        
        <div className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50/80 dark:border-blue-900/60 dark:bg-blue-950/60 px-3.5 py-1.5 text-xs font-semibold text-blue-700 dark:text-blue-300 shadow-sm backdrop-blur-sm mb-8">
            <Sparkles className="h-3.5 w-3.5 text-blue-600 dark:text-blue-400 animate-pulse" />
            <span>Strictly Grounded Retrieval-Augmented Generation</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-slate-900 dark:text-white max-w-4xl mx-auto leading-[1.15]">
            Instant, Verified Answers from Official College Documents
          </h1>

          <p className="mt-6 text-lg sm:text-xl text-slate-600 dark:text-slate-300 max-w-2xl mx-auto font-normal">
            No hallucinations. Every response is dynamically retrieved from authoritative institution PDFs, handbooks, and notices with clickable source citations.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/register"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-6 py-3.5 text-base font-semibold text-white shadow-lg shadow-blue-600/25 hover:bg-blue-700 hover:shadow-xl hover:shadow-blue-600/30 transition-all duration-200"
            >
              Get Started Free
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/login"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl border border-slate-300 bg-white px-6 py-3.5 text-base font-semibold text-slate-700 shadow-sm hover:bg-slate-50 hover:border-slate-400 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800 transition-all"
            >
              Sign In to Assistant
            </Link>
          </div>

          {/* Interactive Demo Question Preview */}
          <div className="mt-16 mx-auto max-w-3xl rounded-2xl border border-slate-200 bg-white p-6 shadow-xl text-left dark:border-slate-800 dark:bg-slate-900">
            <div className="flex items-center gap-2 pb-4 border-b border-slate-100 dark:border-slate-800 text-xs font-medium text-slate-500 dark:text-slate-400">
              <span className="h-3 w-3 rounded-full bg-emerald-500 inline-block"></span>
              Live Knowledge Base Grounding Demonstration
            </div>
            <div className="mt-4 space-y-4">
              <div className="flex gap-3 items-start">
                <div className="h-8 w-8 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-xs font-bold text-slate-700 dark:text-slate-300">
                  Q
                </div>
                <div className="flex-1 bg-slate-50 dark:bg-slate-950 rounded-xl p-3.5 text-sm font-medium text-slate-800 dark:text-slate-200 border border-slate-100 dark:border-slate-800">
                  What is the last date to submit the semester fee without a late penalty?
                </div>
              </div>
              <div className="flex gap-3 items-start">
                <div className="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center text-xs font-bold text-white shadow-sm">
                  AI
                </div>
                <div className="flex-1 bg-blue-50/60 dark:bg-blue-950/40 rounded-xl p-3.5 text-sm text-slate-800 dark:text-slate-200 border border-blue-100/80 dark:border-blue-900/60">
                  <p className="leading-relaxed">
                    According to the official <strong>Academic Calendar 2026-27</strong>, the last date for semester fee submission without penalty is <strong>September 15, 2026</strong>. Late submissions incur a fee of $50 between September 16 and September 25.
                  </p>
                  <div className="mt-3 flex items-center gap-2 text-xs">
                    <span className="font-semibold text-slate-600 dark:text-slate-400">Verified Sources:</span>
                    <span className="inline-flex items-center gap-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-md px-2 py-0.5 font-medium text-blue-700 dark:text-blue-400 shadow-2xs">
                      <FileText className="h-3 w-3" /> Fee_Circular_2026.pdf (Page 2) • 94% match
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* RAG Architecture Section */}
      <section className="py-20 bg-white dark:bg-slate-900 border-y border-slate-200/80 dark:border-slate-800">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400 mb-2">Deterministic Pipeline</h2>
            <p className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white sm:text-4xl">
              How the Verified RAG Architecture Works
            </p>
            <p className="mt-4 text-base text-slate-600 dark:text-slate-400">
              Unlike generic chatbots that make up facts, our architecture executes a 7-stage deterministic retrieval and evidence validation pipeline.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="relative rounded-2xl border border-slate-200 bg-slate-50/50 p-6 flex flex-col items-start hover:shadow-md dark:border-slate-800 dark:bg-slate-950 transition-shadow">
              <div className="h-10 w-10 rounded-xl bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300 flex items-center justify-center font-bold mb-4">
                1
              </div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">Structure Extraction</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                PDFs, DOCX, and TXTs are parsed with strict page-boundary and heading awareness to preserve semantic hierarchies.
              </p>
            </div>

            <div className="relative rounded-2xl border border-slate-200 bg-slate-50/50 p-6 flex flex-col items-start hover:shadow-md dark:border-slate-800 dark:bg-slate-950 transition-shadow">
              <div className="h-10 w-10 rounded-xl bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300 flex items-center justify-center font-bold mb-4">
                2
              </div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">Vector Embeddings</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                Text chunks are converted to high-dimensional embeddings and indexed in PostgreSQL using pgvector.
              </p>
            </div>

            <div className="relative rounded-2xl border border-slate-200 bg-slate-50/50 p-6 flex flex-col items-start hover:shadow-md dark:border-slate-800 dark:bg-slate-950 transition-shadow">
              <div className="h-10 w-10 rounded-xl bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300 flex items-center justify-center font-bold mb-4">
                3
              </div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">Evidence Validation</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                Cosine similarity thresholds filter low-relevance results, rejecting insufficient or off-topic context automatically.
              </p>
            </div>

            <div className="relative rounded-2xl border border-slate-200 bg-slate-50/50 p-6 flex flex-col items-start hover:shadow-md dark:border-slate-800 dark:bg-slate-950 transition-shadow">
              <div className="h-10 w-10 rounded-xl bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 flex items-center justify-center font-bold mb-4">
                4
              </div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">Grounded Generation</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                The LLM generates responses strictly using verified snippets, streaming tokens with direct source citations.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Highlights */}
      <section className="py-20 bg-slate-50 dark:bg-slate-950">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <div className="h-12 w-12 rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center mb-5">
                <Search className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Zero-Hallucination Policy</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                When official documents do not contain the answer, the assistant clearly informs the student rather than fabricating policies or contact numbers.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <div className="h-12 w-12 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mb-5">
                <ShieldCheck className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Role-Based Admin Control</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                Administrators can upload documents, manage departmental collections, view ingestion jobs, and monitor retrieval analytics effortlessly.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <div className="h-12 w-12 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mb-5">
                <Cpu className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Fast Real-Time Streaming</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                Server-Sent Events (SSE) provide immediate feedback as retrieval steps finish and tokens stream smoothly to the interface.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-200 bg-white py-8 text-center text-xs text-slate-500 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-400">
        <div className="mx-auto max-w-7xl px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>© 2026 College RAG Assistant. Built for production academic institutions.</p>
          <div className="flex items-center gap-6">
            <Link href="/login" className="hover:text-slate-800 dark:hover:text-slate-200">Student Portal</Link>
            <Link href="/admin" className="hover:text-slate-800 dark:hover:text-slate-200">Admin Console</Link>
            <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="hover:text-slate-800 dark:hover:text-slate-200">API Docs</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
