import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider } from "@/components/theme-provider";
import { AppProvider } from "@/contexts/AppContext";
import { AuthProvider } from "@/contexts/AuthContext";
import { LanguageProvider } from "@/contexts/LanguageContext";
import { CurrencyProvider } from "@/contexts/CurrencyContext";
import ProtectedRoute from "@/components/ProtectedRoute";
import Index from "./pages/Index";
import PropertyDetail from "./pages/PropertyDetail";
import PostAd from "./pages/PostAd";
import EditProperty from "./pages/EditProperty";
import Dashboard from "./pages/Dashboard";
import NotFound from "./pages/NotFound";
import Auth from "./pages/Auth";
import ForgotPassword from "./pages/ForgotPassword";
import PrivacyPolicy from "./pages/PrivacyPolicy";
import TermsOfService from "./pages/TermsOfService";
import CookiePolicy from "./pages/CookiePolicy";

const queryClient = new QueryClient();

const App = () => (
  <ThemeProvider defaultTheme="light">
    <QueryClientProvider client={queryClient}>
      <LanguageProvider>
        <CurrencyProvider>
          <AuthProvider>
            <AppProvider>
              <TooltipProvider>
                <Toaster />
                <Sonner />
              <BrowserRouter>
                <Routes>
                  <Route path="/" element={<Index />} />
                  <Route path="/listings" element={<Navigate to="/" replace />} />
                  <Route path="/property/:id" element={<PropertyDetail />} />
                  <Route 
                    path="/post-ad" 
                    element={
                      <ProtectedRoute>
                        <PostAd />
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/edit-property/:id" 
                    element={
                      <ProtectedRoute>
                        <EditProperty />
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/dashboard" 
                    element={
                      <ProtectedRoute>
                        <Dashboard />
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/auth" 
                    element={
                      <ProtectedRoute requireAuth={false}>
                        <Auth />
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/forgot-password" 
                    element={
                      <ProtectedRoute requireAuth={false}>
                        <ForgotPassword />
                      </ProtectedRoute>
                    } 
                  />
                  <Route path="/privacy-policy" element={<PrivacyPolicy />} />
                  <Route path="/terms-of-service" element={<TermsOfService />} />
                  <Route path="/cookie-policy" element={<CookiePolicy />} />
                  <Route path="*" element={<NotFound />} />
                </Routes>
              </BrowserRouter>
            </TooltipProvider>
          </AppProvider>
        </AuthProvider>
        </CurrencyProvider>
      </LanguageProvider>
    </QueryClientProvider>
  </ThemeProvider>
);

export default App;