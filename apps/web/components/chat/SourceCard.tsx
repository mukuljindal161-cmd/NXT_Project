"use client";

import React, { useState } from "react";
import { Citation } from "@/lib/api";
import { FileText, ChevronDown, ChevronUp } from "lucide-react";

interface SourceCardProps {
  citations: Citation[];
}

export function SourceCard({ citations }: SourceCardProps) {
  const [expanded, setExpanded] = useState(false);

  if (!citations || citations.length === 0) return null;

  return (
    <div className="mt-3.5 rounded-xl border border-blue-200/80 bg-blue-50/50 p-3.5 text-xs text-slate-700 dark:border-blue-900/60 dark:bg-blue-950/30 dark:text-slate-300 transition-colors">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center justify-between font-semibold text-blue-900 dark:text-blue-300 hover:text-blue-950 dark:hover:text-blue-200 transition-colors"
      >
        <span className="flex items-center gap-1.5">
          <FileText className="h-4 w-4 text-blue-600 dark:text-blue-400" />
          Verified Citations ({citations.length} sources)
        </span>
        {expanded ? (
          <ChevronUp className="h-4 w-4 text-slate-500" />
        ) : (
          <ChevronDown className="h-4 w-4 text-slate-500" />
        )}
      </button>

      {expanded && (
        <div className="mt-3 space-y-2 border-t border-blue-200/60 dark:border-blue-900/60 pt-3">
          {citations.map((c, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between rounded-lg bg-white p-2.5 border border-slate-200/80 shadow-2xs dark:bg-slate-900 dark:border-slate-800 transition-colors"
            >
              <div className="flex items-center gap-2 overflow-hidden">
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-blue-100 text-[10px] font-bold text-blue-700 dark:bg-blue-900/60 dark:text-blue-300">
                  {c.citation_order || idx + 1}
                </span>
                <span className="truncate font-medium text-slate-900 dark:text-slate-100" title={c.document_name}>
                  {c.document_name}
                </span>
              </div>
              <div className="flex items-center gap-3 shrink-0 text-[11px] text-slate-500 dark:text-slate-400">
                {c.page_number && (
                  <span className="rounded bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 font-medium text-slate-600 dark:text-slate-300">
                    Page {c.page_number}
                  </span>
                )}
                <span className="font-semibold text-emerald-600 dark:text-emerald-400">
                  {Math.round(c.similarity_score * 100)}% match
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
