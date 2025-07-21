import { ThemeProvider } from "./contexts/theme-provider";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Home } from "./pages/home";
import { Header } from "./components/ui/header";
import { Footer } from "./components/ui/footer";
import { Sidebar } from "./components/features/ai-assistant/sidebar";

function App() {
  return (
    <>
      <ThemeProvider defaultTheme="light" storageKey="vite-ui-theme">
        <div className="min-h-screen w-full flex-col">
          <Header />
          <span className="flex overflow-hidden">
            <div className="flex w-full flex-col items-center pt-20 pr-20">
              <BrowserRouter>
                <Routes>
                  <Route path="/" element={<Home />}></Route>
                </Routes>
              </BrowserRouter>
              <Footer />
            </div>
            <Sidebar />
          </span>
        </div>
      </ThemeProvider>
    </>
  );
}

export default App;
