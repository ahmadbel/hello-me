"""
Image Processing Utilities Module
This module provides utilities for image processing and manipulation.
"""

import cv2
import numpy as np
import os
from PIL import Image, ImageEnhance, ImageFilter

def resize_image(image, width=None, height=None, inter=cv2.INTER_AREA):
    """
    Resize an image to the specified dimensions.
    
    Args:
        image (numpy.ndarray): The image to resize
        width (int, optional): Target width
        height (int, optional): Target height
        inter: Interpolation method
        
    Returns:
        numpy.ndarray: The resized image
    """
    # Initialize dimensions
    dim = None
    (h, w) = image.shape[:2]
    
    # If both width and height are None, return original image
    if width is None and height is None:
        return image
    
    # If width is None, calculate it from the height
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    
    # If height is None, calculate it from the width
    elif height is None:
        r = width / float(w)
        dim = (width, int(h * r))
    
    # Both width and height are specified
    else:
        dim = (width, height)
    
    # Resize the image
    resized = cv2.resize(image, dim, interpolation=inter)
    
    return resized

def enhance_image(image, brightness=1.0, contrast=1.0, sharpness=1.0):
    """
    Enhance an image by adjusting brightness, contrast, and sharpness.
    
    Args:
        image (numpy.ndarray): The image to enhance
        brightness (float): Brightness factor (1.0 = original)
        contrast (float): Contrast factor (1.0 = original)
        sharpness (float): Sharpness factor (1.0 = original)
        
    Returns:
        numpy.ndarray: The enhanced image
    """
    # Convert to PIL Image
    pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    # Apply enhancements
    if brightness != 1.0:
        enhancer = ImageEnhance.Brightness(pil_img)
        pil_img = enhancer.enhance(brightness)
    
    if contrast != 1.0:
        enhancer = ImageEnhance.Contrast(pil_img)
        pil_img = enhancer.enhance(contrast)
    
    if sharpness != 1.0:
        enhancer = ImageEnhance.Sharpness(pil_img)
        pil_img = enhancer.enhance(sharpness)
    
    # Convert back to OpenCV format
    enhanced = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    return enhanced

def normalize_lighting(image):
    """
    Normalize lighting in an image to improve face recognition in different lighting conditions.
    
    Args:
        image (numpy.ndarray): The image to normalize
        
    Returns:
        numpy.ndarray: The normalized image
    """
    # Convert to LAB color space
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    
    # Split the LAB image into L, A, and B channels
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE to the L channel
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    
    # Merge the CLAHE enhanced L channel with the original A and B channels
    merged = cv2.merge((cl, a, b))
    
    # Convert back to BGR color space
    normalized = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
    
    return normalized

def draw_face_box(image, face_location, color=(0, 255, 0), thickness=2, label=None, confidence=None):
    """
    Draw a box around a face with optional label and confidence.
    
    Args:
        image (numpy.ndarray): The image to draw on
        face_location (tuple): (x, y, w, h) coordinates of the face
        color (tuple): BGR color for the box
        thickness (int): Line thickness
        label (str, optional): Label to display
        confidence (float, optional): Confidence score to display
        
    Returns:
        numpy.ndarray: The image with the face box drawn
    """
    # Make a copy of the image
    result = image.copy()
    
    # Extract face location
    x, y, w, h = face_location
    
    # Draw the box
    cv2.rectangle(result, (x, y), (x + w, y + h), color, thickness)
    
    # If label is provided, draw it
    if label:
        # Prepare the label text
        label_text = label
        if confidence is not None:
            label_text += f" ({confidence:.1f}%)"
        
        # Calculate text size and position
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        font_thickness = 1
        text_size = cv2.getTextSize(label_text, font, font_scale, font_thickness)[0]
        
        # Draw background rectangle for text
        cv2.rectangle(result, (x, y - text_size[1] - 10), (x + text_size[0], y), color, -1)
        
        # Draw text
        cv2.putText(result, label_text, (x, y - 5), font, font_scale, (0, 0, 0), font_thickness)
    
    return result

def create_mosaic(images, rows, cols, padding=5):
    """
    Create a mosaic of images.
    
    Args:
        images (list): List of images to include in the mosaic
        rows (int): Number of rows in the mosaic
        cols (int): Number of columns in the mosaic
        padding (int): Padding between images
        
    Returns:
        numpy.ndarray: The mosaic image
    """
    # Ensure we have enough images
    n_images = len(images)
    if n_images == 0:
        return None
    
    # If we have fewer images than cells, pad with black images
    if n_images < rows * cols:
        # Get the shape of the first image
        h, w = images[0].shape[:2]
        channels = 3 if len(images[0].shape) > 2 else 1
        
        # Create black images to fill the remaining cells
        black_image = np.zeros((h, w, channels), dtype=np.uint8)
        images.extend([black_image] * (rows * cols - n_images))
    
    # Resize all images to the same size
    h, w = images[0].shape[:2]
    resized_images = [resize_image(img, width=w, height=h) for img in images]
    
    # Create the mosaic
    mosaic_h = h * rows + padding * (rows - 1)
    mosaic_w = w * cols + padding * (cols - 1)
    channels = 3 if len(images[0].shape) > 2 else 1
    
    mosaic = np.zeros((mosaic_h, mosaic_w, channels), dtype=np.uint8)
    
    # Place images in the mosaic
    for i in range(rows):
        for j in range(cols):
            idx = i * cols + j
            if idx < len(resized_images):
                y = i * (h + padding)
                x = j * (w + padding)
                mosaic[y:y+h, x:x+w] = resized_images[idx]
    
    return mosaic

def add_timestamp(image, timestamp=None, position='bottom-right', color=(255, 255, 255)):
    """
    Add a timestamp to an image.
    
    Args:
        image (numpy.ndarray): The image to add the timestamp to
        timestamp (str, optional): Timestamp string. If None, current time is used.
        position (str): Position of the timestamp ('top-left', 'top-right', 'bottom-left', 'bottom-right')
        color (tuple): BGR color for the timestamp
        
    Returns:
        numpy.ndarray: The image with the timestamp
    """
    import datetime
    
    # Make a copy of the image
    result = image.copy()
    
    # Get timestamp if not provided
    if timestamp is None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Set font properties
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    font_thickness = 1
    
    # Calculate text size
    text_size = cv2.getTextSize(timestamp, font, font_scale, font_thickness)[0]
    
    # Calculate position
    h, w = image.shape[:2]
    if position == 'top-left':
        x, y = 10, text_size[1] + 10
    elif position == 'top-right':
        x, y = w - text_size[0] - 10, text_size[1] + 10
    elif position == 'bottom-left':
        x, y = 10, h - 10
    else:  # bottom-right
        x, y = w - text_size[0] - 10, h - 10
    
    # Draw text
    cv2.putText(result, timestamp, (x, y), font, font_scale, color, font_thickness)
    
    return result
