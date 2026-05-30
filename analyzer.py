import ast
from collections import defaultdict
import subprocess
import json

def analyze_code(source_code):
    """
    Parses the Python source code into an AST and extracts metrics.
    Runs static analysis (flake8) to check for PEP 8 issues.
    """
    results = {
        "metrics": {
            "cyclomatic_complexity": 0,
            "depth_of_nested_blocks": 0,
            "num_functions": 0,
            "num_loops": 0
        },
        "issues": [],
        "suggestions": [],
        "errors": []
    }

    try:
        # Parse into AST
        tree = ast.parse(source_code)
    except SyntaxError as e:
        results["errors"].append({
            "type": "SyntaxError",
            "message": str(e),
            "line": e.lineno,
            "col": e.offset
        })
        return results
    except Exception as e:
        results["errors"].append({
            "type": "Error",
            "message": f"Failed to parse code: {str(e)}"
        })
        return results

    # Extract metrics using an AST Visitor
    visitor = CodeMetricsVisitor()
    visitor.visit(tree)
    
    results["metrics"]["num_functions"] = visitor.num_functions
    results["metrics"]["num_loops"] = visitor.num_loops
    
    # Simple Cyclomatic Complexity estimation
    # formula: num of decision points + 1
    # For a more robust metric, we could use mccabe or radon libraries.
    # Here we count If, For, While, Try, With
    results["metrics"]["cyclomatic_complexity"] = visitor.num_decision_points + 1
    results["metrics"]["depth_of_nested_blocks"] = visitor.max_depth

    # Run Flake8 for style checks
    flake8_issues = run_flake8(source_code)
    results["issues"].extend(flake8_issues)

    return results

class CodeMetricsVisitor(ast.NodeVisitor):
    def __init__(self):
        self.num_functions = 0
        self.num_loops = 0
        self.num_decision_points = 0
        
        self.current_depth = 0
        self.max_depth = 0

    def enter_block(self, node):
        self.current_depth += 1
        if self.current_depth > self.max_depth:
            self.max_depth = self.current_depth
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_FunctionDef(self, node):
        self.num_functions += 1
        self.num_decision_points += 1 # A function is a decision graph component
        self.enter_block(node)

    def visit_AsyncFunctionDef(self, node):
        self.num_functions += 1
        self.num_decision_points += 1
        self.enter_block(node)

    def visit_If(self, node):
        self.num_decision_points += 1
        self.enter_block(node)
        
    def visit_IfExp(self, node):
        self.num_decision_points += 1
        self.enter_block(node)

    def visit_For(self, node):
        self.num_loops += 1
        self.num_decision_points += 1
        self.enter_block(node)
        
    def visit_AsyncFor(self, node):
        self.num_loops += 1
        self.num_decision_points += 1
        self.enter_block(node)

    def visit_While(self, node):
        self.num_loops += 1
        self.num_decision_points += 1
        self.enter_block(node)
        
    def visit_Try(self, node):
        self.num_decision_points += 1 # Count try/except block
        self.enter_block(node)
        
    def visit_With(self, node):
        self.num_decision_points += 1
        self.enter_block(node)

    def visit_AsyncWith(self, node):
        self.num_decision_points += 1
        self.enter_block(node)


def run_flake8(source_code):
    """
    Writes source code to a temporary file, runs flake8, and parses output.
    Returns a list of issue dictionaries.
    """
    import tempfile
    import os
    issues = []
    
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w', encoding='utf-8') as f:
        f.write(source_code)
        temp_file_name = f.name
        
    try:
        import sys
        # Run flake8 as a subprocess
        # Format: %(row)d|%(col)d|%(code)s|%(text)s
        result = subprocess.run(
            [sys.executable, '-m', 'flake8', '--format=%(row)d|%(col)d|%(code)s|%(text)s', temp_file_name],
            capture_output=True, text=True
        )
        
        output = result.stdout.strip()
        if output:
            lines = output.split('\n')
            for line in lines:
                parts = line.split('|', 3)
                if len(parts) == 4:
                    row, col, code, text = parts
                    issues.append({
                        "line": int(row),
                        "column": int(col),
                        "severity": get_severity_from_code(code),
                        "rule_id": code,
                        "message": text
                    })
    except Exception as e:
        print(f"Flake8 execution failed: {e}")
    finally:
        if os.path.exists(temp_file_name):
            os.remove(temp_file_name)
            
    return issues

def get_severity_from_code(code):
    """
    Map flake8 codes to a severity string (error, warning, info)
    E* are usually errors, W* warnings, F* are PyFlakes errors/fatal.
    """
    if code.startswith('E') or code.startswith('F'):
        return 'error'
    elif code.startswith('W'):
        return 'warning'
    elif code.startswith('C'): # mccabe complexity
        return 'warning'
    return 'info'
