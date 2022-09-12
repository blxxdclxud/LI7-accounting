import os

FILES_PATH = os.path.abspath('./static/files')
print(FILES_PATH)
FONTS_PATH = os.path.abspath('./static/fonts')
DOWNLOADED_FILES_PATH = os.path.abspath('./static/downloaded_files')
SMTP_DATA = {
    "gmail": ("smtp.gmail.com", 465),
    "yandex": ("smtp.yandex.ru", 465),
    "mail": ("smtp.mail.ru", 465)
}
