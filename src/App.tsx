import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthInitializer } from "@/components/providers/AuthInitializer";
import LandingPage from "./pages/LandingPage";
import NameInputPage from "./pages/NameInputPage";
import TopicsPage from "./pages/TopicsPage";
import SwipePage from "./pages/SwipePage";
import TopicSwipePage from "./pages/TopicSwipePage";
import MatchPage from "./pages/MatchPage";
import ChatPage from "./pages/ChatPage";
import RevealPage from "./pages/RevealPage";
import NotFound from "./pages/NotFound";

// Create QueryClient outside component to prevent recreation on re-renders
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

const App = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <AuthInitializer>
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/topics" element={<TopicsPage />} />
              <Route path="/swipe" element={<SwipePage />} />
              <Route path="/topic-swipe" element={<TopicSwipePage />} />
              <Route path="/match" element={<MatchPage />} />
              <Route path="/chat" element={<ChatPage />} />
              <Route path="/reveal" element={<RevealPage />} />
              {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </AuthInitializer>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
};

export default App;
