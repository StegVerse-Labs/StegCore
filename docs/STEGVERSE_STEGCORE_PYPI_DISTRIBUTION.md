# StegVerse StegCore PyPI distribution identity

The canonical source package remains `stegcore` and the Python import namespace remains `stegcore`.

For public package distribution, the immutable PyPI distribution name is:

```text
stegverse-stegcore
```

The release workflow verifies the canonical source identity first, then applies only this deterministic distribution-name substitution in the isolated build workspace before producing the wheel and sdist. No runtime module, source package path, version, or behavior is renamed.

Therefore:

```bash
pip install stegverse-stegcore==0.3.0
```

continues to provide:

```python
import stegcore
```

This avoids collision with the unrelated existing PyPI project named `stegcore` while preserving the StegCore source/runtime identity.