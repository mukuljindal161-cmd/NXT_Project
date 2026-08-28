"use client";

import React, { useEffect, useState } from "react";
import { AdminNav } from "@/components/admin/AdminNav";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { api, CollectionItem } from "@/lib/api";
import { Layers, Plus, Trash2, FolderPlus } from "lucide-react";
import { formatDate } from "@/lib/utils";

export default function AdminCollectionsPage() {
  const [collections, setCollections] = useState<CollectionItem[]>([]);
  const [name, setName] = useState("");
  const [department, setDepartment] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadCollections();
  }, []);

  const loadCollections = async () => {
    try {
      const list = await api.listCollections();
      setCollections(list);
    } catch {}
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setLoading(true);
    try {
      await api.createCollection({ name, department, description });
      setName("");
      setDepartment("");
      setDescription("");
      loadCollections();
    } catch (err: any) {
      alert(err.message || "Failed to create collection");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this collection?")) return;
    try {
      await api.deleteCollection(id);
      loadCollections();
    } catch (err: any) {
      alert(err.message || "Failed to delete collection");
    }
  };

  return (
    <ProtectedRoute requireAdmin>
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 pb-16 transition-colors">
        <AdminNav />

        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-6">
            <h2 className="text-2xl font-extrabold tracking-tight text-slate-900 dark:text-white">Knowledge Collections</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">Partition college documents by department, division, or topic</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Create Form */}
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm h-fit dark:border-slate-800 dark:bg-slate-900">
              <h3 className="text-base font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                <FolderPlus className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                New Collection
              </h3>
              <form onSubmit={handleCreate} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1.5">
                    Collection Name
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Admissions & Financial Aid"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full rounded-xl border border-slate-200 bg-white py-2 px-3 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600/20 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1.5">
                    Department (Optional)
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Academic Affairs"
                    value={department}
                    onChange={(e) => setDepartment(e.target.value)}
                    className="w-full rounded-xl border border-slate-200 bg-white py-2 px-3 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600/20 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1.5">
                    Description
                  </label>
                  <textarea
                    rows={3}
                    placeholder="Details about documents in this collection..."
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    className="w-full rounded-xl border border-slate-200 bg-white py-2 px-3 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600/20 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading || !name.trim()}
                  className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-blue-700 disabled:opacity-50 transition-all"
                >
                  <Plus className="h-4 w-4" />
                  {loading ? "Creating..." : "Create Collection"}
                </button>
              </form>
            </div>

            {/* Collections List */}
            <div className="lg:col-span-2 space-y-3">
              {collections.length === 0 ? (
                <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center text-xs text-slate-400 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-500">
                  No collections created yet.
                </div>
              ) : (
                collections.map((col) => (
                  <div
                    key={col.id}
                    className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm flex items-start justify-between gap-4 dark:border-slate-800 dark:bg-slate-900"
                  >
                    <div className="flex items-start gap-3.5">
                      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600 dark:bg-indigo-950/60 dark:text-indigo-400 shrink-0">
                        <Layers className="h-5 w-5" />
                      </div>
                      <div>
                        <h4 className="text-sm font-bold text-slate-900 dark:text-white">{col.name}</h4>
                        {col.department && (
                          <span className="mt-0.5 inline-block rounded-md bg-slate-100 dark:bg-slate-800 px-2 py-0.5 text-[10px] font-semibold text-slate-600 dark:text-slate-300">
                            {col.department}
                          </span>
                        )}
                        {col.description && (
                          <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">{col.description}</p>
                        )}
                      </div>
                    </div>
                    <button
                      onClick={() => handleDelete(col.id)}
                      className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:text-slate-500 dark:hover:text-rose-400 dark:hover:bg-rose-950/30 transition-colors"
                      title="Delete Collection"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
