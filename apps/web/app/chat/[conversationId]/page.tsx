"use client";

import React from "react";
import { useParams } from "next/navigation";
import { ChatInterface } from "@/components/chat/ChatInterface";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";

export default function DirectConversationPage() {
  const params = useParams();
  const conversationId = params?.conversationId as string | undefined;

  return (
    <ProtectedRoute>
      <ChatInterface initialConversationId={conversationId} />
    </ProtectedRoute>
  );
}
