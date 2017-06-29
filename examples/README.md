# Format of templates #

Files must be of type OpenDocumentText,
i.e. mimetype=application/vnd.oasis.opendocument.text

Fields can be specified as `@@field@@`.

For images, a dummy image must be inserted in the template,
with suitable attributes (width, height, etc.); then a legend
must be appended to the image, with the field name as `@@field@@`.

# Format of data to merge #

Files must be in csv format. A proper sniffing is made to allow
for various delimiters.

Fields to contain image file names or image URLs will be interpreted
as images only when a dummy image in the template document bears
the field name in its legend (as `@@field@@`).

# Examples #

## Three pages with: given name, surname, photo ##

  * data file = `examples/data.csv`
  * template text = `examples/sample1.odt`

