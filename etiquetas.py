#!/usr/bin/env python3
"""
Aplicación de escritorio para generar un PDF de etiquetas con logo, código de barras,
datos de contacto y precio, usando un template rectangular ampliado con títulos y precios dinámicos.
Soporta códigos numéricos y alfanuméricos (EAN13/Code128).
Formato de línea: código;Título del mueble;Precio
"""
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

# Registrar fuente si se necesita
try:
    pdfmetrics.registerFont(TTFont('Helvetica', 'Helvetica.ttf'))
except:
    pass

def truncate_text(canvas, text, font_name, font_size, max_width):
    """Trunca el texto si excede el ancho máximo permitido."""
    original = text
    while canvas.stringWidth(text, font_name, font_size) > max_width and len(text) > 0:
        text = text[:-1]
    if len(text) < len(original):
        if len(text) > 3:
            text = text[:-3] + '...'
        else:
            text = '...'
    return text

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
        
        self.text.insert("1.0", "123456789012;Mesa de Centro Moderna;1299\n")
        self.text.insert("2.0", "ABCDE123;Silla Reclinable de Lujo;2450\n")
        self.text.insert("3.0", "987654321098;Librero Multifuncional Grande;3599")
        
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
        
        config_frame = tk.Frame(main_frame, bg="#f5f5f5")
        config_frame.pack(fill=tk.X, pady=10)
        
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
        """Genera una vista previa de la primera etiqueta"""
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
        
        # Ajustar dimensiones para garantizar 2 etiquetas por fila
        margin_x, margin_y = 10*mm, 15*mm
        label_w, label_h = 95*mm, 45*mm  # Ligeramente más alto para acomodar el contenido
        footer_h = 14*mm  # Más alto para acomodar teléfonos junto al email
        gap_x, gap_y = 5*mm, 8*mm
        
        # Forzar exactamente 2 columnas
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

            # Dibujar rectángulo exterior
            c.rect(x, y, label_w, label_h)
            
            # Línea vertical divisoria en el medio
            mid_x = x + label_w/2
            c.line(mid_x, y, mid_x, y + label_h)
            
            # Línea horizontal para el pie de etiqueta
            c.line(x, y + footer_h, x + label_w, y + footer_h)

            content_top = y + label_h
            content_bottom = y + footer_h
            content_h = content_top - content_bottom

            # Bloque logo
            if self.logo_path and os.path.exists(self.logo_path):
                logo_w, logo_h = 30*mm, 30*mm
                logo_x = x + (label_w/2 - logo_w)/2
                logo_y = content_bottom + (content_h - logo_h)/2
                c.drawImage(self.logo_path, logo_x, logo_y, width=logo_w, height=logo_h,
                            preserveAspectRatio=True, mask='auto')

            # Bloque derecho - título, código y precio con autoajuste
            block_x, block_w = mid_x, label_w/2
            
            # TÍTULO
            max_title_width = block_w - 6*mm
            # Calculamos el tamaño de fuente óptimo basado en la longitud del título
            if len(title) > 30:
                title_font_size = 9
                max_chars_per_line = 20
            elif len(title) > 20:
                title_font_size = 10
                max_chars_per_line = 18
            else:
                title_font_size = 11
                max_chars_per_line = 15
                
            wrap = textwrap.wrap(title, width=max_chars_per_line)
            if len(wrap) > 2:
                wrap = wrap[:2]
                wrap[1] = wrap[1][:-3] + '...'
                
            c.setFont('Helvetica-Bold', title_font_size)
            title_y = content_top - 6*mm
            for i, text_line in enumerate(wrap):
                text_line = truncate_text(c, text_line, 'Helvetica-Bold', title_font_size, max_title_width)
                c.drawCentredString(block_x + block_w/2, title_y - i*5*mm, text_line)
            
            # Calcular el espacio usado por el título
            title_space = 6*mm + len(wrap)*5*mm
            
            # CÓDIGO DE BARRAS - Ajustar tamaño según el espacio disponible
            bar_space = content_h - title_space - 15*mm
            if code.isdigit() and len(code) == 13:
                generator = EAN13(code, writer=ImageWriter())
            else:
                if len(code) > 15:
                    code = code[:15]
                generator = Code128(code, writer=ImageWriter())
                
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            try:
                # Ajustar altura del código de barras según espacio disponible
                bar_height = min(15.0, max(8.0, bar_space/mm))
                
                generator.write(tmp, options={
                    'module_width': 0.4, 
                    'module_height': bar_height, 
                    'quiet_zone': 1, 
                    'write_text': False
                })
                tmp.flush()
                
                bar_h = min(15*mm, bar_space * 0.8)
                bar_w = block_w - 8*mm
                bar_x = block_x + (block_w - bar_w)/2
                bar_y = content_top - title_space - bar_h - 2*mm
                
                c.drawImage(tmp.name, bar_x, bar_y, width=bar_w, height=bar_h, mask='auto')
                c.setFont('Helvetica', 7)
                c.drawCentredString(block_x + block_w/2, bar_y - 3*mm, code)
            finally:
                tmp.close()
                os.unlink(tmp.name)
            
            # PRECIO - Ajustar tamaño según el espacio disponible
            if price:
                # Ajustar tamaño de precio según el espacio disponible
                remaining_space = bar_y - 3*mm - content_bottom
                if remaining_space > 10*mm:
                    price_font_size = 12
                elif remaining_space > 8*mm:
                    price_font_size = 11
                else:
                    price_font_size = 10
                    
                c.setFont('Helvetica-Bold', price_font_size)
                max_price_width = block_w - 6*mm
                price_text = f"${price}"
                price_text = truncate_text(c, price_text, 'Helvetica-Bold', price_font_size, max_price_width)
                price_y = bar_y - 7*mm
                c.drawCentredString(block_x + block_w/2, price_y, price_text)

            # Pie de etiqueta rediseñado - Ahora con teléfonos junto al email
            # 1. Nombre de la tienda
            c.setFont('Helvetica-Bold', 9)
            c.drawString(x + 2*mm, y + footer_h - 4*mm, 'TIMILPAN Y ACULCO')
            
            # 2. Email y teléfonos en la misma línea
            c.setFont('Helvetica', 7)  # Fuente más pequeña para el email
            
            email = 'mueblescarrillo59@gmail.com'
            email_y = y + footer_h - 8*mm
            c.drawString(x + 2*mm, email_y, email)
            
            # Teléfonos en dos líneas
            phone_nums = ['712 162 6915 ', '712 159 0891']
            
            # Distribuir teléfonos en dos líneas
            phone_start_x = x + 2*mm
            phone_line1_y = y + 5*mm
            phone_line2_y = y + 2*mm
            
            # Icono WhatsApp para primer teléfono
            if self.whatsapp_path and os.path.exists(self.whatsapp_path):
                icon_size = 3.5*mm
                c.drawImage(self.whatsapp_path, 
                           phone_start_x,
                           phone_line1_y - icon_size/2,
                           width=icon_size, 
                           height=icon_size, 
                           preserveAspectRatio=True, 
                           mask='auto')
                c.drawString(phone_start_x + icon_size + 1*mm, phone_line1_y, phone_nums[0])
                
                # Icono WhatsApp para segundo teléfono
                c.drawImage(self.whatsapp_path, 
                           x + label_w/2 + 4*mm,
                           phone_line1_y - icon_size/2,
                           width=icon_size, 
                           height=icon_size, 
                           preserveAspectRatio=True, 
                           mask='auto')
                c.drawString(x + label_w/2 + 4*mm + icon_size + 1*mm, phone_line1_y, phone_nums[1])
            else:
                c.drawString(phone_start_x, phone_line1_y, phone_nums[0])
                c.drawString(x + label_w/2 + 4*mm, phone_line1_y, phone_nums[1])
            
        c.save()

if __name__ == '__main__':
    # Requisitos adicionales: pip install reportlab python-barcode Pillow pdf2image
    app = LabelApp()
    app.mainloop()
