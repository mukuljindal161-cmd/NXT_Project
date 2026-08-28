"use client";

import React from "react";
import { useAuth } from "@/lib/auth";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import { User, Mail, ShieldCheck, Calendar, LogOut } from "lucide-react";
import { formatDate } from "@/lib/utils";

export default function ProfilePage() {
  const { user, logout } = useAuth();

  return (
    <ProtectedRoute>
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-slate-900 transition-colors">
          <div className="flex items-center justify-between pb-6 border-b border-slate-100 dark:border-slate-800">
            <div className="flex items-center gap-4">
              <div className="h-16 w-16 rounded-2xl bg-blue-600 text-white flex items-center justify-center text-2xl font-bold shadow-md shadow-blue-500/20">
                {user?.full_name ? user.full_name[0].toUpperCase() : "U"}
              </div>
              <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{user?.full_name || "Student"}</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400">{user?.email}</p>
              </div>
            </div>
            <ThemeToggle />
          </div>

          <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div className="rounded-xl border border-slate-100 bg-slate-50/60 p-5 dark:border-slate-800 dark:bg-slate-950">
              <div className="flex items-center gap-2 text-xs font-semibold uppercase text-slate-400 dark:text-slate-500 mb-1">
                <ShieldCheck className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                Role & Permissions
              </div>
              <p className="text-lg font-bold text-slate-900 dark:text-white capitalize">{user?.role}</p>
            </div>

            <div className="rounded-xl border border-slate-100 bg-slate-50/60 p-5 dark:border-slate-800 dark:bg-slate-950">
              <div className="flex items-center gap-2 text-xs font-semibold uppercase text-slate-400 dark:text-slate-500 mb-1">
                <Calendar className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                Account Created
              </div>
              <p className="text-lg font-bold text-slate-900 dark:text-white">{user ? formatDate(user.created_at) : ""}</p>
            </div>
          </div>

          <div className="mt-8 flex justify-end">
            <button
              onClick={() => logout()}
              className="inline-flex items-center gap-2 rounded-xl bg-rose-50 px-4 py-2.5 text-sm font-semibold text-rose-700 hover:bg-rose-100 dark:bg-rose-950/40 dark:text-rose-400 dark:hover:bg-rose-900/60 transition-colors"
            >
              <LogOut className="h-4 w-4" />
              Sign Out
            </button>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
