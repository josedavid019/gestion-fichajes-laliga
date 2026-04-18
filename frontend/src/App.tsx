import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AppLayout } from "@/components/AppLayout";
import Detection from "./pages/Detection";
import AIQuery from "./pages/AIQuery";
import Prediction from "./pages/Prediction";
import Reports from "./pages/Reports";
import Scouting from "./pages/Scouting";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <AppLayout>
          <Routes>
            <Route path="/" element={<Reports />} />
            <Route path="/detection" element={<Detection />} />
            <Route path="/ai-query" element={<AIQuery />} />
            <Route path="/prediction" element={<Prediction />} />
            <Route path="/scouting" element={<Scouting />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </AppLayout>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
