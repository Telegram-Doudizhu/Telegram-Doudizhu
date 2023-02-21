from cls.card import Card
from cls.cards import Cards
from PIL import Image, ImageDraw, ImageFilter, ImageFont

original_cards: dict[str, bytes] = {}

def generate_card(card: str) -> bytes:
    '''
        generate a card image by card string like "3S", "B"
        return the image in bytes
    '''
    im = Image.new("RGBA", (220, 320), "#FFFFFF00")
    if card == "B" or card == "R":
        color = "Black" if card == "B" else "Red"
        draw = ImageDraw.Draw(im)
        draw.rounded_rectangle([(4, 4), (216, 316)], 30, "#FFFFFF", "#000000", 5)
        draw.text((40, 42), "J", color, ImageFont.truetype("ARLRDBD.TTF", 50), "mm")
        draw.text((40, 87), "O", color, ImageFont.truetype("ARLRDBD.TTF", 50), "mm")
        draw.text((40, 132), "K", color, ImageFont.truetype("ARLRDBD.TTF", 50), "mm")
        draw.text((40, 177), "E", color, ImageFont.truetype("ARLRDBD.TTF", 50), "mm")
        draw.text((40, 222), "R", color, ImageFont.truetype("ARLRDBD.TTF", 50), "mm")
        # draw.text((110, 160), "🤡", color, ImageFont.truetype("seguiemj.ttf", 75), "mm")
        im = im.filter(ImageFilter.SMOOTH)
        im.save(f"./images/{card}.png")
    elif card[0:2] == "10":
        suit = {"S": "♠", "H": "♥", "C": "♣", "D": "♦"}
        color = "Black" if card[-1] == "S" or card[-1] == "C" else "Red"
        draw = ImageDraw.Draw(im)
        draw.rounded_rectangle([(4, 4), (216, 316)] ,30, "#FFFFFF", "#000000", 5)
        draw.text((28, 42), "1", color, ImageFont.truetype("ARLRDBD.TTF", 60), "mm")
        draw.text((52, 42), "0", color, ImageFont.truetype("ARLRDBD.TTF", 60), "mm")
        draw.text((40, 97), suit[card[-1]], color, ImageFont.truetype("YuGothB.ttc", 45), "mm")
        draw.text((110, 160), suit[card[-1]], color, ImageFont.truetype("YuGothB.ttc", 95), "mm")
        im = im.filter(ImageFilter.SMOOTH)
        im.save(f"./images/{card}.png")
    else:
        suit = {"S": "♠", "H": "♥", "C": "♣", "D": "♦"}
        color = "Black" if card[-1] == "S" or card[-1] == "C" else "Red"
        draw = ImageDraw.Draw(im)
        draw.rounded_rectangle([(4, 4), (216, 316)] ,30, "#FFFFFF", "#000000", 5)
        draw.text((40, 42), card[:-1], color, ImageFont.truetype("ARLRDBD.TTF", 60), "mm")
        draw.text((40, 97), suit[card[-1]], color, ImageFont.truetype("YuGothB.ttc", 45), "mm")
        draw.text((110, 160), suit[card[-1]], color, ImageFont.truetype("YuGothB.ttc", 95), "mm")
        im = im.filter(ImageFilter.SMOOTH)
        im.save(f"./images/{card}.png")
    return im.tobytes()

def draw_cards(cards: Cards) -> bytes:
    '''
        generate cards image by cards
        return the image in bytes
    '''
    card_list, corner = cards.cards, 0
    ret = Image.new("RGBA", (220 + (cards.length - 1) * 68, 320), "#FFFFFF00")
    for card in card_list:
        ret.alpha_composite(Image.frombytes("RGBA", (220, 320), original_cards[repr(card)]), (corner, 0))
        corner += 68
    return ret.tobytes()

def graph_init() -> None:
    '''
        initialization function for card drawing
        needs to be run before using other functions
        if the data in './images' folder is missing
        the initialization will redraw and save missing cards
    '''
    cards = [Card(c, j) for c in "34567890JQKA2" for j in range(4)]
    cards.extend([Card("B"), Card("R")])
    for card in cards:
        try:
            im = Image.open(f"./images/{repr(card)}.png")
            original_cards[repr(card)] = im.tobytes()
        except IOError:
            original_cards[repr(card)] = generate_card(repr(card))

__all__ = ('graph_init', 'draw_cards', )
