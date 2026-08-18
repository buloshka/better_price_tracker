import os
import uuid
import httpx
import logging


logger = logging.getLogger("utils.images")

IMAGE_DIR = os.path.join("src", "static", "images", "products")


async def download_product_image(external_url: str) -> str | None:
    """
    Downloads an image from an external CDN and saves it locally.
    Returns the relative path for static hosting, or None if failed.
    """
    if not external_url:
        return None

    try:
        os.makedirs(IMAGE_DIR, exist_ok=True)

        file_extension = external_url.split(".")[-1].split("?")[0]
        if len(file_extension) > 4 or not file_extension.isalnum():
            file_extension = "jpg"

        filename = f"{uuid.uuid4()}.{file_extension}"
        full_path = os.path.join(IMAGE_DIR, filename)

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(external_url)
            if response.status_code == 200:
                with open(full_path, "wb") as f:
                    f.write(response.content)

                return f"images/products/{filename}"

            logger.warning(f"Failed to download image, status code: {response.status_code}")
            return None

    except Exception as exc:
        logger.error(f"Error during downloading product image: {exc}")
        return None
