
Command line tool to pack iOS app into IPA file.

It's a python implementation of Apple version PackageApplication which was written in Perl.

# Installation #

Please make sure your Python is v3.7 or above.

```bash
python3 --version
python3 -m pip install ipa-pack
```

Or, clone from GitHub:
```bash
git clone https://github.com/floatinghotpot/ipa-pack.git
cd ipa-pack
python3 -m pip install -e .
```

# How To Use #

```bash
PackageApplication /path/to/app -o /path/to/ipa_file
```

Example:
```bash
PackageApplication /path/to/myapp.app -o myapp.ipa
```

More options:
```bash
PackageApplication [-s signature] application [-o output_directory]
    [-verbose] [-plugin plugin] || -man || -help

    Options:
        -s <signature>  certificate name to resign application before packaging
        -o              specify output filename
        -plugin         specify an optional plugin
        -help           brief help message
        -man            full documentation
        -v[erbose]      provide details during operation
```

# How It Works #

Apple recommend to use `xcodebuild -exportArchive` and remove it from xcode installation, but actually the command itself is very useful.

So here I write a python implementation of Apple version PackageApplication which was written in Perl.

# Credits #

A simple tool created by Raymond Xie, to pack iOS app to IPA with command line.

Any comments are welcome.
