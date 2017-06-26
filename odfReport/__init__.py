"""
Project py-odf-report
© 2017 Georges Khaznadar <georgesk@debian.org>
This project aims to make it easy to generate reports or multiple
documents from one ODF template and values coming from a database.
Values can be numbers, strings, dates, images.
"""

from odf import opendocument, text, draw, element
from copy import deepcopy
from urllib import request
from urllib.error import URLError
import re, os.path, csv

__counter=1 # counter for file names; defaults to 1 when beginning

class TemplateText:
    """
    implements a template text, and provides methods to do something
    with it
    """
    __counter=0 # static counter for file names
    
    def __init__(self, filename):
        self.original=opendocument.load(filename)
        assert self.original.mimetype == "application/vnd.oasis.opendocument.text"
        TemplateText.__counter=1 # counter for file names; defaults to 1 when beginning
        self.makeCopy()
        return

    def __str__(self):
        return "Template object{ Fields: %s, Frames: %s}" % \
            (self.fields, self.frames)

    def makeCopy(self):
        """
        updates self.document, self.fields and self.name
        from self.original
        """
        self.document=deepcopy(self.original)
        self.fields=self.findFields1()
        self.frames=self.findFrames()
        return
    
    def findFields1(self):
        """
        return a dictionary field name => textNode,
        which allow one to find where to replace a field by a value.
        The syntax for fields is: @@fieldname@@
        """
        nodes=[]
        for p in self.document.getElementsByType(text.P):
            for n in p.childNodes:
                if n.nodeType==element.Node.TEXT_NODE:
                    nodes.append(n)
        result={}
        for n in nodes:
            pattern=re.compile(r"@@([^@]+)@@")
            found=pattern.findall(n.data)
            for f in found:
                result[f]=n
        return result

    def findFrames(self):
        """
        return a list of the draw:frame elements
        """
        return self.document.body.getElementsByType(draw.Frame)

    def replaceFields(self, dico={}, images=[]):
        """
        @param dico a dictionary (key => value)
        @param images a list of filenames or URIs for images
        replaces fields in the generated document when their names
        match a key in dico; then replaces the images in their
        order of appearance.
        """
        for k in dico:
            if k in self.fields:
                new=str(self.fields[k]).replace("@@%s@@" %k, dico[k])
                # replace the text data of the node
                self.fields[k].data=new

        for f,i in zip(self.frames, images):
            # f is a draw.Frame, i is an image filename or URL
            #
            # use self.addPictureFromString(bytes content, string mediatype)
            # then create a node draw:image with attributes
            #    xlink:href pointing to the added picture,
            #    xlink:type = "simple"
            #    xlink:show = "embed"
            #    xlink:actuate = "onLoad"
            # and replace the child nodes of the frame
            djangoUrl=re.compile(
                r'^(?:http|ftp)s?://' # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
                r'localhost|' #localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
                r'(?::\d+)?' # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            imageOK=False
            if os.path.exists(i):
                href=self.document.addPictureFromFile(i, mediatype="image/png")
                imageOK=True
            if djangoUrl.match(i):
                try:
                    with request.urlopen(i) as feed:
                        mediatype=feed.info()["Content-Type"]
                        href=self.document.addPictureFromString(feed.read(), mediatype)
                        if mediatype.startswith("image/"):
                            imageOK=True
                except URLError as e:
                    print("%s; %s not downloaded." % (e,i))
            if imageOK:
                f.childNodes=[]
                f.addElement(draw.Image(href=href))
        return

    def save(self):
        """
        saves the current document
        @return the saved file name
        """
        filename="out_%04d.odt" %  TemplateText.__counter
        self.document.save(filename)
        TemplateText.__counter += 1
        return filename

class Reporter:
    """
    This class is to build reports
    """

    def __init__(self, templatePath, dataPath):
        """
        The constructor.
        @param templatePath filename to build self.template
        @param dataPath filename to build self.dictReader
        """
        self.template=TemplateText(templatePath)
        self.csvfile=open(dataPath)
        dialect = csv.Sniffer().sniff(self.csvfile.read(1024))
        self.csvfile.seek(0)
        self.dictReader=csv.DictReader(self.csvfile, dialect=dialect)

    def run(self):
        """
        make the report
        @return the list of saved files
        """
        saved=[]
        for row in self.dictReader:
            self.template.makeCopy()
            self.template.replaceFields(
                row,
                [row[i] for i in row if i.startswith("img_")]
                )
            saved.append(self.template.save())
        return saved
