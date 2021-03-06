# rough format for area plot templates:
# lines starting with # are ignored
# each line consist in three values separated by spaces
# each template is preceded by a name enclosed in square brackets:
# [template name]
# tags
# month utchour freq
# 11    22      14.250
# month: number month, 1=January
# utchour: UTC time HOUR, 00 to 23
# freq: frequecy in MHz
# example: all months at midnight on 14.100 MHz
[All months midnight 14.100 Mhz]
#year month utchour freq
2010      01      00      14.10
2010      02      00      14.10
2010      03      00      14.10
2010      04      00      14.10
2010      05      00      14.10
2010      06      00      14.10
2010      07      00      14.10
2010      08      00      14.10
2010      09      00      14.10
2010      10      00      14.10
2010      11      00      14.10
2010      12      00      14.10

[All months at 1600z 7.500 MHz]
#month utchour freq
2010      01      16      7.5
2010      02      16      7.5
2010      03      16      7.5
2010      04      16      7.5
2010      05      16      7.5
2010      06      16      7.5
2010      07      16      7.5
2010      08      16      7.5
2010      09      16      7.5
2010      10      16      7.5
2010      11      16      7.5
2010      12      16      7.5


