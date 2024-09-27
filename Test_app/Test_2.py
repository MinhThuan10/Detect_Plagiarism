
# Define the list of colors
color_hex = [
    '#FFB3BA', '#FF677D', '#D4A5A5', '#392F5A', '#31A2AC',
    '#61C0BF', '#6B4226', '#D9BF77', '#ACD8AA', '#FFE156',
    '#6B5B95', '#AB83A1', '#FF6F61', '#F5B041', '#F8CBA6',
    '#FFEBB0', '#EAB8E4', '#BBE4E7', '#F3C6C4', '#F9AFAF',
    '#FFB2D1', '#FBBF8A', '#D8E9A8', '#A4D7E1', '#D5AAFF',
    '#FFC3A0', '#B9FBC0', '#D9BF77', '#D7C9BF', '#A2A2F4',
    '#F5CBA1', '#D1C6E7', '#B6E3F4', '#B3D4FF', '#F1B6C1',
    '#B7E4C7', '#D7D5FF', '#FFB3E6', '#A6B6D4', '#F4D5C4',
    '#F5B941', '#EAE2B7', '#FFD166', '#00BFFF', '#E2E2D5',
    '#FFC4D6', '#A3D9FF', '#C3DA2D', '#FF7B00', '#F7B2A2',
    '#D2B2C3', '#F4D6A0', '#C2C2D6', '#FF758F', '#B6F5A2',
    '#C3C5C1', '#FFD6E8', '#FFE4B5', '#A9DAD6', '#D8A7D7',
    '#FFE156', '#F0EBD8', '#FF686B', '#C9C9FF', '#F2C8E6',
    '#FFBAC0', '#F1B6D1', '#FFB5D8', '#C8B5B5', '#E8CFCF',
    '#C1C2B8', '#C2E2D5', '#F7F5A0', '#F7B0D9', '#F8B9A8',
    '#FFCEFF', '#A1D5E4', '#B1B1E2', '#F8A3C6', '#F9FBB2',
    '#FFE156', '#F3D08A', '#FFC3C5', '#DAE1E7', '#BFDCE5',
    '#FFD5B5', '#F5D6D2', '#D6D5C9', '#E4D8DB', '#D1D5DA',
    '#B6E5B2', '#F4D8A5', '#F7C0D4', '#FFACB7', '#F8A7D2',
    '#FFC1A8', '#F8BCE9', '#D6A1B8', '#FFB3B3', '#FFC9B1',
    '#D4F0C8', '#B6A5D1', '#D6C6C1', '#F7A0B5', '#D6E6D5',
    '#D6A4E5', '#F1D9BF', '#F8A0A1', '#B3D1B7', '#D6C6C6',
    '#FFCB85', '#FFCDA2', '#FFD1C0', '#B1E9E1', '#F8F4A7',
    '#FFB3B3', '#D9D0D0', '#B8E8C3', '#F8B8B8', '#B9A6F5',
]

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

# Example usage:
color_rgb_converted = [hex_to_rgb(hex_code) for hex_code in color_hex]

print(color_rgb_converted)