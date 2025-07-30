from pydantic_settings import BaseSettings


class UploadSettings(BaseSettings):
    # Basic server-side validation for number of files and total size
    # (redundant if frontend validates, but good practice)
    MAX_FILES: int = 10
    MAX_TOTAL_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB


upload_settings = UploadSettings()
