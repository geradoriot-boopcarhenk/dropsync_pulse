import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

def generate_pdf_report(products_list: list, output_filename="relatorio_auditoria.pdf") -> str:
    """Gera um relatório profissional em PDF contendo as métricas fiscais dos produtos monitorados."""
    output_path = os.path.expanduser(f"~/dropsync_pulse/{output_filename}")
    
    # Se estiver rodando dentro do Docker na nuvem, salva no diretório local /app
    if not os.path.exists(os.path.expanduser("~/dropsync_pulse")):
        output_path = os.path.join(os.getcwd(), output_filename)
        
    doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=6
    )
    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor("#4A5568"),
        spaceAfter=20
    )
    
    story.append(Paragraph("⚡ DropSync Pulse — Relatório de Auditoria Fiscal", title_style))
    data_emissao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    story.append(Paragraph(f"Emitido em: {data_emissao} | Ambiente: Produção SaaS Nuvem", meta_style))
    story.append(Spacer(1, 10))
    
    table_data = [["ID", "Produto / Item Monitorado", "Custo (USD)", "Margem", "Status"]]
    
    for prod in products_list:
        table_data.append([
            str(prod.get("id", "-")),
            prod.get("product_name", "Sem Nome"),
            f"$ {float(prod.get('current_cost_usd', 0)):.2f}",
            f"{prod.get('desired_margin_percent', 0)}%",
            "Ativo" if prod.get("is_active", True) else "Pausado"
        ])
        
    report_table = Table(table_data, colWidths=[40, 240, 90, 70, 70])
    report_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 1), (3, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F7FAFC")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#EDF2F7")]),
    ]))
    
    story.append(report_table)
    doc.build(story)
    return output_path
