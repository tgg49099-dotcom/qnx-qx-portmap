"""Static scanner for C and header files (``--scan-dir``).

Walks ``.c`` and ``.h`` files under a project directory using only the Python
standard library, identifies functions and function-like macros defined in the
project (to exclude them), and collects the relative file path and 1-based
line number of every external function call.
"""

import bisect
import os
import re

C_KEYWORDS = frozenset((
    # C89 / C99 / C11 / C23 keywords & operators
    "auto", "break", "case", "char", "const", "continue", "default", "do",
    "double", "else", "enum", "extern", "float", "for", "goto", "if",
    "inline", "int", "long", "register", "restrict", "return", "short",
    "signed", "sizeof", "static", "struct", "switch", "typedef", "union",
    "unsigned", "void", "volatile", "while",
    "_Alignas", "_Alignof", "_Atomic", "_Bool", "_Complex", "_Generic",
    "_Imaginary", "_Noreturn", "_Static_assert", "_Thread_local",
    "alignas", "alignof", "bool", "constexpr", "false", "nullptr",
    "static_assert", "thread_local", "true", "typeof", "typeof_unqual",
    # Preprocessor / compiler builtins
    "defined", "__attribute__", "__attribute", "__asm__", "__asm", "asm",
    "__typeof__", "__typeof", "__extension__", "__alignof__", "__alignof",
    "__builtin_expect", "__builtin_offsetof", "__has_include",
    "__has_attribute", "__has_builtin",
))

_QUALIFIERS_AFTER_PARAMS = frozenset((
    "const", "volatile", "noexcept", "override", "final",
    "__attribute__", "__attribute", "__asm__", "__asm", "asm",
    "__THROW", "__THROWNL", "__nonnull", "__wur",
))

_INCLUDE_RE = re.compile(r"^\s*#\s*include\s*<([^>\r\n]+)>", re.MULTILINE)
_DEFINE_FN_RE = re.compile(r"^(\s*#\s*define\s+([A-Za-z_][A-Za-z0-9_]*)\()")
_DEFINE_OBJ_RE = re.compile(r"^(\s*#\s*define\s+[A-Za-z_][A-Za-z0-9_]*)")
_TOKEN_RE = re.compile(r"->|[A-Za-z_][A-Za-z0-9_]*|[(){}\[\];,.=]")


class ScanError(Exception):
    """Raised when the target directory cannot be scanned."""


class ScanResult(object):
    """Result of scanning a C/H project directory."""

    def __init__(self, root, files, defined, calls, headers):
        self.root = root
        self.files = files
        self.defined = defined
        self.calls = calls
        self.headers = headers

    @property
    def symbols(self):
        return list(self.calls.keys())

    def to_dict(self):
        return {
            "dir": self.root,
            "files": len(self.files),
            "defined_ignored": len(self.defined),
            "headers": list(self.headers),
        }


def _line_offsets(text):
    offsets = [0]
    idx = text.find("\n")
    while idx >= 0:
        offsets.append(idx + 1)
        idx = text.find("\n", idx + 1)
    return offsets


def _blank_preserving_newlines(segment):
    return "".join("\n" if ch == "\n" else " " for ch in segment)


def strip_c_comments_and_strings(source, keep_strings=False):
    """Replaces C comments (and optionally string/char literals) with spaces.

    Every ``\\n`` character is preserved so 1-based line numbers remain exact.
    """
    out = []
    n = len(source)
    i = 0
    while i < n:
        ch = source[i]
        nxt = source[i + 1] if i + 1 < n else ""
        # Line comment // ... (honoring trailing backslash line continuations)
        if ch == "/" and nxt == "/":
            out.append("  ")
            i += 2
            while i < n:
                if source[i] == "\\" and i + 1 < n and source[i + 1] == "\n":
                    out.append(" \n")
                    i += 2
                    continue
                if source[i] == "\\" and i + 2 < n and source[i + 1] == "\r" and source[i + 2] == "\n":
                    out.append("  \n")
                    i += 3
                    continue
                if source[i] == "\n":
                    out.append("\n")
                    i += 1
                    break
                out.append(" ")
                i += 1
            continue
        # Block comment /* ... */
        if ch == "/" and nxt == "*":
            out.append("  ")
            i += 2
            while i < n:
                if source[i] == "*" and i + 1 < n and source[i + 1] == "/":
                    out.append("  ")
                    i += 2
                    break
                out.append("\n" if source[i] == "\n" else " ")
                i += 1
            continue
        # String or character literal
        if ch in ('"', "'"):
            quote = ch
            out.append(ch if keep_strings else " ")
            i += 1
            while i < n:
                c = source[i]
                if c == "\\" and i + 1 < n:
                    c2 = source[i + 1]
                    if keep_strings:
                        out.append(c)
                        out.append(c2)
                    else:
                        out.append(" ")
                        out.append("\n" if c2 == "\n" else " ")
                    i += 2
                    continue
                if c == quote:
                    out.append(c if keep_strings else " ")
                    i += 1
                    break
                if keep_strings:
                    out.append(c)
                else:
                    out.append("\n" if c == "\n" else " ")
                i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _preprocess_strip(code):
    """Handles preprocessor directives while preserving exact line numbers.

    Returns ``(cleaned_code, macro_names, macro_bodies)`` where:
    - ``macro_names`` is the set of function-like macros defined via ``#define NAME(...)``;
    - ``macro_bodies`` is a list of ``(body_text, start_line)`` tuples extracted
      from ``#define`` directives so calls inside macros are captured with exact
      line numbers without interfering with C brace/declaration parsing;
    - all preprocessor directives are blanked in ``cleaned_code`` while keeping
      every ``\\n`` intact.
    """
    macros = set()
    macro_bodies = []
    lines = code.splitlines(True)
    out = []
    i = 0
    total = len(lines)
    while i < total:
        line = lines[i]
        if line.lstrip(" \t").startswith("#"):
            start_line = i + 1
            # Collect the full logical preprocessor directive (\\\n continuations).
            block = [line]
            while block[-1].rstrip("\r\n").endswith("\\") and i + 1 < total:
                i += 1
                block.append(lines[i])
            joined = "".join(block)
            m_fn = _DEFINE_FN_RE.match(joined)
            if m_fn:
                macros.add(m_fn.group(2))
                pos = m_fn.end() - 1
                depth = 0
                end_pos = len(joined)
                while pos < len(joined):
                    if joined[pos] == "(":
                        depth += 1
                    elif joined[pos] == ")":
                        depth -= 1
                        if depth == 0:
                            end_pos = pos + 1
                            break
                    pos += 1
                body_prefix = _blank_preserving_newlines(joined[:end_pos])
                body = joined[end_pos:].replace("\\\n", " \n").replace("\\\r\n", "  \n")
                if body.strip():
                    macro_bodies.append((body_prefix + body, start_line))
            else:
                m_obj = _DEFINE_OBJ_RE.match(joined)
                if m_obj:
                    body_prefix = _blank_preserving_newlines(joined[:m_obj.end()])
                    body = joined[m_obj.end():].replace("\\\n", " \n").replace("\\\r\n", "  \n")
                    if body.strip():
                        macro_bodies.append((body_prefix + body, start_line))
            out.append(_blank_preserving_newlines(joined))
        else:
            out.append(line)
        i += 1
    return "".join(out), macros, macro_bodies


def _match_paren(tokens, open_idx):
    """Returns index of matching ``)`` for ``(`` at *open_idx*, or -1."""
    depth = 0
    for j in range(open_idx, len(tokens)):
        val = tokens[j][0]
        if val == "(":
            depth += 1
        elif val == ")":
            depth -= 1
            if depth == 0:
                return j
    return -1


def _skip_post_param_qualifiers(tokens, idx):
    """Advances past attributes/qualifiers between ``)`` and ``{`` or ``;``."""
    n = len(tokens)
    while idx < n:
        val = tokens[idx][0]
        if val in _QUALIFIERS_AFTER_PARAMS:
            idx += 1
            if idx < n and tokens[idx][0] == "(":
                close = _match_paren(tokens, idx)
                if close < 0:
                    return idx
                idx = close + 1
            continue
        break
    return idx


def _is_knr_definition(tokens, after_paren_idx):
    """Detects K&R C parameter declarations between ``)`` and ``{``."""
    n = len(tokens)
    j = after_paren_idx
    saw_semi = False
    while j < n:
        val = tokens[j][0]
        if val == "{":
            return saw_semi and j > after_paren_idx and tokens[j - 1][0] == ";"
        if val in ("(", "=", "}") or val in ("struct", "union", "enum", "typedef"):
            return False
        if val == ";":
            saw_semi = True
        j += 1
    return False


def _record_call(calls, sym, lineno):
    lines_list = calls.setdefault(sym, [])
    if lineno not in lines_list:
        lines_list.append(lineno)


def scan_file(source):
    """Scans a single C or header source string.

    Returns ``(defined_names, calls_by_symbol, headers)`` where:
    - ``defined_names`` is a ``set`` of function and function-like macro names
      defined in *source*;
    - ``calls_by_symbol`` maps each called identifier to a sorted list of unique
      1-based line numbers;
    - ``headers`` is a list of angle-bracket headers included via ``#include <...>``.
    """
    no_comments = strip_c_comments_and_strings(source, keep_strings=True)
    headers = []
    seen_headers = set()
    for m in _INCLUDE_RE.finditer(no_comments):
        hdr = m.group(1).strip()
        if hdr and hdr not in seen_headers:
            seen_headers.add(hdr)
            headers.append(hdr)

    stripped = strip_c_comments_and_strings(source, keep_strings=False)
    cleaned, macro_defs, macro_bodies = _preprocess_strip(stripped)

    offsets = _line_offsets(cleaned)
    tokens = []
    for m in _TOKEN_RE.finditer(cleaned):
        lineno = bisect.bisect_right(offsets, m.start())
        tokens.append((m.group(0), lineno))

    defined = set(macro_defs)
    non_call_indices = set()
    scope_stack = []  # "extern_c" or "block"

    n = len(tokens)
    stmt_has_eq = False
    stmt_is_typedef = False
    stmt_start = True

    i = 0
    while i < n:
        tok, _line = tokens[i]
        in_file_scope = "block" not in scope_stack

        if tok == "{":
            if in_file_scope and i > 0 and tokens[i - 1][0] == "extern":
                scope_stack.append("extern_c")
            else:
                scope_stack.append("block")
            stmt_has_eq = False
            stmt_is_typedef = False
            stmt_start = True
            i += 1
            continue

        if tok == "}":
            if scope_stack:
                scope_stack.pop()
            stmt_has_eq = False
            stmt_is_typedef = False
            stmt_start = True
            i += 1
            continue

        if tok == ";":
            stmt_has_eq = False
            stmt_is_typedef = False
            stmt_start = True
            i += 1
            continue

        if tok == "=":
            stmt_has_eq = True
            stmt_start = False
            i += 1
            continue

        if tok == "typedef":
            stmt_is_typedef = True
            stmt_start = False
            i += 1
            continue

        if (tok in ("__attribute__", "__attribute", "__asm__", "__asm", "asm")
                and i + 1 < n and tokens[i + 1][0] == "("):
            close = _match_paren(tokens, i + 1)
            if close >= 0:
                for k in range(i, close + 1):
                    non_call_indices.add(k)
                i = close + 1
                continue

        if (in_file_scope and i + 1 < n and tokens[i + 1][0] == "("
                and (tok[0].isalpha() or tok[0] == "_")):
            if tok not in C_KEYWORDS and not stmt_has_eq:
                prev_tok = tokens[i - 1][0] if i > 0 else ""
                if prev_tok not in (".", "->"):
                    close = _match_paren(tokens, i + 1)
                    if close >= 0:
                        after = _skip_post_param_qualifiers(tokens, close + 1)
                        # Support functions returning function pointers:
                        # int (*fn(int a))(int b) { ... }
                        if (after < n and tokens[after][0] == ")"
                                and after + 1 < n and tokens[after + 1][0] == "("):
                            ret_close = _match_paren(tokens, after + 1)
                            if ret_close >= 0:
                                after = _skip_post_param_qualifiers(tokens, ret_close + 1)
                        next_tok = tokens[after][0] if after < n else ""
                        if next_tok == "{" or _is_knr_definition(tokens, after):
                            defined.add(tok)
                            non_call_indices.add(i)
                            for k in range(i + 1, after):
                                non_call_indices.add(k)
                            i = after
                            continue
                        if next_tok == ";" and not stmt_start and not stmt_is_typedef:
                            non_call_indices.add(i)
                            for k in range(i + 1, after):
                                non_call_indices.add(k)
                            i = after
                            continue
                        if stmt_is_typedef:
                            non_call_indices.add(i)
                            for k in range(i + 1, after):
                                non_call_indices.add(k)
                            i = after
                            continue

        stmt_start = False
        i += 1

    # Pass 2: collect all function call sites in the C code.
    calls = {}
    stmt_is_typedef = False
    for idx, (tok, lineno) in enumerate(tokens):
        if tok in (";", "{", "}"):
            stmt_is_typedef = False
            continue
        if tok == "typedef":
            stmt_is_typedef = True
            continue
        if idx in non_call_indices:
            continue
        if idx + 1 >= n or tokens[idx + 1][0] != "(":
            continue
        if not (tok[0].isalpha() or tok[0] == "_"):
            continue
        if tok in C_KEYWORDS:
            continue
        if stmt_is_typedef:
            continue
        if idx > 0 and tokens[idx - 1][0] in (".", "->"):
            continue
        _record_call(calls, tok, lineno)

    # Pass 3: collect calls inside #define macro bodies at their exact lines.
    for body_text, base_line in macro_bodies:
        body_offsets = _line_offsets(body_text)
        body_tokens = []
        for m in _TOKEN_RE.finditer(body_text):
            rel_line = bisect.bisect_right(body_offsets, m.start())
            body_tokens.append((m.group(0), base_line + rel_line - 1))
        bn = len(body_tokens)
        for idx, (tok, lineno) in enumerate(body_tokens):
            if idx + 1 >= bn or body_tokens[idx + 1][0] != "(":
                continue
            if not (tok[0].isalpha() or tok[0] == "_"):
                continue
            if tok in C_KEYWORDS:
                continue
            if idx > 0 and body_tokens[idx - 1][0] in (".", "->"):
                continue
            _record_call(calls, tok, lineno)

    for sym in calls:
        calls[sym].sort()

    return defined, calls, headers


def scan_directory(root_dir, extensions=(".c", ".h")):
    """Walks *root_dir* and returns a :class:`ScanResult` of external C calls.

    - Walks ``.c`` and ``.h`` files recursively in deterministic sorted order.
    - Ignores hidden directories (e.g. ``.git``).
    - Ignores every function or function-like macro defined in any scanned file
      of the project.
    - Records every call site as ``{"file": relative_posix_path, "line": int}``.
    """
    abs_root = os.path.abspath(root_dir)
    if not os.path.isdir(abs_root):
        raise ScanError(abs_root)

    ext_set = tuple(e.lower() for e in extensions)
    scanned_files = []
    project_defined = set()
    raw_calls = {}
    headers_set = set()

    for dirpath, dirnames, filenames in os.walk(abs_root, followlinks=False):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
        for fn in sorted(filenames):
            if not fn.lower().endswith(ext_set):
                continue
            full = os.path.join(dirpath, fn)
            if not os.path.isfile(full):
                continue
            rel = os.path.relpath(full, abs_root).replace(os.sep, "/")
            try:
                with open(full, encoding="utf-8", errors="replace") as fh:
                    source = fh.read()
            except OSError:
                continue
            scanned_files.append(rel)
            defined, file_calls, file_headers = scan_file(source)
            project_defined.update(defined)
            headers_set.update(file_headers)
            for sym, line_nums in file_calls.items():
                sites = raw_calls.setdefault(sym, [])
                for lineno in line_nums:
                    sites.append({"file": rel, "line": lineno})

    # Filter out every function / function-like macro defined anywhere in the project.
    external_calls = {}
    for sym in sorted(raw_calls):
        if sym in project_defined:
            continue
        sites = raw_calls[sym]
        sites.sort(key=lambda loc: (loc["file"], loc["line"]))
        external_calls[sym] = sites

    return ScanResult(
        root=abs_root,
        files=scanned_files,
        defined=sorted(project_defined),
        calls=external_calls,
        headers=sorted(headers_set),
    )
