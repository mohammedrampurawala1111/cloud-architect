"""Minimal YAML-subset parser (Python standard library only).

Supports what the cloud-architect skills emit: block mappings, block lists
(including lists of mappings), inline flow mappings/lists such as
``{ terraform: 1 }`` and ``[typescript, python]``, comments, and plain or
quoted scalars (int, float, bool, null, string).

Not supported (raises YamlError): multi-line strings (| or >), anchors and
aliases, tags, multiple documents. Use JSON for anything more complex.
"""

import re

__all__ = ["loads", "YamlError"]


class YamlError(ValueError):
    """Raised when the input is outside the supported YAML subset."""


_INT = re.compile(r"^[-+]?\d+$")
_FLOAT = re.compile(r"^[-+]?(\d+\.\d*|\.\d+|\d+)([eE][-+]?\d+)?$")


def _strip_comment(line):
    out = []
    quote = None
    for i, ch in enumerate(line):
        if quote:
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            break
        out.append(ch)
    return "".join(out).rstrip()


def _scalar(text, lineno):
    s = text.strip()
    if s == "":
        return None
    if s[0] in ("'", '"'):
        if len(s) < 2 or s[-1] != s[0]:
            raise YamlError("line %d: unterminated quoted string: %s" % (lineno, s))
        body = s[1:-1]
        if s[0] == '"':
            body = (body.replace('\\"', '"').replace("\\n", "\n")
                    .replace("\\t", "\t").replace("\\\\", "\\"))
        else:
            body = body.replace("''", "'")
        return body
    if s[0] in ("|", ">"):
        raise YamlError("line %d: block scalars (| or >) are not supported; use JSON" % lineno)
    if s[0] in ("&", "*", "!"):
        raise YamlError("line %d: anchors, aliases and tags are not supported; use JSON" % lineno)
    low = s.lower()
    if low in ("true", "yes", "on"):
        return True
    if low in ("false", "no", "off"):
        return False
    if low in ("null", "~"):
        return None
    if _INT.match(s):
        return int(s)
    if _FLOAT.match(s):
        return float(s)
    return s


class _Flow:
    """Recursive-descent parser for inline {..} and [..] values."""

    def __init__(self, text, lineno):
        self.s = text
        self.i = 0
        self.lineno = lineno

    def err(self, msg):
        raise YamlError("line %d: %s in inline value: %s" % (self.lineno, msg, self.s))

    def ws(self):
        while self.i < len(self.s) and self.s[self.i] in " \t":
            self.i += 1

    def value(self):
        self.ws()
        if self.i >= len(self.s):
            self.err("unexpected end")
        ch = self.s[self.i]
        if ch == "{":
            return self.mapping()
        if ch == "[":
            return self.sequence()
        return self.plain()

    def plain(self, stop=",]}"):
        start = self.i
        if self.s[self.i] in ("'", '"'):
            q = self.s[self.i]
            self.i += 1
            while self.i < len(self.s) and self.s[self.i] != q:
                self.i += 1
            if self.i >= len(self.s):
                self.err("unterminated quote")
            self.i += 1
            return _scalar(self.s[start:self.i], self.lineno)
        while self.i < len(self.s) and self.s[self.i] not in stop:
            if self.s[self.i] == ":" and ":" in stop:
                break
            self.i += 1
        return _scalar(self.s[start:self.i], self.lineno)

    def mapping(self):
        self.i += 1
        out = {}
        while True:
            self.ws()
            if self.i < len(self.s) and self.s[self.i] == "}":
                self.i += 1
                return out
            key = self.plain(stop=":,}")
            self.ws()
            if self.i >= len(self.s) or self.s[self.i] != ":":
                self.err("expected ':' after key %r" % (key,))
            self.i += 1
            out[str(key)] = self.value()
            self.ws()
            if self.i < len(self.s) and self.s[self.i] == ",":
                self.i += 1
            elif self.i < len(self.s) and self.s[self.i] == "}":
                continue
            else:
                self.err("expected ',' or '}'")

    def sequence(self):
        self.i += 1
        out = []
        while True:
            self.ws()
            if self.i < len(self.s) and self.s[self.i] == "]":
                self.i += 1
                return out
            out.append(self.value())
            self.ws()
            if self.i < len(self.s) and self.s[self.i] == ",":
                self.i += 1
            elif self.i < len(self.s) and self.s[self.i] == "]":
                continue
            else:
                self.err("expected ',' or ']'")


def _value(text, lineno):
    s = text.strip()
    if s.startswith("{") or s.startswith("["):
        f = _Flow(s, lineno)
        v = f.value()
        f.ws()
        if f.i != len(s):
            raise YamlError("line %d: trailing characters after inline value: %s" % (lineno, s))
        return v
    return _scalar(s, lineno)


def _split_key(content, lineno):
    """Return (key, rest) if content is 'key: rest' / 'key:', else None."""
    quote = None
    depth = 0
    for i, ch in enumerate(content):
        if quote:
            if ch == quote:
                quote = None
            continue
        if ch in ("'", '"'):
            quote = ch
        elif ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
        elif ch == ":" and depth == 0 and (i + 1 == len(content) or content[i + 1] in " \t"):
            key = _scalar(content[:i], lineno)
            if key is None:
                raise YamlError("line %d: empty key" % lineno)
            return str(key), content[i + 1:]
    return None


class _Parser:
    def __init__(self, text):
        self.lines = []
        for n, raw in enumerate(text.splitlines(), 1):
            if raw.strip() in ("---", "..."):
                if self.lines:
                    raise YamlError("line %d: multiple documents are not supported" % n)
                continue
            line = _strip_comment(raw)
            if not line.strip():
                continue
            lead = line[: len(line) - len(line.lstrip())]
            if "\t" in lead:
                raise YamlError("line %d: tabs are not allowed for indentation" % n)
            self.lines.append([len(lead), line.strip(), n])
        self.i = 0

    @staticmethod
    def is_item(content):
        return content == "-" or content.startswith("- ")

    def parse(self):
        if not self.lines:
            return None
        first_indent = self.lines[0][0]
        if len(self.lines) == 1 and not self.is_item(self.lines[0][1]) and _split_key(self.lines[0][1], self.lines[0][2]) is None:
            return _value(self.lines[0][1], self.lines[0][2])
        v = self.block(first_indent)
        if self.i < len(self.lines):
            ind, content, n = self.lines[self.i]
            raise YamlError("line %d: unexpected indentation or content: %s" % (n, content))
        return v

    def block(self, indent):
        if self.is_item(self.lines[self.i][1]):
            return self.seq(indent)
        return self.mapping(indent)

    def child(self, indent, allow_same_indent_list):
        """Parse the nested block after 'key:' or '-', if any."""
        if self.i >= len(self.lines):
            return None
        nind, ncontent, _ = self.lines[self.i]
        if nind > indent:
            return self.block(nind)
        if allow_same_indent_list and nind == indent and self.is_item(ncontent):
            return self.seq(indent)
        return None

    def mapping(self, indent):
        out = {}
        while self.i < len(self.lines):
            ind, content, n = self.lines[self.i]
            if ind < indent:
                break
            if ind > indent:
                raise YamlError("line %d: unexpected indentation: %s" % (n, content))
            if self.is_item(content):
                break
            kv = _split_key(content, n)
            if kv is None:
                raise YamlError("line %d: expected 'key: value', got: %s" % (n, content))
            key, rest = kv
            if key in out:
                raise YamlError("line %d: duplicate key %r" % (n, key))
            self.i += 1
            if rest.strip():
                out[key] = _value(rest, n)
            else:
                out[key] = self.child(indent, allow_same_indent_list=True)
        return out

    def seq(self, indent):
        out = []
        while self.i < len(self.lines):
            ind, content, n = self.lines[self.i]
            if ind != indent or not self.is_item(content):
                if ind > indent:
                    raise YamlError("line %d: unexpected indentation: %s" % (n, content))
                break
            rest = content[1:].lstrip()
            if not rest:
                self.i += 1
                out.append(self.child(indent, allow_same_indent_list=False))
                continue
            if rest[0] not in "[{'\"" and _split_key(rest, n) is not None:
                # "- key: value" starts a mapping whose keys align with 'key'.
                item_indent = indent + (len(content) - len(rest))
                self.lines[self.i] = [item_indent, rest, n]
                out.append(self.mapping(item_indent))
                continue
            self.i += 1
            out.append(_value(rest, n))
        return out


def loads(text):
    """Parse a YAML-subset document and return Python objects."""
    return _Parser(text).parse()
