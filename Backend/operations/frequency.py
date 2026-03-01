import numpy as np
import cv2
from scipy import fftpack
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# def frequency_filter(image, filter_type='low', cutoff=30):
#     """
#     Apply frequency domain filter on all 3 RGB channels separately
#     """

#     # Split image into 3 channels (B, G, R in OpenCV)
#     channels = cv2.split(image)
#     filtered_channels = []

#     for channel in channels:
#         # 1) FFT
#         f = fftpack.fft2(channel)
#         fshift = fftpack.fftshift(f)

#         # 2) Create mask
#         rows, cols = channel.shape
#         crow, ccol = rows // 2, cols // 2

#         y, x = np.ogrid[:rows, :cols]
#         distance = np.sqrt((x - ccol)**2 + (y - crow)**2)

#         if filter_type == 'low':
#             mask = distance <= cutoff
#         else:
#             mask = distance > cutoff

#         # 3) Apply mask
#         fshift_filtered = fshift * mask

#         # 4) Inverse FFT
#         f_ishift = fftpack.ifftshift(fshift_filtered)
#         img_filtered = fftpack.ifft2(f_ishift)
#         img_filtered = np.abs(img_filtered)

#         # 5) Normalize
#         img_filtered = (img_filtered - img_filtered.min()) / \
#                        (img_filtered.max() - img_filtered.min()) * 255
#         img_filtered = img_filtered.astype(np.uint8)

#         filtered_channels.append(img_filtered)

#     # Merge filtered channels back into color image
#     filtered_image = cv2.merge(filtered_channels)

#     return filtered_image

def apply_frequency_filter(image, filter_type='low', cutoff=30):
    """
    Apply frequency filter on all 3 channels and return:
    - filtered colored image
    - visualization of frequency spectrum (from first channel)
    """

    # Split image into B, G, R channels
    channels = cv2.split(image)
    filtered_channels = []

    # We will compute visualization from the first channel only
    first_channel_spectrum = None
    first_channel_filtered_spectrum = None

    for idx, channel in enumerate(channels):

        # 1) FFT
        f = fftpack.fft2(channel)
        fshift = fftpack.fftshift(f)

        # Save original magnitude spectrum (only once)
        if idx == 0:
            first_channel_spectrum = 20 * np.log(np.abs(fshift) + 1)

        # 2) Create filter mask
        rows, cols = channel.shape
        crow, ccol = rows // 2, cols // 2

        y, x = np.ogrid[:rows, :cols]
        distance = np.sqrt((x - ccol)**2 + (y - crow)**2)

        if filter_type == 'low':
            mask = distance <= cutoff
        else:
            mask = distance > cutoff

        # 3) Apply filter
        fshift_filtered = fshift * mask

        # Save filtered magnitude spectrum (only once)
        if idx == 0:
            first_channel_filtered_spectrum = 20 * np.log(np.abs(fshift_filtered) + 1)

        # 4) Inverse FFT
        f_ishift = fftpack.ifftshift(fshift_filtered)
        img_filtered = fftpack.ifft2(f_ishift)
        img_filtered = np.abs(img_filtered)

        # 5) Normalize channel
        img_filtered = (img_filtered - img_filtered.min()) / \
                       (img_filtered.max() - img_filtered.min()) * 255
        img_filtered = img_filtered.astype(np.uint8)

        filtered_channels.append(img_filtered)

    # Merge filtered channels back to colored image
    filtered_image = cv2.merge(filtered_channels)

    # ---------------- Visualization ----------------
    plt.figure(figsize=(15, 5))

    plt.subplot(1, 3, 1)
    plt.imshow(first_channel_spectrum, cmap='gray')
    plt.title('Original Frequency Spectrum (Blue Channel)')
    plt.axis('off')

    plt.subplot(1, 3, 2)
    plt.imshow(mask, cmap='gray')
    plt.title(f'{filter_type.capitalize()}-pass Filter Mask')
    plt.axis('off')

    plt.subplot(1, 3, 3)
    plt.imshow(first_channel_filtered_spectrum, cmap='gray')
    plt.title('Filtered Frequency Spectrum (Blue Channel)')
    plt.axis('off')

    plt.tight_layout()

    # Convert figure to base64
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    spectrum_base64 = base64.b64encode(buf.getvalue()).decode()
    plt.close()

    return filtered_image, spectrum_base64