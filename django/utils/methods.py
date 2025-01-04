from PIL import Image


def resize_scale(image, width=400, height=300):
    """Resize large uploaded image

     Scaling images will help reduce load time on the server and client.
     Pros:
        - Reduce client side load time. Images will load faster in client's browser.
        - Reduce storage's costs using cloud base services such as AWS S3 Bucket.
        - Improve overall UI Deign, making images uniformed throughout the entire website.
    Cons:
        - Slight tradeoff in load time, being that all image will be rescaled on every upload.
          This would add a load on the server, but the end results will highly
          outweigh this small computation time.
    """
    try:
        image = Image.open(image.path)
        if image.width > width or image.height > height:
            output_size = (width, height)
            image = image.resize(output_size, Image.ANTIALIAS)
            image.save(image.path)
    except:  # noqa
        pass
