import wx
import wx.adv

class AboutDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="About This App", size=(350, 250), style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP)

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Description text
        about_text = wx.StaticText(panel, label=(
            "Barcode Generator\n"
            "Version 1.0.0\n\n"
            "This is an open-source project.\n"
            "You can support the project financially below:"
        ))
        about_text.Wrap(300)
        vbox.Add(about_text, 0, wx.ALL | wx.LEFT | wx.TOP, 15)

        # Clickable Buy Me a Coffee link
        coffee_link = wx.adv.HyperlinkCtrl(panel, id=wx.ID_ANY,
                                           label="Buy Me a Coffee ☕",
                                           url="https://buymeacoffee.com/tosin789")
        vbox.Add(coffee_link, 0, wx.ALL | wx.LEFT, 15)

        # Copyright
        copyright_text = wx.StaticText(
            panel, 
            label="© 2025 Oluwatosin Joseph Durodola"
        )
        vbox.Add(copyright_text, 0, wx.ALL | wx.LEFT | wx.TOP, 15)

        # OK button
        ok_button = wx.Button(panel, label="OK")
        ok_button.Bind(wx.EVT_BUTTON, lambda event: self.Close())
        vbox.Add(ok_button, 0, wx.ALL | wx.CENTER, 10)

        panel.SetSizer(vbox)
        self.CenterOnParent()
