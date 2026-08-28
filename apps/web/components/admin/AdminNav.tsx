"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import { LayoutDashboard, FileText, Layers, Activity, ArrowLeft } from "lucide-react";

export function AdminNav() {
  const pathname = usePathname();

  const links = [
    { href: "/admin", label: "Dashboard", icon: LayoutDashboard },
    { href: "/admin/documents", label: "Documents", icon: FileText },
    { href: "/admin/collections", label: "Collections", icon: Layers },
    { href: "/admin/jobs", label: "Ingestion Jobs", icon: Activity },
  ];

  return (
    <div className="mb-6 sm:mb-8 border-b border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900 transition-colors">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between py-3.5 sm:py-4">
          <div className="flex items-center gap-3 sm:gap-4">
            <Link
              href="/chat"
              className="inline-flex items-center gap-1 text-xs font-semibold text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white transition-colors"
            >
              <ArrowLeft className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Back to Chat</span>
              <span className="sm:hidden">Chat</span>
            </Link>
            <h1 className="text-base sm:text-xl font-bold text-slate-900 dark:text-white tracking-tight">Admin Console</h1>
          </div>
          <ThemeToggle />
        </div>

        {/* Responsive Horizontal Scroll Tab Bar */}
        <nav className="flex space-x-6 sm:space-x-8 -mb-px overflow-x-auto pb-1 scrollbar-none">
          {links.map((link) => {
            const Icon = link.icon;
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`flex items-center gap-1.5 sm:gap-2 border-b-2 py-2.5 sm:py-3 text-xs sm:text-sm font-semibold transition-colors shrink-0 ${
                  isActive
                    ? "border-blue-600 text-blue-600 dark:border-blue-400 dark:text-blue-400"
                    : "border-transparent text-slate-500 hover:border-slate-300 hover:text-slate-700 dark:text-slate-400 dark:hover:border-slate-700 dark:hover:text-slate-200"
                }`}
              >
                <Icon className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
                {link.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
}
