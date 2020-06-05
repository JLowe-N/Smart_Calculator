from collections import deque
import re
# from infix_to_postfix import infix_to_postfix
# from postfix_calculator import postfix_calc
# hstest issues occured during import - could not find Module.

class SmartCalculator:

    def __init__(self):
        self.calculator_var = {}
        self.calculator_queue = None  # Will be used as a generator to feed user_input to processor in groups of 3
        self.queue_ready = False
        self.processor = []
        self.running = True
        self.user_string = None
        self.calculator_loop()

    def infix_to_postfix(self, infix_string):
        oper_priority = {'+': 1, '-': 1, '/': 2, '*': 2, '^': 3, '(': 4, ')': 4, }
        #  Need to parse string characters and group based on type
        #  Will just remove spaces, since we can't rely on them being there now
        infix_string = infix_string.replace(' ', '')
        #  Now collapse all the addition/subtraction operators
        while '--' in infix_string:
            infix_string = infix_string.replace('--', '+')
        while '+-' in infix_string:
            infix_string = infix_string.replace('+-', '-')
        while '++' in infix_string:
            infix_string = infix_string.replace('++', '+')
        if '**' in infix_string:
            print("Invalid expression")
            return None
        if '//' in infix_string:
            print("Invalid expression")
            return None
        if '%' in infix_string:
            print("Invalid expression")
            return None
        # Now split the string into operands and operators
        # Found through stack-exchange, need to improve my regex and learn tokenizing
        infix_split = re.findall('[+-/*^//()]|\d+|\w+', infix_string)
        # print(infix_split)
        # Ready to convert to postfix now
        working_stack = deque()
        result = deque()

        if infix_split[0] == '-':  # Fixes first term, if it is a negative number or variable
            if infix_split[1].isnumeric():
                infix_split.insert(0, int(''.join((infix_split.pop(0), infix_split.pop(0)))))
                result.append(infix_split.pop(0))
            else:
                infix_split.insert(0, ''.join((infix_split.pop(0), infix_split.pop(0))))
                result.append(infix_split.pop(0))

        for element in infix_split:
            if element == '(':  # Handles rule 5
                working_stack.append('(')
            elif element == ')':  # Handles rule 6, ')' element is ignored.
                parentheses_loop = True
                while parentheses_loop:
                    if len(working_stack) > 0:
                        if working_stack[-1] != '(':
                            result.append(working_stack.pop())
                        else:
                            working_stack.pop()  # Remove the left parentheses, not appended to result
                            parentheses_loop = False
                    else:  # If we don't find a matching left-parentheses, then we have unbalanced expression
                        print("Invalid expression")
                        return None

            elif element.isalnum():  # Handles rule 1, integers/variables never touch the stack
                if element.isdecimal():
                    result.append(int(element))
                else:
                    result.append(element)
            elif len(working_stack) == 0:
                working_stack.append(element)
            elif len(working_stack) > 0 and working_stack[-1] == '(':  # Handles rule 2
                working_stack.append(element)
            elif oper_priority[element] > oper_priority[working_stack[-1]]:  # Handles rule 3
                working_stack.append(element)
            else:
                low_priority_op_loop = True
                while low_priority_op_loop:  # Handles rule 4
                    if len(working_stack) == 0:
                        working_stack.append(element)
                        low_priority_op_loop = False
                    elif oper_priority[element] <= oper_priority[working_stack[-1]] and working_stack[-1] != '(':
                        result.append(working_stack.pop())
                    else:
                        working_stack.append(element)
                        low_priority_op_loop = False
            # Once infix_split has been iterated through, clear the stack and check for unbalanced parantheses
        for _ in range(len(working_stack)):
            element = working_stack.pop()
            if element == '(' or element == ')':
                print("Invalid expression")
                return None
            else:
                result.append(element)
        return result


    def postfix_calc(self, postfix_deque, var_dict):
        working_stack = deque()
        if not isinstance(postfix_deque[0], int):  # Dealing with negative variable in the first position
            if postfix_deque[0].strip('-').isalpha():
                if postfix_deque[0].startswith('-'):
                    try:
                        working_stack.append(-var_dict[postfix_deque.popleft().lstrip('-')])
                    except KeyError:
                        print("Unknown variable")
                        return None
                else:
                    try:
                        working_stack.append(var_dict[postfix_deque.popleft()])
                    except KeyError:
                        print("Unknown variable")
                        return None

        for element in postfix_deque:
            if isinstance(element, int):
                working_stack.append(element)
            elif element.isalpha():
                try:
                    working_stack.append(var_dict[element])
                except:
                    print("Unknown variable")
                    return None
            else:  # Must be an operator
                if element == '+':
                    b = working_stack.pop()
                    a = working_stack.pop()
                    working_stack.append(a + b)
                elif element == '-':
                    b = working_stack.pop()
                    a = working_stack.pop()
                    working_stack.append(a - b)
                elif element == '*':
                    b = working_stack.pop()
                    a = working_stack.pop()
                    working_stack.append(a * b)
                elif element == '/':
                    b = working_stack.pop()
                    a = working_stack.pop()
                    if b != 0:
                        working_stack.append(a // b)
                    else:
                        print("Division by zero error")
                        break
                elif element == '^':
                    b = working_stack.pop()
                    a = working_stack.pop()
                    working_stack.append(a ** b)
                else:
                    print(f"Unknown operator {element} was supplied.")
        # Expression end, return top of stack
        return working_stack[-1]


    def command_handler(self):
        if self.user_string == '/exit':
            print('Bye!')
            self.running = False
        elif self.user_string == '/help':
            print("A calculator that handles basic functions in PEMDAS order of operations by changing "
                  "from infix to postfix (Reverse Polish Notation) to handle the parsing and calculation."
                  "Latin-characters are allowed for simple integer variable assignments by using '=' in the form"
                  "of 'a = 10'.")
        else:
            print("Unknown command")


    def assignment_handler(self):
        if self.user_string.count('=') > 1:
            print("Invalid assignment")
        parsed_string = [element.strip() for element in self.user_string.split('=')]
        if not parsed_string[0].isalpha():
            print("Invalid identifier")
        elif parsed_string[1].isalpha():
            if parsed_string[1] in self.calculator_var.keys():
                self.calculator_var[parsed_string[0]] = self.calculator_var[parsed_string[1]]
            else:
                print("Unknown variable")
        elif not parsed_string[1].lstrip('-').isnumeric():
            print("Invalid assignment")
        else:
            self.calculator_var[parsed_string[0]] = int(parsed_string[1])

    def gather_input(self):
        #print("asking for input")
        self.user_string = input()
        #print(f"received: {self.user_string}")
        if self.user_string == "":
            pass
        elif self.user_string.startswith('/'):
            self.command_handler()
        elif "=" in self.user_string:
            self.assignment_handler()
        else:
            self.queue_ready = True
            #print(f"input gathered, queue status is {self.queue_ready}")


    def calculator_loop(self):
        while self.running == True:
            #print("Loop has started")
            self.gather_input()
            if self.queue_ready:
                infix_expression = self.user_string
                postfix_expression = self.infix_to_postfix(infix_expression)
                if postfix_expression:
                    result = self.postfix_calc(postfix_expression, self.calculator_var)
                    if result:
                        print(result)
                self.queue_ready = False  # reset until new queue created

if __name__ == "__main__":
    SmartCalculator()

#SmartCalculator()

