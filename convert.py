import re
import datetime as dt
import random
from PIL import Image, ImageFont, ImageDraw

def clean_text(string):
    '''Just a bunch of unreadable regex to clean up the original NASA recording'''
    string_1 = re.sub('\f.*\n|Tape.*\n|\(.*\)\n|^\d*|\n\d*\n|\f|.*END OF TAPE.*\n|# # #|.*AIR-TO-GROUND.*\n|.*Three asterisks denote.*\n|\n\d*\n', '', string) #remove a lot of NASA notes
    string_2 = re.sub('.* (?=\d{2} \d{2} \d{2} \d{2})','', string_1) #remove comments preceding timestamps
    string_3 = re.sub('\n\d*\.\n|\n399*','', string_2) #remove numbers from lines
    string_4 = re.sub('\n(?!\d{2} \d{2} \d{2} \d{2})',' ', string_3) #Remove a newline not followed by a timestamp.
    string_5 = re.sub('\n\d{2} \d{2} \d{2} \d{2} [A-Z]{2,3}\n','', string_4) #remove any  orphaned timestamps
    string_6 = string_5.replace('  ', ' ').replace(' .', '.').replace('- -', '').replace('....', '...') #Easier than dealing with . as a special char
    string_7 = string_6.replace('--', '-').split('\n') # need to get rid of 1 line!

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

def wrap_text(string):
    '''split text into equal length strings without splitting words and pad'''
    length = len(string)
    space_indexes = []
    lines =  []
    start = 0
    step_init = 984
    target = step_init + 7 #As spaces after words are considered target needs to be step + 1/2 longest word
    step = step_init

    for i, letter in enumerate(string): #find all the spaces
        if letter == ' ':
            space_indexes.append(i)
    length_spaces = len(space_indexes)

    print('Found all spaces')

    while start + step < len(string):
        #Create a sliding search from as indexing space list is way too slow due to length - actually works somehow!
        current_percentage = round(start / length, 3)
        frame_start = int(max(0, (current_percentage - 0.005) * length_spaces))
        frame_end = int(max(0, (current_percentage + 0.005) * length_spaces))
        frame = space_indexes[frame_start:frame_end]
        assert start == 0  or frame[0] < start < frame[-1], "Reading frame misaligned! Position: {0[0]}, \
        Frame Start: {0[1]}, Frame End: {0[2]}".format([int(current_percentage * length), frame[0], frame[-1]])

        step = min(frame, key=lambda x:abs(x-(start + step))) - start #find closest space to desired line end
        line = string[start:start+step].lstrip() #Cut line and make sure there are no starting spaces
        line = pad_text(line, target)
        lines.append(line) #make a list of uniform length lines
        start, step = start + step + 1, step_init #step + 1 to remove the preceding space
    lines.append(string[start:]) #add whatever is left over in the string 
    return lines

def pad_text(text, target):
    '''Pad lines to required length using random(ish) space insertion'''
    spaces_req = target - len(text)
    line = ''
    for i in text: #make sure line is target length
        if i == ' ' and spaces_req > 0 and random.randrange(0,6) == 0: #randomness to prevent stacking spaces
            line += '  '
            spaces_req -= 1
        else:
            line += i
    return line

def draw_poster(poster_text, textsize, inp):
    '''split out and highlight the words'''
    top_pad = 0.25
    left_pad = 9
    font = ImageFont.truetype("NotCourierSans.otf", textsize) #This font needs to be monopaced!
    im = Image.new("RGBA", (9933, 14043), "black") #A1 Size
    draw = ImageDraw.Draw(im) #Set up sheet to draw on
    for i, text in enumerate(poster_text):
        if "1969-07-21 02:56:48 CDR" in text:
            quote = "1969-07-21 02:56:48 CDR (TRANQ) That's one small step for man, one giant leap for mankind."
            text = text.split(quote)
            width_p1, h1 = draw.textsize(text[0], font=font)
            width_quote, h2 = draw.textsize(quote, font=font)
            draw.text((left_pad, int((i + top_pad) * textsize)), text[0], font=font, fill=(255,255,255,255)) #All text padded 4 pixels left
            draw.text((left_pad + width_p1, int((i + top_pad) * textsize)), quote, font=font, fill=(255,0,0,255)) 
            draw.text((left_pad + width_p1 + width_quote, int((i + top_pad) * textsize)), text[1], font=font, fill=(255,255,255,255))
        else:
            draw.text((left_pad, int((i + top_pad) * textsize)), text, font=font, fill=(255,255,255,255))
    
    if inp == 'y':
        bleedx, bleedy = 10004, 14114
        bufferx, buffery = int((bleedx - 9933) / 2), int((bleedy - 14114) / 2)
        bleed_im = Image.new("RGBA", (10004, 14114), "black") #Bleed area for printing
        bleed_im.paste(im, (bufferx, buffery))
        bleed_im.save("output.png", "PNG")
    else:
        im.save("output.png", "PNG")

def output_text(text):
    with open('output.txt', 'w') as w:
        for line in text:
            w.write(line + '\n\n')

infile = open('apollo11.txt', 'r')
launch_date = dt.datetime(1969, 7, 16, 13, 32, 0) # set the time to 16/07/1969 13:32 UTC
textsize = 16

inp = ' '
while inp.lower() not in ['y', 'n']:
    inp = input('Would you like a bleed area? (Y/N): ').lower()

infile = infile.read()
print('Read infile')
clean_infile = clean_text(infile)
print('Cleaned infile')
outstr = set_timestamp(clean_infile, launch_date)
print('Set Timestamps')
wrapped_outstr = wrap_text(outstr)
print('Cut text into lines')
output_text(wrapped_outstr)
print('Saved text')
draw_poster(wrapped_outstr, textsize, inp)
print('Poster finished!')