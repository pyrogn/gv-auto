from seleniumbase import SB


# with SB(uc=True, headless2=True) as sb:
#     sb.uc_open("https://kaliiiiiiiiii.github.io/brotector/")
#     sb.save_screenshot("brotector_headless.png")

with SB(uc=True, xvfb=True, headed=True) as sb:
    # with SB(uc=True, xvfb=True) as sb:
    # with SB(uc=True) as sb:
    # with SB(uc=True, headless2=True) as sb:
    sb.uc_open("https://kaliiiiiiiiii.github.io/brotector/")
    sb.save_screenshot("brotector_normal1.png")
    sb.reconnect(1)
    sb.save_screenshot("brotector_normal2.png")
    sb.uc_open("https://kaliiiiiiiiii.github.io/brotector/")
    sb.save_screenshot("brotector_normal3.png")
