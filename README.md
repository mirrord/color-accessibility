# color-accessibility
a tool for identifying images, or regions in images, that present difficulties for colorblind individuals.
Specifically, this tool checks text/background pairs (in images and PDFs) for WGAC20 AA compliance.

### installation
download this package, then:
```
cd color-accessibility
pip install .
```

### usage:
```
python -m color-accessibility --[image|pdf] <path to file>
```

