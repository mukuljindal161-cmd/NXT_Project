"use client";

import React from "react";
import { Sparkles } from "lucide-react";

interface SuggestedQuestionsProps {
  onSelect: (question: string) => void;
}

const DEFAULT_QUESTIONS = [
  "What is the fee payment deadline and penalty structure?",
  "What are the library operating hours and borrowing rules?",
  "What is the policy for course registration and add/drop?",
  "What are the hostel room allocation and curfew guidelines?",
];

export function SuggestedQuestions({ onSelect }: SuggestedQuestionsProps) {
  return (
    <div className="mx-auto max-w-2xl px-4 py-8 text-center">
      <div className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-100 text-blue-600 dark:bg-blue-950/60 dark:text-blue-400 mb-4 shadow-sm">
        <Sparkles className="h-6 w-6" />
      </div>
      <h3 className="text-xl font-bold text-slate-900 dark:text-white">How can I assist you today?</h3>
      <p className="mt-1 text-sm text-slate-500 dark:text-slate-400 max-w-md mx-auto">
        Ask anything regarding admissions, exams, hostel rules, fees, or academics.
      </p>

      <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-left">
        {DEFAULT_QUESTIONS.map((q, idx) => (
          <button
            key={idx}
            onClick={() => onSelect(q)}
            className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white p-3.5 text-xs font-medium text-slate-700 shadow-2xs hover:border-blue-500 hover:bg-blue-50/40 hover:text-blue-900 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300 dark:hover:border-blue-500 dark:hover:bg-blue-950/40 dark:hover:text-blue-200 transition-all text-left"
          >
            <span className="text-blue-500 dark:text-blue-400 font-bold">•</span>
            <span className="flex-1">{q}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
