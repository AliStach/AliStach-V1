"""Quality gate enforcement script for CI/CD."""

import subprocess
import sys
from dataclasses import dataclass
from typing import List, Tuple
from pathlib import Path


@dataclass
class CheckResult:
    """Result of a quality check."""
    name: str
    passed: bool
    message: str
    output: str = ""


class QualityGate:
    """Enforce code quality standards."""
    
    def __init__(self, root_path: Path = None):
        """
        Initialize quality gate.
        
        Args:
            root_path: Root path of the project
        """
        self.root_path = root_path or Path.cwd()
        self.src_path = self.root_path / "src"
        self.tests_path = self.root_path / "tests"
    
    def run_command(self, command: List[str]) -> Tuple[int, str, str]:
        """
        Run a shell command and return the result.
        
        Args:
            command: Command to run as list of strings
        
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=self.root_path
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return 1, "", str(e)
    
    def check_formatting(self) -> CheckResult:
        """
        Verify code formatting with Black.
        
        Returns:
            CheckResult with formatting check results
        """
        print("🔍 Checking code formatting with Black...")
        
        returncode, stdout, stderr = self.run_command([
            "black", "--check", "src", "tests"
        ])
        
        if returncode == 0:
            return CheckResult(
                name="Black Formatting",
                passed=True,
                message="All files are properly formatted",
                output=stdout
            )
        else:
            return CheckResult(
                name="Black Formatting",
                passed=False,
                message="Some files need formatting. Run: black src tests",
                output=stdout + stderr
            )
    
    def check_linting(self) -> CheckResult:
        """
        Verify linting with Ruff.
        
        Returns:
            CheckResult with linting check results
        """
        print("🔍 Checking code with Ruff linter...")
        
        returncode, stdout, stderr = self.run_command([
            "ruff", "check", "src", "tests"
        ])
        
        if returncode == 0:
            return CheckResult(
                name="Ruff Linting",
                passed=True,
                message="No linting issues found",
                output=stdout
            )
        else:
            return CheckResult(
                name="Ruff Linting",
                passed=False,
                message="Linting issues found. Run: ruff check --fix src tests",
                output=stdout + stderr
            )
    
    def check_type_coverage(self) -> CheckResult:
        """
        Verify type annotation coverage with mypy.
        
        Returns:
            CheckResult with type checking results
        """
        print("🔍 Checking type annotations with mypy...")
        
        returncode, stdout, stderr = self.run_command([
            "mypy", "src", "--ignore-missing-imports"
        ])
        
        # mypy returns 0 if no errors, 1 if errors found
        if returncode == 0:
            return CheckResult(
                name="Type Checking (mypy)",
                passed=True,
                message="Type checking passed",
                output=stdout
            )
        else:
            return CheckResult(
                name="Type Checking (mypy)",
                passed=False,
                message="Type errors found",
                output=stdout + stderr
            )
    
    def check_test_coverage(self) -> CheckResult:
        """
        Verify test coverage.
        
        Returns:
            CheckResult with test coverage results
        """
        print("🔍 Running tests with coverage...")
        
        returncode, stdout, stderr = self.run_command([
            "pytest", "--cov=src", "--cov-report=term", "--cov-report=xml"
        ])
        
        if returncode == 0:
            # Parse coverage from output
            coverage_line = [line for line in stdout.split('\n') if 'TOTAL' in line]
            
            return CheckResult(
                name="Test Coverage",
                passed=True,
                message=f"All tests passed. {coverage_line[0] if coverage_line else ''}",
                output=stdout
            )
        else:
            return CheckResult(
                name="Test Coverage",
                passed=False,
                message="Some tests failed",
                output=stdout + stderr
            )
    
    def check_security(self) -> CheckResult:
        """
        Check for security vulnerabilities with Bandit.
        
        Returns:
            CheckResult with security check results
        """
        print("🔍 Checking for security issues with Bandit...")
        
        returncode, stdout, stderr = self.run_command([
            "bandit", "-r", "src", "-f", "txt"
        ])
        
        # Bandit returns 0 if no issues, 1 if issues found
        if returncode == 0:
            return CheckResult(
                name="Security Check (Bandit)",
                passed=True,
                message="No security issues found",
                output=stdout
            )
        else:
            # Check if there are only low severity issues
            if "Severity: Low" in stdout and "Severity: Medium" not in stdout and "Severity: High" not in stdout:
                return CheckResult(
                    name="Security Check (Bandit)",
                    passed=True,
                    message="Only low severity issues found (acceptable)",
                    output=stdout
                )
            else:
                return CheckResult(
                    name="Security Check (Bandit)",
                    passed=False,
                    message="Security issues found",
                    output=stdout + stderr
                )
    
    def validate(self, skip_tests: bool = False) -> bool:
        """
        Run all quality checks.
        
        Args:
            skip_tests: Whether to skip running tests
        
        Returns:
            True if all checks pass, False otherwise
        """
        print("\n" + "="*60)
        print("🚀 Running Quality Gate Checks")
        print("="*60 + "\n")
        
        checks = [
            self.check_formatting,
            self.check_linting,
            self.check_type_coverage,
            self.check_security,
        ]
        
        if not skip_tests:
            checks.append(self.check_test_coverage)
        
        results = []
        for check in checks:
            result = check()
            results.append(result)
            
            if result.passed:
                print(f"✅ {result.name}: {result.message}")
            else:
                print(f"❌ {result.name}: {result.message}")
                if result.output:
                    print(f"   Output: {result.output[:200]}...")
            print()
        
        print("="*60)
        passed_count = sum(1 for r in results if r.passed)
        total_count = len(results)
        
        if passed_count == total_count:
            print(f"✅ All {total_count} quality checks passed!")
            print("="*60 + "\n")
            return True
        else:
            print(f"❌ {total_count - passed_count} of {total_count} checks failed")
            print("="*60 + "\n")
            return False


def main():
    """Main entry point for quality gate script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run quality gate checks")
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running tests (faster for quick checks)"
    )
    
    args = parser.parse_args()
    
    gate = QualityGate()
    success = gate.validate(skip_tests=args.skip_tests)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
