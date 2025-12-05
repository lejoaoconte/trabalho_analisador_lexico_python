import sys

PALAVRAS_RESERVADAS = {
    "int": "INTDEF",       
    "float": "FLOATDEF",  
    "char": "CHAR_TYPE", 
    "bool": "BOLL_TYPE",  
    "return": "RETURN",  
    "If": "IF",   
    "if": "IF"        
}

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
    def __init__(self, codigo_fonte):
        self.codigo = codigo_fonte
        self.tamanho = len(codigo_fonte)
        self.cursor = 0 
        self.tokens_encontrados = []

    def proximo_char(self):
        if self.cursor < self.tamanho:
            return self.codigo[self.cursor]
        return None

    def consumir_char(self):
        char = self.proximo_char()
        if char is not None:
            self.cursor += 1
        return char

    def voltar_cursor(self):
        if self.cursor > 0:
            self.cursor -= 1

    def analisar(self):
        while self.cursor < self.tamanho:
            token = self.get_proximo_token()
            if token:
                self.tokens_encontrados.append(token)
        return self.tokens_encontrados

    def get_proximo_token(self):
        estado_atual = 0
        lexema = ""

        while True:
            char = self.consumir_char()
            
            if char is None:
                if estado_atual != 0:
                    pass 
                else:
                    return None
                
            if estado_atual == 0:
                if char is None: return None
                
                if char.isspace():
                    continue 

                lexema += char 

                if char == "'": 
                    conteudo = self.consumir_char()
                    fecha_aspas = self.consumir_char()
                    if fecha_aspas == "'":
                        return "CHAR_CHARACTER" 
                    else:
                        print(f"Erro: Char mal formado. Esperado ['] mas lido [{fecha_aspas}]")
                        return None

                elif char.isdigit():
                    estado_atual = 1
                elif char.isalpha():
                    estado_atual = 4
                elif char == '.':
                    estado_atual = 2
                
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

            elif estado_atual == 1:
                if char is not None and char.isdigit():
                    lexema += char
                elif char == '.':
                    lexema += char
                    estado_atual = 2 
                else:
                    if char is not None: self.voltar_cursor()
                    return "NUM_INT" 

            elif estado_atual == 2:
                if char is not None and char.isdigit():
                    lexema += char
                    estado_atual = 3
                else:
                    print(f"Erro Léxico: Float mal formado '{lexema}'")
                    return None

            elif estado_atual == 3:
                if char is not None and char.isdigit():
                    lexema += char
                else:
                    if char is not None: self.voltar_cursor()
                    return "NUM_FLOAT" 

            elif estado_atual == 4:
                if char is not None and (char.isalnum()):
                    lexema += char
                else:
                    if char is not None: self.voltar_cursor()
                    
                    if lexema in PALAVRAS_RESERVADAS:
                        return PALAVRAS_RESERVADAS[lexema]
                    
                    return "VAR"

            elif estado_atual == 19:
                if char == '=': return "GEQ"
                else:
                    if char is not None: self.voltar_cursor()
                    return "GT"

            elif estado_atual == 20:
                if char == '=': return "LEQ"
                else:
                    if char is not None: self.voltar_cursor()
                    return "LT"

            elif estado_atual == 21:
                if char == '=': return "EQ"
                else:
                    if char is not None: self.voltar_cursor()
                    return "Atribuicao"

            elif estado_atual == 22:
                if char == '=': return "DIF"
                else:
                    if char is not None: self.voltar_cursor()
                    return "NEG"

            elif estado_atual == 17:
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

            elif estado_atual == 24:
                if char == '&': return "AND"
                else:
                    print("Erro: Esperado '&' após '&'")
                    return None

            elif estado_atual == 23:
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

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()