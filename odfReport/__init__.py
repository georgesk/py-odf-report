"""
Project py-odf-report
© 2017 Georges Khaznadar <georgesk@debian.org>
This project aims to make it easy to generate reports or multiple
documents from one ODF template and values coming from a database.
Values can be numbers, strings, dates, images.

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

from odf import opendocument, text, draw, element
from copy import deepcopy
from urllib import request
from urllib.error import URLError
import re, os.path, csv, subprocess

__counter=1 # counter for file names; defaults to 1 when beginning

fieldNamePattern=re.compile(r"@@([^@]+)@@")

djangoUrl=re.compile(
    r'^(?:http|ftp)s?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
    r'localhost|' #localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

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
        self.frames=self.findFrames1()
        return
    
    def findFields1(self):
        """
        @return a dictionary field name => textNode,
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
            found=fieldNamePattern.findall(n.data)
            for f in found:
                result[f]=n
        return result

    def findFrames1(self):
        """
        Searches frames which contain one text-box child, and another
        frame in their subtree. The attribute svg:height is born by
        the inner frame and also as fo:min-height attribute of the
        text-box.
        @return a dictionary field name => (frame, width, height)
        """
        allFrames= self.document.body.getElementsByType(draw.Frame)
        frames=[f for f in allFrames if f.getElementsByType(draw.Frame) and f.getElementsByType(draw.TextBox)]
        dico={}
        for f in frames:
            m=fieldNamePattern.match(str(f))# field name from the legend
            if m:
                fieldName=m.group(1)
                innerFrame=f.getElementsByType(draw.Frame)[1] # not f itself
                dico[fieldName]=(f,
                             innerFrame.getAttribute("width"),
                             innerFrame.getAttribute("height"),
                )
        return dico

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
            if k in self.frames:
                # self.frames[k] is a tuple (frame, width, height)
                # dico[k] is an image filename or URL
                # use self.addPictureFromString(bytes content, string mediatype)
                imageOK=False
                if os.path.exists(dico[k]): # an image filename
                    mediatype=subprocess.run("file --mime-type %s" % dico[k],
                                             stdout=subprocess.PIPE,
                    ).stdout
                    href=self.document.addPictureFromFile(dico[k], mediatype=mediatype)
                    imageOK=True
                if djangoUrl.match(dico[k]):
                    try:
                        with request.urlopen(dico[k]) as feed:
                            mediatype=feed.info()["Content-Type"]
                            href=self.document.addPictureFromString(feed.read(), mediatype)
                            if mediatype.startswith("image/"):
                                imageOK=True
                    except URLError as e:
                        print("%s; %s not downloaded." % (e,dico[k]))
                if imageOK:
                    f,w,h=self.frames[k]
                    f.setAttribute("width",w)
                    f.setAttribute("height",h)
                    f.childNodes=[]                     # drop all children
                    f.addElement(draw.Image(href=href)) # insert the image
                else:
                    print("ERROR: bad image %s" % dico[k])
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
