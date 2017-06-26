# Format of templates #

Files must be of type OpenDocumentText,
i.e. mimetype=application/vnd.oasis.opendocument.text

Fields can be specified as `@@field@@` or opendocument user fields

For images, a dummy image must be inserted in the template,
with suitable attributes (width, height, etc.)

# Format of data to merge #

Files must be in csv format. A proper sniffing is made to allow
for various delimiters.

Fields to contain image file names or image URLs **must** start
with `img_`.

Association between images and document are done in the order of
appearance of image elements in the document, with no concern to the
field name.
