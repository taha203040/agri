import { createFileRoute } from "@tanstack/react-router";
import { AppLayout } from "@/components/AppLayout";
import { Dashboard } from "@/components/Dashboard";

export const Route = createFileRoute("/")({
  component: Index,
  head: () => ({
    meta: [
      { title: "Dashboard · AgriSense AI" },
      { name: "description", content: "RAG-powered agriculture assistant — crop health, disease diagnosis, and AI insights." },
    ],
  }),
});

function Index() {
  return (
    <AppLayout title="Field Overview" subtitle="Monitor crop health, alerts, and resource usage">
      <Dashboard />
    </AppLayout>
  );
}
