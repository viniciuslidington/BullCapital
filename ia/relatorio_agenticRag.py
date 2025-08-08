
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import openai
import time
from typing import List, Dict, Optional
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RelatorioAnualRAG:
    def __init__(self, openai_api_key: str):
        """
        Inicializa o agente RAG para análise de relatórios anuais da WEG
        """
        self.openai_api_key = openai_api_key
        self.session = requests.Session()
        # Headers otimizados para Mac e Chrome
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        })
        
        # Configuracao OpenAI
        openai.api_key = openai_api_key
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model_name="gpt-4o",
            temperature=0.3
        )
        
        self.vector_store = None
        self.qa_chain = None
        
    def buscar_documentos_weg(self) -> List[Dict[str, str]]:
        """
        Busca documentos da WEG na página inicial com abordagem mais flexível
        """
        try:
            logger.info("Acessando página inicial da WEG...")
            
            url_inicial = "https://ri.weg.net/"
            response = self.session.get(url_inicial, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            documentos_encontrados = []
            
            #  buscar todos os links que contenham palavras-chave
            logger.info("Procurando links com palavras-chave")
            
            # Palavras-chave comuns em documentos financeiros
            keywords = [
                'release', 'resultado', 'demonstração', 'financeira', 'apresentação',
                'itr', 'dfp', 'balanço', 'lucro', 'receita'
            ]
            
            # Procurar todos os links na página
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link['href']
                text = link.get_text().strip().lower()
                
                # Verificar se é PDF e contém palavras-chave
                if (href.lower().endswith('.pdf') or 'pdf' in href.lower()) and \
                   (any(keyword in text for keyword in keywords) or 
                    any(keyword in href.lower() for keyword in keywords)):
                    
                    full_url = urljoin(url_inicial, href)
                    nome_original = link.get_text().strip() or "Documento Financeiro"
                    
                    documentos_encontrados.append({
                        'url': full_url,
                        'nome': nome_original
                    })
                    logger.info(f"Documento encontrado: {nome_original}")
            
            # Abordagem 2: Se não encontrou nada, procurar por qualquer PDF
            if not documentos_encontrados:
                logger.info("Nenhum documento específico encontrado, buscando todos os PDFs...")
                for link in links:
                    href = link['href']
                    if href.lower().endswith('.pdf'):
                        full_url = urljoin(url_inicial, href)
                        nome_original = link.get_text().strip() or "Documento PDF"
                        
                        documentos_encontrados.append({
                            'url': full_url,
                            'nome': nome_original
                        })
                        logger.info(f"PDF genérico encontrado: {nome_original}")
            
            # Remover duplicatas
            urls_unicos = {}
            for doc in documentos_encontrados:
                urls_unicos[doc['url']] = doc
            
            documentos_unicos = list(urls_unicos.values())
            logger.info(f"Total de documentos únicos encontrados: {len(documentos_unicos)}")
            
            # Limitar a 5 documentos para evitar sobrecarga
            return documentos_unicos[:5]
            
        except Exception as e:
            logger.error(f"Erro ao buscar documentos: {str(e)}")
            return []
    
    def baixar_relatorio(self, url: str, pasta_destino: str = "relatorios") -> Optional[str]:
        """Baixando um relatório PDF"""
        try:
            os.makedirs(pasta_destino, exist_ok=True)
            
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            
            if not filename or '.' not in filename:
                filename = f"documento_{int(time.time())}.pdf"
            
            filepath = os.path.join(pasta_destino, filename)
            
            logger.info(f"Baixando: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # verifico se eh pdf
            content_type = response.headers.get('content-type', '')
            if 'application/pdf' not in content_type and not url.lower().endswith('.pdf'):
                logger.warning(f"Esse arquivo não é um PDFF: {content_type}")
                return None
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Documento salvo em: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Erro ao baixar {url}: {str(e)}")
            return None

    def extrair_texto_pdf(self, filepath: str) -> str:
        """Extrai texto de um arquivo PDF"""
        try:
            logger.info(f"Extraindo texto de: {filepath}")
            texto_completo = ""
            
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    texto = page.extract_text()
                    if texto:
                        texto_completo += texto + "\n\n"
            
            logger.info(f"Extraído: {len(texto_completo)} caracteres")
            return texto_completo
            
        except Exception as e:
            logger.error(f"Erro ao extrair texto: {str(e)}")
            return ""

    def criar_vector_store(self, textos: List[str]) -> None:
        """Cria o vector store para o RAG"""
        try:
            logger.info("Criando vector store...")
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
            )
            
            all_chunks = []
            for texto in textos:
                chunks = text_splitter.split_text(texto)
                all_chunks.extend(chunks)
            
            logger.info(f"Dividido em {len(all_chunks)} chunks")
            
            # Criar vector store
            self.vector_store = FAISS.from_texts(all_chunks, self.embeddings)
            
            prompt_template = """
            Você é um assistente de investimentos especializado em análise fundamentalista, e toda a sua atuação deve se basear exclusivamente no conteúdo do guia abaixo. Todas as respostas devem ser dadas apenas em português brasileiro, com linguagem clara, natural, direta, sem jargão excessivo e sempre profissional, focando na explicação acessível e rigorosa dos conceitos.

            Regras de atuação:
            - Utilize apenas o conteúdo do guia de referência. Não crie, suponha ou extrapole informações não presentes no texto.
            - Sempre responda no formato de educador: explique conceitos, indicadores, fórmulas, significados, usos práticos, limitações e boas práticas conforme apresentados no guia.
            - Quando perguntado sobre qualquer indicador (ex: EBITDA, ROE, ROIC, P/L, Dividend Yield, Margem Líquida, Ativo Total, Dívida Líquida, EV/EBITDA, etc.), explique com base nas definições, cálculos, relevância, limitações e contexto de uso exatamente como apresentado no material.
            - Sempre que possível, destaque que decisões de análise e investimento exigem avaliação conjunta de múltiplos indicadores e aspectos qualitativos, como gestão, setor, contexto econômico e vantagens competitivas, de acordo com o guia.
            - Ao explicar indicadores, use as fórmulas e exemplos práticos contidos no texto. Nunca utilize exemplos inventados ou informações externas.
            - Caso seja questionado sobre a diferença entre indicadores (ex: ROE x ROIC), traga os pontos de distinção conforme apresentados no documento, inclusive quando abordar análise DuPont ou outras decomposições mencionadas.
            - Sempre destaque as limitações dos indicadores e os riscos de análise isolada, reforçando que cada métrica deve ser considerada no contexto da empresa e do setor, conforme os princípios do guia.
            - Se for perguntado sobre recomendação de compra, venda ou decisão de investimento, nunca responda diretamente e oriente, de acordo com o material, que a função do assistente é esclarecer e ensinar os fundamentos, não recomendar operações no mercado financeiro.
            - Utilize exemplos e referências aos grandes investidores (Benjamin Graham, Warren Buffett, Peter Lynch, etc.) apenas se estiverem descritos no guia, nunca extrapolando além do que está no texto.
            - Caso a resposta não esteja clara ou detalhada no guia de referência, diga explicitamente que não sabe responder com base nesse material.
            - Nunca utilize dados de mercado atual, não busque informações externas, não faça previsões e não utilize análises técnicas. Limite-se sempre ao escopo do guia abaixo.
            - Adote sempre um tom educacional, gentil, sem ser professoral, e evite respostas excessivamente longas ou repetitivas, a não ser que o usuário peça detalhamento.
            - Se a pergunta envolver a escolha de ações, estratégias de investimento, análise de empresas, ou questões sobre valuation, destaque a importância de análise integrada (quantitativa e qualitativa) conforme orientado pelo guia, e oriente o usuário a considerar múltiplos indicadores e contexto, nunca um único fator isolado.
            - Se questionado sobre política de dividendos, crescimento, endividamento, múltiplos de mercado ou temas similares, explique com base no conteúdo do guia, incluindo a relevância de cada indicador e o que está por trás das melhores práticas segundo o material.
            - Se a pergunta for genérica (ex: 'como analisar uma empresa?'), responda com as orientações amplas e os passos sugeridos no guia, reforçando sempre a análise multifatorial e integrada.
            - Se o usuário tentar levar a resposta para temas não abordados no guia, seja transparente e informe que a resposta está limitada ao escopo do documento.
            - Mantenha sempre o compromisso de não sair do conteúdo do guia, mesmo que solicitado.
            - Se não souber, diga que não encontrou informações suficientes.
            - Sempre que possível, mencione valores numéricos e dados concretos.

            Guia de referência:
            {context}

            Pergunta: {question}
            Resposta:"""
            
            PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(search_kwargs={"k": 5}),
                chain_type_kwargs={"prompt": PROMPT},
                return_source_documents=True
            )
            
            logger.info("Vector store criado com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro ao criar vector store: {str(e)}")
            raise

    def processar_documentos_weg(self) -> bool:
        """Processa documentos da WEG com abordagem mais robusta"""
        try:
            logger.info("Iniciando busca por documentos da WEG...")
            
            # 1. Buscar documentos automaticamente
            documentos = self.buscar_documentos_weg()
            
            if not documentos:
                logger.warning("Nenhum documento encontrado automaticamente")
                logger.info("Tentando URL conhecido")
                documentos = [{
                    'url': 'https://api.mziq.com/mzfilemanager/v2/d/50c1bd3e-8ac6-42d9-884f-b9d69f690602/8a3640f7-490e-5cfd-4cd5-bd9de3f4ac5a?origin=1',
                    'nome': 'Release de Resultados WEG'
                }]
            
            logger.info(f"Documentos encontrados: {len(documentos)}")
            
            # 2. Baixar documentos
            textos = []
            for i, doc in enumerate(documentos):
                logger.info(f"[{i+1}/{len(documentos)}] Processando: {doc['nome']}")
                filepath = self.baixar_relatorio(doc['url'])
                
                if filepath:
                    texto = self.extrair_texto_pdf(filepath)
                    if texto and len(texto) > 100:  
                        textos.append(texto)
                        logger.info(f"✓ Texto extraído de {doc['nome']} ({len(texto)} caracteres)")
                    else:
                        logger.warning(f"✗ Texto muito curto ou vazio em {doc['nome']}")
                else:
                    logger.warning(f"✗ Falha ao baixar {doc['nome']}")
                
                time.sleep(1)  
            
            if not textos:
                logger.error("Nenhum texto foi extraído dos documentos")
                return False
            
            logger.info(f"Processando {len(textos)} documentos com conteúdo")
            
            # 3. Criar vector store
            self.criar_vector_store(textos)
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar documentos: {str(e)}")
            return False

    def perguntar(self, pergunta: str) -> Dict[str, any]:
        """Faz uma pergunta sobre os documentos"""
        if not self.qa_chain:
            return {"erro": "Sistema não inicializado. Execute processar_documentos_weg() primeiro."}
        
        try:
            logger.info(f"Pergunta: {pergunta}")
            resultado = self.qa_chain({"query": pergunta})
            
            return {
                "resposta": resultado["result"],
                "fontes": [doc.page_content[:200] + "..." for doc in resultado["source_documents"]]
            }
            
        except Exception as e:
            logger.error(f"Erro ao responder: {str(e)}")
            return {"erro": f"Erro ao processar pergunta: {str(e)}"}

# Exemplo de uso
def main():
    OPENAI_API_KEY= "insira uma chave aq pfvr"

    
    rag = RelatorioAnualRAG(OPENAI_API_KEY)
    
    print("🔍 Processando documentos da WEG (abordagem robusta)...")
    if rag.processar_documentos_weg():
        print("✅ Processamento concluído com sucesso!")
        print("\n💬 Você pode fazer perguntas como:")
        print("   • Quais são os principais resultados financeiros?")
        print("   • Qual foi o lucro líquido nos últimos períodos?")
        print("   • Como está o desempenho das exportações?")
        print("   • Quais são os principais indicadores de sustentabilidade?")
        print("   • Qual foi o crescimento da receita?")
        print("\n(Digite 'sair' para encerrar)\n")
        
        while True:
            try:
                pergunta = input("Pergunta: ").strip()
                if pergunta.lower() in ['sair', 'exit', 'quit', '']:
                    break
                    
                if pergunta:
                    resposta = rag.perguntar(pergunta)
                    if "erro" in resposta:
                        print(f"❌ {resposta['erro']}")
                    else:
                        print(f"✅ {resposta['resposta']}")
                        print(f"📚 Fontes: {len(resposta['fontes'])} trechos relevantes encontrados")
                    print("-" * 80)
            except KeyboardInterrupt:
                print("\n👋 Até logo!")
                break
            except Exception as e:
                print(f"❌ Erro: {str(e)}")
    else:
        print("❌ Falha no processamento - nenhum documento encontrado")

if __name__ == "__main__":
    main()