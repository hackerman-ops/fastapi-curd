import base64
import random
from PIL import Image, ImageDraw
from PIL import ImageFont
from PIL import ImageFilter
from io import BytesIO


def rnd_color():
    """
    生成随机颜色
    :return:
    """
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def rndChar():
    """
    生成随机字母
    :return:
    """
    random_num = str(random.randint(0, 9))
    random_low_alpha = chr(random.randint(97, 122))
    random_char = random.choice([random_num, random_low_alpha])
    return random_char


def check_code(
    width=100, height=40, char_length=5, font_file="FreeMono.ttf", font_size=30
):
    code = []
    img = Image.new(mode="RGB", size=(width, height), color=rnd_color())
    draw = ImageDraw.Draw(img, mode="RGB")

    # 写文字
    font = ImageFont.truetype(font_file, size=font_size)
    for i in range(char_length):
        char = rndChar()
        code.append(char)
        h = random.randint(0, 4)
        draw.text([i * width / char_length, h], char, font=font)  # type: ignore

    # 写干扰点
    for i in range(40):
        draw.point(
            [random.randint(0, width), random.randint(0, height)], fill=rnd_color()
        )

    # 写干扰圆圈
    for i in range(40):
        draw.point(
            [random.randint(0, width), random.randint(0, height)], fill=rnd_color()
        )
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.arc((x, y, x + 4, y + 4), 0, 90, fill=rnd_color())

    # 画干扰线
    for i in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)

        draw.line((x1, y1, x2, y2), fill=rnd_color())

    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    return img, "".join(code)


def get_validate_code():
    img, code = check_code()
    stream = BytesIO()
    img.save(stream, "jpeg")
    data = stream.getvalue()

    encode_data = base64.b64encode(data)
    data = str(encode_data, encoding="utf-8")
    img_data = "data:image/jpeg;base64,{data}".format(data=data)
    return img_data, code
