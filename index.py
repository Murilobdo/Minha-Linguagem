"""
Cainã Antunes - RA: 160831
Guilherme Proença Cravo da Costa - RA: 160068
Jair Rodrigo de Goes Brisola - RA: 160092
Murilo Bernardes de Oliveira - RA: 160036

Regras de produção EBNF:
- Cada token deve ser separado por espaço
- Uma variável "id" deve ser declarada é usado "def"
- Deve ser atribuido um valor "int" ou "id" já declarado ou expressão <expr> a cada variável declarada 
- Resolve equações <expr> com variáveis "id" e números "int" em ordem de prioridade dos operadores básicos "+-*/"
- Resolve primeiro expressões dentro de parênteses e verifica se a ordem e quantidade estão corretas
- Variável "id" como vetor se a sequência de tokens for "[", "int" e/ou "id", 
  para separar cada conteúdo "," se tiver mais de um e termina com "]"
- Vetor não precisa ser inicializado 
- Lógica de sintaxe de repetição "while" <condição> "break" <expr> e/ou "vet" "endwhile"
- Incrementa em 1 variável "id" com "++" na frente  
"""

"""
Problema a ser resolvido:
Inverter um vetor de variáveis "id" e/ou números "int" utilizando o laço de repetição "while"
"""

import re

T_SYMBOL = "symbol"
T_KEYWORD = "def"
T_OP = "op"
T_INT = "int"
T_STRING = "string"
T_ID = "id"
T_IF = "begin_if"
T_ENDIF = "end_if"
T_WHILE = "begin_while"
T_ENDWHILE = "end_while"
T_BREAK = "break"
T_VET = "vetor"
T_EOF = "eof"

class Stack:
    
    def __init__(self):
        self.tokens = []

    def init(self):
        self.tokens = []

    def isEmpty(self):
        return self.tokens == []

    def push(self, token_atual):
        self.tokens.append(token_atual)

    def pop(self):
        return self.tokens.pop()

    def peek(self):
        return self.tokens[len(self.tokens)+1]

    def size(self):
        return len(self.tokens)

class Token():
    
    def __init__(self, tipo, line,valor=None):
        self.tipo = tipo
        self.valor = valor
        self.resultado = None
        self.line = line
                
    def __str__(self):
        return '<%s %s>' % (self.tipo, self.valor)


class StopExecution(Exception):
    def _render_traceback_(self):
        pass

    
def afd_int(token):
    try:
        token = int(token)
        return True
    except:
        return False
    
def afd_string(token):
    if token[0] == '"' and token[-1] == '"':
        if '"' not in token[1:-1]:
            return True
        else:
            raise ValueError('Aspas em um local inesperado.')
    else:
        return False
    
def afd_identificador(token):
    regex = re.compile('[a-zA-Z0-9_]+')
    r = regex.match(token)
    if r is not None:
        if r.group() == token:
            return True
        else:
            return False
    else:
        return False
    
def afd_simbolo(token):
    if token in "()\n":
        return True
    return False
    
def afd_if(token):
    if token == "if" or token == "endif":
        return True
    return False

def afd_while(token):
    if token == "while" or token == "endwhile":
        return True
    return False

def afd_break(token):
    if token in ":,":
        return True
    return False

def afd_def(token):
    if token == "def":
        return True
    return False

def afd_vetor(token):
    if token in "[]":
        return True
    return False
         
def afd_principal(token, NextToken, lista, line):
    
   
    if afd_def(token):
        lista.append(NextToken)
        return Token(T_KEYWORD, line, token )
    
    elif afd_while(token):
        return Token(T_WHILE if token == 'while' else T_ENDWHILE, line, token )
    
    elif afd_if(token):
        return Token(T_IF if token == 'if' else T_ENDIF, line, token )
    
    elif  token in ["=", "+", "*", "/", "-", "<", ">", "{}++".format(token.split("+")[0])]:
        return Token(T_OP, line, token )
    
    elif afd_int(token):
        return Token(T_INT, line, token )
    
    elif afd_string(token):
        return Token(T_STRING, line, token )
    
    elif afd_identificador(token):
        return Token(T_ID, line, token )
    
    elif afd_simbolo(token):
        return Token(T_SYMBOL, line, token )
    
    elif afd_vetor(token):
        return Token(T_VET, line, token )
    
    elif afd_break(token):
        return Token(T_BREAK, line, token ) 
    
    else:
        raise ValueError('Valor inesperado na chave [{}]'.format(token))
        
    return None

def checar_parenteses(line):
    stack = Stack()
    for s in line:
        if(s not in "()"):
            continue
        #econtrei uma abertura
        if s == "(":
            stack.push(s)
        else:
            #econtrei um fechamento
            if(stack.size() > 0):
                elem = stack.pop()
                if elem == "(":
                    continue
                else:
                    stack.push(elem)
            else:
                #empilho o ')'
                stack.push(s)
                break

    if stack.size() > 0 :
        return False
    else:
        return True
    
class Parser():
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = -1
        self.token_atual = None
        self.proximo()

        
    def proximo(self):
        self.pos += 1
        if self.pos >= len(self.tokens):
            self.token_atual = Token(T_EOF, 0)
        else:    
            self.token_atual = self.tokens[self.pos]
        
        print("{}".format(self.token_atual))
        return self.token_atual
    
    def pegar_proximo(self):
        try:
            return self.tokens[self.pos + 1] 
        except Exception:
            pass
    
    def erro(self, msg = ""):
        raise Exception('Erro de sintaxe. {}'.format(msg))
        
    def use(self, tipo, valor=None):
        
        # O id não foi declarado
        if(self.token_atual.tipo == T_ID and (self.token_atual.valor not in list_defs)):
            self.erro("Essa variável não foi declarada [{}]".format(self.token_atual.valor))
        
        if self.token_atual.tipo != tipo:
            self.erro()
        elif valor is not None and self.token_atual.valor != valor:
            self.erro()
        else:
            self.proximo()
    
    def setResultado(self, valorID, resultado):
        for token in self.tokens:
            if(token.valor == valorID):
                token.resultado = resultado
    
    def statement(self):
        """
        statement ::= <def> <id> <op => expr | <id> <op => expr
        """
        
        if (self.token_atual.tipo == T_KEYWORD):
            self.use(T_KEYWORD) # def

        if (self.token_atual.tipo == T_ID):
            valorID = self.token_atual.valor
            self.use(T_ID) #id
            if (self.token_atual.tipo == T_OP and self.token_atual.valor == '='):
                
                if(self.pegar_proximo().valor == "["):
                    self.proximo()
                    self.structure_vetor(valorID)
                else:
                    self.use(T_OP) # = < >
                    x = self.expr() # id ou int
                    self.setResultado(valorID, x)
                
            elif (self.token_atual.tipo == T_INT):
                self.use(T_INT)
            else:
                self.erro()
                
        if (self.token_atual.tipo == T_KEYWORD): 
            self.statement()
        elif (self.token_atual.tipo == T_ID):
            self.use(T_ID) #id
            if (self.token_atual.tipo == T_OP and self.token_atual.valor == '='):
                self.proximo()
                x = self.expr() # id ou int
                self.setResultado(valorID, x)
            if (self.token_atual.tipo != T_EOF):
                self.proximo()
            elif (self.token_atual.tipo == T_EOF):
                self.use(T_EOF)
        
        if(self.token_atual.tipo == T_WHILE):
            self.structure_while()
            self.proximo()
            self.body_while()
            self.execute_while()
            vetor =  [token for token in self.tokens if token.valor == 'vetor'][0]
            vetor_inv =  [token for token in self.tokens if token.valor == 'vetor_inv'][0]
            print("Vetor = ", vetor.resultado)
            print("Vetor invertido = ", vetor_inv.resultado)
                  
                
    def expr(self):
        """
        expr ::= term ( <op + > | <op - > term )
        """
        
        a = self.term()
        while self.token_atual.tipo == T_OP and self.token_atual.valor in ['+','-']:
            op = self.token_atual.valor
            self.use(T_OP)
            
            b = self.term()
            
            if op == "+":
                a += b
            elif op == "-":
                a -= b  
        
        return a
           
    def term(self):
        """
        term ::= factor ( <op *> | <op /> factor )*
        """
        
        a = self.factor()
        while self.token_atual.tipo == T_OP and self.token_atual.valor in ['/','*']:
            op = self.token_atual.valor
            
            self.use(T_OP)
            b = self.factor()
            
            if op == "*":
                a *= b
            elif op == "/":
                a /= b
        
        if (self.token_atual.tipo != T_EOF and self.pegar_proximo().valor == '='):
            self.statement()
        
        return a
               
    def factor(self):
        """
        factor  ::= <id> | <int> | <symbol> | <op>
        """
        
        if self.token_atual.tipo == T_INT:
            x = int(self.token_atual.valor)
            self.use(T_INT)
        elif self.token_atual.tipo == T_ID:
            x = int(self.token_atual.resultado)
            self.use(T_ID)
        elif self.token_atual.tipo == T_SYMBOL:
            self.use(T_SYMBOL)
            x = self.expr()
            self.proximo()
        elif self.token_atual.tipo == T_OP:
            self.use(T_OP)
        else:
            self.erro()
       
        return x 
          
    def structure_if(self):
        self.use(T_IF)
        self.statement()
        self.use(T_BREAK)
        self.statement()
        self.use(T_ENDIF)
    
    def structure_while(self):
        
        if (self.token_atual.tipo == T_WHILE):
            self.use(T_WHILE)
            if (self.token_atual.tipo == T_ID):
                #valorID = self.token_atual.valor
                self.use(T_ID) #id
                if (self.token_atual.tipo == T_OP and self.token_atual.valor in ['<','>','==','<=','>=']):
                    self.use(T_OP) # = < >
                    x = self.expr() # id ou int
                    #self.setResultado(valorID, x)
                elif (self.token_atual.tipo == T_INT):
                    self.use(T_INT)
                elif (self.token_atual.tipo == T_BREAK):
                    self.use(T_BREAK)
                else:
                    self.erro()
    
    def execute_while(self):
        
        #setar token_atual para o inicio do while
        self.token_atual = self.find_while()
        #checar se expressão do while e true
        if(self.expr_while()):
            self.execute_body_while()
            print("OK")
        else:
            print("Não OK")
        #   execute_body_while()
        #caso expressão true setar token_atual para inicio do while
        
    def execute_body_while(self):
        #valueCont = [token for token in self.tokens if token.valor == 'cont'][0].resultado
        
        receptor = self.token_atual.valor
        
        self.use(T_ID)
        self.use(T_VET)
        index_receptor = self.expr()
        self.use(T_VET)
        self.use(T_OP)
        emissor = self.token_atual.valor
        self.use(T_ID)
        self.use(T_VET)
        index_emissor = self.expr()
        self.use(T_VET)
        
        incremento = self.token_atual
        val_incremento = self.token_atual.resultado
       

        for token in self.tokens:
            if(token.valor == receptor):
                vet_emissor = [token for token in self.tokens if token.valor == emissor][0]
                if(vet_emissor.resultado != None and token.resultado != None):
                    token.resultado.append(vet_emissor.resultado[index_emissor - 1])

        if(self.pegar_proximo().valor  == '++'):
            for token in self.tokens:
                if(token.valor == incremento.valor):
                    token.resultado = val_incremento + 1
            self.use(T_ID)
            self.proximo()

        self.token_atual = self.find_while()
        if(self.expr_while()):
            self.execute_body_while()
        
    def find_while(self):
        count = 0
        for token in self.tokens:
            count = count + 1
            if(token.tipo == T_WHILE):
                self.pos = count - 1
                return token
                
    def body_while(self):
        
        if(self.token_atual.tipo == T_ID):
            self.use(T_ID)
            if(self.token_atual.tipo == T_VET):
                self.use(T_VET)
                x = self.expr()
                if(self.token_atual.tipo == T_VET):
                    self.proximo()
                    if(self.token_atual.tipo == T_OP and self.token_atual.valor == '='):
                        self.use(T_OP)
                        self.body_while()
        
        if(self.token_atual.tipo != T_ENDWHILE and self.token_atual.tipo != T_EOF):
            self.proximo()
            self.body_while()
        elif(self.token_atual.tipo == T_ENDWHILE and self.token_atual.tipo != T_EOF):
            self.use(T_ENDWHILE)
            self.structure_while()
            #self.statement()
                
    def expr_while(self):
        #ler a variavel
        self.use(T_WHILE)
        variavel = self.token_atual.resultado
        #ler o operador
        self.use(T_ID)
        operador = self.token_atual.valor
        #ler o valor
        self.use(T_OP)
        numero = int(self.token_atual.valor)
        self.use(T_INT)
        self.use(T_BREAK)
        #aplicar a devida comparação
        if(operador == '<'):
            return variavel < numero
        elif(operador == '>'):
            return variavel > numero
    
    def structure_vetor(self, variavel):
        
        # vetor = [ 5 , 1 , 2 ]

        #pego a variavel
        token = [token for token in self.tokens if token.valor == variavel][0]
        #inicializo o resultado com um vetor vazio
        token.resultado = []
        self.proximo()
        #enquanto não for o ] para cada item
        while(self.token_atual.valor != ']'):
            if(self.token_atual.valor != ',' and self.token_atual.tipo != T_INT):
                self.erro("Caractere inesperado dentro da declaração do vetor")
            if(self.token_atual.valor == ','): 
                self.use(T_BREAK)
                continue
        #   coloco o item dentro do resultado na variavel
            token.resultado.append(int(self.token_atual.valor))
            self.use(T_INT)
        self.proximo()
        self.statement()            

##############################################################################

arquivo = open('codigo.x','r')
ln = 1

tokens = []

regex = re.compile("[(]")
list_defs = []
for l in arquivo.readlines():
    
    # verifico a quantidade de abertua e fechamento de parenteses
    if(len(re.findall(re.compile("[(]"), l)) == len(re.findall(re.compile("[)]"), l))):
        if(checar_parenteses(l) != True):
            print("Erro de abertura/fechamento de parenteses na linha {}".format(ln))
    else:
        print("Erro de sintaxe quantidade de parenteses não confere Linha: {}".format(ln))
    
    l = l.replace('\n','') # remove a quebra de linha
    count = 0
    LineTokens = l.split()
    for token in LineTokens:
        if(token == ''):
            continue 
        
        try:
            if(len(LineTokens) == 1):
                tokens.append(afd_principal(token, None, list_defs, ln))
            elif(LineTokens[count + 1] != None):
                tokens.append(afd_principal(token, LineTokens[count + 1], list_defs, ln))
                
        except Exception as e:
            if(e.args[0] == 'list index out of range' and token == 'endwhile'):
                tokens.append(afd_principal(token, None, list_defs, ln))
            else:
                print(str(e) + " na posicaoo %i da linha %i" % (l.index(token), ln))
                raise StopExecution
    ln += 1 

    
# print("Tokens Defs: {}".format(list_defs))

# print([str(t) for t in tokens])

# analisador sintatico
parser = Parser(tokens)
parser.statement()

