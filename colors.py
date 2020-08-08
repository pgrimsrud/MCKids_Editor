
# palette information is stored in arrays in bank 1 at 0x0000, 0x0020, and 0x0040
# indexes are pulled from 0x69A-0x69D
# looks like that was copied from 0x6700 territory which was unpacked from somewhere in bank 9
# 0x69A gets 4 from bank 9 0xB93D offset 1
# 0x69B gets 2 from bank 9 0xB061 offset 2
# 0x69C gets 1 from bank 9 0xB061 offset 1
# 0x69D gets 0 from bank 9 0xB061 offset 0
    # the 9/B061 came from arrays at 0x8D, 0xB9, 0xE5 in bank 1. the offset came from 0x77D
# I think it fills slots from back to front and ends if it finds a duplicate?
# table of base background colors at bank 1 0x1F7 indexed by stage ID

colors = [
          ( 84, 84, 84,255), #       DARK_GRAY          0x00
          (  0, 30,116,255), #       DARK_GRAY_BLUE     0x01
          (  8, 16,144,255), #       DARK_BLUE          0x02
          ( 48,  0,136,255), #       DARK_PURPLE        0x03
          ( 68,  0,100,255), #       DARK_PINK          0x04
          ( 92,  0, 48,255), #       DARK_FUCHSIA       0x05
          ( 84,  4,  0,255), #       DARK_RED           0x06
          ( 60, 24,  0,255), #       DARK_ORANGE        0x07
          ( 32, 42,  0,255), #       DARK_TAN           0x08
          (  8, 58,  0,255), #       DARK_GREEN         0x09
          (  0, 64,  0,255), #       DARK_LIME_GREEN    0x0A
          (  0, 60,  0,255), #       DARK_SEAFOAM_GREEN 0x0B
          (  0, 50, 60,255), #       DARK_CYAN          0x0C
          (  0,  0,  0,255), #            BLACK_2       0x0D
          (  0,  0,  0,255), #            BLACK         0x0E
          (  0,  0,  0,255), #            BLACK_3       0x0F
          (152,150,152,255), #            GRAY          0x10
          (  8, 76,196,255), #            GRAY_BLUE     0x11
          ( 48, 50,236,255), #            BLUE          0x12
          ( 92, 30,228,255), #            PURPLE        0x13
          (136, 20,176,255), #            PINK          0x14
          (160, 20,100,255), #            FUCHSIA       0x15
          (152, 34, 32,255), #            RED           0x16
          (120, 60,  0,255), #            ORANGE        0x17
          ( 84, 90,  0,255), #            TAN           0x18
          ( 40,114,  0,255), #            GREEN         0x19
          (  8,124,  0,255), #            LIME_GREEN    0x1A
          (  0,118, 40,255), #            SEAFOAM_GREEN 0x1B
          (  0,102,120,255), #            CYAN          0x1C
          (  0,  0,  0,255), #            BLACK_4       0x1D
          (  0,  0,  0,255), #            BLACK_5       0x1E
          (  0,  0,  0,255), #            BLACK_6       0x1F
          (255,255,255,255), #      LIGHT_GRAY          0x20
          ( 76,154,236,255), #      LIGHT_GRAY_BLUE     0x21
          (120,124,236,255), #      LIGHT_BLUE          0x22
          (176, 98,236,255), #      LIGHT_PURPLE        0x23
          (228, 84,236,255), #      LIGHT_PINK          0x24
          (236, 88,180,255), #      LIGHT_FUCHSIA       0x25
          (236,106,100,255), #      LIGHT_RED           0x26
          (212,136, 32,255), #      LIGHT_ORANGE        0x27
          (160,170,  0,255), #      LIGHT_TAN           0x28
          (116,196,  0,255), #      LIGHT_GREEN         0x29
          ( 76,208, 32,255), #      LIGHT_LIME_GREEN    0x2A
          ( 56,204,108,255), #      LIGHT_SEAFOAM_GREEN 0x2B
          ( 56,180,204,255), #      LIGHT_CYAN          0x2C
          ( 60, 60, 60,255), #       DARK_GRAY_2        0x2D
          (  0,  0,  0,255), #            BLACK_7       0x2E
          (  0,  0,  0,255), #            BLACK_8       0x2F
          (255,255,255,255), #            WHITE         0x30
          (168,204,236,255), # VERY_LIGHT_GRAY_BLUE     0x31
          (188,188,236,255), # VERY_LIGHT_BLUE          0x32
          (212,178,236,255), # VERY_LIGHT_PURPLE        0x33
          (236,174,236,255), # VERY_LIGHT_PINK          0x34
          (236,174,212,255), # VERY_LIGHT_FUCHSIA       0x35
          (236,180,176,255), # VERY_LIGHT_RED           0x36
          (228,196,144,255), # VERY_LIGHT_ORANGE        0x37
          (204,210,120,255), # VERY_LIGHT_TAN           0x38
          (180,222,120,255), # VERY_LIGHT_GREEN         0x39
          (168,226,144,255), # VERY_LIGHT_LIME_GREEN    0x3A
          (152,226,180,255), # VERY_LIGHT_SEAFOAM_GREEN 0x3B
          (160,214,228,255), # VERY_LIGHT_CYAN          0x3C
          (160,162,160,255), #            GRAY_2        0x3D
          (  0,  0,  0,255), #            BLACK_9       0x3E
          (  0,  0,  0,255)] #            BLACK_10      0x3F


# need to figure out how the game does this
#palette = [(0,0,0),
#           (100,100,100),
#           (200,200,200),
#           (255,255,255)]