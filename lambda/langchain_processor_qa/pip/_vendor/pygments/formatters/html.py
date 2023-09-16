"""
    pygments.formatters.html
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Formatter for HTML output.

    :copyright: Copyright 2006-2022 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import functools
import os
import sys
import os.path
from io import StringIO

from pip._vendor.pygments.formatter import Formatter
from pip._vendor.pygments.token import Token, Text, STANDARD_TYPES
from pip._vendor.pygments.util import get_bool_opt, get_int_opt, get_list_opt

try:
    import ctags
except ImportError:
    ctags = None

__all__ = ['HtmlFormatter']


_escape_html_table = {
    ord('&'): '&amp;',
    ord('<'): '&lt;',
    ord('>'): '&gt;',
    ord('"'): '&quot;',
    ord("'"): '&#39;',
}


def escape_html(text, table=_escape_html_table):
    """Escape &, <, > as well as single and double quotes for HTML."""
    return text.translate(table)


def webify(color):
    if color.startswith('calc') or color.startswith('var'):
        return color
    else:
        return '#' + color


def _get_ttype_class(ttype):
    fname = STANDARD_TYPES.get(ttype)
    if fname:
        return fname
    aname = ''
    while fname is None:
        aname = '-' + ttype[-1] + aname
        ttype = ttype.parent
        fname = STANDARD_TYPES.get(ttype)
    return fname + aname


CSSFILE_TEMPLATE = '''\
/*
generated by Pygments <https://pygments.org/>
Copyright 2006-2022 by the Pygments team.
Licensed under the BSD license, see LICENSE for details.
*/
%(styledefs)s
'''

DOC_HEADER = '''\
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
   "http://www.w3.org/TR/html4/strict.dtd">
<!--
generated by Pygments <https://pygments.org/>
Copyright 2006-2022 by the Pygments team.
Licensed under the BSD license, see LICENSE for details.
-->
<html>
<head>
  <title>%(title)s</title>
  <meta http-equiv="content-type" content="text/html; charset=%(encoding)s">
  <style type="text/css">
''' + CSSFILE_TEMPLATE + '''
  </style>
</head>
<body>
<h2>%(title)s</h2>

'''

DOC_HEADER_EXTERNALCSS = '''\
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
   "http://www.w3.org/TR/html4/strict.dtd">

<html>
<head>
  <title>%(title)s</title>
  <meta http-equiv="content-type" content="text/html; charset=%(encoding)s">
  <link rel="stylesheet" href="%(cssfile)s" type="text/css">
</head>
<body>
<h2>%(title)s</h2>

'''

DOC_FOOTER = '''\
</body>
</html>
'''


class HtmlFormatter(Formatter):
    r"""
    Format tokens as HTML 4 ``<span>`` tags within a ``<pre>`` tag, wrapped
    in a ``<div>`` tag. The ``<div>``'s CSS class can be set by the `cssclass`
    option.

    If the `linenos` option is set to ``"table"``, the ``<pre>`` is
    additionally wrapped inside a ``<table>`` which has one row and two
    cells: one containing the line numbers and one containing the code.
    Example:

    .. sourcecode:: html

        <div class="highlight" >
        <table><tr>
          <td class="linenos" title="click to toggle"
            onclick="with (this.firstChild.style)
                     { display = (display == '') ? 'none' : '' }">
            <pre>1
            2</pre>
          </td>
          <td class="code">
            <pre><span class="Ke">def </span><span class="NaFu">foo</span>(bar):
              <span class="Ke">pass</span>
            </pre>
          </td>
        </tr></table></div>

    (whitespace added to improve clarity).

    Wrapping can be disabled using the `nowrap` option.

    A list of lines can be specified using the `hl_lines` option to make these
    lines highlighted (as of Pygments 0.11).

    With the `full` option, a complete HTML 4 document is output, including
    the style definitions inside a ``<style>`` tag, or in a separate file if
    the `cssfile` option is given.

    When `tagsfile` is set to the path of a ctags index file, it is used to
    generate hyperlinks from names to their definition.  You must enable
    `lineanchors` and run ctags with the `-n` option for this to work.  The
    `python-ctags` module from PyPI must be installed to use this feature;
    otherwise a `RuntimeError` will be raised.

    The `get_style_defs(arg='')` method of a `HtmlFormatter` returns a string
    containing CSS rules for the CSS classes used by the formatter. The
    argument `arg` can be used to specify additional CSS selectors that
    are prepended to the classes. A call `fmter.get_style_defs('td .code')`
    would result in the following CSS classes:

    .. sourcecode:: css

        td .code .kw { font-weight: bold; color: #00FF00 }
        td .code .cm { color: #999999 }
        ...

    If you have Pygments 0.6 or higher, you can also pass a list or tuple to the
    `get_style_defs()` method to request multiple prefixes for the tokens:

    .. sourcecode:: python

        formatter.get_style_defs(['div.syntax pre', 'pre.syntax'])

    The output would then look like this:

    .. sourcecode:: css

        div.syntax pre .kw,
        pre.syntax .kw { font-weight: bold; color: #00FF00 }
        div.syntax pre .cm,
        pre.syntax .cm { color: #999999 }
        ...

    Additional options accepted:

    `nowrap`
        If set to ``True``, don't wrap the tokens at all, not even inside a ``<pre>``
        tag. This disables most other options (default: ``False``).

    `full`
        Tells the formatter to output a "full" document, i.e. a complete
        self-contained document (default: ``False``).

    `title`
        If `full` is true, the title that should be used to caption the
        document (default: ``''``).

    `style`
        The style to use, can be a string or a Style subclass (default:
        ``'default'``). This option has no effect if the `cssfile`
        and `noclobber_cssfile` option are given and the file specified in
        `cssfile` exists.

    `noclasses`
        If set to true, token ``<span>`` tags (as well as line number elements)
        will not use CSS classes, but inline styles. This is not recommended
        for larger pieces of code since it increases output size by quite a bit
        (default: ``False``).

    `classprefix`
        Since the token types use relatively short class names, they may clash
        with some of your own class names. In this case you can use the
        `classprefix` option to give a string to prepend to all Pygments-generated
        CSS class names for token types.
        Note that this option also affects the output of `get_style_defs()`.

    `cssclass`
        CSS class for the wrapping ``<div>`` tag (default: ``'highlight'``).
        If you set this option, the default selector for `get_style_defs()`
        will be this class.

        .. versionadded:: 0.9
           If you select the ``'table'`` line numbers, the wrapping table will
           have a CSS class of this string plus ``'table'``, the default is
           accordingly ``'highlighttable'``.

    `cssstyles`
        Inline CSS styles for the wrapping ``<div>`` tag (default: ``''``).

    `prestyles`
        Inline CSS styles for the ``<pre>`` tag (default: ``''``).

        .. versionadded:: 0.11

    `cssfile`
        If the `full` option is true and this option is given, it must be the
        name of an external file. If the filename does not include an absolute
        path, the file's path will be assumed to be relative to the main output
        file's path, if the latter can be found. The stylesheet is then written
        to this file instead of the HTML file.

        .. versionadded:: 0.6

    `noclobber_cssfile`
        If `cssfile` is given and the specified file exists, the css file will
        not be overwritten. This allows the use of the `full` option in
        combination with a user specified css file. Default is ``False``.

        .. versionadded:: 1.1

    `linenos`
        If set to ``'table'``, output line numbers as a table with two cells,
        one containing the line numbers, the other the whole code.  This is
        copy-and-paste-friendly, but may cause alignment problems with some
        browsers or fonts.  If set to ``'inline'``, the line numbers will be
        integrated in the ``<pre>`` tag that contains the code (that setting
        is *new in Pygments 0.8*).

        For compatibility with Pygments 0.7 and earlier, every true value
        except ``'inline'`` means the same as ``'table'`` (in particular, that
        means also ``True``).

        The default value is ``False``, which means no line numbers at all.

        **Note:** with the default ("table") line number mechanism, the line
        numbers and code can have different line heights in Internet Explorer
        unless you give the enclosing ``<pre>`` tags an explicit ``line-height``
        CSS property (you get the default line spacing with ``line-height:
        125%``).

    `hl_lines`
        Specify a list of lines to be highlighted. The line numbers are always
        relative to the input (i.e. the first line is line 1) and are
        independent of `linenostart`.

        .. versionadded:: 0.11

    `linenostart`
        The line number for the first line (default: ``1``).

    `linenostep`
        If set to a number n > 1, only every nth line number is printed.

    `linenospecial`
        If set to a number n > 0, every nth line number is given the CSS
        class ``"special"`` (default: ``0``).

    `nobackground`
        If set to ``True``, the formatter won't output the background color
        for the wrapping element (this automatically defaults to ``False``
        when there is no wrapping element [eg: no argument for the
        `get_syntax_defs` method given]) (default: ``False``).

        .. versionadded:: 0.6

    `lineseparator`
        This string is output between lines of code. It defaults to ``"\n"``,
        which is enough to break a line inside ``<pre>`` tags, but you can
        e.g. set it to ``"<br>"`` to get HTML line breaks.

        .. versionadded:: 0.7

    `lineanchors`
        If set to a nonempty string, e.g. ``foo``, the formatter will wrap each
        output line in an anchor tag with an ``id`` (and `name`) of ``foo-linenumber``.
        This allows easy linking to certain lines.

        .. versionadded:: 0.9

    `linespans`
        If set to a nonempty string, e.g. ``foo``, the formatter will wrap each
        output line in a span tag with an ``id`` of ``foo-linenumber``.
        This allows easy access to lines via javascript.

        .. versionadded:: 1.6

    `anchorlinenos`
        If set to `True`, will wrap line numbers in <a> tags. Used in
        combination with `linenos` and `lineanchors`.

    `tagsfile`
        If set to the path of a ctags file, wrap names in anchor tags that
        link to their definitions. `lineanchors` should be used, and the
        tags file should specify line numbers (see the `-n` option to ctags).

        .. versionadded:: 1.6

    `tagurlformat`
        A string formatting pattern used to generate links to ctags definitions.
        Available variables are `%(path)s`, `%(fname)s` and `%(fext)s`.
        Defaults to an empty string, resulting in just `#prefix-number` links.

        .. versionadded:: 1.6

    `filename`
        A string used to generate a filename when rendering ``<pre>`` blocks,
        for example if displaying source code. If `linenos` is set to
        ``'table'`` then the filename will be rendered in an initial row
        containing a single `<th>` which spans both columns.

        .. versionadded:: 2.1

    `wrapcode`
        Wrap the code inside ``<pre>`` blocks using ``<code>``, as recommended
        by the HTML5 specification.

        .. versionadded:: 2.4

    `debug_token_types`
        Add ``title`` attributes to all token ``<span>`` tags that show the
        name of the token.

        .. versionadded:: 2.10


    **Subclassing the HTML formatter**

    .. versionadded:: 0.7

    The HTML formatter is now built in a way that allows easy subclassing, thus
    customizing the output HTML code. The `format()` method calls
    `self._format_lines()` which returns a generator that yields tuples of ``(1,
    line)``, where the ``1`` indicates that the ``line`` is a line of the
    formatted source code.

    If the `nowrap` option is set, the generator is the iterated over and the
    resulting HTML is output.

    Otherwise, `format()` calls `self.wrap()`, which wraps the generator with
    other generators. These may add some HTML code to the one generated by
    `_format_lines()`, either by modifying the lines generated by the latter,
    then yielding them again with ``(1, line)``, and/or by yielding other HTML
    code before or after the lines, with ``(0, html)``. The distinction between
    source lines and other code makes it possible to wrap the generator multiple
    times.

    The default `wrap()` implementation adds a ``<div>`` and a ``<pre>`` tag.

    A custom `HtmlFormatter` subclass could look like this:

    .. sourcecode:: python

        class CodeHtmlFormatter(HtmlFormatter):

            def wrap(self, source, *, include_div):
                return self._wrap_code(source)

            def _wrap_code(self, source):
                yield 0, '<code>'
                for i, t in source:
                    if i == 1:
                        # it's a line of formatted code
                        t += '<br>'
                    yield i, t
                yield 0, '</code>'

    This results in wrapping the formatted lines with a ``<code>`` tag, where the
    source lines are broken using ``<br>`` tags.

    After calling `wrap()`, the `format()` method also adds the "line numbers"
    and/or "full document" wrappers if the respective options are set. Then, all
    HTML yielded by the wrapped generator is output.
    """

    name = 'HTML'
    aliases = ['html']
    filenames = ['*.html', '*.htm']

    def __init__(self, **options):
        Formatter.__init__(self, **options)
        self.title = self._decodeifneeded(self.title)
        self.nowrap = get_bool_opt(options, 'nowrap', False)
        self.noclasses = get_bool_opt(options, 'noclasses', False)
        self.classprefix = options.get('classprefix', '')
        self.cssclass = self._decodeifneeded(options.get('cssclass', 'highlight'))
        self.cssstyles = self._decodeifneeded(options.get('cssstyles', ''))
        self.prestyles = self._decodeifneeded(options.get('prestyles', ''))
        self.cssfile = self._decodeifneeded(options.get('cssfile', ''))
        self.noclobber_cssfile = get_bool_opt(options, 'noclobber_cssfile', False)
        self.tagsfile = self._decodeifneeded(options.get('tagsfile', ''))
        self.tagurlformat = self._decodeifneeded(options.get('tagurlformat', ''))
        self.filename = self._decodeifneeded(options.get('filename', ''))
        self.wrapcode = get_bool_opt(options, 'wrapcode', False)
        self.span_element_openers = {}
        self.debug_token_types = get_bool_opt(options, 'debug_token_types', False)

        if self.tagsfile:
            if not ctags:
                raise RuntimeError('The "ctags" package must to be installed '
                                   'to be able to use the "tagsfile" feature.')
            self._ctags = ctags.CTags(self.tagsfile)

        linenos = options.get('linenos', False)
        if linenos == 'inline':
            self.linenos = 2
        elif linenos:
            # compatibility with <= 0.7
            self.linenos = 1
        else:
            self.linenos = 0
        self.linenostart = abs(get_int_opt(options, 'linenostart', 1))
        self.linenostep = abs(get_int_opt(options, 'linenostep', 1))
        self.linenospecial = abs(get_int_opt(options, 'linenospecial', 0))
        self.nobackground = get_bool_opt(options, 'nobackground', False)
        self.lineseparator = options.get('lineseparator', '\n')
        self.lineanchors = options.get('lineanchors', '')
        self.linespans = options.get('linespans', '')
        self.anchorlinenos = get_bool_opt(options, 'anchorlinenos', False)
        self.hl_lines = set()
        for lineno in get_list_opt(options, 'hl_lines', []):
            try:
                self.hl_lines.add(int(lineno))
            except ValueError:
                pass

        self._create_stylesheet()

    def _get_css_class(self, ttype):
        """Return the css class of this token type prefixed with
        the classprefix option."""
        ttypeclass = _get_ttype_class(ttype)
        if ttypeclass:
            return self.classprefix + ttypeclass
        return ''

    def _get_css_classes(self, ttype):
        """Return the CSS classes of this token type prefixed with the classprefix option."""
        cls = self._get_css_class(ttype)
        while ttype not in STANDARD_TYPES:
            ttype = ttype.parent
            cls = self._get_css_class(ttype) + ' ' + cls
        return cls or ''

    def _get_css_inline_styles(self, ttype):
        """Return the inline CSS styles for this token type."""
        cclass = self.ttype2class.get(ttype)
        while cclass is None:
            ttype = ttype.parent
            cclass = self.ttype2class.get(ttype)
        return cclass or ''

    def _create_stylesheet(self):
        t2c = self.ttype2class = {Token: ''}
        c2s = self.class2style = {}
        for ttype, ndef in self.style:
            name = self._get_css_class(ttype)
            style = ''
            if ndef['color']:
                style += 'color: %s; ' % webify(ndef['color'])
            if ndef['bold']:
                style += 'font-weight: bold; '
            if ndef['italic']:
                style += 'font-style: italic; '
            if ndef['underline']:
                style += 'text-decoration: underline; '
            if ndef['bgcolor']:
                style += 'background-color: %s; ' % webify(ndef['bgcolor'])
            if ndef['border']:
                style += 'border: 1px solid %s; ' % webify(ndef['border'])
            if style:
                t2c[ttype] = name
                # save len(ttype) to enable ordering the styles by
                # hierarchy (necessary for CSS cascading rules!)
                c2s[name] = (style[:-2], ttype, len(ttype))

    def get_style_defs(self, arg=None):
        """
        Return CSS style definitions for the classes produced by the current
        highlighting style. ``arg`` can be a string or list of selectors to
        insert before the token type classes.
        """
        style_lines = []

        style_lines.extend(self.get_linenos_style_defs())
        style_lines.extend(self.get_background_style_defs(arg))
        style_lines.extend(self.get_token_style_defs(arg))

        return '\n'.join(style_lines)

    def get_token_style_defs(self, arg=None):
        prefix = self.get_css_prefix(arg)

        styles = [
            (level, ttype, cls, style)
            for cls, (style, ttype, level) in self.class2style.items()
            if cls and style
        ]
        styles.sort()

        lines = [
            '%s { %s } /* %s */' % (prefix(cls), style, repr(ttype)[6:])
            for (level, ttype, cls, style) in styles
        ]

        return lines

    def get_background_style_defs(self, arg=None):
        prefix = self.get_css_prefix(arg)
        bg_color = self.style.background_color
        hl_color = self.style.highlight_color

        lines = []

        if arg and not self.nobackground and bg_color is not None:
            text_style = ''
            if Text in self.ttype2class:
                text_style = ' ' + self.class2style[self.ttype2class[Text]][0]
            lines.insert(
                0, '%s{ background: %s;%s }' % (
                    prefix(''), bg_color, text_style
                )
            )
        if hl_color is not None:
            lines.insert(
                0, '%s { background-color: %s }' % (prefix('hll'), hl_color)
            )

        return lines

    def get_linenos_style_defs(self):
        lines = [
            'pre { %s }' % self._pre_style,
            'td.linenos .normal { %s }' % self._linenos_style,
            'span.linenos { %s }' % self._linenos_style,
            'td.linenos .special { %s }' % self._linenos_special_style,
            'span.linenos.special { %s }' % self._linenos_special_style,
        ]

        return lines

    def get_css_prefix(self, arg):
        if arg is None:
            arg = ('cssclass' in self.options and '.'+self.cssclass or '')
        if isinstance(arg, str):
            args = [arg]
        else:
            args = list(arg)

        def prefix(cls):
            if cls:
                cls = '.' + cls
            tmp = []
            for arg in args:
                tmp.append((arg and arg + ' ' or '') + cls)
            return ', '.join(tmp)

        return prefix

    @property
    def _pre_style(self):
        return 'line-height: 125%;'

    @property
    def _linenos_style(self):
        return 'color: %s; background-color: %s; padding-left: 5px; padding-right: 5px;' % (
            self.style.line_number_color,
            self.style.line_number_background_color
        )

    @property
    def _linenos_special_style(self):
        return 'color: %s; background-color: %s; padding-left: 5px; padding-right: 5px;' % (
            self.style.line_number_special_color,
            self.style.line_number_special_background_color
        )

    def _decodeifneeded(self, value):
        if isinstance(value, bytes):
            if self.encoding:
                return value.decode(self.encoding)
            return value.decode()
        return value

    def _wrap_full(self, inner, outfile):
        if self.cssfile:
            if os.path.isabs(self.cssfile):
                # it's an absolute filename
                cssfilename = self.cssfile
            else:
                try:
                    filename = outfile.name
                    if not filename or filename[0] == '<':
                        # pseudo files, e.g. name == '<fdopen>'
                        raise AttributeError
                    cssfilename = os.path.join(os.path.dirname(filename),
                                               self.cssfile)
                except AttributeError:
                    print('Note: Cannot determine output file name, '
                          'using current directory as base for the CSS file name',
                          file=sys.stderr)
                    cssfilename = self.cssfile
            # write CSS file only if noclobber_cssfile isn't given as an option.
            try:
                if not os.path.exists(cssfilename) or not self.noclobber_cssfile:
                    with open(cssfilename, "w") as cf:
                        cf.write(CSSFILE_TEMPLATE %
                                 {'styledefs': self.get_style_defs('body')})
            except OSError as err:
                err.strerror = 'Error writing CSS file: ' + err.strerror
                raise

            yield 0, (DOC_HEADER_EXTERNALCSS %
                      dict(title=self.title,
                           cssfile=self.cssfile,
                           encoding=self.encoding))
        else:
            yield 0, (DOC_HEADER %
                      dict(title=self.title,
                           styledefs=self.get_style_defs('body'),
                           encoding=self.encoding))

        yield from inner
        yield 0, DOC_FOOTER

    def _wrap_tablelinenos(self, inner):
        dummyoutfile = StringIO()
        lncount = 0
        for t, line in inner:
            if t:
                lncount += 1
            dummyoutfile.write(line)

        fl = self.linenostart
        mw = len(str(lncount + fl - 1))
        sp = self.linenospecial
        st = self.linenostep
        anchor_name = self.lineanchors or self.linespans
        aln = self.anchorlinenos
        nocls = self.noclasses

        lines = []

        for i in range(fl, fl+lncount):
            print_line = i % st == 0
            special_line = sp and i % sp == 0

            if print_line:
                line = '%*d' % (mw, i)
                if aln:
                    line = '<a href="#%s-%d">%s</a>' % (anchor_name, i, line)
            else:
                line = ' ' * mw

            if nocls:
                if special_line:
                    style = ' style="%s"' % self._linenos_special_style
                else:
                    style = ' style="%s"' % self._linenos_style
            else:
                if special_line:
                    style = ' class="special"'
                else:
                    style = ' class="normal"'

            if style:
                line = '<span%s>%s</span>' % (style, line)

            lines.append(line)

        ls = '\n'.join(lines)

        # If a filename was specified, we can't put it into the code table as it
        # would misalign the line numbers. Hence we emit a separate row for it.
        filename_tr = ""
        if self.filename:
            filename_tr = (
                '<tr><th colspan="2" class="filename">'
                '<span class="filename">' + self.filename + '</span>'
                '</th></tr>')

        # in case you wonder about the seemingly redundant <div> here: since the
        # content in the other cell also is wrapped in a div, some browsers in
        # some configurations seem to mess up the formatting...
        yield 0, (f'<table class="{self.cssclass}table">' + filename_tr +
            '<tr><td class="linenos"><div class="linenodiv"><pre>' +
            ls + '</pre></div></td><td class="code">')
        yield 0, '<div>'
        yield 0, dummyoutfile.getvalue()
        yield 0, '</div>'
        yield 0, '</td></tr></table>'
        

    def _wrap_inlinelinenos(self, inner):
        # need a list of lines since we need the width of a single number :(
        inner_lines = list(inner)
        sp = self.linenospecial
        st = self.linenostep
        num = self.linenostart
        mw = len(str(len(inner_lines) + num - 1))
        anchor_name = self.lineanchors or self.linespans
        aln = self.anchorlinenos
        nocls = self.noclasses

        for _, inner_line in inner_lines:
            print_line = num % st == 0
            special_line = sp and num % sp == 0

            if print_line:
                line = '%*d' % (mw, num)
            else:
                line = ' ' * mw

            if nocls:
                if special_line:
                    style = ' style="%s"' % self._linenos_special_style
                else:
                    style = ' style="%s"' % self._linenos_style
            else:
                if special_line:
                    style = ' class="linenos special"'
                else:
                    style = ' class="linenos"'

            if style:
                linenos = '<span%s>%s</span>' % (style, line)
            else:
                linenos = line

            if aln:
                yield 1, ('<a href="#%s-%d">%s</a>' % (anchor_name, num, linenos) +
                          inner_line)
            else:
                yield 1, linenos + inner_line
            num += 1

    def _wrap_lineanchors(self, inner):
        s = self.lineanchors
        # subtract 1 since we have to increment i *before* yielding
        i = self.linenostart - 1
        for t, line in inner:
            if t:
                i += 1
                href = "" if self.linenos else ' href="#%s-%d"' % (s, i)
                yield 1, '<a id="%s-%d" name="%s-%d"%s></a>' % (s, i, s, i, href) + line
            else:
                yield 0, line

    def _wrap_linespans(self, inner):
        s = self.linespans
        i = self.linenostart - 1
        for t, line in inner:
            if t:
                i += 1
                yield 1, '<span id="%s-%d">%s</span>' % (s, i, line)
            else:
                yield 0, line

    def _wrap_div(self, inner):
        style = []
        if (self.noclasses and not self.nobackground and
                self.style.background_color is not None):
            style.append('background: %s' % (self.style.background_color,))
        if self.cssstyles:
            style.append(self.cssstyles)
        style = '; '.join(style)

        yield 0, ('<div' + (self.cssclass and ' class="%s"' % self.cssclass) +
                  (style and (' style="%s"' % style)) + '>')
        yield from inner
        yield 0, '</div>\n'

    def _wrap_pre(self, inner):
        style = []
        if self.prestyles:
            style.append(self.prestyles)
        if self.noclasses:
            style.append(self._pre_style)
        style = '; '.join(style)

        if self.filename and self.linenos != 1:
            yield 0, ('<span class="filename">' + self.filename + '</span>')

        # the empty span here is to keep leading empty lines from being
        # ignored by HTML parsers
        yield 0, ('<pre' + (style and ' style="%s"' % style) + '><span></span>')
        yield from inner
        yield 0, '</pre>'

    def _wrap_code(self, inner):
        yield 0, '<code>'
        yield from inner
        yield 0, '</code>'

    @functools.lru_cache(maxsize=100)
    def _translate_parts(self, value):
        """HTML-escape a value and split it by newlines."""
        return value.translate(_escape_html_table).split('\n')

    def _format_lines(self, tokensource):
        """
        Just format the tokens, without any wrapping tags.
        Yield individual lines.
        """
        nocls = self.noclasses
        lsep = self.lineseparator
        tagsfile = self.tagsfile

        lspan = ''
        line = []
        for ttype, value in tokensource:
            try:
                cspan = self.span_element_openers[ttype]
            except KeyError:
                title = ' title="%s"' % '.'.join(ttype) if self.debug_token_types else ''
                if nocls:
                    css_style = self._get_css_inline_styles(ttype)
                    if css_style:
                        css_style = self.class2style[css_style][0]
                        cspan = '<span style="%s"%s>' % (css_style, title)
                    else:
                        cspan = ''
                else:
                    css_class = self._get_css_classes(ttype)
                    if css_class:
                        cspan = '<span class="%s"%s>' % (css_class, title)
                    else:
                        cspan = ''
                self.span_element_openers[ttype] = cspan

            parts = self._translate_parts(value)

            if tagsfile and ttype in Token.Name:
                filename, linenumber = self._lookup_ctag(value)
                if linenumber:
                    base, filename = os.path.split(filename)
                    if base:
                        base += '/'
                    filename, extension = os.path.splitext(filename)
                    url = self.tagurlformat % {'path': base, 'fname': filename,
                                               'fext': extension}
                    parts[0] = "<a href=\"%s#%s-%d\">%s" % \
                        (url, self.lineanchors, linenumber, parts[0])
                    parts[-1] = parts[-1] + "</a>"

            # for all but the last line
            for part in parts[:-1]:
                if line:
                    # Also check for part being non-empty, so we avoid creating
                    # empty <span> tags
                    if lspan != cspan and part:
                        line.extend(((lspan and '</span>'), cspan, part,
                                     (cspan and '</span>'), lsep))
                    else:  # both are the same, or the current part was empty
                        line.extend((part, (lspan and '</span>'), lsep))
                    yield 1, ''.join(line)
                    line = []
                elif part:
                    yield 1, ''.join((cspan, part, (cspan and '</span>'), lsep))
                else:
                    yield 1, lsep
            # for the last line
            if line and parts[-1]:
                if lspan != cspan:
                    line.extend(((lspan and '</span>'), cspan, parts[-1]))
                    lspan = cspan
                else:
                    line.append(parts[-1])
            elif parts[-1]:
                line = [cspan, parts[-1]]
                lspan = cspan
            # else we neither have to open a new span nor set lspan

        if line:
            line.extend(((lspan and '</span>'), lsep))
            yield 1, ''.join(line)

    def _lookup_ctag(self, token):
        entry = ctags.TagEntry()
        if self._ctags.find(entry, token.encode(), 0):
            return entry['file'], entry['lineNumber']
        else:
            return None, None

    def _highlight_lines(self, tokensource):
        """
        Highlighted the lines specified in the `hl_lines` option by
        post-processing the token stream coming from `_format_lines`.
        """
        hls = self.hl_lines

        for i, (t, value) in enumerate(tokensource):
            if t != 1:
                yield t, value
            if i + 1 in hls:  # i + 1 because Python indexes start at 0
                if self.noclasses:
                    style = ''
                    if self.style.highlight_color is not None:
                        style = (' style="background-color: %s"' %
                                 (self.style.highlight_color,))
                    yield 1, '<span%s>%s</span>' % (style, value)
                else:
                    yield 1, '<span class="hll">%s</span>' % value
            else:
                yield 1, value

    def wrap(self, source):
        """
        Wrap the ``source``, which is a generator yielding
        individual lines, in custom generators. See docstring
        for `format`. Can be overridden.
        """

        output = source
        if self.wrapcode:
            output = self._wrap_code(output)
        
        output = self._wrap_pre(output)
    
        return output

    def format_unencoded(self, tokensource, outfile):
        """
        The formatting process uses several nested generators; which of
        them are used is determined by the user's options.

        Each generator should take at least one argument, ``inner``,
        and wrap the pieces of text generated by this.

        Always yield 2-tuples: (code, text). If "code" is 1, the text
        is part of the original tokensource being highlighted, if it's
        0, the text is some piece of wrapping. This makes it possible to
        use several different wrappers that process the original source
        linewise, e.g. line number generators.
        """
        source = self._format_lines(tokensource)

        # As a special case, we wrap line numbers before line highlighting
        # so the line numbers get wrapped in the highlighting tag.
        if not self.nowrap and self.linenos == 2:
            source = self._wrap_inlinelinenos(source)

        if self.hl_lines:
            source = self._highlight_lines(source)

        if not self.nowrap:
            if self.lineanchors:
                source = self._wrap_lineanchors(source)
            if self.linespans:
                source = self._wrap_linespans(source)
            source = self.wrap(source)
            if self.linenos == 1:
                source = self._wrap_tablelinenos(source)
            source = self._wrap_div(source)
            if self.full:
                source = self._wrap_full(source, outfile)

        for t, piece in source:
            outfile.write(piece)
