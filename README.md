# Genesis Documentation

1. Create a clean env using python 3.10, install Sphinx and other dependencies

```bash
# In Genesis-dev/
pip install -e ".[docs]"
```

2. Build the documentation and watch the change lively

```bash
# In doc/
rm -rf build/; make html; sphinx-autobuild ./source ./build/html
# zh_CN
rm -rf build/; make html; sphinx-autobuild -b html -E -a -q -z zh_CN ./source ./build/html

```