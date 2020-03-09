from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from random import randint as rint


# Get a UI card request, draw data on default card and return card path
async def request_ui_card():
    # Default size is 1000x650
    default_card = Image.open('support/defaultcard.png')
    draw = ImageDraw.Draw(default_card)
    # font = ImageFont.truetype(<font-file>, <font-size>)
    font_username = ImageFont.truetype('support/fonts/Montserrat-Black.ttf', 62)
    font_dates = ImageFont.truetype('support/fonts/Montserrat-Black.ttf', 20)
    font_member = ImageFont.truetype('support/fonts/Montserrat-Black.ttf', 40)
    font_stats = ImageFont.truetype('support/fonts/Montserrat-Black.ttf', 25)

    # draw username
    draw.text((230, 80), "LunarLite#7766", (255, 255, 255), font=font_username)

    # draw dates
    draw.text((225, 200), "01-10-2016", (255, 255, 255), font=font_dates)
    draw.text((395, 200), "27-07-2017", (255, 255, 255), font=font_dates)

    # draw xth member
    draw.text((570, 182), "1st Member", (255, 255, 255), font=font_member)

    # draw user stats
    draw.text((340, 340), "1234", (255, 255, 255), font=font_stats)
    draw.text((340, 400), "2341", (255, 255, 255), font=font_stats)
    draw.text((340, 460), "3412", (255, 255, 255), font=font_stats)
    draw.text((340, 520), "4123", (255, 255, 255), font=font_stats)

    # create gradient bg and overlay UI
    gradientbg = create_random_gradient_bg(default_card.size)
    gradientbg.save('support/gradient.png')
    gradientbg.paste(default_card, (0, 0), mask=default_card)

    # save file
    gradientbg.save('support/uicard.png')
    print("das gud")


def create_random_gradient_bg(size):
    bgimage = Image.new("RGB", (500, 500), "#FFFFFF")
    draw = ImageDraw.Draw(bgimage)

    r, g, b = rint(0, 255), rint(0, 255), rint(0, 255)
    dr = (rint(0, 255) - r) / 100.
    dg = (rint(0, 255) - g) / 100.
    db = (rint(0, 255) - b) / 100.
    for i in range(500):
        r, g, b = r + dr, g + dg, b + db
        draw.line((i, 0, i, 500), fill=(int(r), int(g), int(b)))

    bgimage = bgimage.resize(size)
    return bgimage
