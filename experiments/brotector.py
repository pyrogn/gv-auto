from seleniumbase import SB


# with SB(uc=True, headless2=True) as sb:
#     sb.uc_open("https://kaliiiiiiiiii.github.io/brotector/")
#     sb.save_screenshot("brotector_headless.png")

with SB(uc=True) as sb:
    sb.uc_open("https://kaliiiiiiiiii.github.io/brotector/")
    sb.reconnect(100)
    sb.save_screenshot("brotector_normal.png")
