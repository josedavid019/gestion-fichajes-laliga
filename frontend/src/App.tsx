import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthProvider } from "@/contexts/AuthContext";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { AdminRoute } from "@/components/AdminRoute";
import { AppLayout } from "@/components/AppLayout";
import Detection from "./pages/Detection";
import AIQuery from "./pages/AIQuery";
import Prediction from "./pages/Prediction";
import Reports from "./pages/Reports";
import Scouting from "./pages/Scouting";
import UserManagement from "./pages/UserManagement";
import PlayerManagement from "./pages/PlayerManagement";
import AuditLogs from "./pages/AuditLogs";
import Login from "./pages/Login";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            {/* Auth routes without layout */}
            <Route path="/login" element={<Login />} />

            {/* Protected routes with layout */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <Reports />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/detection"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <Detection />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/ai-query"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <AIQuery />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/prediction"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <Prediction />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/scouting"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <Scouting />
                  </AppLayout>
                </ProtectedRoute>
              }
            />

            {/* Admin routes - Only accessible by admin */}
            <Route
              path="/admin/users"
              element={
                <AdminRoute>
                  <AppLayout>
                    <UserManagement />
                  </AppLayout>
                </AdminRoute>
              }
            />
            <Route
              path="/admin/players"
              element={
                <AdminRoute>
                  <AppLayout>
                    <PlayerManagement />
                  </AppLayout>
                </AdminRoute>
              }
            />
            <Route
              path="/admin/audit-logs"
              element={
                <AdminRoute>
                  <AppLayout>
                    <AuditLogs />
                  </AppLayout>
                </AdminRoute>
              }
            />

            {/* 404 */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
