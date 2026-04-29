import { createFileRoute } from "@tanstack/react-router";
import { AppLayout } from "@/components/AppLayout";
import { ChatInterface } from "@/components/ChatInterface";

export const Route = createFileRoute("/chat")({
  component: ChatPage,
  head: () => ({
    meta: [
      { title: "RAG Chat · AgriSense AI" },
      { name: "description", content: "Chat with an AI agronomist trained on peer-reviewed sources." },
    ],
  }),
});

function ChatPage() {
  return (
    <AppLayout title="RAG Chat" subtitle="Ask the assistant — answers cite real agronomy sources">
      <ChatInterface />
    </AppLayout>
  );
}
