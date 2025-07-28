import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { CategoriasType } from "@/types/assets";
import {
  Building2,
  ChartNoAxesCombined,
  Coins,
  Earth,
  Layers,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { categoriaData } from "@/data/categoria-data";
import { PathLink } from "@/components/ui/path-link";

export function Ranking() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [categoria, setcategoria] = useState<CategoriasType>(
    (searchParams.get("categoria") as CategoriasType) || "acoes",
  );

  const addQuery = (value: string) => {
    setSearchParams({ categoria: value });
  };

  useEffect(() => {
    const categoriaAtual = searchParams.get("categoria");
    if (categoriaAtual === null) return;
    setcategoria(categoriaAtual as CategoriasType);
  }, [searchParams]);

  return (
    <div className="flex h-auto w-full max-w-[1180px] flex-col gap-8 p-8">
      <PathLink />
      <h1 className="text-foreground/80 flex items-center gap-2 text-3xl font-semibold">
        <ChartNoAxesCombined className="h-8 w-8" /> Ranking de{" "}
        {categoriaData[categoria].shortTitle}
      </h1>
      <Tabs
        defaultValue={searchParams.get("categoria") || "acoes"}
        className="w-full"
        onValueChange={addQuery}
      >
        <TabsList className="gap-3 bg-transparent">
          <TabsTrigger
            value="acoes"
            className="data-[state=active]:bg-primary data-[state=active]:dark:bg-primary data-[state=active]:text-primary-foreground border-border bg-card hover:bg-muted data-[state=active]:border-primary cursor-pointer border p-4 shadow-sm transition-all duration-150"
          >
            <Coins /> Ações
          </TabsTrigger>
          <TabsTrigger
            value="fiis"
            className="data-[state=active]:bg-primary data-[state=active]:dark:bg-primary data-[state=active]:text-primary-foreground border-border bg-card hover:bg-muted data-[state=active]:border-primary cursor-pointer border p-4 shadow-sm transition-all duration-150"
          >
            <Building2 />
            FIIs
          </TabsTrigger>
          <TabsTrigger
            value="etfs"
            className="data-[state=active]:bg-primary data-[state=active]:dark:bg-primary data-[state=active]:text-primary-foreground border-border bg-card hover:bg-muted data-[state=active]:border-primary cursor-pointer border p-4 shadow-sm transition-all duration-150"
          >
            <Layers />
            ETFs
          </TabsTrigger>
          <TabsTrigger
            value="bdrs"
            className="data-[state=active]:bg-primary data-[state=active]:dark:bg-primary data-[state=active]:text-primary-foreground border-border bg-card hover:bg-muted data-[state=active]:border-primary cursor-pointer border p-4 shadow-sm transition-all duration-150"
          >
            <Earth />
            BDRs
          </TabsTrigger>
        </TabsList>
        <TabsContent value="account">
          Make changes to your account here.
        </TabsContent>
        <TabsContent value="password">Change your password here.</TabsContent>
      </Tabs>
    </div>
  );
}

function RankingTabs() {
  return;
}
