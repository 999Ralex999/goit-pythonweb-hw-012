import cloudinary
import cloudinary.uploader
from app.conf.config import settings


class UploadFileService:
    """
    Service for uploading files to Cloudinary

    Attributes:
        cloud_name (str): The name of the cloud
        api_key (str): The API key for Cloudinary
        api_secret (str): The API secret for Cloudinary
    """

    def __init__(self, cloud_name, api_key, api_secret):
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username: str) -> str:
        """
        Upload a file to Cloudinary

        Args:
            file (UploadFile): The file to upload
            username (str): The username of the user

        Returns:
            str: The URL of the uploaded file
        """
        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url


upload_file_service = UploadFileService(
    settings.CLOUDINARY_NAME,
    settings.CLOUDINARY_API_KEY,
    settings.CLOUDINARY_API_SECRET,
)
