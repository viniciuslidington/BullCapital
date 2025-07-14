import re
from typing import Optional

def validate_cpf(cpf: str) -> bool:
    """
    Valida um número de CPF brasileiro.
    
    Verifica se o CPF possui 11 dígitos e se os dígitos verificadores
    estão corretos de acordo com o algoritmo oficial.
    
    Args:
        cpf (str): CPF a ser validado (com ou sem formatação)
        
    Returns:
        bool: True se o CPF for válido, False caso contrário
        
    Examples:
        >>> validate_cpf("123.456.789-09")
        True
        >>> validate_cpf("12345678909")
        True
        >>> validate_cpf("111.111.111-11")
        False
    """
    # Remove formatação (pontos, traços e espaços)
    cpf = clean_cpf(cpf)
    
    # Verifica se possui exatamente 11 dígitos
    if not cpf or len(cpf) != 11 or not cpf.isdigit():
        return False
    
    # Verifica se todos os dígitos são iguais (CPF inválido)
    if cpf == cpf[0] * 11:
        return False
    
    # Calcula o primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    primeiro_digito = ((soma * 10) % 11) % 10
    
    # Calcula o segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    segundo_digito = ((soma * 10) % 11) % 10
    
    # Verifica se os dígitos verificadores estão corretos
    return cpf[9] == str(primeiro_digito) and cpf[10] == str(segundo_digito)


def clean_cpf(cpf: str) -> str:
    """
    Remove a formatação de um CPF, deixando apenas os números.
    
    Args:
        cpf (str): CPF com ou sem formatação
        
    Returns:
        str: CPF apenas com números
        
    Examples:
        >>> clean_cpf("123.456.789-09")
        "12345678909"
        >>> clean_cpf("123 456 789 09")
        "12345678909"
    """
    if not cpf:
        return ""
    return re.sub(r'[^0-9]', '', cpf)


def format_cpf(cpf: str) -> Optional[str]:
    """
    Formata um CPF no padrão brasileiro (XXX.XXX.XXX-XX).
    
    Args:
        cpf (str): CPF sem formatação (apenas números)
        
    Returns:
        str | None: CPF formatado ou None se inválido
        
    Examples:
        >>> format_cpf("12345678909")
        "123.456.789-09"
        >>> format_cpf("1234567890")
        None
    """
    cpf_clean = clean_cpf(cpf)
    
    if len(cpf_clean) != 11:
        return None
        
    return f"{cpf_clean[:3]}.{cpf_clean[3:6]}.{cpf_clean[6:9]}-{cpf_clean[9:]}"
