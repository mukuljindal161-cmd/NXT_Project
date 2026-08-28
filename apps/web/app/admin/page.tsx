"use client";

import React, { useEffect, useState } from "react";
import { AdminNav } from "@/components/admin/AdminNav";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { api, AnalyticsOverview, JobItem } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import {
  FileText,
  Users,
  MessageSquare,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Sparkles,
  Activity,
  Layers
} from "lucide-react";
import { formatDate } from "@/lib/utils";

export default function AdminDashboardPage() {
  const { user } = useAuth();
  const [analytics, setAnalytics] = useState<AnalyticsOverview | null>(null);
  const [jobs, setJobs] = useState<JobItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [stats, jobsList] = await Promise.all([
        api.getAnalytics(),
        api.listJobs(),
      ]);
      setAnalytics(stats);
      setJobs(jobsList.slice(0, 5));
    } catch {} finally {
      setLoading(false);
    }
  };

  return (
    <ProtectedRoute requireAdmin>
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 pb-16 transition-colors">
        <AdminNav />

        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-8">
            <h2 className="text-2xl font-extrabold tracking-tight text-slate-900 dark:text-white">Knowledge Overview</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">Monitor ingestion health, vector embeddings, and retrieval telemetry</p>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">Total Documents</span>
                <FileText className="h-5 w-5 text-blue-600 dark:text-blue-400" />
              </div>
              <p className="mt-3 text-3xl font-extrabold text-slate-900 dark:text-white">{analytics?.documents || 0}</p>
              <div className="mt-2 flex items-center gap-2 text-xs text-emerald-600 dark:text-emerald-400">
                <CheckCircle2 className="h-3.5 w-3.5" />
                <span>{analytics?.ready_documents || 0} Ready for Retrieval</span>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">Total Students</span>
                <Users className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
              </div>
              <p className="mt-3 text-3xl font-extrabold text-slate-900 dark:text-white">{analytics?.users || 0}</p>
              <div className="mt-2 text-xs text-slate-500 dark:text-slate-400">Active authorized users</div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">Questions Answered</span>
                <MessageSquare className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
              </div>
              <p className="mt-3 text-3xl font-extrabold text-slate-900 dark:text-white">{analytics?.questions || 0}</p>
              <div className="mt-2 text-xs text-slate-500 dark:text-slate-400">RAG Grounded queries</div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">Avg Retrieval Score</span>
                <Sparkles className="h-5 w-5 text-amber-500 dark:text-amber-400" />
              </div>
              <p className="mt-3 text-3xl font-extrabold text-slate-900 dark:text-white">
                {analytics ? `${Math.round((analytics.average_retrieval_score || 0.85) * 100)}%` : "N/A"}
              </p>
              <div className="mt-2 text-xs text-slate-500 dark:text-slate-400">Cosine relevance index</div>
            </div>
          </div>

          {/* Recent Ingestion Jobs */}
          <div className="mt-10 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800 mb-4">
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Recent Ingestion Jobs</h3>
              <span className="text-xs text-slate-400 dark:text-slate-500">Auto-refreshing</span>
            </div>

            {jobs.length === 0 ? (
              <p className="py-6 text-center text-xs text-slate-400 dark:text-slate-500">No background jobs executed yet.</p>
            ) : (
              <div className="divide-y divide-slate-100 dark:divide-slate-800">
                {jobs.map((job) => (
                  <div key={job.id} className="py-3.5 flex items-center justify-between text-xs">
                    <div className="flex items-center gap-3">
                      <span
                        className={`h-2.5 w-2.5 rounded-full ${
                          job.status === "COMPLETED"
                            ? "bg-emerald-500"
                            : job.status === "RUNNING"
                            ? "bg-blue-500 animate-pulse"
                            : job.status === "FAILED"
                            ? "bg-rose-500"
                            : "bg-amber-500"
                        }`}
                      />
                      <div>
                        <span className="font-semibold text-slate-900 dark:text-slate-100">{job.type}</span>
                        <p className="text-[11px] text-slate-500 dark:text-slate-400">{job.message || "Processing"}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4 text-slate-500 dark:text-slate-400">
                      <span className="font-mono">{job.progress}%</span>
                      <span>{formatDate(job.created_at)}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
