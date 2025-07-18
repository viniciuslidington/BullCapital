import { ThemeProvider } from "./contexts/theme-provider";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Home } from "./pages/home";
import { Header } from "./components/ui/header";
import { Footer } from "./components/ui/footer";

function App() {
  return (
    <>
      <ThemeProvider defaultTheme="light" storageKey="vite-ui-theme">
        <div className="h-screen max-h-screen w-full flex-col">
          <Header />

          <BrowserRouter>
            <Routes>
              <Route path="/" element={<Home />}></Route>
            </Routes>
          </BrowserRouter>
          <Footer />
        </div>
      </ThemeProvider>
    </>
  );
}

export default App;
