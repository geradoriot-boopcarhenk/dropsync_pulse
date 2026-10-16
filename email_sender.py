import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configurações de autenticação segura do Gmail
GMAIL_USER = "seu_email@gmail.com"
GMAIL_APP_PASSWORD = "sua_senha_de_app_do_gmail"  # Vamos gerar essa senha especial no Google

def disparar_email_entrega(email_cliente, nome_cliente):
    """
    Dispara um e-mail HTML profissional entregando a licença do SaaS.
    """
    mensagem = MIMEMultipart()
    mensagem["From"] = GMAIL_USER
    mensagem["To"] = email_cliente
    mensagem["Subject"] = "⚡ Sua Licença DropSync Pulse Chegou!"

    corpo_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="background-color: #111; padding: 20px; text-align: center; color: #fff;">
                <h1 style="color: #ffcc00; margin: 0;">⚡ DropSync Pulse</h1>
            </div>
            <div style="padding: 20px; border: 1px solid #eee;">
                <p>Olá, <b>{nome_cliente}</b>!</p>
                <p>O seu pagamento via Pix foi recebido e processado com sucesso pelo nosso gateway.</p>
                <p style="background: #f9f9f9; padding: 15px; border-left: 5px solid #ffcc00;">
                    🔑 <b>Sua Chave de Acesso:</b> <code>DSP-PRO-{nome_cliente.split()[0].upper()}-99283</code>
                </p>
                <p>Acesse o painel analítico e configure seus produtos da Shopee agora mesmo!</p>
                <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                <caption style="font-size: 11px; color: #999;">DropSync Pulse SaaS — Todos os direitos reservados.</caption>
            </div>
        </body>
    </html>
    """
    mensagem.attach(MIMEText(corpo_html, "html"))

    try:
        with smtplib.SMTP_SSL("://gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_mail(GMAIL_USER, email_cliente, mensagem.as_string())
        print(f"📧 [E-mail] Notificação de entrega enviada com sucesso para {email_cliente}!")
    except Exception as e:
        print(f"❌ [E-mail Erro] Falha ao despachar e-mail: {e}")
