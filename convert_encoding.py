#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Convert text files between arbitrary encodings and line endings.

Usage:
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
"""


"""
   Copyright (C) 2007  Michael Goerz

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import codecs
import getopt
import os
import os.path
import locale
import shutil



def main():
    """Command line program for converting encodings and end-of-lines """
    #
    # command line parsing / initialization
    global warn
    try:
        opts, files = getopt.getopt(sys.argv[1:], "hf:t:e:o:rlqnd",
                                                 ["help", "from=", "to=","eol=",
                                                  "recursive", "followlinks",
                                                  "quiet", "nocodec", "out=",
                                                  "dotfiles"])
    except getopt.GetoptError, details:
        warn(details)
        exit(2)
    locale.setlocale(locale.LC_ALL, '')
    from_enc = locale.getpreferredencoding()
    to_enc = locale.getpreferredencoding()
    eol = os.linesep
    recursive = False
    followlinks = False
    dotfiles = False
    guess = False
    nocodec = False
    outfilename = ""
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        if o in ("-f", "--from"):
            if a == 'guess':
                guess = True
            else:
                from_enc = a
        if o in ("-t", "--to"):
            to_enc = a
        if o in ("-o", "--out"):
            outfilename = os.path.normcase(a)
        if o in ("-r", "--recursive"):
            recursive = True
        if o in ("-d", "--dotfiles"):
            dotfiles = True
        if o in ("-q", "--quiet"):
            warn = no_warn
        if o in ("-n", "--nocodec"):
            nocodec = True
        if o in ("-e", "--eol"):
            eolmode = a.lower()
            os_eols = {'unix':"\n",
                       'linux':"\n",
                       'dos':"\r\n",
                       'win':"\r\n",
                       'mac':"\r"}
            try:
                eol = os_eols[eolmode]
            except KeyError:
                warn("'%s' is not a valid name for a line ending." % eolmode)
                warn("Use 'unix', 'linux', 'dos', 'win', or 'mac'.")
                warn("Converting to your default line ending")
        if o in ("-l", "--followlinks"):
            recursive = True
        if o in ("-l", "--followlinks"):
            followlinks = True
    #
    # put together what we actually have to do
    if nocodec:
        rec_function = lambda infilename: convert_eol(infilename, eol, \
                                          outfilename.replace('#', infilename))
    else:
        if guess:
            warn("WARNING: guessing the input encoding is dangerous. "
                  + "Make sure to check the results.\n")
            rec_function = lambda infilename: \
                               convert_encoding(
                                   infilename,
                                   guess_file_encoding(infilename, from_enc),
                                   to_enc,
                                   eol,
                                   outfilename.replace('#', infilename))
        else:
           rec_function = lambda infilename: \
                              convert_encoding(
                                  infilename,
                                  from_enc,
                                  to_enc,
                                  eol,
                                  outfilename.replace('#', infilename))
    #
    # Run through all the files
    file_recursor(rec_function, files, recursive, followlinks, dotfiles)


def warn(msg, nl=True):
    """ print a warning message to stderr """
    sys.stderr.write(str(msg))
    if nl: sys.stderr.write("\n")

def no_warn(msg, nl=True):
    pass



def file_recursor(function=None, file_list=(), recurse=True, 
                  followlinks=True, dotfiles=False):
    """ Call function(file) for each file in file_list.

        If recurse is True, go into directories recursively. If followlinks is
        True, follow symbolic links. If dotfiles is true, process all files and 
        dirs beginning with a dot, if they are in a subdirectory that is
        processed recursively.
        
        Notice that even when dotfiles is True, you still have to explicitly
        put dotfiles in your initial filelist.

        All names in the file_list will be fully expanded as a glob and with
        environment variables
    """
    from glob import glob
    for name in file_list:
        name = os.path.expanduser(name)
        name = os.path.expandvars(name)
        name = os.path.normpath(name)
        if len(glob(name)) > 1:
            file_recursor(function, glob(name), recurse, followlinks)
            continue
        elif len(glob(name)) == 1:
            name = glob(name)[0]
        if os.path.islink(name):
            if not followlinks:
                warn("'%s' is a symlink, but following links is not activated" \
                       % name)
                continue
            else:
                name = os.readlink(name)
        if os.path.isfile(name):
            function(name)
        elif os.path.isdir(name):
            if name != '..':
                if recurse:
                    file_recursor(function, glob(os.path.join(name, '*')), 
                                  recurse, followlinks)
                    if dotfiles:
                        file_recursor(function, glob(os.path.join(name, '.*')), 
                                      recurse, followlinks)
                else:
                    warn("'%s' is a directory, but recursive handling is not activated" % name)
        else:
            warn("Can't process '%s'. Not found.\n" % name)
            continue


def convert_encoding(infilename, from_enc, to_enc, eol=os.linesep, 
                     outfilename=""):
    """ Convert a text file from_enc to_enc

        If eol is given, it must be an appropriate string to terminate a line,
        i.e. "\\n", "\\r\\n", "\\r". It defaults to the standard line ending
        for your OS (os.linesep)

        If outfilename is given, the results will be written to that file, if
        not, the conversion is done in-place

        from_enc and to_enc are strings containing a name for any
        encoding known to Python. See
        http://docs.python.org/lib/standard-encodings.html
    """

    def error_cleanup():
        if hasattr(infile, 'close'):
            infile.close()
        if hasattr(outfile, 'close'):
            outfile.close()
        if os.path.isfile(outfilename) and os.path.isfile(infilename):
            os.remove(outfilename)

    warn("Processing %s ...  " % infilename, nl=False)
    if os.path.isfile(infilename):
        #
        # choose temp file
        tempfilename = infilename + "." + to_enc
        while os.path.isfile(tempfilename):
            tempfilename = tempfilename + "x"
        #
        # open original file (infile) and tempfile (outfile)
        infile = outfile = None
        try:
            infile = codecs.open(infilename, "rb", from_enc)
        except Exception, details:
            warn("Error opening %s: %s" % (infilename, details));
            error_cleanup()
            return None
        try:
            outfile = codecs.open(tempfilename, "wb", to_enc)
        except Exception, details:
            warn("Error opening %s: %s" % (tempfilename, details))
            error_cleanup()
            return None
        #
        # go through infile, convert, and write to outfile
        try:
            for line in infile:
                try:
                    line = line.replace("\r\n", "\n") # win
                    line = line.replace("\r", "\n") # mac
                    line = line.replace("\n", eol)
                    outfile.write(line)
                except Exception, details:
                    raise Exception, "Error writing to %s: %s" \
                                     % (tempfilename, details);
        except Exception, details:
            warn("Error in I/O: %s" % details)
            error_cleanup()
        else:
            #
            # Finish up: overwrite original file with tempfile
            try:
                infile.close()
                outfile.close()
                shutil.copystat(infilename, tempfilename)
                overwrite = False
                if outfilename == "":
                    outfilename = infilename
                    overwrite = True
                rename_file(tempfilename, outfilename, overwrite)
                warn("%s was successfully converted from %s to %s" \
                      % (infilename, from_enc, to_enc))
                warn("") # finish a block
            except Exception, details:
                warn("Renaming %s to %s FAILED. File was not converted: %s" \
                      % (tempfilename, infilename, details))
                error_cleanup()
                warn("") # finish a block
            

    else:
        warn("File '%s' does not exist\n" % file)


def convert_eol(infilename, eol=os.linesep, outfilename=""):
    """ Convert just the end of line of a textfile

        If eol is given, it must be an appropriate string to terminate a line,
        i.e. "\\n", "\\r\\n", "\\r". It defaults to the standard line ending
        for your os (os.linesep)

        If outfilename is given, the results will be written to that file, if
        not, the conversion is done in-place

        The encoding of the file is left untouched
    """
    def error_cleanup():
        if hasattr(infile, 'close'):
            infile.close()
        if hasattr(outfile, 'close'):
            outfile.close()
        if os.path.isfile(tempfilename) and os.path.isfile(infilename):
            os.remove(tempfilename)

    warn("Processing %s ...  " % infilename, nl=False)
    if os.path.isfile(infilename):
        #
        # choose temp file
        tempfilename = infilename + "." + "eol"
        while os.path.isfile(tempfilename):
            tempfilename = tempfilename + "x"
        #
        # open original file (infile) and tempfile (outfile)
        infile = outfile = None
        try:
            infile = open(infilename, "rb")
        except Exception, details:
            warn("Error opening %s: %s" % (infilename, details));
            error_cleanup()
            return None
        try:
            outfile = open(tempfilename, "wb")
        except Exception, details:
            warn("Error opening %s: %s" % (tempfilename, details))
            error_cleanup()
            return None
        #
        # go through infile, convert, and write to outfile
        try:
            for line in infile:
                try:
                    if "\x00\r" in line or "\x00\n" in line:
                        eol = eol.replace("\r", "\x00\r")
                        eol = eol.replace("\n", "\x00\n")
                    line = line.replace("\r\n", "\n") # win
                    line = line.replace("\x00\r\x00\n", "\n") # utf16 win
                    line = line.replace("\r", "\n") # mac
                    line = line.replace("\x00\r", "\n") # utf16 mac
                    line = line.replace("\x00\n", "\n") # utf16 unix
                    line = line.replace("\n", eol)
                    outfile.write(line)
                except Exception, details:
                    raise Exception, "Error writing to %s: %s" \
                                      % (tempfilename, details);
        except Exception, details:
            warn("Error in I/O: %s" % details)
            error_cleanup()
        else:
            #
            # Finish up: overwrite original file with tempfile
            try:
                infile.close()
                outfile.close()
                shutil.copystat(infilename, tempfilename)
                overwrite = False
                if outfilename == "":
                    outfilename = infilename
                    overwrite = True
                rename_file(tempfilename, outfilename, overwrite)
                warn("Successfully converted eol for %s" % infilename)
                warn("") # finish a block
            except Exception, details:
                warn("Renaming %s to %s FAILED. File was not converted: %s" \
                      % (tempfilename, infilename, details))
                error_cleanup()
                warn("") # finish a block

    else:
        warn("File '%s' does not exist\n" % file)





def guess_encoding(data):
    """ Given a byte string, attempt to decode it.

        Taken from:
        http://www.pyzine.com/Issue008/Section_Articles/article_Encodings.html#guessing-the-encoding

        Tries the standard 'UTF8' and 'latin-1' encodings,
        Plus several gathered from locale information.

        The calling program *must* first call
            locale.setlocale(locale.LC_ALL, '')

        If successful it returns
            (decoded_unicode, successful_encoding)
        If unsuccessful it raises a ``UnicodeError``
    """
    successful_encoding = None
    # we make 'utf-8' the first encoding
    encodings = ['utf-8']
    #
    # next we add anything we can learn from the locale
    try:
        encodings.append(locale.nl_langinfo(locale.CODESET))
    except AttributeError:
        pass
    try:
        encodings.append(locale.getlocale()[1])
    except (AttributeError, IndexError):
        pass
    try:
        encodings.append(locale.getdefaultlocale()[1])
    except (AttributeError, IndexError):
        pass
    #
    # we try try the rest now
    encodings = encodings + ['latin-1', 'mbcs', 'big5', 'euc_jp', 'euc_kr',
                             'gb2312', 'gbk', 'gb18030', 'hz', 'iso2022_jp',
                             'koi8_u', 'ptcp154', 'shift_jis' ]
    for enc in encodings:
        # some of the locale calls
        # may have returned None
        if not enc:
            continue
        try:
            decoded = unicode(data, enc)
            successful_encoding = enc

        except (UnicodeError, LookupError):
            pass
        else:
            break
    if not successful_encoding:
         raise UnicodeError(
        'Unable to decode input data.  Tried the following encodings: %s.'
        % ', '.join([repr(enc) for enc in encodings if enc]))
    else:
         return (decoded, successful_encoding)



def guess_file_encoding(filename, default):
    """ Guess the encoding of a text file

        If the function is able to guess an encoding for filename, return that
        encoding, otherwise return the default.

        Note that guessing an encoding is not fool-proof, this might return the
        wrong encoding.

        Adapted from:
        http://www.pyzine.com/Issue008/Section_Articles/article_Encodings.html#guessing-the-encoding
    """
    try:
        f = open(filename, "rb")
        the_text = f.read()
        f.close()
    except Exception, details:
        warn("Error while trying to guess the encoding of file %s: %s" \
              % (filename, details))
        return default

    bomdict = { codecs.BOM_UTF8 : 'UTF8',
                codecs.BOM_UTF16_BE : 'UTF-16BE',
                codecs.BOM_UTF16_LE : 'UTF-16LE' }

    # check if there is Unicode signature
    for bom, encoding in bomdict.items():
        if the_text.startswith(bom):
            the_text = the_text[len(bom):]
            break
        else:
            bom  = None
            encoding = None

    if encoding is None:    # there was no BOM
        try:
            unicode_text, encoding = guess_encoding(the_text)
        except UnicodeError:
            warn("Can't work out the encoding of file '%s'." % filename)
            warn("Assuming the default encoding: %s" % default)
            return default
    warn("Guessed encoding for file '%s': %s" % (filename, encoding))
    return encoding



def rename_file(file1, file2, overwrite=False):
    """ Rename file1 to file2, ask for directions if file2 already exists """
    if os.path.isfile(file1):
        if os.path.isfile(file2):
            while not overwrite:
                answer = raw_input("%s already exists. Do you want to overwrite? Yes [No] Abort: " \
                                    % file2).lower()
                if answer == 'yes':
                    overwrite = True
                elif answer == 'abort':
                    return None
                else:
                    answer = raw_input("Enter a new filename: ")
                    if answer != '': file2 = os.path.normcase(answer)
                    if not os.path.isfile(file2):
                        overwrite = True
            if file2 != file1: os.remove(file2)
        try:
            os.rename(file1, file2)
        except Exception, details:
            warn( "Failed to rename %s to %s: %s" % (file1, file2, details) )



def usage():
    """ Print usage for main program """
    print __doc__


if __name__ == "__main__":
    main()
