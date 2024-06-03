# Generated from Mithon.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .MithonParser import MithonParser
else:
    from MithonParser import MithonParser

class DeclarationError(Exception):
    pass

class MithonVisitor(ParseTreeVisitor):

    def __init__(self):
        self.scopes = [{}]
        self.function_declarations = {}
        self.loop_depth = 0
        super().__init__()
        
    def pushScope(self):
        self.scopes.append({})

    def popScope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()

    def addVariable(self, name, type, value, modifier=None):
        self.scopes[-1][name] = (type, value, modifier)

    def lookupVariable(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise Exception(f"Variable {name} not defined")

    def visitProgram(self, ctx:MithonParser.ProgramContext):
        for statement in ctx.statement():
            self.visit(statement)

    def visitStatement(self, ctx:MithonParser.StatementContext):
        if ctx.varDeclaration():
            return self.visitVarDeclaration(ctx.varDeclaration())
        elif ctx.constDeclaration():
            return self.visitConstDeclaration(ctx.constDeclaration())
        elif ctx.printFunction():
            return self.visitPrintFunction(ctx.printFunction())
        elif ctx.ifStatement():
            return self.visitIfStatement(ctx.ifStatement())
        elif ctx.forLoop():
            return self.visitForLoop(ctx.forLoop())
        elif ctx.whileLoop():
            return self.visitWhileLoop(ctx.whileLoop())
        elif ctx.expressionStatement():
            return self.visitExpressionStatement(ctx.expressionStatement())
        elif ctx.functionDeclaration():
            return self.visitFunctionDeclaration(ctx.functionDeclaration())
        elif ctx.returnStatement():
            return self.visitReturnStatement(ctx.returnStatement())
        elif ctx.augAssignment():
            return self.visitAugAssignment(ctx.augAssignment())
        
    def visitAugAssignment(self, ctx: MithonParser.augAssignment):

        left = ctx.getChild(0).getText()
        operator = ctx.getChild(1).getText()
        right_value = self.visitExpression(ctx.getChild(2))

        left_value = self.lookupVariable(left)[1]

        if type(left_value) != type(right_value):
            raise TypeError(f"unsupported operand type(s) for {operator}: {type(left_value).__name__} and {type(right_value).__name__}")

        match operator:
            case "+=":
                self.updateVariable(left, left_value + right_value)
            case "-=":
                self.updateVariable(left, left_value - right_value)
            case "*=":
                self.updateVariable(left, left_value - right_value)
            case "/=":
                if right_value != 0:
                    self.updateVariable(left, left_value - right_value)
                else:
                    raise ZeroDivisionError("division by zero")
            case "%=":
                if right_value != 0:
                    self.updateVariable(left, left_value % right_value)
                else:
                    raise ZeroDivisionError("integer modulo by zero")

    # Visit a parse tree produced by MithonParser#statement_list.
    def visitStatement_list(self, ctx: MithonParser.Statement_listContext):
        return_value = None 
        
        for statement in ctx.statement():
            return_value = self.visit(statement)
            
            if return_value == 'break':
                return 'break'

            if return_value == 'continue':
                return 'continue'

            if return_value is not None:
                return return_value
        
        return return_value


    # Visit a parse tree produced by MithonParser#printFunction.
    def visitPrintFunction(self, ctx:MithonParser.PrintFunctionContext):
        expressions = ctx.expressionList().expression()
        for expr in expressions:
            value = self.visit(expr)
            print(value, end=' ')
        print()

    def prepareVariable(self, ctx):
        
        t = ctx.type_()
        ct = ctx.complexType()
        i = ctx.IDENTIFIER()
        e = ctx.expression()
        
        if t and i and e:
            var_type = t.getText()
            var_name = i.getText()
            expression_result = self.visit(e)
        elif ct and i and e:
            var_type = ct.getText()
            var_name = i.getText()
            expression_result = self.visit(e)

            if not isinstance(expression_result, list):
                raise DeclarationError(f"Invalid {var_type} declaration. Provided value has to be in [values] format.")

        elif i and e and not t:
            
            var_name = i.getText()
            expression_result = self.visit(e)

            if not ct and isinstance(expression_result, list):
                raise DeclarationError(f"ComplexType has to be specified: List[type], Matrix[type], Array[int, type].")

            var_type = type(expression_result).__name__  

        elif (t or ct) and i and not e:
            var_type = t.getText() if t else ct.getText()
            var_name = i.getText()
            expression_result = None 
        else:
            raise DeclarationError("Invalid variable declaration. Must include a type or initialization.")
        
        return var_name, var_type, expression_result

    def visitVarDeclaration(self, ctx:MithonParser.VarDeclarationContext):
    
        var_name, var_type, expression_result = self.prepareVariable(ctx)

        if var_name:
            self.addVariable(var_name, var_type, expression_result)
        else:
            raise DeclarationError("Variable declaration error: Name required")


    # Visit a parse tree produced by MithonParser#constDeclaration.
    def visitConstDeclaration(self, ctx:MithonParser.ConstDeclarationContext):
        
        var_name, var_type, expression_result = self.prepareVariable(ctx.varDeclaration())

        if var_name:
            self.addVariable(var_name, var_type, expression_result, "const")
        else:
            raise DeclarationError("Variable declaration error: Name required")

    def visitForLoop(self, ctx:MithonParser.ForLoopContext):
        self.loop_depth += 1  

        loop_var_name = ctx.IDENTIFIER(0).getText()

        init_expr = ctx.expression(0)
        init_value = self.visit(init_expr)
        self.addVariable(loop_var_name, type(init_value).__name__, init_value, None)

        condition_expr = ctx.expression(1)
        condition = self.visit(condition_expr)
        
        self.pushScope()

        while condition:

            return_value = self.visit(ctx.statement_list())

            if return_value == 'break':
                break

            if return_value == 'continue':
                continue

            if return_value is not None:
                self.popScope()
                self.loop_depth -= 1 
                return return_value

            increment_expr = ctx.expression(2)
            increment_value = self.visit(increment_expr)
            #self.updateVariable(loop_var_name, increment_value)

            condition = self.visit(condition_expr)

        self.popScope()
        self.loop_depth -= 1 

    def visitWhileLoop(self, ctx: MithonParser.WhileLoopContext):
            self.loop_depth += 1
            condition = self.visit(ctx.expression())
            self.pushScope()

            while condition:
                return_value = self.visit(ctx.statement_list())

                if return_value == 'break':
                    break

                if return_value == 'continue':
                    continue

                if return_value is not None:
                    self.popScope()
                    self.loop_depth -= 1
                    return return_value

                condition = self.visit(ctx.expression())

            self.popScope()
            self.loop_depth -= 1
        
    def updateVariable(self, name, value):

        for scope in reversed(self.scopes):
            if name in scope:
                if scope[name][2] == 'const':
                    raise TypeError("Cannot modify const variable.")
                var_type = scope[name][0]  
                modifier = scope[name][-1]
                scope[name] = (var_type, value, modifier) 
                return
            
        raise Exception(f"Variable {name} not defined")

    # Visit a parse tree produced by MithonParser#ifStatement.
    def visitIfStatement(self, ctx:MithonParser.IfStatementContext):
        if_condition = self.visit(ctx.expression(0))
        
        if if_condition:
            self.pushScope()
            return_value = self.visit(ctx.statement_list(0))
            self.popScope()
            if return_value is not None:
                return return_value
        else:
            handled = False
            for i in range(1, len(ctx.expression())):
                expr = ctx.expression(i)
                result = self.visit(expr)
                if result:
                    self.pushScope()
                    return_value = self.visit(ctx.statement_list(i))
                    self.popScope()
                    if return_value is not None: 
                        return return_value
                    handled = True
                    break
            
            if not handled:
                else_index = len(ctx.expression()) 
                else_stmt_list = ctx.statement_list(else_index)
                
                if else_stmt_list is not None:
                    self.pushScope()
                    return_value = self.visit(else_stmt_list)
                    self.popScope()
                    if return_value is not None:
                        return return_value
                    
    # Visit a parse tree produced by MithonParser#functionDeclaration.
    def visitFunctionDeclaration(self, ctx: MithonParser.FunctionDeclarationContext):
        function_name = ctx.IDENTIFIER().getText()
        return_type_ctx = ctx.func_return_type() if ctx.func_return_type() else None
        parameter_list_ctx = ctx.parameterList(0) if ctx.parameterList() else None

        parameter_list = []
        for i in range(len(parameter_list_ctx.IDENTIFIER())):
            parameter_list.append((parameter_list_ctx.type_()[i].getText(), parameter_list_ctx.IDENTIFIER()[i].getText()))

        function_body = ctx.statement_list()

        return_type = return_type_ctx.getText() if return_type_ctx else None

        # Store the function declaration information in the function_declarations dictionary
        self.function_declarations[function_name] = {
            'return_type': return_type,
            'parameters': parameter_list,
            'body': function_body
        }
        
        if return_type != 'None' and not self.doesFunctionReturn(function_body):
            raise Exception(f"Function '{function_name}' must return a value of type {return_type}")

    def doesFunctionReturn(self, ctx):
        for statement in ctx.statement():
            if 'return' in statement.getText():
                return True
        return False

    # Visit a parse tree produced by MithonParser#parameterList.
    def visitParameterList(self, ctx:MithonParser.ParameterListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MithonParser#functionCall.
    def visitFunctionCall(self, ctx: MithonParser.FunctionCallContext):
        function_name = ctx.IDENTIFIER().getText()
        argument_list = ctx.argumentList(0) if ctx.argumentList() else []

        if function_name == 'len':
            if len(argument_list.expression()) != 1:
                raise Exception(f"Function 'len' expects 1 argument, but {len(argument_list.expression())} were provided")
            arg_value = self.visit(argument_list.expression(0))
            return self.handle_len_function(arg_value)

        if function_name in self.function_declarations:
            function_info = self.function_declarations[function_name]
            parameter_list = function_info['parameters']
            function_body = function_info['body']

            if len(argument_list.expression()) != len(parameter_list):
                raise Exception(f"Function '{function_name}' expects {len(parameter_list)} arguments, but {len(argument_list.expression())} were provided")

            argument_list = argument_list.expression()

            self.pushScope()

            for parameter, argument in zip(parameter_list, argument_list):
                arg_value = self.visit(argument)
                if parameter[0] != 'string' and type(arg_value).__name__ != parameter[0]:
                    raise Exception(f"Argument {parameter[1]} expected type: {parameter[0]}. Got: {type(arg_value).__name__} instead.")
                self.addVariable(parameter[1], parameter[0], arg_value)

            return_value = self.visit(function_body)

            self.popScope()

            return return_value
        else:
            raise Exception(f"Function '{function_name}' is not defined")
    
    def handle_len_function(self, arg):
        if isinstance(arg, (str, list)):
            return len(arg)
        else:
            raise Exception(f"Function 'len' is not applicable to type: {type(arg).__name__}")

    def visitReturnStatement(self, ctx: MithonParser.ReturnStatementContext):
        return_value = self.visit(ctx.expression())
        return return_value

    # Visit a parse tree produced by MithonParser#argumentList.
    def visitArgumentList(self, ctx:MithonParser.ArgumentListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MithonParser#expressionList.
    def visitExpressionList(self, ctx:MithonParser.ExpressionListContext):
        return self.visitChildren(ctx)


    def visitExpressionStatement(self, ctx:MithonParser.ExpressionStatementContext):
        expression = ctx.expression()
        # Default behavior for other expression statements
        return self.visit(expression)


    # Visit a parse tree produced by MithonParser#expression.
    def visitExpression(self, ctx:MithonParser.ExpressionContext):
        if ctx.logicalOrExpression():
            return self.visitLogicalOrExpression(ctx.logicalOrExpression())
        else:
            return self.visitAugAssignment(ctx.augAssignment())


    # Visit a parse tree produced by MithonParser#logicalOrExpression.
    def visitLogicalOrExpression(self, ctx:MithonParser.LogicalOrExpressionContext):
        if len(ctx.logicalAndExpression()) > 1:
            result = False
            for expr in ctx.logicalAndExpression():
                result = result or self.visit(expr)
            return result
        else:
            return self.visit(ctx.logicalAndExpression(0))

    # Visit a parse tree produced by MithonParser#logicalAndExpression.
    def visitLogicalAndExpression(self, ctx:MithonParser.LogicalAndExpressionContext):
        if len(ctx.equalityExpression()) > 1:
            result = True
            for expr in ctx.equalityExpression():
                result = result and self.visit(expr)
            return result
        else:
            return self.visit(ctx.equalityExpression(0))

    # Visit a parse tree produced by MithonParser#equalityExpression.
    def visitEqualityExpression(self, ctx:MithonParser.EqualityExpressionContext):
        left = self.visitRelationalExpression(ctx.relationalExpression(0))

        if len(ctx.relationalExpression()) > 1:
            operator = ctx.getChild(1).getText()
            right = self.visitRelationalExpression(ctx.relationalExpression(1))
            if operator == '==':
                return left == right
            elif operator == '!=':
                return left != right
            
        return left


    # Visit a parse tree produced by MithonParser#relationalExpression.
    def visitRelationalExpression(self, ctx:MithonParser.RelationalExpressionContext):
        left = self.visitAdditiveExpression(ctx.additiveExpression(0))

        # jeżeli wyrażenie składa się z więcej niż 1 dziecka, czyli w ogóle mamy operator to wchodzimy dalej
        if ctx.getChildCount() > 1:
            operator = ctx.getChild(1).getText()
            right = self.visitAdditiveExpression(ctx.additiveExpression(1))
            if operator == '<':
                return left < right
            elif operator == '>':
                return left > right
            elif operator == '<=':
                return left <= right
            elif operator == '>=':
                return left >= right
            
        return left

    # Visit a parse tree produced by MithonParser#additiveExpression.
    def visitAdditiveExpression(self, ctx:MithonParser.AdditiveExpressionContext):
        if ctx.getChildCount() == 1:
            return self.visit(ctx.getChild(0))

        right = self.visit(ctx.getChild(2))  
        operator = ctx.getChild(1).getText() 

        if operator in ('+', '-'):
            left_value = self.visit(ctx.getChild(0)) 
            if operator == '+':
                return left_value + right
            elif operator == '-':
                return left_value - right
        else:
            raise Exception("Unsupported operator: " + operator)

    
        
    def is_variable(self, name):
        return any(name in scope for scope in self.scopes)

    def visitMultiplicativeExpression(self, ctx:MithonParser.MultiplicativeExpressionContext):
        left = self.visitUnaryExpression(ctx.unaryExpression(0))
        result = left
        for i in range(1, len(ctx.unaryExpression())):
            operator = ctx.getChild(2*i - 1).getText()
            right = self.visitUnaryExpression(ctx.unaryExpression(i))
            if operator == '*':
                result *= right
            elif operator == '/':
                if right != 0:
                    result /= right
                else:
                    raise ZeroDivisionError
            
        return result

    def visitUnaryExpression(self, ctx:MithonParser.UnaryExpressionContext):
        if ctx.getChildCount() == 1:
            return self.visitPrimaryExpression(ctx.primaryExpression())
        elif ctx.getChild(0).getText() == 'not':
            operand = self.visitPrimaryExpression(ctx.primaryExpression())
            return not operand
        elif ctx.getChild(0).getText() == '-':
            operand = self.visitPrimaryExpression(ctx.primaryExpression())
            return -operand
        return None


    # Visit a parse tree produced by MithonParser#primaryExpression.
    def visitPrimaryExpression(self, ctx:MithonParser.PrimaryExpressionContext):
        if ctx.INTEGER():
            return int(ctx.INTEGER().getText())
        elif ctx.DOUBLE():
            return float(ctx.DOUBLE().getText())
        elif ctx.STRING():
            return ctx.STRING().getText()[1:-1]
        elif ctx.getText() == 'true':
            return True
        elif ctx.getText() == 'false':
            return False
        elif ctx.list_():
            return [self.visitExpression(exp) for exp in ctx.list_().expressionList().expression()]
        elif ctx.listIndexation():
            index = self.visitExpression(ctx.listIndexation().expression())

            values = self.lookupVariable(ctx.listIndexation().IDENTIFIER().getText())[1]

            if not (isinstance(values, list) or isinstance(values, str)):
                raise TypeError("Invalid type for indexation")

            if index > len(values):
                raise IndexError(f"index {index} out of range for length {len(values)}")
            
            return values[index]

        elif ctx.getText() == 'break':
            if self.loop_depth > 0:
                return 'break'
            else:
                raise Exception("'break' is only allowed within a loop")
        elif ctx.getText() == 'continue':
            if self.loop_depth > 0:
                return 'continue'
            else:
                raise Exception("'continue' is only allowed within a loop")
        elif ctx.IDENTIFIER():
            var_name = ctx.IDENTIFIER().getText()
            var_info = self.lookupVariable(var_name)  
            if var_info is not None:
                var_type, var_value, modifier = var_info 
                return var_value
            else:
                raise Exception(f"Variable '{var_name}' is not defined or has no value.")
        elif ctx.expression():
            return self.visit(ctx.expression()) 
        else:
            return self.visitChildren(ctx)


del MithonParser