import pytesseract
from PIL import Image

# 画像ファイルのパス
image_path = 'XSS.jpg'

# 画像を開く
image = Image.open(image_path)

# 画像のテキストを読み取る
text = pytesseract.image_to_string(image, lang='jpn')

# 読み取られたテキストを出力する
print(text)

# ファイルにテキストを書き込む
output_file = '{}_text_jp.txt'.format(image_path[:-4])
with open(output_file, 'w', encoding='utf-8') as file:
    file.write(text)