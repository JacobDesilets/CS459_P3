import re
from collections import Counter
from pathlib import Path

parent_dir = Path(__file__).parent
words_src = parent_dir / 'data' / 'big.txt'

words = Counter(re.findall(r'\w+', open(words_src).read().lower()))

print(words)