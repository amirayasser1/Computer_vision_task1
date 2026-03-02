import base64
from io import BytesIO
import matplotlib.pyplot as plt


def fig_to_base64():
    """
    Convert the current matplotlib figure to a base64-encoded PNG string.
    Closes the figure after conversion to free memory.
    """
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode()
    plt.close()
    return img_base64
