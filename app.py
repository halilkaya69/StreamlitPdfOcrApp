import streamlit as st
import pdfplumber
import pytesseract
from PIL import Image
import io
import pandas as pd
import fitz  # PyMuPDF

class App:
    """
    PDF İçerik Çıkarma Uygulaması ana sınıfı.
    Bu sınıf, PDF dosyalarından metin, tablo ve görüntü çıkarma işlemlerini yönetir.
    Üç farklı yöntem sunar: PDFPlumber, PyTesseract (OCR) ve PyMuPDF.
    """
    def __init__(self):
        self.setup_page()
        self.setup_tesseract()
        
    def setup_page(self):
        """Streamlit sayfa yapılandırmasını ayarlar"""
        st.set_page_config(page_title="PDF OCR Uygulaması", layout="wide")
        
    def setup_tesseract(self):
        """
        Tesseract OCR yapılandırmasını ayarlar
        Not: Bu path'i kendi sisteminize göre güncellemeniz gerekebilir
        """
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
    def create_sidebar(self):
        """
        Streamlit kenar çubuğunu oluşturur ve kullanıcı seçimlerini yönetir
        Returns:
            tuple: (seçilen_yöntem, çıktı_formatı, yüklenen_dosya)
        """
        st.sidebar.title("PDF İşleme Seçenekleri")
        method = st.sidebar.selectbox(
            "Çıkarma Yöntemi Seçin",
            ["PDFPlumber", "PyTesseract (OCR)", "PyMuPDF"]
        )
        
        output_format = st.sidebar.radio(
            "Çıktı Formatı",
            ["Markdown", "JSON"]
        )
        
        uploaded_file = st.sidebar.file_uploader("Bir PDF dosyası yükleyin", type="pdf")
        
        return method, output_format, uploaded_file

    def extract_with_pdfplumber(self, pdf_file):
        """
        PDFPlumber kullanarak PDF'den içerik çıkarır
        Args:
            pdf_file: Yüklenen PDF dosyası
        Returns:
            tuple: (metin, tablolar, görseller)
        """
        text = ""
        tables = []
        images = []
        
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                # Metin çıkarma
                text += page.extract_text() + "\n\n"
                
                # Tablo çıkarma
                for table in page.extract_tables():
                    tables.append(table)
                
                # Görüntü çıkarma
                if page.images:
                    images.extend(page.images)
        
        return text, tables, images

    def extract_with_pytesseract(self, pdf_file):
        """
        PyTesseract OCR kullanarak PDF'den metin çıkarır
        Bu yöntem özellikle taranan (scanned) PDF'ler için uygundur
        Args:
            pdf_file: Yüklenen PDF dosyası
        Returns:
            tuple: (metin, tablolar(boş), görseller)
        """
        text = ""
        images = []
        
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap()
            img = Image.open(io.BytesIO(pix.tobytes()))
            
            # OCR ile metin çıkarma
            text += pytesseract.image_to_string(img, lang="tur") + "\n\n"
            images.append(img)
        
        return text, [], images

    def extract_with_pymupdf(self, pdf_file):
        """
        PyMuPDF kullanarak PDF'den içerik çıkarır
        Bu yöntem genellikle en hızlı seçenektir
        Args:
            pdf_file: Yüklenen PDF dosyası
        Returns:
            tuple: (metin, tablolar(boş), görseller)
        """
        text = ""
        images = []
        
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text() + "\n\n"
            
            # Görüntüleri çıkarma
            for img in page.get_images():
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                images.append(Image.open(io.BytesIO(image_bytes)))
        
        return text, [], images

    def display_results(self, text, tables, images, output_format):
        """
        Çıkarılan içeriği Streamlit arayüzünde gösterir
        Args:
            text (str): Çıkarılan metin
            tables (list): Çıkarılan tablolar
            images (list): Çıkarılan görseller
            output_format (str): Çıktı formatı (Markdown veya JSON)
        """
        if output_format == "Markdown":
            st.header("Çıkarılan Metin")
            st.markdown(text)
            
            if tables:
                st.header("Çıkarılan Tablolar")
                for i, table in enumerate(tables, 1):
                    st.subheader(f"Tablo {i}")
                    df = pd.DataFrame(table[1:], columns=table[0])
                    st.table(df)
            
            if images:
                st.header("Çıkarılan Görüntüler")
                for i, img in enumerate(images, 1):
                    st.subheader(f"Görüntü {i}")
                    st.image(img, use_column_width=True)
        
        else:  # JSON
            result = {
                "text": text,
                "tables": tables,
                "images_count": len(images)
            }
            st.json(result)

    def process_pdf(self, method, pdf_file):
        """
        Seçilen yönteme göre PDF işleme işlemini yönlendirir
        Args:
            method (str): Seçilen işleme yöntemi
            pdf_file: Yüklenen PDF dosyası
        Returns:
            tuple: (metin, tablolar, görseller)
        Raises:
            Exception: PDF işleme sırasında oluşan hatalar
        """
        try:
            if method == "PDFPlumber":
                return self.extract_with_pdfplumber(pdf_file)
            elif method == "PyTesseract (OCR)":
                return self.extract_with_pytesseract(pdf_file)
            elif method == "PyMuPDF":
                return self.extract_with_pymupdf(pdf_file)
            else:
                raise ValueError(f"Geçersiz metod seçimi: {method}")
        except Exception as e:
            raise Exception(f"PDF işlenirken bir hata oluştu ({method}): {str(e)}")
        
    def run(self):
        """
        Uygulamayı başlatır ve ana akışı yönetir
        """
        st.title("PDF İçerik Çıkarma Uygulaması")
        st.write("""
        Bu uygulama, PDF dosyalarından metin, tablo ve görüntüleri çıkarmak için farklı yöntemler sunar.
        Soldaki menüden bir yöntem seçin ve bir PDF dosyası yükleyin.
        """)

        # Sidebar'ı oluştur
        method, output_format, uploaded_file = self.create_sidebar()

        if uploaded_file is not None:
            st.sidebar.success("PDF başarıyla yüklendi!")
            
            try:
                with st.spinner(f"PDF işleniyor... ({method})"):
                    text, tables, images = self.process_pdf(method, uploaded_file)
                self.display_results(text, tables, images, output_format)
                st.success("PDF başarıyla işlendi!")
            except Exception as e:
                st.error(f"Bir hata oluştu: {str(e)}")
                st.info("Farklı bir yöntem denemeyi veya başka bir PDF dosyası yüklemeyi deneyin.")
        else:
            st.info("Lütfen soldaki menüden bir PDF dosyası yükleyin.")


