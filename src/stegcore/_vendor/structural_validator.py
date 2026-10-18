"""Bounded, offline structural validation candidate; NEVER governance authorization."""
import calendar
import hashlib
import json
import re

DIALECT = "stegverse-bounded-v1"
MAX_SCHEMA_DEPTH = 32
MAX_INSTANCE_DEPTH = 256
# pattern (T13): a dialect-neutral subset that means the same in Python re and ECMA-262
# and cannot backtrack catastrophically; anything outside it fails closed.
MAX_PATTERN_LENGTH = 256
MAX_PATTERN_INPUT_LENGTH = 4096
MAX_UNBOUNDED_QUANTIFIERS = 1
SUPPORTED = {"type", "required", "properties", "additionalProperties", "items", "enum", "const", "minLength", "maxLength", "minimum", "maximum",
             "minItems", "maxItems", "uniqueItems", "pattern", "format", "exclusiveMinimum", "exclusiveMaximum",
             "allOf", "if", "then", "else", "$ref",
             "anyOf", "oneOf", "not", "minProperties", "maxProperties", "prefixItems",
             "propertyNames", "contains", "minContains", "maxContains"}
# Contract 1.7: anyOf / oneOf / not evaluate isolated trial branches under the same budget;
# additionalProperties may be a subschema; prefixItems validates positions, and `items` then
# applies to the remaining positions (`items: false` is admitted only as the closing form of a
# prefixItems tuple; other boolean subschemas stay unsupported). `default` is an annotation.
# propertyNames applies its subschema to each object key; contains counts matching items,
# bounded by minContains (default 1) and maxContains.
BRANCH_LISTS = ("allOf", "anyOf", "oneOf")
# Composition and references (contract 1.6): $defs only at the root, $ref only to "#/$defs/<name>"
# with a plain name, no reference cycles, and a bounded evaluation budget. Remote, relative,
# anchor and nested-$defs references stay unsupported and fail closed.
ROOT_DEFINITIONS = "$defs"
LOCAL_REF_PREFIX = "#/$defs/"
MAX_EVALUATION_STEPS = 200_000
# format (T13b) is asserted, not annotated, so the SDK validator can replace jsonschema
# FormatChecker uses without the optional rfc3339-validator dependency. Stdlib only.
SUPPORTED_FORMATS = ("date", "date-time")
# Annotation-only keywords: accepted and ignored, as in 2020-12 they never affect validity.
ANNOTATIONS = {"title", "description", "$comment", "examples", "default"}
# Root-only identity metadata (T12): no effect on validity. $schema must name exactly the
# dialect the ecosystem uses (all StegVerse-Labs/.github schemas declare it); anything else
# fails closed. Below the root both stay unsupported, since $ref/$defs resolution is not.
REFERENCE_DIALECT_URI = "https://json-schema.org/draft/2020-12/schema"
ROOT_IDENTITY = {"$schema", "$id"}
TYPES = {"null": lambda v: v is None, "boolean": lambda v: type(v) is bool,
         "integer": lambda v: type(v) is int, "number": lambda v: type(v) in (int, float),
         "string": lambda v: isinstance(v, str), "array": lambda v: isinstance(v, list),
         "object": lambda v: isinstance(v, dict)}

# Machine-readable compatibility contract. Every divergence from JSON Schema 2020-12
# is in the fail-closed direction: the candidate may reject what the reference
# accepts, never the reverse.
CONTRACT = {
    "dialect": DIALECT,
    "contract_version": "1.7",
    "composition": {"keywords": ["allOf", "anyOf", "oneOf", "not", "if", "then", "else", "contains", "propertyNames"], "references": "$ref to #/$defs/<name> only; $defs at the root only; cycles rejected",
                    "max_evaluation_steps": MAX_EVALUATION_STEPS},
    "format": {"asserted": list(SUPPORTED_FORMATS), "standard": "RFC 3339 (date, date-time); calendar-checked; leap second 60 rejected",
               "other_values": "rejected (UNSUPPORTED_FORMAT)"},
    "pattern_subset": {"dialect": "intersection of Python re (ASCII) and ECMA-262", "max_length": MAX_PATTERN_LENGTH,
                       "max_input_length": MAX_PATTERN_INPUT_LENGTH, "max_unbounded_quantifiers": MAX_UNBOUNDED_QUANTIFIERS,
                       "quantifiable": "single atoms; groups only with ?", "excluded": ". \\s \\b backreferences lookaround flags { \\- outside a class; -- && || ~~ inside a class"},
    "supported_keywords": sorted(SUPPORTED),
    "annotation_keywords": sorted(ANNOTATIONS),
    "root_identity_keywords": {"$schema": REFERENCE_DIALECT_URI, "$id": "string"},
    "max_schema_depth": MAX_SCHEMA_DEPTH,
    "max_instance_depth": MAX_INSTANCE_DEPTH,
    "instance_values": "JSON only: null, bool, int, finite float, str, list, dict with str keys",
    "reference": "JSON Schema 2020-12 (jsonschema Draft202012Validator) as differential oracle only",
    "divergences_fail_closed": [
        "integer-valued floats such as 1.0 are not type integer",
        "boolean subschemas (true/false) are unsupported, except items: false closing a prefixItems tuple",
        "every keyword outside supported_keywords is rejected; $schema, $id and $defs only at the root",
        "$ref other than #/$defs/<name>, and reference cycles, are rejected",
        "evaluation beyond max_evaluation_steps is rejected (EVALUATION_BUDGET_EXCEEDED)",
        "$schema other than the 2020-12 URI is rejected",
        "external registries and dialects other than this one are rejected",
        "schemas nested deeper than max_schema_depth or not JSON-encodable are rejected",
        "instances that are not JSON values (NaN, Infinity, sets, tuples, bytes, non-string keys) are rejected",
        "instances nested deeper than max_instance_depth are rejected",
        "pattern outside pattern_subset is rejected; strings longer than max_input_length fail a pattern",
        "format is asserted for date and date-time (2020-12 default is annotation); other formats are rejected; second=60 is rejected",
    ],
    "authority_effect": "NONE",
}

def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()

def json_equal(a, b):
    """JSON value equality: booleans are never numbers, 1 equals 1.0, containers compare deeply."""
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if type(a) in (int, float) and type(b) in (int, float):
        return a == b
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(json_equal(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(json_equal(a[k], b[k]) for k in a)
    return type(a) is type(b) and a == b

def _equality_key(value):
    """Hashable key under JSON equality (1 == 1.0, True != 1); instance depth is already bounded."""
    if isinstance(value, bool):
        return ("bool", value)
    if type(value) is int:
        # Converting an arbitrary-precision JSON integer to float can overflow.
        return ("num", value)
    if type(value) is float:
        return ("num", int(value) if value.is_integer() else value)
    if isinstance(value, list):
        return ("arr", tuple(_equality_key(v) for v in value))
    if isinstance(value, dict):
        return ("obj", tuple(sorted((k, _equality_key(v)) for k, v in value.items())))
    return (type(value).__name__, value)

def pointer(parts):
    return "".join("/" + str(p).replace("~", "~0").replace("/", "~1") for p in parts)

def _instance_finding(instance):
    """First non-JSON value or depth violation in the instance, found iteratively (no recursion)."""
    stack = [(instance, [], 0)]
    while stack:
        value, path, depth = stack.pop()
        if depth > MAX_INSTANCE_DEPTH:
            return {"path": pointer(path), "code": "INSTANCE_DEPTH_EXCEEDED"}
        if value is None or isinstance(value, (bool, str)) or type(value) is int:
            continue
        if type(value) is float:
            if value != value or value in (float("inf"), float("-inf")):
                return {"path": pointer(path), "code": "INVALID_INSTANCE_ENCODING"}
            continue
        if type(value) is list:
            stack.extend((item, path + [i], depth + 1) for i, item in reversed(list(enumerate(value))))
            continue
        if type(value) is dict:
            if any(type(k) is not str for k in value):
                return {"path": pointer(path), "code": "INVALID_INSTANCE_ENCODING"}
            stack.extend((value[k], path + [k], depth + 1) for k in sorted(value, reverse=True))
            continue
        return {"path": pointer(path), "code": "INVALID_INSTANCE_ENCODING"}
    return None

_SIMPLE_ESCAPES = set("\\.^$*+?()[]{}|/-")
_CLASS_ESCAPES = set("dw")
_CLASS_SET_OPERATORS = set("-&|~")

def _pattern_subset_error(pattern):
    """None when pattern is inside the safe dialect-neutral subset, else a reason code."""
    if not isinstance(pattern, str) or not pattern or len(pattern) > MAX_PATTERN_LENGTH:
        return "INVALID_PATTERN"
    i, n, unbounded = 0, len(pattern), 0
    last = None  # "atom", "group", or None (not quantifiable)
    depth = 0
    while i < n:
        c = pattern[i]
        if c == "\\":
            if i + 1 >= n:
                return "INVALID_PATTERN"
            e = pattern[i + 1]
            # \- is valid only inside a class under ECMA-262 unicode mode.
            if (e not in _SIMPLE_ESCAPES and e not in _CLASS_ESCAPES) or e == "-":
                return "UNSUPPORTED_PATTERN"
            i, last = i + 2, "atom"
        elif c == "[":
            j = i + 1
            if j < n and pattern[j] == "^":
                j += 1
            if j < n and pattern[j] == "]":
                return "UNSUPPORTED_PATTERN"
            while j < n and pattern[j] != "]":
                if pattern[j] == "[":
                    return "UNSUPPORTED_PATTERN"
                if pattern[j] == "\\":
                    if j + 1 >= n or (pattern[j + 1] not in _SIMPLE_ESCAPES and pattern[j + 1] not in _CLASS_ESCAPES):
                        return "UNSUPPORTED_PATTERN"
                    j += 2
                elif pattern[j] in _CLASS_SET_OPERATORS and pattern.startswith(pattern[j] * 2, j):
                    # --, &&, ||, ~~ are set operations in ECMA-262 v mode and future Python re.
                    return "UNSUPPORTED_PATTERN"
                else:
                    j += 1
            if j >= n:
                return "INVALID_PATTERN"
            i, last = j + 1, "atom"
        elif c == "(":
            if pattern.startswith("(?", i):
                return "UNSUPPORTED_PATTERN"
            depth += 1
            i, last = i + 1, None
        elif c == ")":
            if depth == 0:
                return "INVALID_PATTERN"
            depth -= 1
            i, last = i + 1, "group"
        elif c in "*+?":
            if last is None or (last == "group" and c != "?"):
                return "UNSUPPORTED_PATTERN"
            if c != "?":
                unbounded += 1
            i, last = i + 1, None
            if i < n and pattern[i] in "*+?{":
                return "UNSUPPORTED_PATTERN"
        elif c == "{":
            m = re.match(r"\{(\d{1,4})(,(\d{0,4}))?\}", pattern[i:])
            if not m or last != "atom":
                return "UNSUPPORTED_PATTERN"
            low, comma, high = int(m.group(1)), m.group(2), m.group(3)
            if comma and not high:
                unbounded += 1
            elif high and int(high) < low:
                return "INVALID_PATTERN"
            i, last = i + len(m.group(0)), None
            if i < n and pattern[i] in "*+?{":
                return "UNSUPPORTED_PATTERN"
        elif c in "^$|":
            i, last = i + 1, None
        elif c in ".}]":
            return "UNSUPPORTED_PATTERN"
        else:
            i, last = i + 1, "atom"
    if depth:
        return "INVALID_PATTERN"
    if unbounded > MAX_UNBOUNDED_QUANTIFIERS:
        return "UNSUPPORTED_PATTERN"
    try:
        re.compile(pattern, re.ASCII)
    except re.error:
        return "INVALID_PATTERN"
    return None

def _ecma_end_anchor(pattern):
    """Rewrite each unescaped $ outside a character class to \\Z. In Python re, $ also
    matches before a trailing newline; in ECMA-262 (no m flag) it matches only at the end."""
    out, i, in_class = [], 0, False
    while i < len(pattern):
        c = pattern[i]
        if c == "\\":
            out.append(pattern[i:i + 2])
            i += 2
            continue
        if c == "[":
            in_class = True
        elif c == "]":
            in_class = False
        out.append("\\Z" if c == "$" and not in_class else c)
        i += 1
    return "".join(out)

def _pattern_matches(pattern, value):
    return re.search(_ecma_end_anchor(pattern), value, re.ASCII) is not None

_DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})\Z", re.ASCII)
_DATE_TIME = re.compile(
    r"(\d{4})-(\d{2})-(\d{2})[Tt](\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(?:[Zz]|([+-])(\d{2}):(\d{2}))\Z", re.ASCII)

def _valid_date(year, month, day):
    return 1 <= month <= 12 and 1 <= day <= calendar.monthrange(year, month)[1]

def _format_ok(fmt, value):
    """RFC 3339 full-date / date-time, calendar-checked, stdlib only."""
    if fmt == "date":
        m = _DATE.match(value)
        return bool(m) and _valid_date(*map(int, m.groups()))
    m = _DATE_TIME.match(value)
    if not m:
        return False
    year, month, day, hour, minute, second = map(int, m.groups()[:6])
    if not _valid_date(year, month, day) or hour > 23 or minute > 59 or second > 59:
        return False
    if m.group(7):
        return int(m.group(8)) <= 23 and int(m.group(9)) <= 59
    return True

def _ref_name(ref, definitions):
    """The $defs entry a supported local reference names, else None."""
    if not isinstance(ref, str) or not ref.startswith(LOCAL_REF_PREFIX):
        return None
    name = ref[len(LOCAL_REF_PREFIX):]
    if not name or any(c in name for c in "/~%#") or name not in definitions:
        return None
    return name

def _ref_targets(spec):
    """Names referenced from spec without crossing into $defs (iterative)."""
    names, stack = set(), [spec]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            ref = node.get("$ref")
            if isinstance(ref, str) and ref.startswith(LOCAL_REF_PREFIX):
                names.add(ref[len(LOCAL_REF_PREFIX):])
            stack.extend(v for k, v in node.items() if k != ROOT_DEFINITIONS and isinstance(v, (dict, list)))
        elif isinstance(node, list):
            stack.extend(v for v in node if isinstance(v, (dict, list)))
    return names

def _ref_cycle(definitions):
    """True when any $defs entry reaches itself through references."""
    edges = {name: _ref_targets(spec) & definitions.keys() for name, spec in definitions.items()}
    for start in edges:
        seen, stack = set(), list(edges[start])
        while stack:
            name = stack.pop()
            if name == start:
                return True
            if name not in seen:
                seen.add(name)
                stack.extend(edges[name])
    return False

def _preflight_root(schema, error):
    definitions = schema.get(ROOT_DEFINITIONS, {}) if isinstance(schema, dict) else {}
    if not isinstance(definitions, dict) or any(not isinstance(k, str) for k in definitions):
        error([ROOT_DEFINITIONS], "INVALID_DEFINITIONS")
        definitions = {}
    elif _ref_cycle(definitions):
        error([ROOT_DEFINITIONS], "REF_CYCLE")
    _preflight(schema, [], error, definitions=definitions)
    for name in sorted(definitions):
        _preflight(definitions[name], [ROOT_DEFINITIONS, name], error, 1, definitions)

def _preflight(spec, path, error, depth=0, definitions=None):
    """Check every reachable subschema, including branches the instance never visits."""
    definitions = {} if definitions is None else definitions
    if depth > MAX_SCHEMA_DEPTH or not isinstance(spec, dict):
        error(path, "INVALID_SCHEMA_OR_DEPTH")
        return
    allowed = SUPPORTED | ANNOTATIONS | (ROOT_IDENTITY | {ROOT_DEFINITIONS} if depth == 0 else set())
    for key in sorted(spec.keys() - allowed):
        error(path, "UNSUPPORTED_KEYWORD:" + key)
    if depth == 0 and "$schema" in spec and spec["$schema"] != REFERENCE_DIALECT_URI:
        error(path, "UNSUPPORTED_DIALECT_URI")
    if depth == 0 and "$id" in spec and not isinstance(spec["$id"], str):
        error(path, "INVALID_IDENTITY:$id")
    types = spec.get("type")
    if types is not None:
        choices = types if isinstance(types, list) else [types]
        if not choices or any(not isinstance(t, str) or t not in TYPES for t in choices):
            error(path, "UNSUPPORTED_TYPE")
    if "required" in spec and (not isinstance(spec["required"], list) or
        any(not isinstance(k, str) for k in spec["required"]) or
        len(spec["required"]) != len(set(k for k in spec["required"] if isinstance(k, str)))):
        error(path, "INVALID_REQUIRED")
    if "enum" in spec and (not isinstance(spec["enum"], list) or not spec["enum"]):
        error(path, "INVALID_ENUM")
    extra = spec.get("additionalProperties")
    if isinstance(extra, dict):
        _preflight(extra, path + ["additionalProperties"], error, depth + 1, definitions)
    elif "additionalProperties" in spec and type(extra) is not bool:
        error(path, "UNSUPPORTED_ADDITIONAL_PROPERTIES")
    for key in ("minProperties", "maxProperties"):
        if key in spec and (type(spec[key]) is not int or spec[key] < 0):
            error(path, "INVALID_BOUND:" + key)
    for key in ("minLength", "maxLength"):
        if key in spec and (type(spec[key]) is not int or spec[key] < 0):
            error(path, "INVALID_BOUND:" + key)
    for key in ("minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum"):
        if key in spec and type(spec[key]) not in (int, float):
            error(path, "INVALID_BOUND:" + key)
    if "$ref" in spec and _ref_name(spec["$ref"], definitions) is None:
        error(path, "UNSUPPORTED_REF")
    for key in BRANCH_LISTS:
        if key in spec:
            if not isinstance(spec[key], list) or not spec[key]:
                error(path, "INVALID_" + key.upper())
            else:
                for i, sub in enumerate(spec[key]):
                    _preflight(sub, path + [key, i], error, depth + 1, definitions)
    for key in ("minContains", "maxContains"):
        if key in spec and (type(spec[key]) is not int or spec[key] < 0):
            error(path, "INVALID_BOUND:" + key)
    for key in ("if", "then", "else", "not", "propertyNames", "contains"):
        if key in spec:
            _preflight(spec[key], path + [key], error, depth + 1, definitions)
    for key in ("minItems", "maxItems"):
        if key in spec and (type(spec[key]) is not int or spec[key] < 0):
            error(path, "INVALID_BOUND:" + key)
    if "uniqueItems" in spec and type(spec["uniqueItems"]) is not bool:
        error(path, "INVALID_BOUND:uniqueItems")
    if "format" in spec and spec["format"] not in SUPPORTED_FORMATS:
        error(path, "UNSUPPORTED_FORMAT")
    if "pattern" in spec:
        reason = _pattern_subset_error(spec["pattern"])
        if reason:
            error(path, reason)
    for key in ("title", "description", "$comment"):
        if key in spec and not isinstance(spec[key], str):
            error(path, "INVALID_ANNOTATION:" + key)
    if "examples" in spec and not isinstance(spec["examples"], list):
        error(path, "INVALID_ANNOTATION:examples")
    props = spec.get("properties", {})
    if not isinstance(props, dict) or any(not isinstance(k, str) for k in props):
        error(path, "INVALID_PROPERTIES")
    else:
        for k in sorted(props):
            _preflight(props[k], path + ["properties", k], error, depth + 1, definitions)
    if "prefixItems" in spec:
        if not isinstance(spec["prefixItems"], list) or not spec["prefixItems"]:
            error(path, "INVALID_PREFIXITEMS")
        else:
            for i, sub in enumerate(spec["prefixItems"]):
                _preflight(sub, path + ["prefixItems", i], error, depth + 1, definitions)
    if "items" in spec and not (spec["items"] is False and "prefixItems" in spec):
        _preflight(spec["items"], path + ["items"], error, depth + 1, definitions)

def _admit_schema(schema, schema_digest, dialect, registry):
    def refused(code):
        return {"valid": False, "errors": [{"path": "", "code": code}], "authority_effect": "NONE"}
    if dialect != DIALECT or registry is not None:
        return refused("UNSUPPORTED_DIALECT_OR_REGISTRY")
    try:
        actual = hashlib.sha256(canonical_bytes(schema)).hexdigest()
    except (TypeError, ValueError, RecursionError):
        # RecursionError: nesting beyond the encoder's stack is refused, never raised.
        return refused("INVALID_SCHEMA_ENCODING")
    if actual != schema_digest:
        return refused("SCHEMA_DIGEST_MISMATCH")
    errors = []
    _preflight_root(schema, lambda path, code: errors.append({"path": pointer(path), "code": code}))
    return {"valid": not errors, "errors": errors, "schema_digest": actual, "dialect": dialect, "authority_effect": "NONE"}

def _indeterminate(code):
    """Error codes that mean the schema could not be evaluated, as opposed to the instance failing it."""
    return (code in ("EVALUATION_BUDGET_EXCEEDED", "INVALID_SCHEMA_OR_DEPTH", "INVALID_OBJECT_SCHEMA")
            or code.startswith(("UNSUPPORTED_", "INVALID_")))

def check_schema(schema, schema_digest, dialect=DIALECT, registry=None):
    """Schema validity alone, independent of any instance. Returns findings, not ALLOW."""
    return _admit_schema(schema, schema_digest, dialect, registry)

def validate(instance, schema, schema_digest, dialect=DIALECT, registry=None):
    """Returns structural findings, not ALLOW. Unknown features fail closed."""
    admitted = _admit_schema(schema, schema_digest, dialect, registry)
    if admitted["errors"]:
        return admitted
    actual = admitted["schema_digest"]
    finding = _instance_finding(instance)
    if finding is not None:
        return {"valid": False, "errors": [finding], "schema_digest": actual, "dialect": dialect, "authority_effect": "NONE"}
    errors = []
    definitions = schema.get(ROOT_DEFINITIONS, {})
    budget = [MAX_EVALUATION_STEPS]
    def visit(value, spec, path, depth=0, sink=errors):
        def error(where, code):
            sink.append({"path": pointer(where), "code": code})
        budget[0] -= 1
        if budget[0] < 0:
            error(path, "EVALUATION_BUDGET_EXCEEDED")
            return
        if depth > MAX_SCHEMA_DEPTH or not isinstance(spec, dict):
            error(path, "INVALID_SCHEMA_OR_DEPTH")
            return
        for key in sorted(spec.keys() - SUPPORTED - ANNOTATIONS - (ROOT_IDENTITY | {ROOT_DEFINITIONS} if depth == 0 else set())):
            error(path, "UNSUPPORTED_KEYWORD:" + key)
        if "$ref" in spec:
            visit(value, definitions[_ref_name(spec["$ref"], definitions)], path, depth + 1, sink)
        for sub in spec.get("allOf", []):
            visit(value, sub, path, depth + 1, sink)
        def passes(sub, subject=value):
            """Evaluate one branch in isolation: True or False, or None when the branch could
            not be evaluated (budget, depth, unsupported or invalid schema). An indeterminate
            branch propagates its structural errors; it never counts as an ordinary failure,
            so not / else / anyOf can never fail open on it."""
            trial = []
            visit(subject, sub, path, depth + 1, trial)
            structural = [e for e in trial if _indeterminate(e["code"])]
            if structural:
                seen = {(e["path"], e["code"]) for e in sink}
                for e in structural:
                    if (e["path"], e["code"]) not in seen:
                        seen.add((e["path"], e["code"]))
                        sink.append(e)
                return None
            return not trial
        for key, code in (("anyOf", "ANYOF"), ("oneOf", "ONEOF")):
            if key in spec:
                outcomes = [passes(sub) for sub in spec[key]]
                if None not in outcomes and ((key == "anyOf" and not any(outcomes)) or
                                             (key == "oneOf" and outcomes.count(True) != 1)):
                    error(path, code)
        if "not" in spec and passes(spec["not"]) is True:
            error(path, "NOT")
        if "if" in spec:
            outcome = passes(spec["if"])
            if outcome is True and "then" in spec:
                visit(value, spec["then"], path, depth + 1, sink)
            elif outcome is False and "else" in spec:
                visit(value, spec["else"], path, depth + 1, sink)
        types = spec.get("type")
        if types is not None:
            choices = types if isinstance(types, list) else [types]
            if not choices or any(not isinstance(t, str) or t not in TYPES for t in choices):
                error(path, "UNSUPPORTED_TYPE")
                return
            if not any(TYPES[t](value) for t in choices):
                error(path, "TYPE")
                return
        if "const" in spec and not json_equal(value, spec["const"]):
            error(path, "CONST")
        if "enum" in spec:
            if not isinstance(spec["enum"], list):
                error(path, "INVALID_ENUM")
            elif not any(json_equal(value, member) for member in spec["enum"]):
                error(path, "ENUM")
        if isinstance(value, dict):
            props = spec.get("properties", {})
            required = spec.get("required", [])
            if not isinstance(props, dict) or not isinstance(required, list) or any(not isinstance(k, str) for k in required):
                error(path, "INVALID_OBJECT_SCHEMA")
                return
            for k in sorted(required):
                if k not in value:
                    error(path + [k], "REQUIRED")
            extra = spec.get("additionalProperties", True)
            if not isinstance(extra, dict) and type(extra) is not bool:
                error(path, "UNSUPPORTED_ADDITIONAL_PROPERTIES")
            for k in sorted(value):
                if k in props:
                    visit(value[k], props[k], path + [k], depth + 1, sink)
                elif extra is False:
                    error(path + [k], "ADDITIONAL_PROPERTY")
                elif isinstance(extra, dict):
                    visit(value[k], extra, path + [k], depth + 1, sink)
            if "propertyNames" in spec:
                for k in sorted(value):
                    visit(k, spec["propertyNames"], path + [k], depth + 1, sink)
            if "minProperties" in spec and len(value) < spec["minProperties"]:
                error(path, "MINPROPERTIES")
            if "maxProperties" in spec and len(value) > spec["maxProperties"]:
                error(path, "MAXPROPERTIES")
        if isinstance(value, list):
            prefix = spec.get("prefixItems", [])
            for i, sub in enumerate(prefix[:len(value)]):
                visit(value[i], sub, path + [i], depth + 1, sink)
            rest = spec.get("items")
            if rest is False and prefix:
                for i in range(len(prefix), len(value)):
                    error(path + [i], "ITEMS")
            elif "items" in spec:
                for i in range(len(prefix), len(value)):
                    visit(value[i], rest, path + [i], depth + 1, sink)
        if isinstance(value, list) and "contains" in spec:
            outcomes = [passes(spec["contains"], item) for item in value]
            if None not in outcomes:
                matched = outcomes.count(True)
                if matched < spec.get("minContains", 1):
                    error(path, "CONTAINS")
                elif "maxContains" in spec and matched > spec["maxContains"]:
                    error(path, "MAXCONTAINS")
        if isinstance(value, list):
            if "minItems" in spec and len(value) < spec["minItems"]:
                error(path, "MINITEMS")
            if "maxItems" in spec and len(value) > spec["maxItems"]:
                error(path, "MAXITEMS")
            if spec.get("uniqueItems") is True:
                seen = set()
                for item in value:
                    key = _equality_key(item)
                    if key in seen:
                        error(path, "UNIQUE_ITEMS")
                        break
                    seen.add(key)
        if isinstance(value, str) and spec.get("format") in SUPPORTED_FORMATS and not _format_ok(spec["format"], value):
            error(path, "FORMAT")
        if isinstance(value, str) and "pattern" in spec:
            if len(value) > MAX_PATTERN_INPUT_LENGTH:
                error(path, "PATTERN_INPUT_TOO_LONG")
            elif not _pattern_matches(spec["pattern"], value):
                error(path, "PATTERN")
        if type(value) in (int, float):
            if type(spec.get("exclusiveMinimum")) in (int, float) and not value > spec["exclusiveMinimum"]:
                error(path, "EXCLUSIVEMINIMUM")
            if type(spec.get("exclusiveMaximum")) in (int, float) and not value < spec["exclusiveMaximum"]:
                error(path, "EXCLUSIVEMAXIMUM")
        for key, kind in (("minLength", str), ("maxLength", str), ("minimum", (int, float)), ("maximum", (int, float))):
            if key not in spec:
                continue
            bound = spec[key]
            if key.endswith("Length"):
                if type(bound) is not int or bound < 0:
                    error(path, "INVALID_BOUND:" + key)
                elif isinstance(value, str) and ((key == "minLength" and len(value) < bound) or (key == "maxLength" and len(value) > bound)):
                    error(path, key.upper())
            elif type(bound) not in (int, float):
                error(path, "INVALID_BOUND:" + key)
            elif type(value) in (int, float) and ((key == "minimum" and value < bound) or (key == "maximum" and value > bound)):
                error(path, key.upper())
    visit(instance, schema, [])
    return {"valid": not errors, "errors": errors, "schema_digest": actual, "dialect": dialect, "authority_effect": "NONE"}
