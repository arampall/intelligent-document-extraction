"""
Image preprocessing functions for document extraction.
"""

from pdf2image import convert_from_path
import cv2


def convert_pdf_to_image(file_path):
    """Convert PDF file to list of images.
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        List of PIL Image objects
    """
    # TODO: Add error handling for corrupted/invalid PDFs
    return convert_from_path(file_path, fmt='jpg')


def convert_to_grayscale(image):
    """Convert the image to grayscale.
    
    Args:
        image: Input image (numpy array)
        
    Returns:
        Grayscale image
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def reduce_noise(gray_image):
    """Apply Gaussian blur to reduce noise.
    
    Args:
        gray_image: Grayscale image
        
    Returns:
        Blurred image
    """
    # TODO: Make kernel size (5,5) configurable
    return cv2.GaussianBlur(gray_image, (5, 5), 0)


def binarize_image(blur_reduced_image):
    """Apply adaptive thresholding to create binary image.
    
    Args:
        blur_reduced_image: Noise-reduced grayscale image
        
    Returns:
        Binary (black and white) image
    """
    # TODO: Make block size (11) and constant (4) configurable
    return cv2.adaptiveThreshold(
        blur_reduced_image,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,  # Invert the colors (text becomes white because of matplotlib)
        11,  # Block size
        4   # Constant C
    )


def deskew_image(image):
    """Correct the skew of an image by finding the minimum area rectangle
    of the text block and rotating accordingly.
    
    Args:
        image: Binary image with white text on black background
        
    Returns:
        Deskewed image
    """
    # TODO: Add error handling for images with no text/contours
    
    # Find all non-zero (white) pixels
    coords = cv2.findNonZero(image)

    # Get the minimum area bounding rectangle
    # It returns (center(x,y), (width, height), angle of rotation)
    rect = cv2.minAreaRect(coords)
    angle = rect[-1] - 90

    # The `cv2.minAreaRect` angle has a specific range.
    # We need to adjust it for our rotation.
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = angle

    # Get the rotation matrix and rotate the image
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h),
                             flags=cv2.INTER_CUBIC,
                             borderMode=cv2.BORDER_REPLICATE)
    print(f"-> Detected skew angle: {angle:.2f} degrees")

    # Now, rotate the original grayscale image by the same angle
    (h, w) = rotated.shape
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    deskewed_gray = cv2.warpAffine(rotated, M, (w, h),
                                  flags=cv2.INTER_CUBIC,
                                  borderMode=cv2.BORDER_REPLICATE)

    return deskewed_gray


def process_one_image(image):
    """Apply all preprocessing steps to a single image.
    
    Args:
        image: Input image (PIL Image or numpy array)
        
    Returns:
        Preprocessed image ready for OCR
    """
    # TODO: Add logging instead of print statements
    image = convert_to_grayscale(image)
    print("-> Converted image to grayscale..")
    image = reduce_noise(image)
    print("-> Reduced noise in the image..")
    image = binarize_image(image)
    print("-> Binarized the image..")
    image = deskew_image(image)
    print("-> Corrected image orientation..")
    return image
