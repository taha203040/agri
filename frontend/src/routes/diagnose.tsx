import { createFileRoute } from "@tanstack/react-router";
import { AppLayout } from "@/components/AppLayout";
import { DiseaseDiagnosis } from "@/components/DiseaseDiagnosis";

export const Route = createFileRoute("/diagnose")({
  component: DiagnosePage,
  head: () => ({
    meta: [
      { title: "Plant Disease Diagnosis · AgriSense AI" },
      { name: "description", content: "Upload a leaf photo to instantly diagnose plant disease and get treatment recommendations." },
    ],
  }),
});

function DiagnosePage() {
  return (
    <AppLayout
      title="Disease Diagnosis"
      subtitle="Upload a leaf photo for instant AI analysis"
    >
      <DiseaseDiagnosis />
    </AppLayout>
  );
}
