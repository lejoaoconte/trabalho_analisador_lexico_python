import sys

# Dicionário de palavras reservadas conforme especificado na Tabela 1 do trabalho.
# Mapeia o lexema (string encontrada) para o token correspondente.
PALAVRAS_RESERVADAS = {
    "int": "INTDEF",       
    "float": "FLOATDEF",  
    "char": "DEFCHAR",     # Ajustado conforme solicitado
    "bool": "DEFBOOL",     # Ajustado conforme solicitado
    "return": "RETURN",  
    "If": "IF",   # Especificado no PDF como 'If'
    "if": "IF"    # Adicionado para robustez
}

# Dicionário para tokens de caractere único (símbolos especiais e operadores simples).
TOKENS_SIMPLES = {
    "(": "LParenteses",    
    ")": "RParenteses",    
    "{": "LChave",         
    "}": "RChave",         
    "[": "Lcolchete",      
    "]": "RColchete",      
    "+": "SUM",            
    "-": "SUB",            
    "*": "MULT",           
    "/": "DIV",            
    "%": "RESTO",          
    ",": "Virgula",        
    ";": "PVirgula"        
}

class AnalisadorLexico:
    """
    Implementação de um Analisador Léxico baseado em Autômato Finito Determinístico (AFD).
    O analisador lê o código fonte caractere por caractere e agrupa lexemas em tokens.
    """
    def __init__(self, codigo_fonte):
        self.codigo = codigo_fonte
        self.tamanho = len(codigo_fonte)
        self.cursor = 0   # Aponta para a posição atual de leitura no código
        self.tokens_encontrados = []
        
        # Variável de estado para contexto semântico simples
        # Armazena qual foi o último tipo declarado (int, bool, float, char)
        # para decidir se 0 ou 1 devem ser NUM_INT ou BOOL_TYPE.
        self.ultimo_tipo_declarado = None 

    def proximo_char(self):
        """Retorna o caractere na posição atual sem avançar o cursor (Lookahead)."""
        if self.cursor < self.tamanho:
            return self.codigo[self.cursor]
        return None

    def consumir_char(self):
        """Retorna o caractere atual e avança o cursor (Consumo da fita de entrada)."""
        char = self.proximo_char()
        if char is not None:
            self.cursor += 1
        return char

    def voltar_cursor(self):
        """
        Retrocede o cursor em uma posição.
        Fundamental para implementar transições de 'outro' (other).
        """
        if self.cursor > 0:
            self.cursor -= 1

    def analisar(self):
        """Loop principal que consome todo o arquivo gerando a lista de tokens."""
        while self.cursor < self.tamanho:
            token = self.get_proximo_token()
            if token:
                self.tokens_encontrados.append(token)
        return self.tokens_encontrados

    def get_proximo_token(self):
        """
        Método central que implementa a lógica do AFD.
        A variável 'estado_atual' rastreia em qual nó do grafo o autômato se encontra.
        """
        estado_atual = 0  # Estado Inicial (Q0)
        lexema = ""

        while True:
            char = self.consumir_char()
            
            # Condição de parada: Fim do arquivo (EOF)
            if char is None:
                if estado_atual != 0:
                    pass 
                else:
                    return None
                
            # --- Lógica do Estado 0 (Inicial) ---
            if estado_atual == 0:
                if char is None: return None
                
                if char.isspace():
                    continue 

                lexema += char 

                # Tratamento de literais char (ex: 'a') -> Retorna CHAR_TYPE
                if char == "'": 
                    conteudo = self.consumir_char()
                    fecha_aspas = self.consumir_char()
                    if fecha_aspas == "'":
                        return "CHAR_TYPE" # Literal caractere sempre retorna CHAR_TYPE
                    else:
                        print(f"Erro: Char mal formado. Esperado ['] mas lido [{fecha_aspas}]")
                        return None

                # Transições do Estado 0 baseadas no caractere lido:
                elif char.isdigit():
                    estado_atual = 1   # Vai para estado de Inteiro
                elif char.isalpha():
                    estado_atual = 4   # Vai para estado de Identificador/Palavra Reservada
                elif char == '.':
                    estado_atual = 2   # Início de float sem parte inteira (ex: .5)
                
                # Transições para Operadores
                elif char == '>': estado_atual = 19
                elif char == '<': estado_atual = 20
                elif char == '=': estado_atual = 21
                elif char == '!': estado_atual = 22
                elif char == '&': estado_atual = 24
                elif char == '|': estado_atual = 23
                elif char == '/': estado_atual = 17 
                
                elif char in TOKENS_SIMPLES:
                    return TOKENS_SIMPLES[char]
                
                else:
                    print(f"Erro Léxico: Caractere inválido '{char}'")
                    return None

            # --- Estado 1: Lendo Inteiro ---
            elif estado_atual == 1:
                if char is not None and char.isdigit():
                    lexema += char
                elif char == '.':
                    lexema += char
                    estado_atual = 2 
                else:
                    # O número acabou.
                    if char is not None: self.voltar_cursor()
                    
                    # Lógica de Contexto solicitada:
                    # Se for 0 ou 1, verificamos se estamos num contexto de bool ou int
                    if (lexema == "0" or lexema == "1") and self.ultimo_tipo_declarado == "DEFBOOL":
                        return "BOOL_TYPE"
                        
                    return "NUM_INT" 

            # --- Estado 2: Ponto Detectado ---
            elif estado_atual == 2:
                if char is not None and char.isdigit():
                    lexema += char
                    estado_atual = 3 # Confirma float
                else:
                    print(f"Erro Léxico: Float mal formado '{lexema}'")
                    return None

            # --- Estado 3: Corpo do Float ---
            elif estado_atual == 3:
                if char is not None and char.isdigit():
                    lexema += char
                else:
                    if char is not None: self.voltar_cursor()
                    return "NUM_FLOAT" 

            # --- Estado 4: Identificadores e Palavras Reservadas ---
            elif estado_atual == 4:
                if char is not None and (char.isalnum()):
                    lexema += char
                else:
                    if char is not None: self.voltar_cursor()
                    
                    # Verifica se é palavra reservada
                    if lexema in PALAVRAS_RESERVADAS:
                        token = PALAVRAS_RESERVADAS[lexema]
                        
                        # MEMÓRIA DE CONTEXTO:
                        # Se encontramos uma palavra que define tipo, atualizamos o estado
                        if token in ["INTDEF", "FLOATDEF", "DEFCHAR", "DEFBOOL"]:
                            self.ultimo_tipo_declarado = token
                            
                        return token
                    
                    return "VAR"

            # --- Estados de Operadores (19, 20, 21, 22, 17, 24, 23) ---
            elif estado_atual == 19: # > ou >=
                if char == '=': return "GEQ"
                else:
                    if char is not None: self.voltar_cursor()
                    return "GT"

            elif estado_atual == 20: # < ou <=
                if char == '=': return "LEQ"
                else:
                    if char is not None: self.voltar_cursor()
                    return "LT"

            elif estado_atual == 21: # = ou ==
                if char == '=': return "EQ"
                else:
                    if char is not None: self.voltar_cursor()
                    return "Atribuicao"

            elif estado_atual == 22: # ! ou !=
                if char == '=': return "DIF"
                else:
                    if char is not None: self.voltar_cursor()
                    return "NEG"

            elif estado_atual == 17: # / ou //
                if char == '/':
                    while self.cursor < self.tamanho:
                        c = self.consumir_char()
                        if c == '\n': break
                    estado_atual = 0
                    lexema = ""
                    continue
                else:
                    if char is not None: self.voltar_cursor()
                    return "DIV"

            elif estado_atual == 24: # &&
                if char == '&': return "AND"
                else:
                    print("Erro: Esperado '&' após '&'")
                    return None

            elif estado_atual == 23: # ||
                if char == '|': return "OR"
                else:
                    print("Erro: Esperado '|' após '|'")
                    return None

def main():
    if len(sys.argv) < 2:
        print("Uso: python lexico.py <nome_do_arquivo>")
        return

    nome_arquivo = sys.argv[1]
    
    try:
        with open(nome_arquivo, 'r') as f:
            codigo_fonte = f.read()
        
        lexer = AnalisadorLexico(codigo_fonte)
        lista_tokens = lexer.analisar()
        
        saida_formatada = " ".join(lista_tokens)
        nome_saida = nome_arquivo.split('.')[0] + ".lex"
        
        with open(nome_saida, 'w') as f_out:
            f_out.write(saida_formatada)
            
        print(f"Análise concluída com sucesso!")
        print(f"Entrada:\n{codigo_fonte}")
        print("-" * 30)
        print(f"Saída:\n{saida_formatada}")
        print("-" * 30)
        print(f"Arquivo gerado: {nome_saida}")

    except FileNotFoundError:
        print(f"Erro: Arquivo '{nome_arquivo}' não encontrado.")
    except Exception as e:
        print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    main()