"""Check actual encoded playback, including the zero-duration GIF regression."""
from pathlib import Path
import re
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def gif_timing(path):
    data = path.read_bytes()
    if data[:6] not in (b'GIF87a', b'GIF89a'):
        raise ValueError('Not a GIF')
    position = 13 + (3 * (2 ** ((data[10] & 7) + 1)) if data[10] & 128 else 0)
    delays, loop, pending = [], None, 0

    def blocks(start):
        payload = bytearray()
        while data[start]:
            size = data[start]
            payload.extend(data[start+1:start+1+size])
            start += size + 1
        return start + 1, bytes(payload)

    while position < len(data):
        marker = data[position]
        position += 1
        if marker == 0x3b:
            return delays, loop
        if marker == 0x21:
            label = data[position]
            position += 1
            if label == 0xf9:
                pending = int.from_bytes(data[position+2:position+4], 'little') * 10
                position += data[position] + 2
            elif label == 0xff:
                size = data[position]
                application = data[position+1:position+1+size]
                position, payload = blocks(position+1+size)
                if application == b'NETSCAPE2.0' and payload[:1] == b'\x01':
                    loop = int.from_bytes(payload[1:3], 'little')
            else:
                position, _ = blocks(position)
        elif marker == 0x2c:
            packed = data[position+8]
            position += 9
            if packed & 128:
                position += 3 * 2 ** ((packed & 7) + 1)
            position, _ = blocks(position+1)  # skip LZW minimum code size
            delays.append(pending)
            pending = 0
        else:
            raise ValueError('Unexpected GIF block')
    raise ValueError('Missing GIF trailer')


class MotionAssetsTests(unittest.TestCase):
    def test_every_embedded_visual_is_configured_to_animate(self):
        sources = re.findall(r'<img[^>]+src="([^"]+)"', (ROOT/'README.md').read_text(encoding='utf-8'))
        self.assertGreater(len(sources), 0)
        for source in sources:
            with self.subTest(source=source):
                self.assertTrue(source.startswith('./assets/'))
                file = ROOT / source.split('?', 1)[0]
                self.assertTrue(file.is_file(), source)
                if file.suffix == '.svg':
                    svg = file.read_text(encoding='utf-8')
                    ET.fromstring(svg)
                    self.assertRegex(svg, r'repeatCount="indefinite"|animation:[^;}]*infinite')
                else:
                    self.assertEqual(file.suffix, '.gif', 'A still image was embedded')
                    delays, loop = gif_timing(file)
                    self.assertGreater(len(delays), 1)
                    self.assertEqual(loop, 0)

    def test_encoded_gif_delays_are_readable_and_match_the_documented_loops(self):
        hero, hero_loop = gif_timing(ROOT/'assets/hero-motion.gif')
        tour, tour_loop = gif_timing(ROOT/'assets/queueless-interface-tour.gif')
        self.assertEqual(hero_loop, 0)
        self.assertGreaterEqual(len(hero), 24)
        self.assertTrue(all(delay >= 80 for delay in hero), hero)
        self.assertEqual(sum(hero), 6000)
        self.assertEqual(tour_loop, 0)
        self.assertEqual(tour, [1700, 1700, 1700, 1700])


if __name__ == '__main__':
    unittest.main()
