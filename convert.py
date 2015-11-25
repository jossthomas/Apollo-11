import re
import datetime as dt
import random
from PIL import Image, ImageFont, ImageDraw

def wrap_text(string):
    '''split text into equal length strings without splitting words and pad'''
    space_indexes = []
    lines =  []
    start = 0
    step_init = 981
    target = step_init + 10
    step = step_init

    for i, letter in enumerate(string): #find all the spaces
        if letter == ' ':
            space_indexes.append(i)

    while start + step < len(string):
        while start + step not in space_indexes:
            step += 1
        line = string[start:start+step].lstrip() #Cut line and make sure there are no starting spaces

        spaces_add = target - len(line)
        line2 = ''
        
        for i in line: #try and make sure line is target length
            if i == ' ' and spaces_add > 0 and random.randrange(0,6) == 0: #randomness to prevent stacking spaces
                line2 += '  '
                spaces_add -= 1
            else:
                line2 += i

        lines.append(line2) #put newlines approximately every step_init chars
        start, step = start + step + 1, step_init #step + 1 to remove the preceding space
    lines.append(string[start:])

    return lines

def clean_text(string):
    string_1 = re.sub('\f.*\n|Tape.*\n|\(.*\)\n|^\d*|\n\d*\n|\f|.*END OF TAPE.*\n|# # #|.*AIR-TO-GROUND.*\n|.*Three asterisks denote.*\n|\n\d*\n', '', string) #remove a lot of NASA notes
    string_2 = re.sub('.* (?=\d{2} \d{2} \d{2} \d{2})','', string_1) #remove comments preceding timestamps
    string_3 = re.sub('\n\d*\.\n|\n399*','', string_2) #remove numbers from lines
    string_4 = re.sub('\n(?!\d{2} \d{2} \d{2} \d{2})',' ', string_3) #Remove a newline not followed by a timestamp.
    string_5 = re.sub('\n\d{2} \d{2} \d{2} \d{2} [A-Z]{2,3}\n','', string_4) #remove any  orphaned timestamps
    string_6 = string_5.replace('  ', ' ').replace(' .', '.').replace('- -', '').replace('....', '...') #Easier than dealing with . as a special char
    string_7 = string_6.split('\n')

    return string_7

def set_timestamp(text, launch_date):
    '''Nasa timestamps are in seconds from launch, want to replace with absolute times'''
    outstr = ''
    for i in text:
        if not i in ('', '\n', '\n ', ' '):
            time = [int(i) for i in re.findall('\d{2}', i[0:12])] #Find the timestamp and seperate it into its components (days, hours, minutes, seconds)
            transmission_time = launch_date + dt.timedelta(time[0], (time[1] * 3600) + (time[2] * 60) + time[3]) #add the launch date to the timestamp
            line = '{} {} '.format(transmission_time, i[12:]) 
            outstr += line
    return outstr

def draw_poster(poster_text, textsize):
    font = ImageFont.truetype("NotCourierSans.otf", textsize) #This font needs to be monopaced!
    im = Image.new("RGBA", (9922, 14036), "black")
    draw = ImageDraw.Draw(im)
    for i, text in enumerate(poster_text):
        if "That's  one small step for man, one giant leap for mankind." in text:
            #print(text)
            draw.text((4, int((i + 3/16) * textsize)), text, font=font, fill=(255,0,0,255))
        else:
            draw.text((4, int((i + 3/16) * textsize)), text, font=font, fill=(255,255,255,255))

    im.save("output.png", "PNG")

def output_text(text):
    with open('output.txt', 'w') as w:
        for line in text:
            w.write(line + '\n\n')

infile = open('apollo11.txt', 'r')
launch_date = dt.datetime(1969, 7, 16, 13, 32, 0) # set the time to 16/07/1969 13:32 UTC
textsize = 16

infile = infile.read()
clean_infile = clean_text(infile)
outstr = set_timestamp(clean_infile, launch_date)
wrapped_outstr = wrap_text(outstr)
output_text(wrapped_outstr)
draw_poster(wrapped_outstr, textsize)
