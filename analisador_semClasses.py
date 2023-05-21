import re

def lex(input_string):
    current_line = 1
    current_position = 0
    tokens = []

    while current_position < len(input_string):
        token = get_next_token()
        if token is not None:
            tokens.append(token)

    tokens.append(('EOF', '', current_line))
    return tokens

def get_next_token():
    if input_string[current_position].isspace():
        if input_string[current_position] == '\n':
            current_line += 1
        current_position += 1
        return None

    for pattern, token_type in token_patterns:
        match = re.match(pattern, input_string[current_position:])
        if match:
            lexeme = match.group(0)
            token = (token_type, lexeme, current_line)
            current_position += len(lexeme)
            return token

    invalid_char = input_string[current_position]
    current_position += 1
    return ('ERROR', invalid_char, current_line)

def parse(tokens):
    current_token_index = 0

    def assignment_statement():
        identificador = identificador()
        if current_token()[0] != 'ATRIBUIÇÃO':
            raise SyntaxError("Esperado := após o identificador na declaração de atribuição")

        consume_token('ATRIBUIÇÃO')
        expressao = expression()
        return ('atribuição', identificador, expressao)

    def expression():
        expressao_simples = simple_expression()
        if current_token()[0] in ['EQ', 'DIF', 'LT', 'LTE', 'GTE', 'GT', 'OU', 'E']:
            operador_relacional = relational_operator()
            expressao_simples_2 = simple_expression()
            return ('expressão', expressao_simples, operador_relacional, expressao_simples_2)

        return expressao_simples

    def simple_expression():
        sinal = sign()
        termo = term()
        while current_token()[0] in ['SOMA', 'SUB']:
            operador_aditivo = adding_operator()
            termo_2 = term()
            termo = ('termo', termo, operador_aditivo, termo_2)

        return ('expressão_simples', sinal, termo)

    def term():
        fator = factor()
        while current_token()[0] in ['MULT', 'DIV']:
            operador_multiplicativo = multiplying_operator()
            fator_2 = factor()
            fator = ('fator', fator, operador_multiplicativo, fator_2)

        return ('termo', fator)

    def factor():
        tipo_token_atual = current_token()[0]
        if tipo_token_atual == 'IDENTIFICADOR':
            identificador = identificador()
            return ('fator', identificador)
        elif tipo_token_atual == 'LPAREN':
            consume_token('LPAREN')
            expressao = expression()
            consume_token('RPAREN')
            return ('fator', expressao)
        elif tipo_token_atual == 'NOT':
            consume_token('NOT')
            fator = factor()
            return ('fator', 'not', fator)
        elif tipo_token_atual == 'NÚMERO':
            número = número()
            return ('fator', número)
        else:
            raise SyntaxError("Fator inválido")

    def relational_operator():
        tipo_token = current_token()[0]
        if tipo_token in ['EQ', 'DIF', 'LT', 'LTE', 'GTE', 'GT', 'OU', 'E']:
            consume_token(tipo_token)
            return tipo_token
        else:
            raise SyntaxError("Operador relacional esperado")

    def adding_operator():
        tipo_token = current_token()[0]
        if tipo_token in ['SOMA', 'SUB']:
            consume_token(tipo_token)
            return tipo_token
        else:
            raise SyntaxError("Operador aditivo esperado")

    def multiplying_operator():
        tipo_token = current_token()[0]
        if tipo_token in ['MULT', 'DIV']:
            consume_token(tipo_token)
            return tipo_token
        else:
            raise SyntaxError("Operador multiplicativo esperado")

    def sign():
        tipo_token = current_token()[0]
        if tipo_token in ['SOMA', 'SUB']:
            consume_token(tipo_token)
            return tipo_token
        else:
            return '<vazio>'

    def identificador():
        token = current_token()
        consume_token('IDENTIFICADOR')
        return token[1]

    def número():
        token = current_token()
        consume_token('NÚMERO')
        return token[1]

    def current_token():
        if current_token_index < len(tokens):
            return tokens[current_token_index]
        else:
            return ('EOF', '', current_token_index)

    def consume_token(tipo_token_esperado):
        token = current_token()
        if token[0] == tipo_token_esperado:
            nonlocal current_token_index
            current_token_index += 1
        else:
            raise SyntaxError(f"Esperado {tipo_token_esperado}, encontrado {token[0]}")

    ast = assignment_statement()
    if current_token()[0] != 'EOF':
        raise SyntaxError("Token inesperado após a declaração de atribuição")

    return ast

def imprimir_tabela_tokens(tokens):
    print("Tabela de Tokens:")
    print("-----------------")
    print("Tipo de Token - Lexema - Linha")
    for token in tokens:
        print(f"{token[0]} - Lexema: {token[1]} - Linha: {token[2]}")
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
    tokens = lex(input_string)
    imprimir_tabela_tokens(tokens)
    try:
        ast = parse(tokens)
        imprimir_árvore_sintática(ast)
        print("Análise sintática concluída com sucesso")
    except SyntaxError as e:
        print(f"Erro de sintaxe: {str(e)}")

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
    (r'[a-zA-Z][a-zA-Z0-9]*','IDENTIFICADOR'),
    (r'[0-9]+','NÚMERO'),
]

input_string = '''
x := 5 + 3
y := x * 2
'''

analisar(input_string)
