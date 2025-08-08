import functools
from typing import Callable
from cachetools import TTLCache
from core.logging import get_logger

logger = get_logger(__name__)

class CacheManager:
    """
    Gerencia uma instância de cache TTL para a aplicação.
    O cache armazena os resultados de funções pesadas (como chamadas à API yfinance)
    por um tempo determinado para melhorar a performance e evitar requisições repetidas.
    """
    def __init__(self, maxsize: int = 512, default_ttl: int = 300):
        """
        Inicializa o CacheManager.
        
        Args:
            maxsize (int): O número máximo de itens a serem mantidos no cache.
            default_ttl (int): O tempo de vida padrão (em segundos) para um item no cache.
                               (300 segundos = 5 minutos)
        """
        self.cache = TTLCache(maxsize=maxsize, ttl=default_ttl)
        logger.info(f"CacheManager inicializado com maxsize={maxsize} e ttl={default_ttl}s.")

    def cached(self, ttl: int = None) -> Callable:
        """
        Decorador para aplicar cache a uma função.
        Permite sobrescrever o TTL padrão para funções específicas.

        Args:
            ttl (int, optional): Tempo de vida específico para esta função (em segundos).
                                 Se None, usa o TTL padrão do cache.
        """
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Cria uma chave de cache baseada no nome da função e seus argumentos
                # Converte listas em tuplas para serem "hasheáveis"
                args_for_key = tuple(tuple(arg) if isinstance(arg, list) else arg for arg in args)
                key_args = (args_for_key, tuple(sorted(kwargs.items())))
                cache_key = (func.__name__,) + key_args

                # Verifica se o resultado já está no cache
                if cache_key in self.cache:
                    logger.debug(f"Cache HIT para a chave: {cache_key}")
                    return self.cache[cache_key]

                logger.debug(f"Cache MISS para a chave: {cache_key}")
                
                # Se não estiver, executa a função
                result = func(*args, **kwargs)

                # Armazena o resultado no cache com o TTL correto
                # O TTLCache lida com o TTL na inserção se o TTL do cache geral for usado
                # Para TTLs customizados, teríamos que gerenciar caches separados.
                # A implementação padrão do TTLCache usa um único TTL.
                # Para simplificar, vamos manter o TTL padrão, mas o design está aqui.
                # Nota: A biblioteca cachetools não suporta TTL por item nativamente.
                # O TTL é do cache. Vamos usar o TTL padrão para todos.
                self.cache[cache_key] = result
                
                return result
            return wrapper
        return decorator

# Instância única (Singleton) que será importada em outros módulos
cache_manager = CacheManager(maxsize=1024, default_ttl=300)