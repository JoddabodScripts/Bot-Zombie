"""nerimity lint — static checks for common bot code mistakes."""
from __future__ import annotations
import ast
import os
import sys
from pathlib import Path


def _py_files(path: str) -> list[Path]:
    p = Path(path)
    if p.is_file():
        return [p]
    return list(p.rglob("*.py"))


class _Visitor(ast.NodeVisitor):
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.issues: list[str] = []
        self._commands: list[str] = []
        self._slash: list[str] = []
        self._buttons: list[str] = []
        self._button_ids: list[tuple[str, int]] = []  # (id_string, lineno)
        self._has_error_handler = False
        self._has_slash_error_handler = False
        self._has_button_error_handler = False

    def _warn(self, node: ast.AST, msg: str) -> None:
        line = getattr(node, "lineno", "?")
        self.issues.append(f"  {self.filename}:{line}  {msg}")

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        for dec in node.decorator_list:
            name = ast.unparse(dec)
            if "on_command_error" in name:
                self._has_error_handler = True
            if "on_slash_error" in name:
                self._has_slash_error_handler = True
            if "on_button_error" in name:
                self._has_button_error_handler = True

            if ".command(" in name or ".command_private(" in name or ".slash(" in name:
                if "description=" not in name:
                    self._warn(node, f"@command '{node.name}' has no description= — won't show in help")
                self._commands.append(node.name)

            if ".slash(" in name:
                self._slash.append(node.name)

            # @bot.button("id") — extract the ID string and check for duplicates
            if ".button(" in name:
                self._buttons.append(node.name)
                if isinstance(dec, ast.Call) and dec.args:
                    arg = dec.args[0]
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        self._button_ids.append((arg.value, node.lineno))

            # @bot.cron("expr") — validate cron syntax
            if ".cron(" in name:
                if isinstance(dec, ast.Call) and dec.args:
                    arg = dec.args[0]
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        self._check_cron(node, arg.value)

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.visit_FunctionDef(node)  # type: ignore

    def visit_Await(self, node: ast.Await) -> None:
        """Detect await bot.wait_for(...) calls missing a timeout= argument."""
        call = node.value
        if isinstance(call, ast.Call):
            func_str = ast.unparse(call.func)
            if "wait_for" in func_str:
                kwarg_names = {kw.arg for kw in call.keywords}
                if "timeout" not in kwarg_names:
                    self._warn(node, "wait_for() called without timeout= — can hang forever")
        self.generic_visit(node)

    def _check_cron(self, node: ast.AST, expr: str) -> None:
        try:
            import croniter
            if not croniter.croniter.is_valid(expr):
                self._warn(node, f"Invalid cron expression: {expr!r}")
        except ImportError:
            pass  # croniter not installed, skip


def lint_files(paths: list[str]) -> list[str]:
    all_issues: list[str] = []
    visitors: list[_Visitor] = []

    for path in paths:
        for f in _py_files(path):
            try:
                tree = ast.parse(f.read_text(), filename=str(f))
            except SyntaxError as e:
                all_issues.append(f"  {f}: SyntaxError: {e}")
                continue
            v = _Visitor(str(f))
            v.visit(tree)
            all_issues.extend(v.issues)
            visitors.append(v)

    # Global checks across all files
    has_any_command = any(v._commands or v._slash for v in visitors)
    has_error_handler = any(v._has_error_handler for v in visitors)
    has_slash_error_handler = any(v._has_slash_error_handler for v in visitors)
    has_button_error_handler = any(v._has_button_error_handler for v in visitors)
    has_buttons = any(v._buttons for v in visitors)
    has_slash = any(v._slash for v in visitors)

    if has_any_command and not has_error_handler:
        all_issues.append("  (global)  No @bot.on_command_error handler found — errors will only be logged")
    if has_slash and not has_slash_error_handler:
        all_issues.append("  (global)  No @bot.on_slash_error handler found")
    if has_buttons and not has_button_error_handler:
        all_issues.append("  (global)  No @bot.on_button_error handler found")

    # Duplicate button IDs across all files
    all_button_ids: list[tuple[str, str, int]] = []
    for v in visitors:
        for bid, lineno in v._button_ids:
            all_button_ids.append((bid, v.filename, lineno))
    seen: dict[str, tuple[str, int]] = {}
    for bid, fname, lineno in all_button_ids:
        if bid in seen:
            prev_fname, prev_line = seen[bid]
            all_issues.append(
                f"  {fname}:{lineno}  Duplicate button ID {bid!r} "
                f"(first seen at {prev_fname}:{prev_line})"
            )
        else:
            seen[bid] = (fname, lineno)

    return all_issues


def run_lint(paths: list[str]) -> None:
    issues = lint_files(paths)
    if not issues:
        print("✅ No issues found.")
        return
    print(f"⚠️  {len(issues)} issue(s) found:\n")
    for issue in issues:
        print(issue)
    sys.exit(1)
