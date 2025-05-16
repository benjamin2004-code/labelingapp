#!/usr/bin/env python3
import os
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from barcode import EAN13, Code128
from barcode.writer import ImageWriter
from PIL import Image, ImageTk
import textwrap

try:
    pdfmetrics.registerFont(TTFont('Helvetica', 'Helvetica.ttf'))
except:
    pass

class LabelApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Generador de Etiquetas - Muebles Carrillo")
        self.geometry("800x600")
        self.configure(bg="#f5f5f5")
        self.logo_path = None
        self.logo_img = None
        self.whatsapp_path = None
        self.whatsapp_img = None

        main_frame = tk.Frame(self, bg="#f5f5f5", padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_frame = tk.Frame(main_frame, bg="#f5f5f5")
        title_frame.pack(fill=tk.X, pady=(0, 10))
        title_label = tk.Label(title_frame, text="Generador de Etiquetas para Muebles Carrillo", 
                              font=("Arial", 16, "bold"), bg="#f5f5f5")
        title_label.pack()
        
        instr_frame = tk.Frame(main_frame, bg="#f5f5f5")
        instr_frame.pack(fill=tk.X, pady=(0, 5))
        lbl = tk.Label(instr_frame, text="Ingrese lista de etiquetas (código;título;precio), una por línea:", 
                      font=("Arial", 10), bg="#f5f5f5")
        lbl.pack(anchor='w')
        
        text_frame = tk.Frame(main_frame, bg="#f5f5f5")
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.text = tk.Text(text_frame, height=12, font=("Arial", 10), wrap="word")
        scrollbar = ttk.Scrollbar(text_frame, command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text.insert("1.0", "1234567890123;Mesa de Centro Moderna;1299\n")
        self.text.insert("2.0", "ABCDE123;Silla Reclinable de Lujo;2450\n")
        self.text.insert("3.0", "9876543210987;Librero Multifuncional Grande y MuyCompletoParaEspaciosPequeños;3599\n")
        
        logos_frame = tk.Frame(main_frame, bg="#f5f5f5")
        logos_frame.pack(fill=tk.X, pady=10)
        
        logo_subframe = tk.Frame(logos_frame, bg="#f5f5f5")
        logo_subframe.pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Button(logo_subframe, text="Seleccionar Logo de Empresa", 
                 command=self.select_logo, bg="#e0e0e0", 
                 font=("Arial", 10), padx=10).pack(anchor='w')
        self.logo_preview = tk.Label(logo_subframe, text="Logo: Ninguno", 
                                    bg="#f5f5f5", width=30, anchor='w')
        self.logo_preview.pack(anchor='w', pady=5)
        
        whatsapp_subframe = tk.Frame(logos_frame, bg="#f5f5f5")
        whatsapp_subframe.pack(side=tk.LEFT)
        
        tk.Button(whatsapp_subframe, text="Seleccionar Icono WhatsApp", 
                 command=self.select_whatsapp, bg="#e0e0e0", 
                 font=("Arial", 10), padx=10).pack(anchor='w')
        self.whatsapp_preview = tk.Label(whatsapp_subframe, text="Icono: Ninguno", 
                                       bg="#f5f5f5", width=30, anchor='w')
        self.whatsapp_preview.pack(anchor='w', pady=5)
        
        btn_frame = tk.Frame(main_frame, bg="#f5f5f5")
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Vista Previa", command=self.preview_label, 
                 width=20, bg="#4CAF50", fg="white", 
                 font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Generar PDF", command=self.generate_pdf, 
                 width=20, bg="#2196F3", fg="white", 
                 font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Salir", command=self.destroy, 
                 width=10, bg="#f44336", fg="white", 
                 font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
                 
        self.status_var = tk.StringVar()
        self.status_var.set("Listo para generar etiquetas")
        status_bar = tk.Label(self, textvariable=self.status_var, 
                            bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def select_logo(self):
        path = filedialog.askopenfilename(
            title="Seleccione archivo de logo",
            filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.gif"), ("Todos", "*.*")]
        )
        if path:
            self.logo_path = path
            try:
                img = Image.open(path)
                img.thumbnail((60, 60))
                self.logo_img = ImageTk.PhotoImage(img)
                self.logo_preview.config(image=self.logo_img, text="")
                self.status_var.set(f"Logo cargado: {os.path.basename(path)}")
            except Exception as e:
                self.logo_preview.config(text=f"Error: {os.path.basename(path)}", image='')
                self.status_var.set(f"Error al cargar logo: {str(e)}")
        else:
            self.logo_path = None
            self.logo_preview.config(text="Logo: Ninguno", image='')

    def select_whatsapp(self):
        path = filedialog.askopenfilename(
            title="Seleccione icono de WhatsApp",
            filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.gif"), ("Todos", "*.*")]
        )
        if path:
            self.whatsapp_path = path
            try:
                img = Image.open(path)
                img.thumbnail((30, 30))
                self.whatsapp_img = ImageTk.PhotoImage(img)
                self.whatsapp_preview.config(image=self.whatsapp_img, text="")
                self.status_var.set(f"Icono WhatsApp cargado: {os.path.basename(path)}")
            except Exception as e:
                self.whatsapp_preview.config(text=f"Error: {os.path.basename(path)}", image='')
                self.status_var.set(f"Error al cargar icono: {str(e)}")
        else:
            self.whatsapp_path = None
            self.whatsapp_preview.config(text="Icono: Ninguno", image='')

    def preview_label(self):
        raw = self.text.get("1.0", tk.END).strip()
        lines = [l for l in raw.splitlines() if l.strip()]
        if not lines:
            messagebox.showwarning("Advertencia", "La lista de etiquetas está vacía.")
            return
        try:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                pdf_path = tmp.name
            self._create_pdf([lines[0]], pdf_path, preview=True)
            try:
                from pdf2image import convert_from_path
                images = convert_from_path(pdf_path, size=(550, 250))
                preview_window = tk.Toplevel(self)
                preview_window.title("Vista Previa de Etiqueta")
                preview_window.geometry("550x250")
                img = images[0]
                photo = ImageTk.PhotoImage(img)
                label = tk.Label(preview_window, image=photo)
                label.image = photo
                label.pack(expand=True, fill=tk.BOTH)
                os.unlink(pdf_path)
                self.status_var.set("Vista previa generada")
            except ImportError:
                messagebox.showinfo("Información", 
                                  "Para utilizar la vista previa, instale pdf2image:\npip install pdf2image")
                os.unlink(pdf_path)
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar vista previa:\n{e}")

    def generate_pdf(self):
        raw = self.text.get("1.0", tk.END).strip()
        lines = [l for l in raw.splitlines() if l.strip()]
        if not lines:
            messagebox.showwarning("Advertencia", "La lista de etiquetas está vacía.")
            return
        out_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files","*.pdf")]
        )
        if not out_path:
            return
        try:
            self.status_var.set("Generando PDF...")
            self.update_idletasks()
            self._create_pdf(lines, out_path)
            self.status_var.set(f"PDF generado exitosamente: {os.path.basename(out_path)}")
            messagebox.showinfo("Éxito", f"PDF generado: {out_path}")
        except Exception as e:
            self.status_var.set(f"Error al generar PDF: {str(e)}")
            messagebox.showerror("Error", f"Ocurrió un error:\n{e}")

    def _create_pdf(self, lines, output, preview=False):
        PAGE_W, PAGE_H = 210*mm, 297*mm
        c = canvas.Canvas(output, pagesize=(PAGE_W, PAGE_H))
        margin_x, margin_y = 10*mm, 15*mm
        label_w, label_h = 95*mm, 45*mm
        gap_x, gap_y = 5*mm, 8*mm
        cols = 2
        rows = int((PAGE_H - 2*margin_y + gap_y) // (label_h + gap_y))
        max_per_page = cols * rows

        for line_index, line in enumerate(lines):
            page_num = line_index // max_per_page
            pos_in_page = line_index % max_per_page
            row = pos_in_page // cols
            col = pos_in_page % cols
            if pos_in_page == 0 and line_index > 0:
                c.showPage()
            x = margin_x + col * (label_w + gap_x)
            y = PAGE_H - margin_y - label_h - row * (label_h + gap_y)
            c.rect(x, y, label_w, label_h)
            mid_x = x + label_w/2
            c.line(mid_x, y, mid_x, y + label_h)
            parts = line.split(';')
            if len(parts) >= 3:
                code, title, price = parts[0], parts[1], parts[2]
            elif len(parts) == 2:
                code, title, price = parts[0], parts[1], ""
            elif len(parts) == 1:
                code, title, price = parts[0], "", ""
            else:
                continue
            code, title, price = code.strip(), title.strip(), price.strip()

            # Columna izquierda (logo, datos, teléfonos)
            left_x = x
            left_w = label_w / 2
            left_center = left_x + left_w / 2
            content_top = y + label_h
            icon_size = 3.5*mm
            phone_nums = ['712 162 6915', '712 159 0891']

            min_text_space = 24*mm
            max_logo_h = max(10*mm, label_h - min_text_space)
            logo_h = min(30*mm, max_logo_h)
            logo_w = logo_h

            if self.logo_path and os.path.exists(self.logo_path):
                logo_x = left_center - logo_w / 2
                logo_y = content_top - logo_h - 2*mm
                c.drawImage(self.logo_path, logo_x, logo_y, width=logo_w, height=logo_h,
                            preserveAspectRatio=True, mask='auto')
                text_y = logo_y - 4*mm
            else:
                text_y = content_top - 10*mm

            min_text_y = y + 12*mm
            if text_y < min_text_y:
                text_y = min_text_y

            c.setFont('Helvetica-Bold', 9)
            c.drawCentredString(left_center, text_y, 'TIMILPAN Y ACULCO')
            text_y -= 5*mm

            c.setFont('Helvetica', 7)
            email = 'mueblescarrillo59@gmail.com'
            c.drawCentredString(left_center, text_y, email)
            text_y -= 5*mm

            min_phone_y = y + 4*mm
            needed_height = len(phone_nums) * (icon_size + 2*mm)
            if text_y - needed_height < min_phone_y:
                phone_spacing = icon_size + 1*mm
            else:
                phone_spacing = 4*mm

            for phone in phone_nums:
                if self.whatsapp_path and os.path.exists(self.whatsapp_path):
                    icon_x = left_center - (c.stringWidth(phone, 'Helvetica', 8)/2) - icon_size - 1*mm
                    c.drawImage(self.whatsapp_path, icon_x, text_y - icon_size/2,
                                width=icon_size, height=icon_size, preserveAspectRatio=True, mask='auto')
                    c.setFont('Helvetica', 8)
                    c.drawString(icon_x + icon_size + 1*mm, text_y, phone)
                else:
                    c.setFont('Helvetica', 8)
                    c.drawCentredString(left_center, text_y, phone)
                text_y -= phone_spacing

            # Columna derecha (precio, TÍTULO, barcode)
            right_x = x + left_w
            block_w = label_w / 2
            block_center = right_x + block_w/2
            top = y + label_h
            current_y = top - 6*mm

            # PRECIO
            if price:
                c.setFont('Helvetica-Bold', 13)
                c.setFillColorRGB(0, 0, 0)
                price_text = f"${price}"
                c.drawCentredString(block_center, current_y, price_text)
                current_y -= 5*mm

            # --- TÍTULO ENTRE PRECIO Y BARCODE, NUNCA SE DESBORDA ---
            max_title_width = block_w - 7*mm
            min_font_size = 7
            max_font_size = 13

            barcode_space = 18*mm
            available_height = (current_y - y) - barcode_space
            if available_height < min_font_size + 2:
                available_height = min_font_size + 2

            title_font_size = max_font_size
            lines = []

            while title_font_size >= min_font_size:
                c.setFont('Helvetica-Bold', title_font_size)
                char_width = c.stringWidth('W', 'Helvetica-Bold', title_font_size)
                chars_per_line = max(1, int(max_title_width // (char_width if char_width > 0 else 1)))
                wrap = textwrap.wrap(title, width=chars_per_line, break_long_words=True, break_on_hyphens=False)
                needed_height = len(wrap) * (title_font_size + 2)
                if needed_height <= available_height:
                    lines = wrap
                    break
                title_font_size -= 1
            if not lines:
                c.setFont('Helvetica-Bold', min_font_size)
                char_width = c.stringWidth('W', 'Helvetica-Bold', min_font_size)
                chars_per_line = max(1, int(max_title_width // (char_width if char_width > 0 else 1)))
                lines = textwrap.wrap(title, width=chars_per_line, break_long_words=True, break_on_hyphens=False)

            for text_line in lines:
                c.setFont('Helvetica-Bold', title_font_size)
                c.setFillColorRGB(0, 0, 0)
                c.drawCentredString(block_center, current_y, text_line)
                current_y -= (title_font_size + 2)
            current_y -= 2*mm

            # CÓDIGO DE BARRAS
            if code.isdigit() and len(code) == 13:
                generator = EAN13(code, writer=ImageWriter())
            else:
                if len(code) > 15:
                    code = code[:15]
                generator = Code128(code, writer=ImageWriter())
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            try:
                generator.write(tmp, options={
                    'module_width': 0.4,
                    'module_height': 12.0,
                    'quiet_zone': 1,
                    'write_text': False
                })
                tmp.flush()
                bar_w = block_w - 8*mm
                bar_h = 14*mm
                bar_x = right_x + (block_w - bar_w)/2
                bar_y = current_y - bar_h + 3*mm

                c.drawImage(tmp.name, bar_x, bar_y, width=bar_w, height=bar_h, mask='auto')
                c.setFont('Helvetica', 8)
                c.setFillColorRGB(0, 0, 0)
                c.drawCentredString(block_center, bar_y - 3*mm, code)
            finally:
                tmp.close()
                os.unlink(tmp.name)
        c.save()

if __name__ == '__main__':
    # Requisitos: pip install reportlab python-barcode Pillow pdf2image
    app = LabelApp()
    app.mainloop()
