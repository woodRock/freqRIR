# Sphinx 

## Stubbing 

We need to create a `.rst` file stub for each module we want to see in the documentation. This can be done with the `sphinx-apidoc` command. This generated a stub for each module that is specified in the `modules.rst` file. Should a module containing python docstring, in Google Docstring format, the sphinx `autodoc` extensions will automatically generated the documentation from the source code. However, we need to stub each module manually. This can be done as follows ([source](https://samnicholls.net/2016/06/15/how-to-sphinx-readthedocs/))

```bash
cd docs/
sphinx-apidoc -o source/ ../freqrir
```
