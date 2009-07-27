#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''模块名
@version: $Id$
@author: U{Jiahua Huang <jhuangjiahua@gmail.com>}
@license: LGPL
@see: 参考资料链接等等
'''

import gtk, gobject
import thread
import time
import subprocess

import os, sys
import base64

try: import i18n
except: from gettext import gettext as _

latex_mark_list = [
    ["√¯",    r" \sqrt {}"],
    ["÷",     r" \frac {} {}"],    
    ["∫",     r" \int "],
    ["⋅",      r" \cdot "],
    [" ± ",   r" \pm "],
    [" ∓ ",    r" \mp "],
    [" ∨ ",   r" \lor" ],
    [" ∧ ",   r" \land "],
    [" ≤ ",   r" \le "],
    [" ≥ ",   r" \ge "],
    [" ≡ ",   r" \equiv "],
    [" ∼ ",   r" \sim "],
    ["∥ ",    r" \parallel "],
    [" ⊥ ",   r" \perp "],
    ["∞",     r" \infty "],
    ["⨯",      r" \times "],
    [" ≪ ",   r" \ll "],
    [" ≫ ",   r" \gg "],
    [" ≃ ",    r" \simeq "],
    [" ≈ ",   r" \approx "],
    [" ≠ ",   r" \neq "],
    ["∠",     r" \angle "],
    ["△",     r" \triangle "],
    ["∑",     r" \sum "],
    ["⇒",     r" \Rightarrow "],
    ["⇔",     r" \Leftrightarrow "],
    ["∧",     r" \wedge "],
    ["∨",     r" \vee "],
    ["¬",      r" \neg "],
    ["∀",     r" \forall "],
    ["∃",     r" \exists "],
    ["∅",      r" \varnothing "],
    ["∈",     r" \in "],
    ["∉",      r" \notin "],
    ["⊆",     r" \subseteq "],
    ["⊂",     r" \subset "],
    ["∪",     r" \cup "],
    ["⋂",      r" \cap "],
    ["→",     r" \to "],
    ["↦",      r" \mapsto "],
    ["∏",     r" \prod "],
    ["○",     r" \circ "],
#    ["sin",    r" \sin "],
#    ["cos",    r" \cos "],
#    ["tan",    r" \tan "],
#    ["ctan",   r" \ctab "],
#    ["asin",   r" \asin "],
#    ["acos",   r" \acos "],
#    ["atan",   r" \atan "],
#    ["actan",  r" \actan "],
#    ["log",    r" \log "],
#    ["ln",     r" \ln "],
    ["α",     r" \alpha "],
    ["β",     r" \beta "],
    ["Γ",     r" \Gamma "],
    ["γ",     r" \gamma "],
    ["Δ",     r" \Delta "],
    ["δ",     r" \delta "],
    ["ϵ",      r" \epsilon "],
    ["ε",     r" \varepsilon "],
    ["ζ",     r" \zeta "],
    ["η",     r" \eta "],
    ["Θ",     r" \Theta "],
    ["θ",     r" \theta "],
    ["ϑ",      r" \vartheta "],
    ["ι",     r" \iota "],
    ["κ",     r" \kappa "],
    ["Λ",     r" \Lambda "],
    ["λ",     r" \lambda "],
    ["μ",     r" \mu "],
    ["ν",     r" \nu "],
    ["Ξ",     r" \Xi "],
    ["ξ",     r" \xi "],
    ["Π",     r" \Pi "],
    ["π",     r" \pi "],
    ["ϖ",      r" \varpi "],
    ["ρ",     r" \rho "],
    ["ϱ",      r" \varrho "],
    ["Σ",     r" \Sigma "],
    ["σ",     r" \sigma "],
    ["ς",      r" \varsigma "],
    ["τ",     r" \tau "],
    ["Υ",     r" \Upsilon "],
    ["υ",     r" \upsilon "],
    ["Φ",     r" \Phi "],
    ["ϕ",      r" \phi "],
    ["φ",     r" \varphi "],
    ["χ",     r" \chi "],
    ["Ψ",     r" \Psi "],
    ["ψ",     r" \psi "],
    ["Ω",     r" \Omega "],
    ["ω",     r" \omega "],
]

class GtkToolBoxView(gtk.TextView):
    '''流式布局 ToolBox
    '''
    def __init__(self, latex=""):
        '''初始化
        '''
        self.__gobject_init__()
        self.unset_flags(gtk.CAN_FOCUS)
        self.set_editable(0)
        self.set_wrap_mode(gtk.WRAP_WORD)
        pass

    def add(self, widget):
        '''插入 Widget
        '''
        buffer = self.get_buffer()
        iter = buffer.get_end_iter()
        anchor = buffer.create_child_anchor(iter)
        buffer.insert(iter, "")
        self.add_child_at_anchor(widget, anchor)
        pass

class LatexMathExpressionsEditor(gtk.Table):
    '''LaTex 数学公式编辑器
    '''
    def __init__(self, latex=""):
        '''初始化
        '''
        self.__gobject_init__()
        self.set_row_spacings(10)
        self.set_col_spacings(10)
        ## latex edit
        scrolledwindow1 = gtk.ScrolledWindow()
        scrolledwindow1.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolledwindow1.show()
        scrolledwindow1.set_shadow_type(gtk.SHADOW_IN)

        self.latex_textview = gtk.TextView()
        self.latex_textview.set_wrap_mode(gtk.WRAP_WORD)
        self.latex_textview.set_cursor_visible(True)
        self.latex_textview.set_indent(5)
        self.latex_textview.set_editable(True)
        self.latex_textview.show()
        buffer = self.latex_textview.get_buffer()
        buffer.set_text(latex)
        scrolledwindow1.add(self.latex_textview)

        self.attach(scrolledwindow1, 0, 1, 0, 1)
        ## latex preview
        self.latex_image = gtk.Image()
        #self.latex_image.set_size_request(200, 100)
        self.latex_image.set_padding(0, 0)
        self.latex_image.show()

        box = gtk.EventBox()
        box.show()
        box.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color("#FFFFFF"))
        box.add(self.latex_image)
        
        self.attach(box, 0, 1, 1, 2)
        ## toolbox
        toolview = GtkToolBoxView()
        toolview.show()
        for text, mark in latex_mark_list:
            label = gtk.Label()
            label.set_markup(text)
            label.set_size_request(30, 20)
            label.show()
            button = gtk.Button()
            button.unset_flags(gtk.CAN_FOCUS)
            button.add(label)
            button.set_relief(gtk.RELIEF_NONE)
            button.connect("clicked", self.on_insert_tex_mark, text, mark)
            button.show()
            toolview.add(button)
            pass
        scrolledwindow2 = gtk.ScrolledWindow()
        #scrolledwindow2.set_size_request(300, 400)
        scrolledwindow2.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolledwindow2.show()
        scrolledwindow2.set_shadow_type(gtk.SHADOW_IN)
        scrolledwindow2.add(toolview)
        self.attach(scrolledwindow2, 1, 2, 0, 2)

        self.show_all()

        thread.start_new_thread(self._up_preview, ())
        pass

    def get_latex(self, *args):
        '''获取 LaTex
        '''
        buffer = self.latex_textview.get_buffer()
        return buffer.get_text(buffer.get_start_iter(),buffer.get_end_iter())

    def set_pic(self, data):
        '''设置图像
        '''
        if not data:
            return self.latex_image.set_from_stock(gtk.STOCK_DIALOG_ERROR, 6)
        pix = gtk.gdk.PixbufLoader()
        pix.write(data)
        pix.close()
        self.latex_image.set_from_pixbuf(pix.get_pixbuf())
        return

    def _up_preview(self, *args):
        '''用于定时更新预览
        '''
        old_latex = ""
        while True:
            time.sleep(2)
            if not self.get_window():
                break
            latex = self.get_latex()
            if latex == old_latex:
                continue
            pic = tex2gif(latex, 0)
            old_latex = self.get_latex()
            if latex == self.get_latex():
                gobject.idle_add(self.set_pic, pic)
                pass
            pass
        #-print 'done'
        return

    def up_preview(self, pic):
        '''更新预览'''
        return

    def insert_latex_mark(self, view, mark, text=""):
        '''在 gtk.TextView 插入 LaTex 标记
        '''
        buffer = view.get_buffer()
        bounds = buffer.get_selection_bounds()
        select = bounds and buffer.get_slice(bounds[0], bounds[1]) or text
        if '%' in mark:
            mark = mark % select
            pass
        buffer.delete_selection(1, 1)
        buffer.insert_at_cursor(mark)
        pass

    def on_insert_tex_mark(self, widget, text, mark):
        print 'on_insert_tex_mark:', text, mark
        self.insert_latex_mark(self.latex_textview, mark)
        pass

def latex_dlg(latex="E=MC^2", title=_("LaTeX math expressions"), parent=None):
    dlg = gtk.Dialog(title, parent, gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
            gtk.STOCK_OK, gtk.RESPONSE_OK    ))
    dlg.set_default_size(650, 400)
    editor = LatexMathExpressionsEditor(latex)
    dlg.vbox.pack_start(editor, True, True, 5)
    dlg.show_all()
    resp = dlg.run()
    latex = editor.get_latex()
    dlg.destroy()
    if resp == gtk.RESPONSE_OK:
        return latex
    return None    

def stastr(stri):
    '''处理字符串的  '   "
    '''
    return stri.replace("\\","\\\\").replace(r'"',r'\"').replace(r"'",r"\'").replace('\n',r'\n')

def tex2gif(tex, transparent=1):
    '''将 latex 数学公式转为 gif 图片，依赖 mimetex

    mimetex -d -s 7 '公式'
    '''
    if transparent: 
        cmd = ['mimetex', '-d', '-s', '7', tex]
        pass
    else:
        cmd = ['mimetex', '-d', '-o', '-s', '7', tex]
        pass
    i = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    gif = i.communicate()[0]
    if gif.startswith('GIF'):
        return gif
    return ""

def gif2base64(gif):
    '''将 gif 图像转为 base64 内联图像
    '''
    return 'data:image/gif;base64,%s' % base64.encodestring(gif).replace('\n', '')

def tex2html(tex):
    '''将 latex 数学公式转为 base64 内联图像
    '''
    return '<img alt="mimetex:%s" onDblClick="if(uptex) uptex(this);" style="border: 0;" src="%s" />' % (stastr(tex), gif2base64(tex2gif(tex)))


if __name__=="__main__":
    gtk.gdk.threads_init()
    latex = ' '.join(sys.argv[1:]) or 'E=MC^2'
    latex = latex_dlg(latex)
    print latex
    #print tex2html(latex)
    pass


