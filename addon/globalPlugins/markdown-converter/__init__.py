# markdown to html, complemento de NVDA que funciona para convertir texto en formato markdown a formato html.
# Este archivo está cubierto por la Licencia Pública General GNU
# Consulte el archivo COPYING.txt para obtener más detalles.
# Copyrigth (C) 2024 Marco Leija <marcomolinaleija@hotmail.com>


import globalPluginHandler
import globalVars
import addonHandler
addonHandler.initTranslation()
import scriptHandler
from api import getClipData, copyToClip
from ui import message
import wx
import os
import sys
dirLib = os.path.dirname(__file__)
sys.path.append(os.path.join(dirLib, "lib"))
import mistune
mistune.__path__.append(os.path.join(dirLib, "lib", "mistune"))
del sys.path[-2:]

markdown_converter = mistune.create_markdown()

def disableInSecureMode(decoratedCls):
    if globalVars.appArgs.secure:
        return globalPluginHandler.GlobalPlugin
    return decoratedCls
@disableInSecureMode
class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    @scriptHandler.script(
        #Translators: This is the description of what the keyboard shortcut will do. Takes the text from the clipboard to convert it to html (It will only convert what follows the appropriate syntax)
        description=_("Toma del portapapeles el texto para convertirlo a html (Solo convertirá lo que siga la sintaxis adecuada)."),
        gesture="kb:NVDA+alt+M",
        # Translators: Category name of the addon
        category=_("Convertor markdown a html")
    )

    def script_convert_from_clipboard(self, gesture):
        text_to_convert = getClipData()
        text_html = markdown_converter(text_to_convert)
        copyToClip(text_html)
        # Translators: This message announces that the conversion has been successful
        message(_("Texto convertido exitosamente"))

    @scriptHandler.script(
        # Translators: This is the description of the key shortcut to convert from a text file with .md extension
        description=_("Abre un diálogo que permite la selección de un archivo .md,  markdown"),
        gesture="kb:NVDA+shift+alt+F",
        # Translators: category name of the addon
        category=_("Convertor markdown a html")
    )

    def script_openMarkdownDialog(self, gesture):
        wx.CallAfter(self.asyncOpenMarkdownDialog)

    def asyncOpenMarkdownDialog(self):
        wildcard = "*.md|*.md"
        with wx.FileDialog(None, "Seleccione un archivo Markdown", wildcard=wildcard,
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            filePath = fileDialog.GetPath()
            wx.CallAfter(self.processMarkdownFile, filePath)

    def processMarkdownFile(self, filePath):
        try:
            with open(filePath, 'r', encoding='utf-8') as file:
                markdownContent = file.read()
            htmlContent = markdown_converter(markdownContent)
            wx.CallAfter(copyToClip, htmlContent)
            # Translators: This message announces that the conversion has been successful
            wx.CallAfter(wx.MessageBox, _("Archivo Markdown convertido y copiado exitosamente al portapapeles"), _("Información:"), wx.OK | wx.ICON_INFORMATION)
        except IOError:
            # Translators: If an error occurs during the conversion, the following message will inform you.
            wx.CallAfter(wx.MessageBox, _("Nó ha sido posible abrir el archivo seleccionado"), _("Error:"), wx.OK | wx.ICON_ERROR)