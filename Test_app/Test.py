color_hex = []
color_rbg = []

factor = 0.05  # Mức độ làm nhạt (0 là giữ nguyên màu gốc, 1 là trắng hoàn toàn)

for i in range(500):
    # Tạo mã màu hex
    color = "#{:06x}".format(i * 123456 % 0xFFFFFF)
    
    # Chuyển đổi sang RGB
    hex_color = color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255

    # Làm nhạt màu
    r = r + (1 - r) * factor
    g = g + (1 - g) * factor
    b = b + (1 - b) * factor
    color = (r, g, b)
    color_rbg.append(color)
    # Chuyển đổi lại sang hex và thêm vào mảng
    light_color = "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))
    color_hex.append(light_color)

# print(color_hex)
print(color_rbg)
