import pymupdf  # import package PyMuPDF

# open input PDF 
doc = pymupdf.open("./test/Data/LuanVan.pdf")

needle = """THÀNH PHỐ HỒ CHÍ MINH"""

# Iterate through all pages in the document
for pno in range(len(doc)):
    page = doc[pno]
    
    # Search for the text on the current page
    quads = page.search_for(needle, quads=True)

    # If quads were found, highlight the text
    if quads:
        for quad in quads:
            page.add_highlight_annot(quad)
        print(f"Đã đánh dấu văn bản tại trang {pno + 1}")
    else:
        print(f"Không tìm thấy văn bản tại trang {pno + 1}")

# Save the document with the changes
doc.save("./test/Data/output.pdf")
print("Tài liệu đã được lưu với các đánh dấu.")
