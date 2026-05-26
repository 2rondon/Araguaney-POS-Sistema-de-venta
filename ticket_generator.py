import os
import database
from reportlab.lib.pagesizes import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def generar_ticket_pdf(id_venta, carrito_productos):
    # 1. Obtener datos fiscales del comercio
    conn = database.get_connection()
    cfg = conn.execute("SELECT nombre_comercio, rif, direccion, iva_general, igtf FROM configuracion WHERE id = 1").fetchone()
    
    # Datos por defecto si la configuración está vacía
    nombre_comercio = cfg[2] if (cfg and cfg[2]) else "ARAGUANEY POS"
    rif = cfg[3] if (cfg and cfg[3]) else "G-00000000-0"
    direccion = cfg[4] if (cfg and cfg[4]) else "Dirección Comercial"
    tasa_iva = cfg[0] if cfg else 16.0
    tasa_igtf = cfg[1] if cfg else 3.0
    conn.close()

    # 2. Configurar dimensiones del Ticket de 80mm
    ANCHO_TICKET = 80 * mm
    # El largo se calcula dinámicamente según la cantidad de ítems para evitar saltos de página
    LARGO_ESTIMADO = (110 + (len(carrito_productos) * 15)) * mm 
    
    # Asegurar que exista carpeta de recibos
    if not os.path.exists("facturas"): os.makedirs("facturas")
    ruta_pdf = f"facturas/Ticket_{id_venta}.pdf"
    
    # Crear documento base sin márgenes excesivos
    doc = SimpleDocTemplate(
        ruta_pdf, 
        pagesize=(ANCHO_TICKET, LARGO_ESTIMADO),
        leftMargin=4*mm, rightMargin=4*mm, topMargin=5*mm, bottomMargin=5*mm
    )
    
    styles = getSampleStyleSheet()
    
    # Estilos tipográficos compactos para tiqueteras
    style_centro = ParagraphStyle('Centro', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, alignment=TA_CENTER)
    style_comercio = ParagraphStyle('Comercio', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=14, alignment=TA_CENTER)
    style_izq = ParagraphStyle('Izq', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, alignment=TA_LEFT)
    style_der = ParagraphStyle('Der', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, alignment=TA_RIGHT)
    style_der_bold = ParagraphStyle('DerB', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, alignment=TA_RIGHT)

    story = []
    
    # Encabezado Comercial
    story.append(Paragraph(f"<b>{nombre_comercio}</b>", style_comercio))
    story.append(Paragraph(f"RIF: {rif}", style_centro))
    story.append(Paragraph(f"{direccion}", style_centro))
    story.append(Spacer(1, 4 * mm))
    
    # Info de la Venta
    story.append(Paragraph(f"<b>TICKET: #{id_venta}</b>", style_izq))
    story.append(Paragraph("Condición: Venta al Contado", style_izq))
    story.append(Paragraph("------------------------------------------------------------------", style_centro))
    
    # Tabla de Productos
    # Estructura: Cantidad | Descripción | Total
    tabla_datos = [[Paragraph("<b>Cant</b>", style_izq), Paragraph("<b>Descripción</b>", style_izq), Paragraph("<b>Total</b>", style_der)]]
    
    subtotal = 0.0
    for p in carrito_productos:
        # Suponiendo estructura del carrito: [codigo, descripcion, precio_unitario, cantidad, aplica_iva]
        desc = p[1]
        precio_u = float(p[2])
        cant = int(p[3])
        total_item = precio_u * cant
        subtotal += total_item
        
        tabla_datos.append([
            Paragraph(str(cant), style_izq),
            Paragraph(desc, style_izq),
            Paragraph(f"${total_item:.2f}", style_der)
        ])
    
    # Ancho de columnas calculado para los 72mm útiles de la cinta de 80mm
    tabla_prod = Table(tabla_datos, colWidths=[10*mm, 44*mm, 18*mm])
    tabla_prod.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('TOPPADDING', (0,0), (-1,-1), 1),
    ]))
    story.append(tabla_prod)
    
    story.append(Paragraph("------------------------------------------------------------------", style_centro))
    
    # Totales y Cálculos Fiscales
    iva_calculado = subtotal * (tasa_iva / 100.0)
    total_general = subtotal + iva_calculado
    
    tabla_totales_datos = [
        [Paragraph("SUBTOTAL:", style_izq), Paragraph(f"${subtotal:.2f}", style_der)],
        [Paragraph(f"IVA ({tasa_iva}%):", style_izq), Paragraph(f"${iva_calculado:.2f}", style_der)],
        [Paragraph("<b>TOTAL A PAGAR ($):</b>", style_izq), Paragraph(f"<b>${total_general:.2f}</b>", style_der_bold)]
    ]
    
    tabla_totales = Table(tabla_totales_datos, colWidths=[40*mm, 32*mm])
    tabla_totales.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(tabla_totales)
    
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph("¡Gracias por su compra!", style_centro))
    story.append(Paragraph("Araguaney POS - Enterprise", style_centro))
    
    # Construir archivo definitivo
    doc.build(story)
    return ruta_pdf