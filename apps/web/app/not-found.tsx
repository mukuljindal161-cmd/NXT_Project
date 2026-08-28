import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function NotFound() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center text-center px-4">
      <h2 className="text-3xl font-extrabold text-slate-900">404 - Page Not Found</h2>
      <p className="mt-2 text-sm text-slate-500 max-w-md">
        The requested page does not exist in the College Assistant portal.
      </p>
      <Link
        href="/"
        className="mt-6 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-blue-700 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Return Home
      </Link>
    </div>
  );
}
