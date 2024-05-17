from typing import List, Tuple, Dict
import csv
import fitz


class Highlight:
    def __init__(self, text: str, highlight_color: str, text_color: str):
        self.text = text
        self.highlight_color = highlight_color
        self.text_color = text_color


class HighlightParser:
    @staticmethod
    def parse_highlight(annot: fitz.Annot, wordlist: List[Tuple[float, float, float, float, str, int, int, int]]) -> str:
        points = annot.vertices
        quad_count = int(len(points) / 4)
        sentences = []

        for i in range(quad_count):
            r = fitz.Quad(points[i * 4: i * 4 + 4]).rect
            words = [w for w in wordlist if fitz.Rect(w[:4]).intersects(r)]
            sentences.append(" ".join(w[4] for w in words))

        return " ".join(sentences)


class HighlightHandler:
    @staticmethod
    def handle_page(page) -> List[Highlight]:
        wordlist = page.get_text("words")
        wordlist.sort(key=lambda w: (w[3], w[0]))

        highlights = []
        annot = page.first_annot
        while annot:
            if annot.type[0] == 8:
                text = HighlightParser.parse_highlight(annot, wordlist)
                highlight_color = HighlightHandler.get_highlight_color(annot)
                text_color = HighlightHandler.get_text_color(wordlist)
                highlights.append(Highlight(text, highlight_color, text_color))
            annot = annot.next
        return highlights

    @staticmethod
    def get_highlight_color(annot: fitz.Annot) -> str:
        highlight_color = annot.colors.get("stroke", (0, 0, 0))
        return "#{:02X}{:02X}{:02X}".format(*map(lambda x: int(x * 255), highlight_color))

    @staticmethod
    def get_text_color(wordlist: List[Tuple[float, float, float, float, str, int, int, int]]) -> str:
        text_color = (0, 0, 0)
        if wordlist:
            text_color = wordlist[0][5:8]
        return "#{:02X}{:02X}{:02X}".format(*text_color)


def main(filepath: str) -> None:
    doc = fitz.open(filepath)
    highlights = []
    for page in doc:
        highlights += HighlightHandler.handle_page(page)

    with open("highlights.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["text", "highlight_color", "text_color"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for highlight in highlights:
            writer.writerow(highlight.__dict__)


if __name__ == "__main__":
    main("./sample.pdf")

