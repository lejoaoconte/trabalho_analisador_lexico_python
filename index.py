import sys

# ==============================================================================
# DEFINIÇÃO DOS TOKENS E PALAVRAS RESERVADAS
# Baseado na Tabela 1 do documento PDF 
# ==============================================================================

# Lista de palavras reservadas que mapeiam para tokens específicos.
# Se o autômato reconhecer uma palavra (State 4), verificamos esta lista.
PALAVRAS_RESERVADAS = {
    "int": "INTDEF",       # [cite: 40, 41]
    "float": "FLOATDEF",   # [cite: 44, 45]
    "char": "CHAR_TYPE",   # [cite: 66, 67]
    "bool": "BOLL_TYPE",   # [cite: 69, 70] - Nota: Mantido 'BOLL' conforme PDF, mesmo que 'BOOL' seja o comum.
    "return": "RETURN",    # [cite: 71, 72]
    "If": "IF",            # [cite: 73, 74] - Nota: O PDF especifica "If" com I maiúsculo na Tabela 1.
    "if": "IF"             # Adicionado 'if' minúsculo por segurança, caso seja erro de digitação no PDF.
}

# Mapeamento de operadores simples para Tokens (para estados finais diretos)
TOKENS_SIMPLES = {
    "(": "LParenteses",    # [cite: 23]
    ")": "RParenteses",    # [cite: 26]
    "{": "LChave",         # [cite: 28]
    "}": "RChave",         # [cite: 32]
    "[": "Lcolchete",      # [cite: 36]
    "]": "RColchete",      # [cite: 39]
    "+": "SUM",            # [cite: 24]
    "-": "SUB",            # [cite: 27]
    "*": "MULT",           # [cite: 30]
    "/": "DIV",            # [cite: 34]
    "%": "RESTO",          # [cite: 37]
    ",": "Virgula",        # [cite: 68]
    ";": "PVirgula"        # [cite: 68]
}

# ==============================================================================
# CLASSE DO ANALISADOR LÉXICO
# Implementa a lógica do AFD desenhado no JFLAP [cite: 104]
# ==============================================================================

class AnalisadorLexico:
    def __init__(self, codigo_fonte):
        """
        Inicializa o analisador com o código fonte completo.
        :param codigo_fonte: String contendo todo o conteúdo do arquivo de entrada.
        """
        self.codigo = codigo_fonte
        self.tamanho = len(codigo_fonte)
        self.cursor = 0  # Ponteiro para o caractere atual sendo lido
        self.tokens_encontrados = [] # Lista para armazenar o resultado

    def proximo_char(self):
        """
        Retorna o próximo caractere do buffer sem avançar o cursor (Lookahead).
        Retorna None se for fim de arquivo (EOF).
        """
        if self.cursor < self.tamanho:
            return self.codigo[self.cursor]
        return None

    def consumir_char(self):
        """
        Lê e retorna o caractere atual, avançando o cursor.
        """
        char = self.proximo_char()
        if char is not None:
            self.cursor += 1
        return char

    def voltar_cursor(self):
        """
        Recua o cursor em 1 (usado quando lemos um char extra para decidir o token).
        """
        if self.cursor > 0:
            self.cursor -= 1

    def analisar(self):
        """
        Método principal que percorre o código e extrai tokens até o fim do arquivo.
        """
        while self.cursor < self.tamanho:
            token = self.get_proximo_token()
            if token:
                self.tokens_encontrados.append(token)
        
        return self.tokens_encontrados

    def get_proximo_token(self):
        """
        Simula o AFD para encontrar o próximo token.
        Baseado nos estados e transições do arquivo .jff [cite: 104-123]
        """
        estado_atual = 0  # Estado inicial (q0) [cite: 104]
        lexema = ""       # String que está sendo formada

        # Loop para processar caracteres enquanto não definirmos um token (ou erro)
        while True:
            char = self.consumir_char()
            
            # Se acabou o arquivo e estamos no estado 0, terminamos.
            if char is None:
                if estado_atual != 0:
                    # Se arquivo acabou mas estávamos lendo algo (ex: número), 
                    # precisamos processar o estado final antes de sair.
                    # Vamos tratar como se tivesse recebido um espaço (OUTRO-TIPO)
                    pass 
                else:
                    return None

            # ------------------------------------------------------------------
            # LÓGICA DE TRANSIÇÃO DE ESTADOS (Switch Case gigante simulando o AFD)
            # ------------------------------------------------------------------
            
            # --- ESTADO 0: INICIAL ---
            if estado_atual == 0:
                if char is None: return None
                
                # Ignorar espaços em branco iniciais (Estado 5 no JFLAP apenas consome e volta)
                # O PDF diz: "espaço em branco poderá ser usado como marcador" [cite: 16]
                if char.isspace():
                    continue 

                lexema += char # Começa a formar o token

                if char.isdigit():
                    estado_atual = 1 # Vai para Inteiro [cite: 105]
                elif char.isalpha():
                    estado_atual = 4 # Vai para Word/Var [cite: 106]
                elif char == '.':
                    estado_atual = 2 # Parte decimal solta? (Transição 1->2 existe, mas 0->2 não explícita no JFLAP, assumindo erro ou tratar no float)
                    # Nota: JFLAP não tem 0->2 direto. Se começar com ponto, é erro na C simplificada.
                    # Mas vamos assumir comportamento padrão.
                elif char == '"':
                    # O JFLAP não mostra strings explicitamente além de chars, mas vamos focar no JFLAP.
                    pass
                
                # Operadores e Delimitadores
                elif char == '>': estado_atual = 19 # [cite: 110]
                elif char == '<': estado_atual = 20 # [cite: 111]
                elif char == '=': estado_atual = 21 # [cite: 111] Atribuicao ou EQ
                elif char == '!': estado_atual = 22 # [cite: 112]
                elif char == '&': estado_atual = 24 # [cite: 112] AND (precisa de outro &)
                elif char == '|': estado_atual = 23 # [cite: 112] OR (precisa de outro |)
                elif char == '/': estado_atual = 17 # [cite: 110] Div ou Comentário
                
                # Caracteres de parada imediata (Simples)
                elif char in TOKENS_SIMPLES:
                    return TOKENS_SIMPLES[char]
                
                else:
                    # Caractere inválido
                    print(f"Erro Léxico: Caractere inválido '{char}'")
                    return None

            # --- ESTADO 1: LENDO INTEIRO [cite: 105] ---
            elif estado_atual == 1:
                if char is not None and char.isdigit():
                    lexema += char # Continua no estado 1 [cite: 115]
                elif char == '.':
                    lexema += char
                    estado_atual = 2 # Vai para ponto flutuante [cite: 105, 119]
                else:
                    # OUTRO-TIPO: O número acabou. Devolve o char e retorna o token.
                    if char is not None: self.voltar_cursor()
                    return "NUM_INT" # [cite: 55]

            # --- ESTADO 2: LEU O PONTO (.) DO FLOAT ---
            elif estado_atual == 2:
                if char is not None and char.isdigit():
                    lexema += char
                    estado_atual = 3 # Agora é um Float válido [cite: 115]
                else:
                    # Erro: Ex: "12." sem número depois.
                    # O PDF define float como (digitos)*.(digitos)+ [cite: 60]
                    # Logo, deve haver dígito após o ponto.
                    print(f"Erro Léxico: Float mal formado '{lexema}'")
                    return None

            # --- ESTADO 3: LENDO DECIMAL DO FLOAT [cite: 105] ---
            elif estado_atual == 3:
                if char is not None and char.isdigit():
                    lexema += char # Loop no estado 3 [cite: 115]
                else:
                    # OUTRO-TIPO
                    if char is not None: self.voltar_cursor()
                    return "NUM_FLOAT" # [cite: 59]

            # --- ESTADO 4: LENDO PALAVRA (Keyword ou Var) [cite: 106] ---
            elif estado_atual == 4:
                # JFLAP transição 4->4 é [a-zA-Z0-9] [cite: 120]
                if char is not None and (char.isalnum()):
                    lexema += char
                else:
                    # OUTRO-TIPO: Fim da palavra
                    if char is not None: self.voltar_cursor()
                    
                    # Verificação Semântica do Léxico:
                    # 1. É palavra reservada?
                    if lexema in PALAVRAS_RESERVADAS:
                        return PALAVRAS_RESERVADAS[lexema]
                    
                    # 2. É uma variável válida? 
                    # PDF Tabela 1: VAR(letras,digitos)+ [cite: 76]
                    # Exemplo PDF: VARa 
                    # Isso implica que variáveis DEVEM começar com o prefixo "VAR" nesta linguagem.
                    if lexema.startswith("VAR") and len(lexema) > 3:
                        return "VAR"
                    
                    # Se não for keyword nem começar com VAR, tecnicamente não está na tabela.
                    # Porém, em compiladores reais, retornariamos um ID genérico. 
                    # Seguindo estritamente o exemplo do PDF "int VARa", 'int' é INTDEF, 'VARa' é VAR.
                    # Se o código tiver 'abc', seria erro nesta linguagem estrita?
                    # Vamos assumir que se não começa com VAR e não é reservada, é erro ou apenas ignorado.
                    # Para robustez, vou retornar ERROR se não for VAR, seguindo o PDF estrito.
                    if lexema == "VAR": return "VAR" # Caso limite apenas "VAR"
                    return "Erro: Identificador inválido (deve iniciar com VAR)"

            # --- ESTADO 19: LENDO MAIOR (>) [cite: 110] ---
            elif estado_atual == 19:
                if char == '=':
                    return "GEQ" # >= [cite: 50]
                else:
                    if char is not None: self.voltar_cursor()
                    return "GT"  # > [cite: 57]

            # --- ESTADO 20: LENDO MENOR (<) [cite: 111] ---
            elif estado_atual == 20:
                if char == '=':
                    return "LEQ" # <= [cite: 53]
                else:
                    if char is not None: self.voltar_cursor()
                    return "LT"  # < [cite: 61]

            # --- ESTADO 21: LENDO IGUAL (=) [cite: 111] ---
            elif estado_atual == 21:
                if char == '=':
                    return "EQ" # == [cite: 42]
                else:
                    # Importante: PDF diz para ter cuidado com = e == 
                    if char is not None: self.voltar_cursor()
                    return "Atribuicao" # = [cite: 46]

            # --- ESTADO 22: LENDO EXCLAMAÇÃO (!) [cite: 111] ---
            elif estado_atual == 22:
                if char == '=':
                    return "DIF" # != [cite: 64]
                else:
                    if char is not None: self.voltar_cursor()
                    return "NEG" # ! [cite: 62]

            # --- ESTADO 17: LENDO BARRA (/) ---
            elif estado_atual == 17:
                if char == '/':
                    # Estado 18 no JFLAP (//). Comentário de linha.
                    # Consumir até o fim da linha e não retornar token.
                    while self.cursor < self.tamanho:
                        c = self.consumir_char()
                        if c == '\n': break
                    estado_atual = 0
                    lexema = "" # Reseta lexema
                    continue # Volta para o loop principal buscando novo token
                else:
                    if char is not None: self.voltar_cursor()
                    return "DIV" # [cite: 34]

            # --- ESTADO 24: LENDO E COMERCIAL (&) ---
            elif estado_atual == 24:
                if char == '&':
                    return "AND" # && [cite: 48]
                else:
                    # PDF só define &&, não define & bitwise.
                    print("Erro: Esperado '&' após '&'")
                    return None

            # --- ESTADO 23: LENDO PIPE (|) ---
            elif estado_atual == 23:
                if char == '|':
                    return "OR" # || [cite: 52]
                else:
                    print("Erro: Esperado '|' após '|'")
                    return None


# ==============================================================================
# FUNÇÃO PRINCIPAL (MAIN)
# Lê argumentos e executa a conversão 
# ==============================================================================

def main():
    # Verifica se o arquivo foi passado como parâmetro
    if len(sys.argv) < 2:
        print("Uso: python lexico.py <nome_do_arquivo>")
        return

    nome_arquivo = sys.argv[1]
    
    try:
        # Lê o arquivo de entrada
        with open(nome_arquivo, 'r') as f:
            codigo_fonte = f.read()
        
        # Instancia e executa o analisador
        lexer = AnalisadorLexico(codigo_fonte)
        lista_tokens = lexer.analisar()
        
        # Formata a saída separada por espaços [cite: 15]
        saida_formatada = " ".join(lista_tokens)
        
        # Gera nome do arquivo de saída (ex: input.txt -> input.lex)
        nome_saida = nome_arquivo.split('.')[0] + ".lex"
        
        with open(nome_saida, 'w') as f_out:
            f_out.write(saida_formatada)
            
        print(f"Análise concluída com sucesso!")
        print(f"Entrada: {codigo_fonte.strip()}")
        print(f"Saída: {saida_formatada}")
        print(f"Arquivo gerado: {nome_saida}")

    except FileNotFoundError:
        print(f"Erro: Arquivo '{nome_arquivo}' não encontrado.")
    except Exception as e:
        print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    main()