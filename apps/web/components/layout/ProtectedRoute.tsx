"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { GraduationCap, RefreshCw } from "lucide-react";

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAdmin?: boolean;
}

export function ProtectedRoute({ children, requireAdmin = false }: ProtectedRouteProps) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      if (!user) {
        router.push("/login");
      } else if (requireAdmin && user.role !== "admin") {
        router.push("/chat");
      }
    }
  }, [user, loading, requireAdmin, router]);

  if (loading) {
    return (
      <div className="flex min-h-[70vh] flex-col items-center justify-center text-slate-500 dark:text-slate-400 gap-3">
        <div className="h-12 w-12 rounded-2xl bg-blue-600/10 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400 animate-pulse">
          <GraduationCap className="h-6 w-6" />
        </div>
        <div className="flex items-center gap-2 text-xs font-medium">
          <RefreshCw className="h-3.5 w-3.5 animate-spin" />
          <span>Verifying authorization...</span>
        </div>
      </div>
    );
  }

  if (!user || (requireAdmin && user.role !== "admin")) {
    return null;
  }

  return <>{children}</>;
}
