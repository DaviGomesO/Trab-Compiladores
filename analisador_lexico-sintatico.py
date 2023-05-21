import re

class Token:
    def __init__(self, token_type, lexeme, line):
        self.token_type = token_type
        self.lexeme = lexeme
        self.line = line

    def __str__(self):
        return f"{self.token_type} - Lexema: {self.lexeme} - Linha: {self.line}"

class Lexer:
    def __init__(self, input_string):
        self.input_string = input_string
        self.tokens = []
        self.current_line = 1
        self.current_position = 0

    def lex(self):
        while self.current_position < len(self.input_string):
            token = self._get_next_token()
            if token is not None:
                self.tokens.append(token)

        self.tokens.append(Token('EOF', '', self.current_line))
        return self.tokens

    def _get_next_token(self):
        # Ignorar espaços em branco
        if self.input_string[self.current_position].isspace():
            if self.input_string[self.current_position] == '\n':
                self.current_line += 1
            self.current_position += 1
            return None

        # Identificar tokens
        for pattern, token_type in token_patterns:
            match = re.match(pattern, self.input_string[self.current_position:])
            if match:
                lexeme = match.group(0)
                token = Token(token_type, lexeme, self.current_line)
                self.current_position += len(lexeme)
                return token

        # Erro léxico: caractere inválido
        invalid_char = self.input_string[self.current_position]
        self.current_position += 1
        return Token('ERROR', invalid_char, self.current_line)

token_patterns = [
    (r':=', 'ATRIBUIÇÃO'),
    (r'not', 'NOT'),
    (r'or', 'OU'),
    (r'and', 'E'),
    (r'div', 'DIV'),
    (r'=', 'EQ'),
    (r'<>','DIF'),
    (r'<','LT'),
    (r'<=','LTE'),
    (r'>=','GTE'),
    (r'>','GT'),
    (r'\+','SOMA'),
    (r'-','SUB'),
    (r'\*','MULT'),
    (r'\(','LPAREN'),
    (r'\)','RPAREN'),
    (r'[a-zA-Z][a-zA-Z0-9]*', 'IDENTIFICADOR'),
    (r'\d+', 'NÚMERO'),
]

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0

    def parse(self):
        ast = self.assignment_statement()
        if self.current_token().token_type != 'EOF':
            self._raise_syntax_error("Token inesperado após a declaração de atribuição")

        return ast

    def assignment_statement(self):
        identificador = self.identificador()
        if self.current_token().token_type != 'ATRIBUIÇÃO':
            self._raise_syntax_error("Esperado := após o identificador na declaração de atribuição")

        self._consume_token('ATRIBUIÇÃO')
        expressao = self.expression()
        return ('atribuição', identificador, expressao)

    def expression(self):
        expressao_simples = self.simple_expression()
        if self.current_token().token_type in ['EQ', 'DIF', 'LT', 'LTE', 'GTE', 'GT', 'OU', 'E']:
            operador_relacional = self.relational_operator()
            expressao_simples_2 = self.simple_expression()
            return ('expressão', expressao_simples, operador_relacional, expressao_simples_2)

        return expressao_simples

    def simple_expression(self):
        sinal = self.sign()
        termo = self.term()
        while self.current_token().token_type in ['SOMA', 'SUB']:
            operador_aditivo = self.adding_operator()
            termo_2 = self.term()
            termo = ('termo', termo, operador_aditivo, termo_2)

        return ('expressão_simples', sinal, termo)

    def term(self):
        fator = self.factor()
        while self.current_token().token_type in ['MULT', 'DIV']:
            operador_multiplicativo = self.multiplying_operator()
            fator_2 = self.factor()
            fator = ('fator', fator, operador_multiplicativo, fator_2)

        return ('termo', fator)

    def factor(self):
        tipo_token_atual = self.current_token().token_type
        if tipo_token_atual == 'IDENTIFICADOR':
            identificador = self.identificador()
            return ('fator', identificador)
        elif tipo_token_atual == 'LPAREN':
            self._consume_token('LPAREN')
            expressao = self.expression()
            self._consume_token('RPAREN')
            return ('fator', expressao)
        elif tipo_token_atual == 'NOT':
            self._consume_token('NOT')
            fator = self.factor()
            return ('fator', 'not', fator)
        elif tipo_token_atual == 'NÚMERO':
            número = self.número()
            return ('fator', número)
        else:
            self._raise_syntax_error("Fator inválido")

    def relational_operator(self):
        tipo_token = self.current_token().token_type
        if tipo_token in ['EQ', 'DIF', 'LT', 'LTE', 'GTE', 'GT', 'OU', 'E']:
            self._consume_token(tipo_token)
            return tipo_token
        else:
            self._raise_syntax_error("Operador relacional esperado")

    def adding_operator(self):
        tipo_token = self.current_token().token_type
        if tipo_token in ['SOMA', 'SUB']:
            self._consume_token(tipo_token)
            return tipo_token
        else:
            self._raise_syntax_error("Operador aditivo esperado")

    def multiplying_operator(self):
        tipo_token = self.current_token().token_type
        if tipo_token in ['MULT', 'DIV']:
            self._consume_token(tipo_token)
            return tipo_token
        else:
            self._raise_syntax_error("Operador multiplicativo esperado")

    def sign(self):
        tipo_token = self.current_token().token_type
        if tipo_token in ['SOMA', 'SUB']:
            self._consume_token(tipo_token)
            return tipo_token
        else:
            return '<vazio>'

    def identificador(self):
        token = self.current_token()
        self._consume_token('IDENTIFICADOR')
        return token.lexeme

    def número(self):
        token = self.current_token()
        self._consume_token('NÚMERO')
        return token.lexeme

    def current_token(self):
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        else:
            return Token('EOF', '', self.current_token_index)

    def _consume_token(self, tipo_token_esperado):
        token = self.current_token()
        if token.token_type == tipo_token_esperado:
            self.current_token_index += 1
        else:
            self._raise_syntax_error(f"Esperado {tipo_token_esperado}, encontrado {token.token_type}")

    def _raise_syntax_error(self, mensagem):
        token = self.current_token()
        raise SyntaxError(f"Erro de sintaxe na linha {token.line}: {mensagem}")

def imprimir_tabela_tokens(tokens):
    print("Tabela de Tokens:")
    print("-----------------")
    print("Tipo de Token - Lexema - Linha")
    for token in tokens:
        print(token)
    print()

def imprimir_árvore_sintática(ast):
    print("Árvore Sintática:")
    print("-----------------")
    imprimir_ast(ast)
    print()

def imprimir_ast(node, level=0):
    if isinstance(node, tuple):
        for item in node:
            imprimir_ast(item, level+1)
    else:
        print("  " * level + str(node))

def analisar(input_string):
    lexer = Lexer(input_string)
    tokens = lexer.lex()
    imprimir_tabela_tokens(tokens)

    parser = Parser(tokens)
    ast = parser.parse()
    imprimir_árvore_sintática(ast)

    if parser.current_token().token_type != 'EOF':
        print("Erro: Token inesperado após a declaração de atribuição")
    else:
        print("Análise sintática concluída com sucesso")

cadeia_entrada = input("Digite a cadeia de entrada: ")
analisar(cadeia_entrada)
