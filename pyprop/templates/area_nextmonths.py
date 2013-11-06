
import gtk
from datetime import datetime
from dateutil.relativedelta import relativedelta


class templates:
    name = 'Next N Months'

    def __init__(self, parent):
        self.parent = parent
        self.ret_templates = {} # { templatename : [(month_i,utc,freq),...]}
        self.current_month = None
        self.current_year = None
        self.current_utc = 12
        self.current_freq = 3.0
        self.iter = None

    def get_names(self):
        return [self.name,]

    def get_params(self):
        return []

    def load(self):
        return

    def set_ini(self, model):
        if len(model):
            iter = model.get_iter(len(model)-1)
            y,m,u,f = model.get(iter,0,2,3,4)
            self.current_year = y
            self.current_month = m
            self.current_utc = u if u else 12
            self.current_freq = float(f) if f > 3 else 3.0


    def run(self):
        tups = []
        if not self.current_year:
            cur = datetime.now()
        else:
            cur = datetime(self.current_year, self.current_month, 1)
        if not self.current_month or not self.iter:
            dialog = gtk.Dialog(_("Next N Months Area Template Properties"),
                       self.parent,
                       gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.WIN_POS_CENTER_ON_PARENT,
                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
            vb = gtk.VBox()
            hb = gtk.HBox(2)
            l = gtk.Label(_('Number of months to add:'))
            adj = gtk.Adjustment(float(self.iter) if self.iter else 12, 1, 100, 1, 5, 0)
            em = gtk.SpinButton(adj)
            em.set_wrap(True)
            hb.pack_start(l)
            hb.pack_end(em)
            vb.pack_start(hb)
            hb = gtk.HBox(2)
            l = gtk.Label(_('UTC hour:'))
            adj = gtk.Adjustment(self.current_utc, 1.0, 23.0, 1.0, 5.0, 0)
            eh = gtk.SpinButton(adj)
            eh.set_wrap(True)
            hb.pack_start(l)
            hb.pack_end(eh)
            vb.pack_start(hb)
            hb = gtk.HBox(2)
            adj = gtk.Adjustment(self.current_freq, 3.0, 30.0, 0.1, 1.0, 0)
            l = gtk.Label(_('Frequency (MHz):'))
            ef = gtk.SpinButton(adj, 1.0, 3)
            ef.set_wrap(True)
            hb.pack_start(l)
            hb.pack_end(ef)
            vb.pack_start(hb)
            dialog.vbox.pack_start(vb)
            dialog.show_all()

            ret = dialog.run()
            iter = em.get_value_as_int()
            utc = eh.get_value_as_int()
            freq = ef.get_value()
            dialog.destroy()
            if ret != -3: return 1

        else:
            utc = self.current_utc
            freq = self.current_freq
            iter = self.iter

        delta = relativedelta(months=+1)
        for i in range(iter):
            cur = cur + delta
            tups.append((cur.year, cur.month, utc, freq))
        self.ret_templates[self.name] = tups

