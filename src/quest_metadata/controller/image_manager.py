"""
Module providing a singleton class for managing image operations.

Classes:
- ImageProps: NamedTuple representing properties for image operations.
- ImageManager: Singleton class for managing image resizing and cropping.
"""

from io import BytesIO
from typing import NamedTuple

from PIL.Image import Image
from PIL.Image import open as open_image
from typing_extensions import final

from base.classes import Singleton
from utils.async_runner import AsyncRunner


class ImageProps(NamedTuple):
    """
    NamedTuple representing properties for image manipulation.

    Attributes:
    - max_width (int | None): Maximum width of the image.
    - max_height (int | None): Maximum height of the image.
    - min_height (int | None): Minimum height of the image.
    - min_width (int | None): Minimum width of the image.
    - crop_height (int | None): Height for cropping the image.
    - crop_width (int | None): Width for cropping the image.
    """
    max_width: int | None = None
    max_height: int | None = None
    min_height: int | None = None
    min_width: int | None = None
    crop_height: int | None = None
    crop_width: int | None = None


@final
class ImageManager(Singleton):
    """
    Singleton class for managing image operations.

    Attributes:
    - _async_runner (AsyncRunner): Instance of the AsyncRunner class.

    Methods:
    - resize_image: Asynchronously resize an image based on specified
        properties.
    - resize_image_sync: Synchronously resize an image based on specified
        properties.
    - crop_image: Asynchronously crop an image based on specified properties.
    - crop_image_sync: Synchronously crop an image based on specified
        properties.
    - _get_bytes: Get bytes data from an image or bytes.
    - _get_image: Get a PIL Image instance from an image or bytes.
    """

    def __init__(
        self,
        async_runner: AsyncRunner,
    ) -> None:
        super().__init__()
        self._logger.info("Initializing image manager")
        self._async_runner: AsyncRunner = async_runner

    async def resize_image(
        self,
        image: bytes | Image,
        props: ImageProps
    ) -> bytes:
        """
        Asynchronously resize an image based on specified properties.

        Args:
        - image (bytes | Image): Input image data or PIL Image instance.
        - props (ImageProps): Image properties for resizing.

        Returns:
        - bytes: Resized image data.
        """
        return await self._async_runner.call(
            self.resize_image_sync,
            image=image,
            props=props
        )

    @classmethod
    def resize_image_sync(
        cls,
        image: bytes | Image,
        props: ImageProps
    ) -> bytes:
        """
        Synchronously resize an image based on specified properties.

        Args:
        - image (bytes | Image): Input image data or PIL Image instance.
        - props (ImageProps): Image properties for resizing.

        Returns:
        - bytes: Resized image data.
        """
        orig: Image = cls._get_image(image)
        ratio: float = orig.width / orig.height
        new_width: int = orig.width
        new_height: int = orig.height

        if props.max_height is not None and new_height > props.max_height:
            new_height = props.max_height
            new_width = int(new_height * ratio)

        if props.min_height is not None and new_height < props.min_height:
            new_height = props.min_height
            new_width = int(new_height * ratio)

        if props.max_width is not None and new_width > props.max_width:
            new_width = props.max_width
            new_height = int(new_width / ratio)

        if props.min_width is not None and new_width < props.min_width:
            new_width = props.min_width
            new_height = int(new_width / ratio)

        new_image: Image = orig.resize((new_width, new_height))
        return cls.crop_image_sync(new_image, props)

    async def crop_image(
        self,
        image: bytes | Image,
        props: ImageProps
    ) -> bytes:
        """
        Asynchronously crop an image based on specified properties.

        Args:
        - image (bytes | Image): Input image data or PIL Image instance.
        - props (ImageProps): Image properties for cropping.

        Returns:
        - bytes: Cropped image data.
        """
        return await self._async_runner.call(
            self.crop_image_sync,
            image=image,
            props=props
        )

    @classmethod
    def crop_image_sync(cls, image: bytes | Image, props: ImageProps) -> bytes:
        """
        Synchronously crop an image based on specified properties.

        Args:
        - image (bytes | Image): Input image data or PIL Image instance.
        - props (ImageProps): Image properties for cropping.

        Returns:
        - bytes: Cropped image data.
        """
        if props.crop_height is None and props.crop_width is None:
            return cls._get_bytes(image)
        orig: Image = cls._get_image(image)
        left = 0
        top = 0
        right: int = orig.width
        bottom: int = orig.height
        if props.crop_height is not None and orig.height > props.crop_height:
            top = int(orig.height / 2 - props.crop_height / 2)
            bottom = top + props.crop_height
        if props.crop_width is not None and orig.width > props.crop_width:
            left = int(orig.width / 2 - props.crop_width / 2)
            right = left + props.crop_width
        new_image: Image = orig.crop((left, top, right, bottom))
        return cls._get_bytes(new_image)

    @classmethod
    def _get_bytes(cls, image: Image | bytes) -> bytes:
        """
        Get bytes data from an image or bytes.

        Args:
        - image (Image | bytes): Input image data or PIL Image instance.

        Returns:
        - bytes: Image data in bytes.
        """
        if isinstance(image, bytes):
            return image
        with BytesIO() as new_buffer:
            image.save(new_buffer, format="png", optimize=True, quality=95)
            return new_buffer.getvalue()

    @classmethod
    def _get_image(cls, image: Image | bytes) -> Image:
        """
        Get a PIL Image instance from an image or bytes.

        Args:
        - image (Image | bytes): Input image data or PIL Image instance.

        Returns:
        - Image: PIL Image instance.
        """
        if isinstance(image, Image):
            return image
        return open_image(BytesIO(image))
