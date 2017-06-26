# Purpose of py-odf-report #

The program **py-odf-report** aims to make it easy to output
series of documents made with a template text and a set of data, which
can contain text or images (as references). In year 2017, this is quite
hard to make it directly with LibreOffice : inserting texts from a database
is easy, but image references are not resolved, neither turned into
image insertion.

## Format of templates ##

Files must be of type OpenDocumentText,
i.e. mimetype=application/vnd.oasis.opendocument.text

Fields can be specified as `@@field@@` or opendocument user fields

For images, a dummy image must be inserted in the template,
with suitable attributes (width, height, etc.)

## Format of data to merge ##

Files must be in csv format. A proper sniffing is made to allow
for various delimiters.

Fields to contain image file names or image URLs **must** start
with `img_`.

Association between images and document are done in the order of
appearance of image elements in the document, with no concern to the
field name.

## Output of the program ##

the program will write a set of files, with a file name like
`out_xxxx.odt`, xxxx being a four-digit number

# CREDITS #

  * © 2017, Georges Khaznadar <georgesk@debian.org>
  
# LICENSE #

  * GPL-3+
  
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

  
