# convert_encoding.py

[http://github.com/goerz/convert_encoding.py](http://github.com/goerz/convert_encoding.py)

Author: [Michael Goerz](http://michaelgoerz.net)

Convert text files between arbitrary encodings and line endings.

This code is licensed under the [GPL](http://www.gnu.org/licenses/gpl.html)

## Install ##

Store the `convert_encoding.py` script anywhere in your `$PATH`.

## Usage ##

    convert_encoding.py [options] file1 file2 ...

    Options are:
        -f enc,  --from=enc    the input encoding
                               (default: locale.getpreferredencoding())
                               Set this to 'guess' if the encoding is unknown.
        -t enc,  --to=enc      the output encoding
                               (default: locale.getpreferredencoding())
        -e code, --eol=code    the end-of-line mode (see below)
        -o file, --out=file    where to write the converted data. Conversion is
                               done in-place if this is omitted
        -n, --nocodec          ignore input and output encoding, just process eol
        -r, --recursive        go into directories recursively
        -l, --followlinks      follow symbolic links
        -d, --dotfiles         in combination with -r: process files that begin
                               with a dot, if they are found in a directory reached
                               by recursion. You still have to specify dotfiles
                               explicitly in the initial filelist.
        -q, --quiet            don't display warnings or status messages

    For valid encoding names, see
    http://docs.python.org/lib/standard-encodings.html

    Accepted values for the eol code are: 'unix', 'linux', 'dos', 'win', 'mac'.
    If you do not specify an end-of-line, it will be set to your system's default,
    regardless of the original end-of-line.

    Any '#' in the out-filename will be replaced with the full name of the input
    file.

    Note that guessing the input encoding is not foolproof in any way. Always
    provide an explicit input encoding if you can.

    The program supports full unix style globbing on all operation systems,
    independently of your shell's capabilities. Also, environment variables
    and '~' will be expanded following the usual conventions.

    The file may also be used as a module from python.
