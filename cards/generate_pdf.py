import qrcode
from fpdf import FPDF
from pathlib import Path
import os
from core.settings import STATIC_ROOT

def generate_qr_pdf(data, card_image='card.png'):
    # ----------------------------
    # Configuration
    # ----------------------------
    CARD_WIDTH = 85
    CARD_HEIGHT = 55
    MARGIN_X = 4.0
    MARGIN_Y = 4.0
    GAP_X = 4.0
    GAP_Y = 4.0

    CARDS_PER_ROW = 2
    CARDS_PER_PAGE = 10

    QR_SIZE = 35
    QR_OFFSET_X = 4.8
    QR_OFFSET_Y = 12.3
    TEXT_OFFSET_X = 16
    TEXT_OFFSET_Y = 6

    QR_FOLDER = Path(os.path.join(STATIC_ROOT, 'qrcodes'))
    CARD_FILE = os.path.join(STATIC_ROOT, 'assets', card_image)
    QR_FOLDER.mkdir(parents=True, exist_ok=True)

    # ----------------------------
    # PDF Class Definition
    # ----------------------------
    class PDFCardGenerator(FPDF):

        def add_card(self, code_text: str, code_n: str, x: float, y: float):
            qr_path = QR_FOLDER / f"{code_text}.png"
            qrcode.make(code_text).save(qr_path)

            self.image(CARD_FILE, x=x, y=y, w=CARD_WIDTH, h=CARD_HEIGHT)
            self.image(str(qr_path), x=x + QR_OFFSET_X, y=y + QR_OFFSET_Y, w=QR_SIZE, h=QR_SIZE)

            self.set_font('Arial', '', 8)
            self.text(x=x + TEXT_OFFSET_X, y=y + TEXT_OFFSET_Y, txt=code_n)

    # ----------------------------
    # Generate PDF
    # ----------------------------
    pdf = PDFCardGenerator()
    pdf.set_title("oracard - Cards")
    pdf.add_page()

    x, y = MARGIN_X, MARGIN_Y
    card_count = 0

    for code_text, code_n in data:
        pdf.add_card(code_text, code_n, x, y)
        card_count += 1

        x += CARD_WIDTH + GAP_X

        if card_count % CARDS_PER_ROW == 0:
            x = MARGIN_X
            y += CARD_HEIGHT + GAP_Y

        if card_count % CARDS_PER_PAGE == 0:
            pdf.add_page()
            x, y = MARGIN_X, MARGIN_Y

    return pdf
