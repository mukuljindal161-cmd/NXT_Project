"use client";

import React, { useEffect, useState } from "react";
import { AdminNav } from "@/components/admin/AdminNav";
import { UploadModal } from "@/components/admin/UploadModal";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { api, DocumentItem } from "@/lib/api";
import {
  FileText,
  Upload,
  Search,
  Trash2,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  Clock,
  Layers
} from "lucide-react";
import { formatDate } from "@/lib/utils";

export default function AdminDocumentsPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [search, setSearch] = useState("");
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDocs();
  }, [search]);

  const loadDocs = async () => {
    try {
      setLoading(true);
      const res = await api.listDocuments({ search });
      setDocuments(res.items || []);
    } catch {} finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this document and all its indexed vector chunks?")) return;
    try {
      await api.deleteDocument(id);
      loadDocs();
    } catch (e: any) {
      alert(e.message || "Failed to delete document");
    }
  };

  const handleReindex = async (id: string) => {
    try {
      await api.reindexDocument(id);
      loadDocs();
    } catch (e: any) {
      alert(e.message || "Failed to re-index document");
    }
  };

  return (
    <ProtectedRoute requireAdmin>
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 pb-16 transition-colors">
        <AdminNav />

        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
            <div>
              <h2 className="text-xl sm:text-2xl font-extrabold tracking-tight text-slate-900 dark:text-white">Document Management</h2>
              <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">Upload, re-index, and manage official institution records</p>
            </div>
            <button
              onClick={() => setIsUploadOpen(true)}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-blue-700 transition-colors w-full sm:w-auto shrink-0"
            >
              <Upload className="h-4 w-4" />
              Upload Document
            </button>
          </div>

          {/* Filters */}
          <div className="mb-6 flex items-center gap-3">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3.5 top-2.5 h-4 w-4 text-slate-400 dark:text-slate-500" />
              <input
                type="text"
                placeholder="Search by title or filename..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full rounded-xl border border-slate-200 bg-white py-2 pl-10 pr-4 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600/20 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-100 dark:focus:border-blue-500"
              />
            </div>
          </div>

          {/* Responsive Table Container */}
          <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden dark:border-slate-800 dark:bg-slate-900">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[640px] text-left text-xs text-slate-600 dark:text-slate-300">
                <thead className="bg-slate-50/80 dark:bg-slate-950/80 text-[11px] uppercase tracking-wider font-semibold text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800">
                  <tr>
                    <th className="px-4 sm:px-6 py-3.5">Document</th>
                    <th className="px-4 sm:px-6 py-3.5">Status</th>
                    <th className="px-4 sm:px-6 py-3.5">Version</th>
                    <th className="px-4 sm:px-6 py-3.5">Chunks</th>
                    <th className="px-4 sm:px-6 py-3.5">Uploaded</th>
                    <th className="px-4 sm:px-6 py-3.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {documents.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="px-6 py-8 text-center text-slate-400 dark:text-slate-500">
                        {loading ? "Loading documents..." : "No documents found."}
                      </td>
                    </tr>
                  ) : (
                    documents.map((doc) => (
                      <tr key={doc.id} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40 transition-colors">
                        <td className="px-4 sm:px-6 py-4">
                          <div className="flex items-center gap-3">
                            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-50 text-blue-600 dark:bg-blue-950/60 dark:text-blue-400 shrink-0">
                              <FileText className="h-4 w-4" />
                            </div>
                            <div>
                              <p className="font-semibold text-slate-900 dark:text-white">{doc.title}</p>
                              <p className="text-[11px] text-slate-400 dark:text-slate-500">{doc.original_filename} ({(doc.file_size / 1024).toFixed(1)} KB)</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 sm:px-6 py-4">
                          <span
                            className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[11px] font-semibold ${
                              doc.status === "READY"
                                ? "bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-900"
                                : doc.status === "PROCESSING"
                                ? "bg-blue-50 text-blue-700 border border-blue-200 dark:bg-blue-950/40 dark:text-blue-300 dark:border-blue-900 animate-pulse"
                                : doc.status === "FAILED"
                                ? "bg-rose-50 text-rose-700 border border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-900"
                                : "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300"
                            }`}
                          >
                            {doc.status === "READY" && <CheckCircle2 className="h-3 w-3" />}
                            {doc.status === "FAILED" && <AlertCircle className="h-3 w-3" />}
                            {doc.status === "PROCESSING" && <RefreshCw className="h-3 w-3 animate-spin" />}
                            {doc.status}
                          </span>
                        </td>
                        <td className="px-4 sm:px-6 py-4 font-mono text-slate-700 dark:text-slate-300">v{doc.version}</td>
                        <td className="px-4 sm:px-6 py-4 font-semibold text-slate-900 dark:text-white">{doc.chunk_count} chunks</td>
                        <td className="px-4 sm:px-6 py-4 text-slate-500 dark:text-slate-400">{formatDate(doc.created_at)}</td>
                        <td className="px-4 sm:px-6 py-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => handleReindex(doc.id)}
                              className="p-1.5 rounded-lg text-slate-400 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-slate-800 transition-colors"
                              title="Re-index Chunks"
                            >
                              <RefreshCw className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => handleDelete(doc.id)}
                              className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-colors"
                              title="Delete Document"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <UploadModal
          isOpen={isUploadOpen}
          onClose={() => setIsUploadOpen(false)}
          onSuccess={() => loadDocs()}
        />
      </div>
    </ProtectedRoute>
  );
}
