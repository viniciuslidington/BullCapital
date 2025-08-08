import { ThemeProvider } from "./contexts/theme-provider";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { Home } from "./pages/home";
import { Header } from "./components/ui/header";
import { Footer } from "./components/ui/footer";
import { Sidebar } from "./components/features/ai-assistant/sidebar";
import { Asset } from "./pages/asset";
import { Ranking } from "./pages/ranking";
import { ScrollToTop } from "./components/ui/scrolltotop";
import { queryClientConfig } from "./hooks/queries/queries-config";
import { Toaster } from "./components/ui/sonner";

const queryClient = new QueryClient(queryClientConfig);

function App() {
  return (
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <ReactQueryDevtools initialIsOpen={false} />
        <ScrollToTop />
        <Toaster position="top-center" richColors />
        <ThemeProvider defaultTheme="light" storageKey="vite-ui-theme">
          <div className="dark:bg-background/50 fixed top-20 z-[-2] h-screen w-screen bg-white bg-[radial-gradient(100%_60%_at_50%_0%,rgba(200,96,242,0.3)_0,rgba(142,81,255,0)_50%,rgba(240,240,240,1)_100%)] dark:bg-[radial-gradient(100%_70%_at_50%_0%,rgba(142,81,255,0.3)_0,rgba(142,81,255,0)_50%,rgba(142,81,255,0)_100%)]"></div>

          <div className="min-h-screen w-full flex-col">
            <Header />
            <div className="flex overflow-hidden">
              <div className="flex w-full flex-col items-center pt-20 pr-20">
                <Routes>
                  <Route path="/" element={<Home />}></Route>
                  <Route path="/:ticker" element={<Asset />}></Route>
                  <Route path="/ranking" element={<Ranking />}></Route>
                </Routes>

                <Footer />
              </div>
              <Sidebar />
            </div>
          </div>
        </ThemeProvider>
      </QueryClientProvider>
    </BrowserRouter>
  );
}

export default App;
