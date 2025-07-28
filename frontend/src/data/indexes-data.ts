export const indexesData = {
  price: {
    title: "Preço",
    description: `Preço atual da ação, ETF ou outro ativo no mercado. Representa o valor pelo qual o ativo está sendo negociado no momento da consulta.`,
  },
  priceChangePercent: {
    title: "Variação",
    description: `Representa a variação percentual do preço do ativo em um determinado período (normalmente 1 dia). Indica se o ativo valorizou ou desvalorizou em relação ao fechamento anterior.`,
  },
  roe: {
    title: "ROE (Return on Equity)",
    description: `ROE (Return on Equity) mede a rentabilidade de uma empresa em relação ao patrimônio líquido dos acionistas. Indica quanto lucro líquido é gerado para cada unidade de capital próprio investido, mostrando a eficiência da gestão. 

A fórmula é: Lucro Líquido ÷ Patrimônio Líquido, com resultado expresso em percentual.`,
  },
  dy: {
    title: "Dividend Yield",
    description: `Dividend Yield indica o retorno em dividendos que o investidor recebe em relação ao preço atual da ação. É uma medida da rentabilidade dos dividendos pagos pela empresa. 

A fórmula é: (Dividendos Anuais ÷ Preço da Ação) x 100%.`,
  },
  yearHigh: {
    title: "Max 52s",
    description: `Preço máximo atingido pelo ativo nos últimos 52 semanas (1 ano). É um indicador importante para avaliar o potencial de valorização e resistência do preço.`,
  },
  marketCap: {
    title: "Valor de mercado",
    description: `Valor total de mercado da empresa calculado pela multiplicação do preço da ação pelo número total de ações em circulação. 

A fórmula é: Preço da Ação x Número de Ações.`,
  },
  peRatio: {
    title: "Preço / Lucro ",
    description: `O Índice P/L (Preço/Lucro) mede quanto os investidores estão dispostos a pagar por cada unidade de lucro da empresa. 

A fórmula é: Preço da Ação ÷ Lucro por Ação (LPA).`,
  },
  netMargin: {
    title: "Margem Líquida (Ações/BDRs)",
    description: `Margem Líquida indica a porcentagem do lucro líquido obtido sobre a receita total da empresa, mostrando a eficiência operacional. 

A fórmula é: (Lucro Líquido ÷ Receita Total) x 100%.`,
  },
  pFfo: {
    title: "Preço / Fundos das Operações",
    description: `P/FFO (Price/Funds From Operations) é um indicador usado em fundos imobiliários para relacionar o preço da cota com a geração real de caixa do fundo. Ele mede quanto o investidor está pagando em relação ao desempenho operacional, sendo útil para avaliar a eficiência do fundo na distribuição de resultados recorrentes. 

A fórmula é: Preço da Cota ÷ FFO por Cota.`,
  },
  pVp: {
    title: "Preço / Valor Patrimonial",
    description: `P/VP (Preço/Valor Patrimonial) compara o preço da cota com o valor contábil do patrimônio do fundo. Esse indicador mostra se a cota está sendo negociada acima (ágio) ou abaixo (deságio) do valor real dos ativos, ajudando a identificar distorções entre preço de mercado e valor patrimonial. 

A fórmula é: Preço da Cota ÷ Valor Patrimonial por Cota.`,
  },
};
