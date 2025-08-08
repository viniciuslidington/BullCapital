import {
  Banknote,
  Building,
  Factory,
  Flame,
  Laptop,
  PackageSearch,
  Phone,
  PlugZap,
  ShieldCheck,
  ShoppingCart,
  Stethoscope,
} from "lucide-react";

export const SECTOR_OPTIONS = [
  {
    label: "Materiais Básicos",
    value: "Basic Materials",
    icon: <Factory className="mr-2 h-4 w-4" />,
  },
  {
    label: "Serviços de Comunicação",
    value: "Communication Services",
    icon: <Phone className="mr-2 h-4 w-4" />,
  },
  {
    label: "Consumo Cíclico",
    value: "Consumer Cyclical",
    icon: <ShoppingCart className="mr-2 h-4 w-4" />,
  },
  {
    label: "Consumo Não Cíclico",
    value: "Consumer Defensive",
    icon: <ShieldCheck className="mr-2 h-4 w-4" />,
  },
  {
    label: "Energia",
    value: "Energy",
    icon: <Flame className="mr-2 h-4 w-4" />,
  },
  {
    label: "Serviços Financeiros",
    value: "Financial Services",
    icon: <Banknote className="mr-2 h-4 w-4" />,
  },
  {
    label: "Saúde",
    value: "Healthcare",
    icon: <Stethoscope className="mr-2 h-4 w-4" />,
  },
  {
    label: "Industriais",
    value: "Industrials",
    icon: <PackageSearch className="mr-2 h-4 w-4" />,
  },
  {
    label: "Imobiliário",
    value: "Real Estate",
    icon: <Building className="mr-2 h-4 w-4" />,
  },
  {
    label: "Tecnologia",
    value: "Technology",
    icon: <Laptop className="mr-2 h-4 w-4" />,
  },
  {
    label: "Utilidade Pública",
    value: "Utilities",
    icon: <PlugZap className="mr-2 h-4 w-4" />,
  },
];

export const SECTOR_TRANSLATE = {
  "Basic Materials": "Materiais Básicos",
  "Communication Services": "Serviços de Comunicação",
  "Consumer Cyclical": "Consumo Cíclico",
  "Consumer Defensive": "Consumo Não Cíclico",
  Energy: "Energia",
  "Financial Services": "Serviços Financeiros",
  Healthcare: "Saúde",
  Industrials: "Industriais",
  "Real Estate": "Imobiliário",
  Technology: "Tecnologia",
  Utilities: "Utilidade Pública",
};
