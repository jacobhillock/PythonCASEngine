import re

class Engine:
    def __init__ (self, func_):
        self.func = func_
        self.pre_process()
    
    def pre_process (self):
        # regular expressions
        var_regex = re.compile(r'[a-zA-Z]\w*')
        wht_regex = re.compile(r'\s+')
        clc_regex = re.compile(r'[\[\]\(\)\/\*\+\-\^]')

        # remove whitespaces and define variables
        self.func = wht_regex.subn("", self.func)[0]
        self.vars = set(var_regex.findall(self.func))

        # listify the function
        t_func = self.func
        self.l_func = []
        while (match := clc_regex.search(t_func)) is not None:
            span = match.span()
            if span[0] == 0:
                self.l_func.append(t_func[0:span[1]])
            else:
                self.l_func.append(t_func[0:span[0]])
                self.l_func.append(t_func[span[0]:span[1]])
            t_func = t_func[span[1]:]
        self.l_func.append(t_func)

        # convert numbers to floats for calculation
        for i in range(len(self.l_func)):
            try:
                self.l_func[i] = float(self.l_func[i])
            except Exception:
                pass
    
    def eval (self, **vars):
        # make a hard copy of the list function
        expr = [i for i in self.l_func]
        vars_copy = [i for i in self.vars]
        # replace variables with numbers
        for var in vars:
            for i in range(len(expr)):
                if expr[i] == var:
                    expr[i] = vars[var]
            if var in vars_copy:
                vars_copy.remove(var)
        
        if len(vars_copy) > 0:
            raise Exception(f'Error: Not all variables have been evaluated. Including: {vars_copy}')
        
        # pre setup for parenthesis handling
        list_  = []
        list_i = []
        run = True
        i = 0

        # evaluate the expresion
        while run:
            if i >= len(expr):
                run = False

            # add bracket to search for at end of the list
            elif expr[i] == '[':
                list_.append(']')
                list_i.append(i)
            elif expr[i] == '(':
                list_.append(')')
                list_i.append(i)
            
            # found closing bracket and now to evaluate
            elif expr[i] in [']', ')']:
                # closing bracket matchs
                if expr[i] == list_[len(list_)-1]:
                    pair = [list_i.pop(len(list_)-1), i]
                    val = self.__compute(expr[pair[0]+1:pair[1]])
                    # remove evaluated section and move iterator back 
                    expr = expr[:pair[0]] + val + expr[pair[1]+1:]
                    list_.pop(len(list_)-1)
                    i -= (pair[1] - pair[0])
                else:
                    raise Exception('Error: Invalid paranthesis pairing detected')
            
            i+= 1
        
        final = self.__compute(expr)
        return final[0]

    
    def __compute (self, expr):
        # symboles and a matching function to evaluate them
        symbs = {
            '^': lambda a, b: a**b,
            '*': lambda a, b: a*b,
            '+': lambda a, b: a+b,
        }

        if len(expr) > 1:
            # turn devision and subtraction into their positive counterparts
            for i in range(len(expr)):
                if expr[i] == '-':
                    expr[i] = '+'
                    expr[i+1] *= -1
                elif expr[i] == '/':
                    expr[i] = '*'
                    expr[i+1] = 1 / expr[i+1]
            
            # evaluate expressions
            for symb in symbs.keys():
                for i in reversed(range(len(expr))):
                    if expr[i] == symb:
                        try:
                            val = symbs[symb](expr[i-1], expr[i+1])
                        except Exception:
                            raise Exception('Error: invalid placement of mathematical opperator detected')
                        expr = expr[:i-1] + [val] + expr[i+2:]
        return expr

    

if __name__ == '__main__':
    engine = Engine('(x+z)^2 - (x+z) - 2')
    min_ = -4
    max_ = 4
    dencity = 10
    for i in range (min_*dencity, max_*dencity+1):
        x = i/dencity
        print(f'x={x}: y={engine.eval(x=x, z=1)}')
