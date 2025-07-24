import { ThemeProvider } from "./contexts/theme-provider";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Home } from "./pages/home";
import { Header } from "./components/ui/header";
import { Footer } from "./components/ui/footer";
import { Sidebar } from "./components/features/ai-assistant/sidebar";
import { Asset } from "./pages/asset";
import { Highlight } from "./pages/highlight";

function App() {
  return (
    <>
      <BrowserRouter>
        <ThemeProvider defaultTheme="light" storageKey="vite-ui-theme">
          <div className="min-h-screen w-full flex-col">
            <Header />
            <div className="flex overflow-hidden">
              <div className="flex w-full flex-col items-center pt-20 pr-20">
                <Routes>
                  <Route path="/" element={<Home />}></Route>
                  <Route path="/:ticker" element={<Asset />}></Route>
                  <Route path="/destaque" element={<Highlight />}></Route>
                </Routes>

                <Footer />
              </div>
              <Sidebar />
            </div>
          </div>
        </ThemeProvider>
      </BrowserRouter>
    </>
  );
}

export default App;
