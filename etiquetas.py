#!/usr/bin/env python3
"""
Aplicación de escritorio para generar un PDF de etiquetas con logo, código de barras y datos de contacto.
Soporta códigos numéricos y alfanuméricos usando Code128 para cadenas con letras.
"""
import os
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from barcode import EAN13, Code128
from barcode.writer import ImageWriter

class LabelApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Generador de Etiquetas - Muebles Carrillo")
        self.geometry("600x400")

        lbl = tk.Label(self, text="Ingrese lista de etiquetas (código;título), una por línea:")
        lbl.pack(pady=(10,0))
        self.text = tk.Text(self, height=10)
        self.text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        frame = tk.Frame(self)
        frame.pack(pady=5)
        tk.Button(frame, text="Generar PDF", command=self.generate_pdf).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Salir", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def generate_pdf(self):
        raw = self.text.get("1.0", tk.END).strip()
        lines = [l for l in raw.splitlines() if l.strip()]
        if not lines:
            messagebox.showwarning("Advertencia", "La lista de etiquetas está vacía.")
            return

        out_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                filetypes=[("PDF files","*.pdf")])
        if not out_path:
            return

        try:
            self._create_pdf(lines, out_path)
            messagebox.showinfo("Éxito", f"PDF generado: {out_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error:\n{e}")

    def _create_pdf(self, lines, output):
        PAGE_W, PAGE_H = 210*mm, 297*mm
        c = canvas.Canvas(output, pagesize=(PAGE_W, PAGE_H))
        margin_x, margin_y = 10*mm, 10*mm
        label_w, label_h = 80*mm, 50*mm
        gap_x, gap_y = 5*mm, 5*mm
        cols = 2

        x = margin_x
        y = PAGE_H - margin_y - label_h
        col = 0

        for line in lines:
            code, title = (line.split(';') + [''])[:2]
            code, title = code.strip(), title.strip()

            # Borde
            c.rect(x, y, label_w, label_h)

            # Logo
            logo = 'logo.png'
            if os.path.exists(logo):
                c.drawImage(logo, x + 2*mm, y + label_h - 32*mm,
                            width=30*mm, height=30*mm, preserveAspectRatio=True, mask='auto')

            # Elige generador: EAN13 para solo dígitos, Code128 para alfanuméricos
            if code.isdigit() and len(code) == 13:
                generator = EAN13(code, writer=ImageWriter())
            else:
                generator = Code128(code, writer=ImageWriter())

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            try:
                # Usar write_text=False para ocultar texto interno y evitar font_size=0
                generator.write(tmp, options={
                    'module_width': 0.3,
                    'module_height': 15.0,
                    'quiet_zone': 1,
                    'write_text': False
                })
                tmp.flush()
                bar_w = label_w - 36*mm
                bar_x = x + label_w - 2*mm - bar_w
                bar_y = y + label_h - 32*mm
                c.drawImage(tmp.name, bar_x, bar_y, width=bar_w, height=30*mm, mask='auto')
            finally:
                tmp.close()
                os.unlink(tmp.name)

            # Título y código
            c.setFont("Helvetica", 10)
            c.drawCentredString(bar_x + bar_w/2, bar_y + 30*mm + 3*mm, title)
            c.setFont("Helvetica", 8)
            c.drawCentredString(bar_x + bar_w/2, bar_y - 4*mm, code)

            # Línea divisoria
            c.line(x, y + 15*mm, x + label_w, y + 15*mm)

            # Pie contacto
            c.setFont("Helvetica", 7)
            c.drawString(x + 2*mm, y + 12*mm, "TIMILPAN Y ACULCO")
            c.drawString(x + 2*mm, y + 8*mm, "mueblescarrillo59@gmail.com")
            whatsapp_icon = 'whatsapp-icon.png'
            for i, num in enumerate(["712 162 6915", "712 159 0891"]):
                yy = y + 12*mm - i*6*mm
                if os.path.exists(whatsapp_icon):
                    c.drawImage(whatsapp_icon, x + label_w - 20*mm, yy, width=6*mm, height=6*mm, mask='auto')
                c.drawString(x + label_w - 13*mm, yy + 1*mm, num)

            # Avanzar
            col += 1
            if col >= cols:
                col = 0
                x = margin_x
                y -= label_h + gap_y
                if y < margin_y:
                    c.showPage()
                    y = PAGE_H - margin_y - label_h
            else:
                x += label_w + gap_x

        c.save()

if __name__ == "__main__":
    # Instala: pip install reportlab python-barcode Pillow
    app = LabelApp()
    app.mainloop()
