import sys

# Dicionário de palavras reservadas conforme especificado na Tabela 1 do trabalho.
# Mapeia o lexema (string encontrada) para o token correspondente.
RESERVED_WORDS = {
    "int": "INTDEF",       
    "float": "FLOATDEF",  
    "char": "DEFCHAR",  
    "bool": "DEFBOOL",   
    "return": "RETURN",  
    "If": "IF",   # Como está no PDF, mas pode ser "if" iremos adicionar abaixo dependendo do caso
    "if": "IF"  
}

# Dicionário para tokens de caractere único (símbolos especiais e operadores simples).
SIMPLE_TOKENS = {
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

class LexicalAnalyzer:
    """
    Implementação de um Analisador Léxico baseado em Autômato Finito Determinístico (AFD).
    O analisador lê o código fonte caractere por caractere e agrupa lexemas em tokens.
    """
    def __init__(self, source_code):
        self.code = source_code
        self.length = len(source_code)
        self.cursor = 0   # Aponta para a posição inicial de leitura no código
        self.found_tokens = []
        
        # Variável de estado para contexto semântico simples
        # Armazena qual foi o último tipo declarado (int, bool, float, char)
        # para decidir se 0 ou 1 devem ser NUM_INT ou BOOL_TYPE.
        self.last_declared_type = None 

    def peek_char(self):
        """Retorna o caractere na posição atual sem avançar o cursor (Lookahead)."""
        if self.cursor < self.length:
            return self.code[self.cursor]
        return None

    def consume_char(self):
        """Retorna o caractere atual e avança o cursor (Consumo da fita de entrada)."""
        char = self.peek_char()
        if char is not None:
            self.cursor += 1
        return char

    def backtrack_cursor(self):
        """
        Retrocede o cursor em uma posição.
        Fundamental para implementar transições de 'outro' (other).
        """
        if self.cursor > 0:
            self.cursor -= 1

    def analyze(self):
        """Loop principal que consome todo o arquivo gerando a lista de tokens."""
        while self.cursor < self.length:
            token = self.get_next_token()
            if token:
                self.found_tokens.append(token)
        return self.found_tokens

    def get_next_token(self):
        """
        Método central que implementa a lógica do AFD.
        A variável 'estado_atual' rastreia em qual nó do grafo o autômato se encontra.
        """
        current_state = 0  # Estado Inicial (Q0)
        lexeme = ""

        while True:
            char = self.consume_char()
            
            # Condição de parada: Fim do arquivo (EOF)
            if char is None:
                if current_state != 0:
                    pass 
                else:
                    return None
                
            # --- Lógica do Estado 0 (Inicial) ---
            if current_state == 0:
                if char is None: return None
                # Lê a linha até encontrar um caractere branco
                if char.isspace():
                    continue 

                lexeme += char 

                # Tratamento de literais char (ex: 'a') -> Retorna CHAR_TYPE
                # Se tiver aspas simples, consome o próximo caractere e verifica o fechamento
                # Caso seja válido, retorna CHAR_TYPE, senão, erro léxico.
                if char == "'": 
                    content = self.consume_char()
                    closing_quote = self.consume_char()
                    if closing_quote == "'":
                        return "CHAR_TYPE" # Literal caractere sempre retorna CHAR_TYPE
                    else:
                        print(f"Error: Malformed char. Expected ['] but read [{closing_quote}]")
                        return None

                # Transições do Estado 0 baseadas no caractere lido:
                elif char.isdigit():
                    # Se o caractere for dígito, vai para estado de Inteiro
                    # ou seja começa a ler um número inteiro
                    current_state = 1   # Vai para estado de Inteiro
                elif char.isalpha():
                    # Se for letra, vai para estado de Identificador/Palavra Reservada
                    current_state = 4   # Vai para estado de Identificador/Palavra Reservada
                elif char == '.':
                    # Se começar com ponto, vai para estado de float
                    # (Item extra não pedido e não aceito em C)
                    current_state = 2   # Início de float sem parte inteira (ex: .5)
                
                # Transições para Operadores
                elif char == '>': current_state = 19
                elif char == '<': current_state = 20
                elif char == '=': current_state = 21
                elif char == '!': current_state = 22
                elif char == '&': current_state = 24
                elif char == '|': current_state = 23
                elif char == '/': current_state = 17 
                
                # Tokens de caractere único
                elif char in SIMPLE_TOKENS:
                    return SIMPLE_TOKENS[char]
                
                else:
                    print(f"Lexical Error: Invalid character '{char}'")
                    return None

            # --- Estado 1: Lendo Inteiro ---
            elif current_state == 1:
                if char is not None and char.isdigit():
                    lexeme += char
                elif char == '.':
                    lexeme += char
                    current_state = 2 
                else:
                    # O número acabou.
                    if char is not None: self.backtrack_cursor()
                    
                    # Lógica de Contexto solicitada:
                    # Se for 0 ou 1, verificamos se estamos num contexto de bool ou int
                    if (lexeme == "0" or lexeme == "1") and self.last_declared_type == "BOOLDEF":
                        return "BOOL_TYPE"
                        
                    return "NUM_INT" 

            # --- Estado 2: Ponto Detectado ---
            elif current_state == 2:
                if char is not None and char.isdigit():
                    lexeme += char
                    current_state = 3 # Confirma float
                else:
                    print(f"Lexical Error: Malformed float '{lexeme}'")
                    return None

            # --- Estado 3: Corpo do Float ---
            elif current_state == 3:
                if char is not None and char.isdigit():
                    lexeme += char
                else:
                    # Se o número acabou
                    if char is not None: self.backtrack_cursor()
                    return "NUM_FLOAT" 

            # --- Estado 4: Identificadores e Palavras Reservadas ---
            elif current_state == 4:
                if char is not None and (char.isalnum()):
                    lexeme += char
                else:
                    if char is not None: self.backtrack_cursor()
                    
                    # Verifica se é palavra reservada
                    if lexeme in RESERVED_WORDS:
                        token = RESERVED_WORDS[lexeme]
                        
                        # MEMÓRIA DE CONTEXTO:
                        # Se encontramos uma palavra que define tipo, atualizamos o estado
                        if token in ["INTDEF", "FLOATDEF", "CHARDEF", "BOOLDEF"]:
                            self.last_declared_type = token
                            
                        return token
                    
                    return "VAR"

            # --- Estados de Operadores (19, 20, 21, 22, 17, 24, 23) ---
            elif current_state == 19: # > ou >=
                # Se o próximo caractere for '=', é GEQ (maior igual)
                # senão, é GT (maior que)
                if char == '=': return "GEQ"
                else:
                    if char is not None: self.backtrack_cursor()
                    return "GT"

            elif current_state == 20: # < ou <=
                # Se o próximo caractere for '=', é LEQ (menor igual)
                # senão, é LT (menor que)
                if char == '=': return "LEQ"
                else:
                    if char is not None: self.backtrack_cursor()
                    return "LT"

            elif current_state == 21: # = ou ==
                # Se o próximo caractere for '=', é EQ (igualdade)
                # senão, é Atribuicao (atribuição)
                if char == '=': return "EQ"
                else:
                    if char is not None: self.backtrack_cursor()
                    return "Atribuicao"

            elif current_state == 22: # ! ou !=
                # Se o próximo caractere for '=', é DIF (diferente)
                # senão, é NEG (negação)
                if char == '=': return "DIF"
                else:
                    if char is not None: self.backtrack_cursor()
                    return "NEG"

            elif current_state == 17: # / ou //
                # Se o próximo caractere for '/', é comentário de linha
                # senão, é DIV (divisão)
                # quando é comentário, consome até o fim da linha e reinicia o estado
                if char == '/':
                    while self.cursor < self.length:
                        c = self.consume_char()
                        if c == '\n': break
                    current_state = 0
                    lexeme = ""
                    continue
                else:
                    if char is not None: self.backtrack_cursor()
                    return "DIV"

            elif current_state == 24: # &&
                # Se o próximo caractere for '&', é AND (e lógico)
                # senão, é erro léxico
                if char == '&': return "AND"
                else:
                    print("Error: Expected '&' after '&'")
                    return None

            elif current_state == 23: # ||
                # Se o próximo caractere for '|', é OR (ou lógico)
                # senão, é erro léxico
                if char == '|': return "OR"
                else:
                    print("Error: Expected '|' after '|'")
                    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python lexico.py <filename>")
        return
    
    # Obter o nome do arquivo a partir dos argumentos da linha de comando
    filename = sys.argv[1]
    
    
    # Leitura do arquivo de entrada
    try:
        with open(filename, 'r') as f:
            source_code = f.read()
        
        # Análise Léxica
        lexer = LexicalAnalyzer(source_code)
        # Gera a lista de tokens
        token_list = lexer.analyze()
        
        # Formata a saída como uma string única separada por espaços
        formatted_output = " ".join(token_list)
        output_filename = "output.lex"
        
        # Escrita do arquivo de saída
        with open(output_filename, 'w') as f_out:
            f_out.write(formatted_output)
            
        print(f"Analysis completed successfully!")
        # Linha para debug do input
        #print(f"Input:\n{source_code}")
        #print("-" * 30)
        print(f"Output:\n{formatted_output}")
        print("-" * 30)
        print(f"Generated file: {output_filename}")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()