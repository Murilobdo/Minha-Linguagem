import re

T_SYMBOL = "symbol"
T_KEYWORD = "def"
T_OP = "op"
T_INT = "int"
T_STRING = "string"
T_ID = "id"
T_IF = "if"
T_ENDIF = "endif"
T_ELSE = "else"
T_ENDELSE = "endelse"
T_WHILE = "while"
T_ENDWHILE = "endwhile"
T_BREAK = "break"
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
    
    def __init__(self, tipo, valor=None):
        self.tipo = tipo
        self.valor = valor
        self.resultado = None
                
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
    if token in "()":
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
    if token == ":":
        return True
    return False

def afd_def(token):
    if token == "def":
        return True
    return False
         
def afd_principal(token, NextToken, lista):
    
    if afd_def(token):
        lista.append(NextToken)
        return Token(T_KEYWORD, token)
    
    elif token in "=+*/-<>":
        return Token(T_OP, token)
    
    elif afd_int(token):
        return Token(T_INT, token)
    
    elif afd_string(token):
        return Token(T_STRING, token)
    
    elif afd_identificador(token):
        return Token(T_ID, token)
    
    elif afd_simbolo(token):
        return Token(T_SYMBOL, token)
    
    elif afd_if(token):
        return Token(T_IF, token)
    
    elif afd_while(token):
        return Token(T_WHILE, token)
    
    elif afd_break(token):
        return Token(T_BREAK, token) 
    
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
            self.token_atual = Token(T_EOF)
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
        statement ::= <def> <id> <op => | <id> <op =>
        """
        
        if (self.token_atual.tipo == T_KEYWORD):
            self.use(T_KEYWORD) # def
        if (self.token_atual.tipo == T_ID):
            valorID = self.token_atual.valor
            self.use(T_ID) #id
            if (self.token_atual.tipo == T_OP and self.token_atual.valor in ['=','<','>']):
                self.use(T_OP) # = < >
                x = self.expr() # id ou int
                self.setResultado(valorID, x)
            elif (self.token_atual.tipo == T_INT):
                self.use(T_INT)
            else:
                self.erro()
                
        if(self.token_atual.tipo == T_KEYWORD): 
            self.statement()
        elif(self.token_atual.tipo == T_ID):
            self.use(T_ID) #id
            if(self.token_atual.tipo == T_OP):
                self.proximo()
                x = self.expr() # id ou int
                self.setResultado(valorID, x)
            if(self.token_atual.tipo != T_EOF):
                self.proximo()
        
            
        
    def expr(self):
        """
        expr ::= term ( <op + > | <op - > term ) *
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
        term ::= factor ( <op * > | <op / > factor)*
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

    def parenteses(self):
        
        """
        parenteses  ::= <symbol (> factor
        """ 
        
        while self.token_atual.tipo == T_SYMBOL:
            self.use(T_SYMBOL)
            self.factor()         
        
    def rif(self):
        
        if self.token_atual.tipo == T_WHILE:
            self.use(T_WHILE)
            self.statement()
            self.use(T_BREAK)
            self.statement()
            self.use(T_ENDWHILE)
        else:
            self.erro()
    
    def rwhile(self):
        
        if self.token_atual.tipo == T_WHILE:
            self.use(T_WHILE)
            self.statement()
            self.use(T_BREAK)
            self.statement()
            self.use(T_ENDWHILE)
        else:
            self.erro()
    

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
        try:
            if(LineTokens[count + 1] != None):
                tokens.append(afd_principal(token, LineTokens[count + 1], list_defs))
        except Exception as e:
            print(tokens)
            print(str(e) + " na posição %i da linha %i" % (l.index(token), ln))
            raise StopExecution
    ln += 1 

print([str(t) for t in tokens])
    
print("Tokens Defs: {}".format(list_defs))


# analisador sintatico
parser = Parser(tokens)
parser.statement()
