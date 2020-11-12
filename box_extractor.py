import PyPDF2
from PyPDF2.utils import PdfReadError
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'/usr/local/Cellar/tesseract/4.1.1/bin/tesseract'


def extract_image(pdf_path):
    results = []
    with open(pdf_path, 'rb') as file:
        try:
            pdf_file = PyPDF2.PdfFileReader(file)
        except PdfReadError as e:
            print(e)
        print(1)
        for page in pdf_file.pages:
            decoder = page['/Resources']['/XObject']['/Im0']['/Filter']

            if decoder == '/DCTDecode':
                file_type = 'jpg'
            elif decoder == '/FlateDecode':
                file_type = 'png'
            elif decoder == '/JPXDecode':
                file_type = 'jp2'
            else:
                file_type = 'bmp'
            data = page['/Resources']['/XObject']['/Im0']._data
            results.append((data, file_type))
    return results


def save_images(image_data, name):
    with open(name, 'wb') as file:
        file.write(image_data)


def get_serial_number(file_path):
    numbers = []
    image = Image.open(file_path)
    text = pytesseract.image_to_string(image, 'rus')
    print(1)


if __name__ == '__main__':
    pdf_path = '/Users/ilaburcev/Desktop/data_mining_geek/4696_4.pdf'
    image = "/Users/ilaburcev/Desktop/data_mining_geek/4696_0.jpg"
    # images = extract_image(pdf_path)
    # _ = [save_images(itm[0], f'{4696}_{idx}.{itm[1]}') for idx, itm in enumerate(images)]
    get_serial_number(image)
    print(1)
