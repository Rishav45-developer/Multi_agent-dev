import zipfile
import io

def create_zip_from_files(files: dict) -> bytes:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename, code in files.items():
            zip_file.writestr(filename, code)
    zip_buffer.seek(0)
    return zip_buffer.getvalue()