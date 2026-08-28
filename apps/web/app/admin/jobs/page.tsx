"use client";

import React, { useEffect, useState } from "react";
import { AdminNav } from "@/components/admin/AdminNav";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { api, JobItem } from "@/lib/api";
import { Activity, RefreshCw, CheckCircle2, AlertCircle, Clock } from "lucide-react";
import { formatDate } from "@/lib/utils";

export default function AdminJobsPage() {
  const [jobs, setJobs] = useState<JobItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadJobs();
    const interval = setInterval(loadJobs, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadJobs = async () => {
    try {
      const list = await api.listJobs();
      setJobs(list);
    } catch {} finally {
      setLoading(false);
    }
  };

  return (
    <ProtectedRoute requireAdmin>
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 pb-16 transition-colors">
        <AdminNav />

        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
            <div>
              <h2 className="text-xl sm:text-2xl font-extrabold tracking-tight text-slate-900 dark:text-white">Ingestion Execution Jobs</h2>
              <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">Live monitoring of text extraction, chunking, and embedding generation</p>
            </div>
            <button
              onClick={loadJobs}
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800 transition-colors w-full sm:w-auto shrink-0"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </button>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden dark:border-slate-800 dark:bg-slate-900">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[640px] text-left text-xs text-slate-600 dark:text-slate-300">
                <thead className="bg-slate-50/80 dark:bg-slate-950/80 text-[11px] uppercase tracking-wider font-semibold text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800">
                  <tr>
                    <th className="px-4 sm:px-6 py-3.5">Job ID & Type</th>
                    <th className="px-4 sm:px-6 py-3.5">Status</th>
                    <th className="px-4 sm:px-6 py-3.5">Progress</th>
                    <th className="px-4 sm:px-6 py-3.5">Message / Details</th>
                    <th className="px-4 sm:px-6 py-3.5 text-right">Created At</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {jobs.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="px-6 py-8 text-center text-slate-400 dark:text-slate-500">
                        No background jobs recorded yet.
                      </td>
                    </tr>
                  ) : (
                    jobs.map((job) => (
                      <tr key={job.id} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40 transition-colors">
                        <td className="px-4 sm:px-6 py-4">
                          <div className="flex items-center gap-3">
                            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 dark:bg-indigo-950/60 dark:text-indigo-400 shrink-0">
                              <Activity className="h-4 w-4" />
                            </div>
                            <div>
                              <p className="font-semibold text-slate-900 dark:text-white">{job.type}</p>
                              <p className="font-mono text-[10px] text-slate-400 dark:text-slate-500">{job.id}</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 sm:px-6 py-4">
                          <span
                            className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[11px] font-semibold ${
                              job.status === "COMPLETED"
                                ? "bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-900"
                                : job.status === "RUNNING"
                                ? "bg-blue-50 text-blue-700 border border-blue-200 dark:bg-blue-950/40 dark:text-blue-300 dark:border-blue-900 animate-pulse"
                                : job.status === "FAILED"
                                ? "bg-rose-50 text-rose-700 border border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-900"
                                : "bg-amber-50 text-amber-700 border border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-900"
                            }`}
                          >
                            {job.status === "COMPLETED" && <CheckCircle2 className="h-3 w-3" />}
                            {job.status === "RUNNING" && <RefreshCw className="h-3 w-3 animate-spin" />}
                            {job.status === "FAILED" && <AlertCircle className="h-3 w-3" />}
                            {job.status}
                          </span>
                        </td>
                        <td className="px-4 sm:px-6 py-4">
                          <div className="w-32 sm:w-36">
                            <div className="flex justify-between text-[11px] font-semibold text-slate-700 dark:text-slate-300 mb-1">
                              <span>{job.progress}%</span>
                            </div>
                            <div className="h-1.5 w-full rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                              <div
                                className="h-full bg-blue-600 rounded-full transition-all duration-300"
                                style={{ width: `${job.progress}%` }}
                              />
                            </div>
                          </div>
                        </td>
                        <td className="px-4 sm:px-6 py-4 max-w-xs truncate">
                          <p className="text-slate-800 dark:text-slate-200">{job.message || "—"}</p>
                          {job.error_message && (
                            <p className="text-rose-600 dark:text-rose-400 text-[11px] font-mono">{job.error_message}</p>
                          )}
                        </td>
                        <td className="px-4 sm:px-6 py-4 text-right text-slate-500 dark:text-slate-400 font-mono">
                          {formatDate(job.created_at)}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
