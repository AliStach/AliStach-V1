"""Repository analyzer for code quality and modernization analysis."""

import ast
import hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import re


@dataclass
class AnalysisResult:
    """Results from repository analysis."""
    dead_code: List[str] = field(default_factory=list)
    unused_imports: Dict[str, List[str]] = field(default_factory=dict)
    duplicated_logic: List[Tuple[str, str, int]] = field(default_factory=list)
    missing_types: List[str] = field(default_factory=list)
    type_coverage: Dict[str, float] = field(default_factory=dict)
    deprecated_patterns: List[str] = field(default_factory=list)
    circular_dependencies: List[Tuple[str, str]] = field(default_factory=list)
    naming_violations: List[str] = field(default_factory=list)
    architectural_violations: List[str] = field(default_factory=list)


class RepositoryAnalyzer:
    """Analyze repository for optimization opportunities."""
    
    def __init__(self, root_path: Path):
        self.root_path = Path(root_path)
        self.python_files: List[Path] = []
        self.analysis_result = AnalysisResult()
        self.all_definitions: Dict[str, Set[str]] = defaultdict(set)
        self.all_references: Dict[str, Set[str]] = defaultdict(set)
        self.imports_by_file: Dict[str, Set[str]] = defaultdict(set)
        self.module_dependencies: Dict[str, Set[str]] = defaultdict(set)
    
    def analyze(self) -> AnalysisResult:
        """Run complete repository analysis."""
        print("🔍 Starting repository analysis...")
        
        self._scan_python_files()
        print(f"   Found {len(self.python_files)} Python files")
        
        self._build_symbol_tables()
        
        print("   Detecting dead code...")
        self._detect_dead_code()
        
        print("   Detecting unused imports...")
        self._detect_unused_imports()
        
        print("   Detecting code duplication...")
        self._detect_duplicated_logic()
        
        print("   Checking type coverage...")
        self._check_type_coverage()
        
        print("   Detecting deprecated patterns...")
        self._detect_deprecated_patterns()
        
        print("   Analyzing architectural patterns...")
        self._detect_circular_dependencies()
        self._check_naming_conventions()
        self._check_architectural_patterns()
        
        print("✅ Analysis complete!")
        return self.analysis_result
    
    def _scan_python_files(self):
        """Scan for all Python files."""
        exclude_dirs = {'__pycache__', '.git', '.venv', 'venv', 'env', 'node_modules', '.pytest_cache'}
        
        for py_file in self.root_path.rglob("*.py"):
            if not any(excluded in py_file.parts for excluded in exclude_dirs):
                self.python_files.append(py_file)
    
    def _build_symbol_tables(self):
        """Build symbol tables for all files."""
        for file_path in self.python_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                tree = ast.parse(content, filename=str(file_path))
                
                # Collect definitions
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        self.all_definitions[str(file_path)].add(node.name)
                
                # Collect references
                for node in ast.walk(tree):
                    if isinstance(node, ast.Name):
                        self.all_references[str(file_path)].add(node.id)
                
                # Collect imports
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            name = alias.asname if alias.asname else alias.name
                            self.imports_by_file[str(file_path)].add(name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            for alias in node.names:
                                name = alias.asname if alias.asname else alias.name
                                self.imports_by_file[str(file_path)].add(name)
                                # Track module dependencies
                                self.module_dependencies[str(file_path)].add(node.module)
            
            except Exception as e:
                print(f"   Warning: Could not parse {file_path}: {e}")
    
    def _detect_dead_code(self):
        """Identify unused functions and classes."""
        for file_path, definitions in self.all_definitions.items():
            for definition in definitions:
                # Check if definition is referenced anywhere
                is_referenced = False
                
                # Check in all files
                for ref_file, references in self.all_references.items():
                    if ref_file != file_path and definition in references:
                        is_referenced = True
                        break
                
                # Check if it's a special method or main
                if definition.startswith('_') and not definition.startswith('__'):
                    continue  # Private methods might be intentionally unused
                if definition in ['main', '__init__', '__main__']:
                    continue
                
                if not is_referenced:
                    rel_path = Path(file_path).relative_to(self.root_path)
                    self.analysis_result.dead_code.append(
                        f"{rel_path}::{definition} - Unused function/class"
                    )
    
    def _detect_unused_imports(self):
        """Find unused imports in each file."""
        for file_path in self.python_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                tree = ast.parse(content, filename=str(file_path))
                
                imported_names = set()
                used_names = set()
                
                # Collect all imported names
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            name = alias.asname if alias.asname else alias.name.split('.')[0]
                            imported_names.add(name)
                    elif isinstance(node, ast.ImportFrom):
                        for alias in node.names:
                            if alias.name != '*':
                                name = alias.asname if alias.asname else alias.name
                                imported_names.add(name)
                
                # Collect all used names (excluding imports themselves)
                class NameCollector(ast.NodeVisitor):
                    def __init__(self):
                        self.names = set()
                        self.in_import = False
                    
                    def visit_Import(self, node):
                        pass  # Skip import statements
                    
                    def visit_ImportFrom(self, node):
                        pass  # Skip import statements
                    
                    def visit_Name(self, node):
                        self.names.add(node.id)
                        self.generic_visit(node)
                    
                    def visit_Attribute(self, node):
                        if isinstance(node.value, ast.Name):
                            self.names.add(node.value.id)
                        self.generic_visit(node)
                
                collector = NameCollector()
                collector.visit(tree)
                used_names = collector.names
                
                # Find unused imports
                unused = imported_names - used_names
                
                if unused:
                    rel_path = str(Path(file_path).relative_to(self.root_path))
                    self.analysis_result.unused_imports[rel_path] = sorted(list(unused))
            
            except Exception as e:
                print(f"   Warning: Could not analyze imports in {file_path}: {e}")
    
    def _detect_duplicated_logic(self):
        """Find duplicated code blocks with similarity analysis."""
        # Store code blocks with their metadata
        code_blocks: List[Tuple[str, str, int, str, int]] = []  # (normalized_code, file, line, name, length)
        
        for file_path in self.python_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                tree = ast.parse(content, filename=str(file_path))
                rel_path = str(Path(file_path).relative_to(self.root_path))
                
                # Analyze functions and methods for duplication
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Skip very small functions (likely not worth consolidating)
                        if len(node.body) < 3:
                            continue
                        
                        # Get function body as normalized string
                        func_code = self._normalize_code_block(node)
                        
                        # Only consider functions with substantial code
                        if len(func_code) > 150:
                            code_blocks.append((
                                func_code,
                                rel_path,
                                node.lineno,
                                node.name,
                                len(func_code)
                            ))
                
            except Exception as e:
                print(f"   Warning: Could not analyze duplication in {file_path}: {e}")
        
        # Find similar code blocks using multiple strategies
        self._find_exact_duplicates(code_blocks)
        self._find_similar_code(code_blocks)
    
    def _normalize_code_block(self, node: ast.AST) -> str:
        """Normalize code block for comparison."""
        try:
            # Use ast.unparse if available (Python 3.9+)
            if hasattr(ast, 'unparse'):
                code = ast.unparse(node)
            else:
                # Fallback to ast.dump for older Python versions
                code = ast.dump(node)
            
            # Normalize: remove extra whitespace, standardize formatting
            normalized = re.sub(r'\s+', ' ', code)
            # Remove variable names to detect structural similarity
            # This helps find code that does the same thing with different names
            normalized = re.sub(r'\b[a-z_][a-z0-9_]*\b', 'VAR', normalized)
            normalized = re.sub(r'\b[A-Z][a-zA-Z0-9]*\b', 'CLASS', normalized)
            
            return normalized.strip()
        except Exception:
            return ""
    
    def _find_exact_duplicates(self, code_blocks: List[Tuple[str, str, int, str, int]]):
        """Find exact duplicate code blocks."""
        code_hashes: Dict[str, List[Tuple[str, int, str]]] = defaultdict(list)
        
        for normalized_code, file_path, line_no, name, length in code_blocks:
            # Create hash of normalized code
            code_hash = hashlib.md5(normalized_code.encode()).hexdigest()
            code_hashes[code_hash].append((file_path, line_no, name))
        
        # Report exact duplicates
        for code_hash, locations in code_hashes.items():
            if len(locations) > 1:
                # Report all pairs of duplicates
                for i in range(len(locations)):
                    for j in range(i + 1, len(locations)):
                        loc1 = locations[i]
                        loc2 = locations[j]
                        
                        # Skip if same file (might be intentional overloading)
                        if loc1[0] == loc2[0]:
                            continue
                        
                        self.analysis_result.duplicated_logic.append((
                            f"{loc1[0]}:L{loc1[1]}::{loc1[2]}",
                            f"{loc2[0]}:L{loc2[1]}::{loc2[2]}",
                            100  # 100% similarity (exact match)
                        ))
    
    def _find_similar_code(self, code_blocks: List[Tuple[str, str, int, str, int]]):
        """Find similar (but not identical) code blocks."""
        # Compare code blocks pairwise for similarity
        for i in range(len(code_blocks)):
            for j in range(i + 1, len(code_blocks)):
                code1, file1, line1, name1, len1 = code_blocks[i]
                code2, file2, line2, name2, len2 = code_blocks[j]
                
                # Skip if same file
                if file1 == file2:
                    continue
                
                # Skip if already found as exact duplicate
                if code1 == code2:
                    continue
                
                # Calculate similarity
                similarity = self._calculate_similarity(code1, code2)
                
                # Report if similarity is high (70-99%)
                if 70 <= similarity < 100:
                    self.analysis_result.duplicated_logic.append((
                        f"{file1}:L{line1}::{name1}",
                        f"{file2}:L{line2}::{name2}",
                        similarity
                    ))
    
    def _calculate_similarity(self, code1: str, code2: str) -> int:
        """Calculate similarity percentage between two code blocks."""
        # Use a simple token-based similarity metric
        tokens1 = set(code1.split())
        tokens2 = set(code2.split())
        
        if not tokens1 or not tokens2:
            return 0
        
        # Jaccard similarity
        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)
        
        if union == 0:
            return 0
        
        similarity = (intersection / union) * 100
        return int(similarity)
    
    def _check_type_coverage(self):
        """Check for missing type annotations."""
        for file_path in self.python_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                tree = ast.parse(content, filename=str(file_path))
                
                total_functions = 0
                typed_functions = 0
                total_args = 0
                typed_args = 0
                total_class_attrs = 0
                typed_class_attrs = 0
                
                # Track classes for attribute analysis
                for node in ast.walk(tree):
                    # Check function signatures and return types
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Skip special methods
                        if node.name.startswith('__') and node.name.endswith('__'):
                            continue
                        
                        total_functions += 1
                        
                        # Check return type
                        if node.returns:
                            typed_functions += 1
                        else:
                            rel_path = Path(file_path).relative_to(self.root_path)
                            self.analysis_result.missing_types.append(
                                f"{rel_path}:L{node.lineno}::{node.name} - Missing return type"
                            )
                        
                        # Check argument types
                        for arg in node.args.args:
                            if arg.arg != 'self' and arg.arg != 'cls':
                                total_args += 1
                                if arg.annotation:
                                    typed_args += 1
                                else:
                                    rel_path = Path(file_path).relative_to(self.root_path)
                                    self.analysis_result.missing_types.append(
                                        f"{rel_path}:L{node.lineno}::{node.name}({arg.arg}) - Missing argument type"
                                    )
                    
                    # Check class attributes
                    elif isinstance(node, ast.ClassDef):
                        # Check class-level attributes (AnnAssign nodes)
                        for item in node.body:
                            if isinstance(item, ast.AnnAssign):
                                # This is a typed class attribute
                                total_class_attrs += 1
                                typed_class_attrs += 1
                            elif isinstance(item, ast.Assign):
                                # This is an untyped class attribute
                                for target in item.targets:
                                    if isinstance(target, ast.Name):
                                        # Skip private/dunder attributes
                                        if not target.id.startswith('_'):
                                            total_class_attrs += 1
                                            rel_path = Path(file_path).relative_to(self.root_path)
                                            self.analysis_result.missing_types.append(
                                                f"{rel_path}:L{item.lineno}::{node.name}.{target.id} - Missing class attribute type"
                                            )
                            elif isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                # Check __init__ for instance attributes
                                if item.name == '__init__':
                                    for stmt in ast.walk(item):
                                        if isinstance(stmt, ast.Assign):
                                            for target in stmt.targets:
                                                # Check for self.attribute assignments
                                                if isinstance(target, ast.Attribute):
                                                    if isinstance(target.value, ast.Name) and target.value.id == 'self':
                                                        # Skip private attributes
                                                        if not target.attr.startswith('_'):
                                                            total_class_attrs += 1
                                                            rel_path = Path(file_path).relative_to(self.root_path)
                                                            self.analysis_result.missing_types.append(
                                                                f"{rel_path}:L{stmt.lineno}::{node.name}.{target.attr} - Missing instance attribute type"
                                                            )
                                        elif isinstance(stmt, ast.AnnAssign):
                                            # Typed instance attribute
                                            if isinstance(stmt.target, ast.Attribute):
                                                if isinstance(stmt.target.value, ast.Name) and stmt.target.value.id == 'self':
                                                    total_class_attrs += 1
                                                    typed_class_attrs += 1
                
                # Calculate coverage for this file
                total_items = total_functions + total_class_attrs
                typed_items = typed_functions + typed_class_attrs
                
                if total_items > 0:
                    coverage = (typed_items / total_items) * 100
                    rel_path = str(Path(file_path).relative_to(self.root_path))
                    self.analysis_result.type_coverage[rel_path] = round(coverage, 2)
            
            except Exception as e:
                print(f"   Warning: Could not analyze types in {file_path}: {e}")
    
    def _detect_deprecated_patterns(self):
        """Identify deprecated patterns and outdated code."""
        deprecated_patterns = [
            (r'%\s*\(', 'Old-style string formatting (use f-strings)'),
            (r'\.format\(', 'str.format() (consider f-strings)'),
            (r'except\s*:', 'Bare except clause (specify exception type)'),
            (r'from\s+typing\s+import\s+.*\bDict\b', 'typing.Dict (use dict in Python 3.9+)'),
            (r'from\s+typing\s+import\s+.*\bList\b', 'typing.List (use list in Python 3.9+)'),
            (r'from\s+typing\s+import\s+.*\bTuple\b', 'typing.Tuple (use tuple in Python 3.9+)'),
        ]
        
        for file_path in self.python_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    for pattern, description in deprecated_patterns:
                        if re.search(pattern, line):
                            rel_path = Path(file_path).relative_to(self.root_path)
                            self.analysis_result.deprecated_patterns.append(
                                f"{rel_path}:L{line_num} - {description}"
                            )
            
            except Exception as e:
                print(f"   Warning: Could not analyze patterns in {file_path}: {e}")
    
    def _detect_circular_dependencies(self):
        """Detect circular dependencies between modules."""
        def find_cycles(graph: Dict[str, Set[str]]) -> List[Tuple[str, str]]:
            cycles = []
            visited = set()
            rec_stack = set()
            
            def dfs(node: str, path: List[str]):
                visited.add(node)
                rec_stack.add(node)
                path.append(node)
                
                for neighbor in graph.get(node, set()):
                    if neighbor not in visited:
                        dfs(neighbor, path.copy())
                    elif neighbor in rec_stack:
                        # Found a cycle
                        cycle_start = path.index(neighbor)
                        cycle = path[cycle_start:]
                        if len(cycle) >= 2:
                            cycles.append((cycle[0], cycle[-1]))
                
                rec_stack.remove(node)
            
            for node in graph:
                if node not in visited:
                    dfs(node, [])
            
            return cycles
        
        cycles = find_cycles(self.module_dependencies)
        for cycle in cycles:
            self.analysis_result.circular_dependencies.append(cycle)
    
    def _check_naming_conventions(self):
        """Check naming convention consistency."""
        for file_path in self.python_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                tree = ast.parse(content, filename=str(file_path))
                
                for node in ast.walk(tree):
                    rel_path = Path(file_path).relative_to(self.root_path)
                    
                    # Check function names (should be snake_case)
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Skip dunder methods and AST visitor methods (visit_*)
                        if not node.name.startswith('__') and not node.name.startswith('visit_'):
                            if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                                self.analysis_result.naming_violations.append(
                                    f"{rel_path}:L{node.lineno}::function '{node.name}' - Should use snake_case"
                                )
                    
                    # Check class names (should be PascalCase)
                    elif isinstance(node, ast.ClassDef):
                        if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                            self.analysis_result.naming_violations.append(
                                f"{rel_path}:L{node.lineno}::class '{node.name}' - Should use PascalCase"
                            )
            
            except Exception as e:
                print(f"   Warning: Could not check naming in {file_path}: {e}")
    
    def _check_architectural_patterns(self):
        """Identify architectural violations."""
        # Check for proper separation of concerns
        for file_path in self.python_files:
            rel_path = Path(file_path).relative_to(self.root_path)
            parts = rel_path.parts
            
            # Check if API endpoints import from other API endpoints
            if 'api' in parts and 'endpoints' in parts:
                try:
                    content = file_path.read_text(encoding='utf-8')
                    tree = ast.parse(content, filename=str(file_path))
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ImportFrom):
                            if node.module and 'api.endpoints' in node.module:
                                self.analysis_result.architectural_violations.append(
                                    f"{rel_path}:L{node.lineno} - API endpoint importing from another endpoint"
                                )
                
                except Exception as e:
                    print(f"   Warning: Could not check architecture in {file_path}: {e}")
    
    def generate_report(self, output_path: Optional[Path] = None) -> str:
        """Generate comprehensive analysis report."""
        if output_path is None:
            output_path = self.root_path / "docs" / "analysis" / "repository-audit-report.md"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report_lines = [
            "# Repository Analysis Report",
            "",
            f"**Generated**: {self._get_timestamp()}",
            f"**Repository**: {self.root_path.name}",
            f"**Files Analyzed**: {len(self.python_files)}",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            self._generate_summary(),
            "",
            "---",
            "",
            "## 1. Dead Code Detection",
            "",
            self._format_dead_code_section(),
            "",
            "## 2. Unused Imports",
            "",
            self._format_unused_imports_section(),
            "",
            "## 3. Code Duplication",
            "",
            self._format_duplication_section(),
            "",
            "## 4. Type Coverage Analysis",
            "",
            self._format_type_coverage_section(),
            "",
            "## 5. Deprecated Patterns",
            "",
            self._format_deprecated_patterns_section(),
            "",
            "## 6. Architectural Analysis",
            "",
            self._format_architectural_section(),
            "",
            "---",
            "",
            "## Recommendations",
            "",
            self._generate_recommendations(),
            "",
            "---",
            "",
            "## Next Steps",
            "",
            "1. Review this report with the development team",
            "2. Prioritize issues by severity and impact",
            "3. Create tasks for addressing high-priority issues",
            "4. Run analysis again after fixes to track progress",
            "",
        ]
        
        report_content = "\n".join(report_lines)
        output_path.write_text(report_content, encoding='utf-8')
        
        print(f"\n📄 Report saved to: {output_path}")
        return report_content
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _generate_summary(self) -> str:
        """Generate executive summary."""
        total_issues = (
            len(self.analysis_result.dead_code) +
            sum(len(imports) for imports in self.analysis_result.unused_imports.values()) +
            len(self.analysis_result.duplicated_logic) +
            len(self.analysis_result.missing_types) +
            len(self.analysis_result.deprecated_patterns) +
            len(self.analysis_result.circular_dependencies) +
            len(self.analysis_result.naming_violations) +
            len(self.analysis_result.architectural_violations)
        )
        
        avg_type_coverage = 0
        if self.analysis_result.type_coverage:
            avg_type_coverage = sum(self.analysis_result.type_coverage.values()) / len(self.analysis_result.type_coverage)
        
        return f"""
| Metric | Count |
|--------|-------|
| Total Issues Found | {total_issues} |
| Dead Code Items | {len(self.analysis_result.dead_code)} |
| Files with Unused Imports | {len(self.analysis_result.unused_imports)} |
| Duplicated Code Blocks | {len(self.analysis_result.duplicated_logic)} |
| Missing Type Annotations | {len(self.analysis_result.missing_types)} |
| Deprecated Patterns | {len(self.analysis_result.deprecated_patterns)} |
| Circular Dependencies | {len(self.analysis_result.circular_dependencies)} |
| Naming Violations | {len(self.analysis_result.naming_violations)} |
| Architectural Violations | {len(self.analysis_result.architectural_violations)} |
| Average Type Coverage | {avg_type_coverage:.1f}% |

**Overall Health**: {'🟢 Good' if total_issues < 50 else '🟡 Needs Improvement' if total_issues < 150 else '🔴 Critical'}
"""
    
    def _format_dead_code_section(self) -> str:
        """Format dead code section."""
        if not self.analysis_result.dead_code:
            return "✅ No dead code detected.\n"
        
        lines = [f"Found **{len(self.analysis_result.dead_code)}** potentially unused definitions:\n"]
        for item in self.analysis_result.dead_code[:20]:  # Limit to first 20
            lines.append(f"- `{item}`")
        
        if len(self.analysis_result.dead_code) > 20:
            lines.append(f"\n*...and {len(self.analysis_result.dead_code) - 20} more*")
        
        return "\n".join(lines)
    
    def _format_unused_imports_section(self) -> str:
        """Format unused imports section."""
        if not self.analysis_result.unused_imports:
            return "✅ No unused imports detected.\n"
        
        lines = [f"Found unused imports in **{len(self.analysis_result.unused_imports)}** files:\n"]
        
        for file_path, imports in list(self.analysis_result.unused_imports.items())[:10]:
            lines.append(f"\n**{file_path}**:")
            for imp in imports:
                lines.append(f"  - `{imp}`")
        
        if len(self.analysis_result.unused_imports) > 10:
            lines.append(f"\n*...and {len(self.analysis_result.unused_imports) - 10} more files*")
        
        return "\n".join(lines)
    
    def _format_duplication_section(self) -> str:
        """Format code duplication section."""
        if not self.analysis_result.duplicated_logic:
            return "✅ No significant code duplication detected.\n"
        
        # Separate exact duplicates from similar code
        exact_duplicates = [(l1, l2, s) for l1, l2, s in self.analysis_result.duplicated_logic if s == 100]
        similar_code = [(l1, l2, s) for l1, l2, s in self.analysis_result.duplicated_logic if s < 100]
        
        lines = [f"Found **{len(self.analysis_result.duplicated_logic)}** duplicated/similar code blocks:\n"]
        
        if exact_duplicates:
            lines.append(f"\n### Exact Duplicates ({len(exact_duplicates)})\n")
            lines.append("These code blocks are identical and should be consolidated into shared functions:\n")
            
            for loc1, loc2, similarity in exact_duplicates[:8]:
                lines.append(f"\n- **100% identical**:")
                lines.append(f"  - `{loc1}`")
                lines.append(f"  - `{loc2}`")
                lines.append(f"  - **Suggestion**: Extract to shared utility function")
            
            if len(exact_duplicates) > 8:
                lines.append(f"\n*...and {len(exact_duplicates) - 8} more exact duplicates*")
        
        if similar_code:
            lines.append(f"\n### Similar Code ({len(similar_code)})\n")
            lines.append("These code blocks are similar and may benefit from consolidation:\n")
            
            # Sort by similarity (highest first)
            similar_code.sort(key=lambda x: x[2], reverse=True)
            
            for loc1, loc2, similarity in similar_code[:8]:
                lines.append(f"\n- **{similarity}% similar**:")
                lines.append(f"  - `{loc1}`")
                lines.append(f"  - `{loc2}`")
                if similarity >= 85:
                    lines.append(f"  - **Suggestion**: High similarity - consider extracting common logic")
                else:
                    lines.append(f"  - **Suggestion**: Review for potential refactoring opportunities")
            
            if len(similar_code) > 8:
                lines.append(f"\n*...and {len(similar_code) - 8} more similar blocks*")
        
        lines.append("\n### Consolidation Benefits\n")
        lines.append("- Reduced code maintenance burden")
        lines.append("- Improved consistency across codebase")
        lines.append("- Easier bug fixes (fix once, apply everywhere)")
        lines.append("- Better testability with shared functions")
        
        return "\n".join(lines)
    
    def _format_type_coverage_section(self) -> str:
        """Format type coverage section."""
        if not self.analysis_result.type_coverage:
            return "⚠️ No type coverage data available.\n"
        
        lines = ["### Coverage by File\n"]
        
        sorted_coverage = sorted(
            self.analysis_result.type_coverage.items(),
            key=lambda x: x[1]
        )
        
        for file_path, coverage in sorted_coverage[:15]:
            emoji = "🟢" if coverage >= 80 else "🟡" if coverage >= 50 else "🔴"
            lines.append(f"- {emoji} `{file_path}`: {coverage}%")
        
        if len(sorted_coverage) > 15:
            lines.append(f"\n*...and {len(sorted_coverage) - 15} more files*")
        
        lines.append(f"\n### Missing Type Annotations\n")
        lines.append(f"Found **{len(self.analysis_result.missing_types)}** missing type annotations.\n")
        
        for item in self.analysis_result.missing_types[:15]:
            lines.append(f"- `{item}`")
        
        if len(self.analysis_result.missing_types) > 15:
            lines.append(f"\n*...and {len(self.analysis_result.missing_types) - 15} more*")
        
        return "\n".join(lines)
    
    def _format_deprecated_patterns_section(self) -> str:
        """Format deprecated patterns section."""
        if not self.analysis_result.deprecated_patterns:
            return "✅ No deprecated patterns detected.\n"
        
        lines = [f"Found **{len(self.analysis_result.deprecated_patterns)}** deprecated patterns:\n"]
        
        for item in self.analysis_result.deprecated_patterns[:20]:
            lines.append(f"- `{item}`")
        
        if len(self.analysis_result.deprecated_patterns) > 20:
            lines.append(f"\n*...and {len(self.analysis_result.deprecated_patterns) - 20} more*")
        
        return "\n".join(lines)
    
    def _format_architectural_section(self) -> str:
        """Format architectural analysis section."""
        lines = []
        
        # Circular dependencies
        lines.append("### Circular Dependencies\n")
        if not self.analysis_result.circular_dependencies:
            lines.append("✅ No circular dependencies detected.\n")
        else:
            lines.append(f"Found **{len(self.analysis_result.circular_dependencies)}** circular dependencies:\n")
            for mod1, mod2 in self.analysis_result.circular_dependencies[:10]:
                lines.append(f"- `{mod1}` ↔️ `{mod2}`")
        
        # Naming violations
        lines.append("\n### Naming Convention Violations\n")
        if not self.analysis_result.naming_violations:
            lines.append("✅ No naming violations detected.\n")
        else:
            lines.append(f"Found **{len(self.analysis_result.naming_violations)}** naming violations:\n")
            for item in self.analysis_result.naming_violations[:15]:
                lines.append(f"- `{item}`")
            if len(self.analysis_result.naming_violations) > 15:
                lines.append(f"\n*...and {len(self.analysis_result.naming_violations) - 15} more*")
        
        # Architectural violations
        lines.append("\n### Architectural Violations\n")
        if not self.analysis_result.architectural_violations:
            lines.append("✅ No architectural violations detected.\n")
        else:
            lines.append(f"Found **{len(self.analysis_result.architectural_violations)}** architectural violations:\n")
            for item in self.analysis_result.architectural_violations[:10]:
                lines.append(f"- `{item}`")
        
        return "\n".join(lines)
    
    def _generate_recommendations(self) -> str:
        """Generate actionable recommendations."""
        recommendations = []
        
        if self.analysis_result.dead_code:
            recommendations.append(
                "1. **Remove Dead Code**: Review and safely remove unused functions and classes to reduce codebase size."
            )
        
        if self.analysis_result.unused_imports:
            recommendations.append(
                "2. **Clean Up Imports**: Use tools like `autoflake` or `ruff` to automatically remove unused imports."
            )
        
        if self.analysis_result.duplicated_logic:
            recommendations.append(
                "3. **Consolidate Duplicated Code**: Extract common logic into shared utility functions."
            )
        
        if self.analysis_result.missing_types:
            avg_coverage = sum(self.analysis_result.type_coverage.values()) / len(self.analysis_result.type_coverage) if self.analysis_result.type_coverage else 0
            if avg_coverage < 80:
                recommendations.append(
                    f"4. **Improve Type Coverage**: Current average is {avg_coverage:.1f}%. Add type annotations to reach 100%."
                )
        
        if self.analysis_result.deprecated_patterns:
            recommendations.append(
                "5. **Modernize Code**: Replace deprecated patterns with modern Python equivalents (f-strings, built-in types)."
            )
        
        if self.analysis_result.circular_dependencies:
            recommendations.append(
                "6. **Break Circular Dependencies**: Refactor module structure to eliminate circular imports."
            )
        
        if self.analysis_result.naming_violations:
            recommendations.append(
                "7. **Fix Naming Conventions**: Ensure functions use snake_case and classes use PascalCase."
            )
        
        if self.analysis_result.architectural_violations:
            recommendations.append(
                "8. **Address Architectural Issues**: Review and fix violations of separation of concerns."
            )
        
        if not recommendations:
            recommendations.append("✅ **Excellent!** No major issues found. Continue maintaining code quality.")
        
        return "\n".join(recommendations)


def main():
    """Run repository analysis."""
    import sys
    
    root_path = Path.cwd()
    if len(sys.argv) > 1:
        root_path = Path(sys.argv[1])
    
    print(f"Analyzing repository: {root_path}\n")
    
    analyzer = RepositoryAnalyzer(root_path)
    result = analyzer.analyze()
    
    print("\n" + "="*60)
    analyzer.generate_report()
    print("="*60)


if __name__ == "__main__":
    main()
