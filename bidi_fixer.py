"""
Fix bidirectional text issues in Persian/English subtitles
Fixes mixed RTL (Persian) and LTR (English) text display problems
"""

import re

# Unicode control characters
RLM = '\u200F'  # Right-to-Left Mark
LRM = '\u200E'  # Left-to-Right Mark
RLE = '\u202B'  # Right-to-Left Embedding
PDF = '\u202C'  # Pop Directional Formatting

def fix_bidi_text(text: str) -> str:
    """
    Fix bidirectional text issues in mixed Persian/English text
    Uses RLE to force RTL, LRM around English words, and PDF to close
    """
    if not text or not text.strip():
        return text
    
    # Pattern to match English letters, numbers, and hyphens
    english_pattern = r'([A-Za-z0-9\-]+)'
    
    # Wrap English words with LRM marks to keep them LTR
    fixed_text = re.sub(english_pattern, lambda m: f'{LRM}{m.group(1)}{LRM}', text)
    
    # Wrap the entire text in RLE...PDF to force RTL direction
    fixed_text = f'{RLE}{fixed_text}{PDF}'
    
    return fixed_text.strip()


def fix_srt_file(srt_path: str, output_path: str = None):
    """
    Fix bidirectional text in an SRT subtitle file
    
    Args:
        srt_path: Path to input SRT file
        output_path: Path to output file (if None, overwrites input)
    """
    if output_path is None:
        output_path = srt_path
    
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Only fix text lines (not numbers or timestamps)
        if line.strip() and not line.strip().isdigit() and '-->' not in line:
            fixed_lines.append(fix_bidi_text(line))
        else:
            fixed_lines.append(line)
    
    fixed_content = '\n'.join(fixed_lines)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    return output_path


def test_bidi_fix():
    """Test the bidi fix function"""
    test_cases = [
        "من T-Y-O-Lو P-SOLهستم",
        "من یک معلم TYOLهستم",
        "این TESOLو TEYLاست",
        "من یک معلم زبان انگلیسی با مدارک TYOLو P-SOLهستم",
    ]
    
    print("=== Bidi Fix Test Results ===\n")
    for test in test_cases:
        fixed = fix_bidi_text(test)
        print(f"Original: {test}")
        print(f"Fixed:    {fixed}")
        print(f"Hex:      {fixed.encode('unicode-escape').decode('ascii')}")
        print("-" * 50)


if __name__ == '__main__':
    test_bidi_fix()
